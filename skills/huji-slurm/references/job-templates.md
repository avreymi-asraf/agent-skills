# Job Templates

Copy into your repo (e.g. `jobs/`), replace every `<placeholder>`, and keep it in git so the run is reproducible. All templates assume `~/lab_env.sh` from the SKILL's [Storage-and-Environment] topic exists on the cluster. `#SBATCH` lines must come directly after the shebang, before any command; shell variables are **not** expanded inside `#SBATCH` lines, so log paths there are written in full.

## 1. `train.sbatch` — one GPU, resumable, safe to run as killable

```bash
#!/bin/bash
# log file = logs/<run-name>_<jobid>.out  (%x = job name, %j = job id)
#SBATCH --job-name=<run-name>        # no '/' here: it would break the %x log path
#SBATCH --output=/cs/labs/<supervisor>/<login>/logs/%x_%j.out
#SBATCH --time=16:0:0
#SBATCH -c8
#SBATCH --mem=32g
#SBATCH --gres=gg:g0:1
#SBATCH --mail-type=END,FAIL
##SBATCH --killable          # uncomment for killable (no lab limit, can be preempted)
##SBATCH --requeue           # uncomment together with --killable
set -euo pipefail
source ~/lab_env.sh
cd "$LAB/<repo>"

RUN_NAME=<run-name>                       # stable across requeues; do not use the job id
CKPT_DIR=$LAB/checkpoints/$RUN_NAME
mkdir -p "$CKPT_DIR"

echo "job=$SLURM_JOB_ID restart=${SLURM_RESTART_COUNT:-0} node=$(hostname) gpu=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv

# The training entry point must resume from the latest checkpoint in CKPT_DIR when one exists.
uv run --env-file .env python -m <package>.train \
  --config configs/<config>.yaml \
  --run-name "$RUN_NAME" \
  --output-dir "$CKPT_DIR" \
  --resume auto \
  --num-workers "${SLURM_CPUS_PER_TASK:-4}"
```

Submit: `mkdir -p $LAB/logs && sbatch jobs/train.sbatch`. Override at submit time without editing: `sbatch --killable --requeue --gres=gpu:l40s:1 jobs/train.sbatch`.

## 2. `sweep.sbatch` — job array, one config per task

```bash
#!/bin/bash
#SBATCH --job-name=<sweep-name>
#SBATCH --output=/cs/labs/<supervisor>/<login>/logs/%x_%A_%a.out
#SBATCH --time=8:0:0
#SBATCH -c4
#SBATCH --mem=24g
#SBATCH --gres=gg:g0:1
#SBATCH --killable
#SBATCH --requeue
#SBATCH --array=0-<N-1>%4            # N configs, at most 4 running at once
set -euo pipefail
source ~/lab_env.sh
cd "$LAB/<repo>"

CONFIGS=(configs/sweep/*.yaml)       # N files; the array range must match
CFG=${CONFIGS[$SLURM_ARRAY_TASK_ID]}
RUN_NAME=<sweep-name>-$(basename "$CFG" .yaml)

uv run --env-file .env python -m <package>.train \
  --config "$CFG" --run-name "$RUN_NAME" \
  --output-dir "$LAB/checkpoints/$RUN_NAME" --resume auto
```

Count configs before submitting: `ls configs/sweep/*.yaml | wc -l`. Cancel one task: `scancel <array-id>_<task>`; all: `scancel <array-id>`.

## 3. Interactive debugging (short, killable)

```bash
srun --killable -c4 --mem=16g --time=2:0:0 --gres=gg:g0:1 --job-name=debug --pty bash
# inside: source ~/lab_env.sh; cd $LAB/<repo>; uv run python -m <package>.train --max-steps 20
```

Exit the shell as soon as you are done; an idle interactive job still holds the GPU. If the GPU is not visible in an interactive job on a GPU-group cluster, add `--interactive` to `srun`, or `ssh` to the allocated node after the job starts (wiki workaround).

## 4. CPU-only job (preprocessing, CPU evals)

```bash
sbatch -M cinder -c16 --mem=32g --time=6:0:0 --job-name=prep \
  --output=/cs/labs/<supervisor>/<login>/logs/%x_%j.out \
  --wrap 'source ~/lab_env.sh && cd $LAB/<repo> && uv run python -m <package>.preprocess'
```

`-M cinder` (or `-M phoenix,cinder` to take whichever starts first) keeps GPU nodes free. Monitor with `squeue -M cinder`.

## 5. Chain jobs instead of polling

```bash
PRE=$(sbatch --parsable jobs/preprocess.sbatch | cut -d';' -f1)
TRN=$(sbatch --parsable --dependency=afterok:$PRE jobs/train.sbatch | cut -d';' -f1)
sbatch --dependency=afterok:$TRN jobs/eval.sbatch
```
