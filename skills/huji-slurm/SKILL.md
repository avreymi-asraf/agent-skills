---
name: huji-slurm
description: Runs training and evaluation jobs on the Hebrew University CS (HUJI CSE) Slurm clusters, mainly phoenix (and cinder), from a local machine or an agent over SSH. Covers login through the bava jump host with OTP, sbatch/srun/job arrays, HUJI-only flags (--killable, GPU groups gg:g0/g4/g10, vmem), lab limits (slimits), home-quota-safe uv/HF/W&B setup on /cs/labs, checkpoint-and-requeue training, and agent-driven submit-and-poll. Use whenever a job is to run on phoenix, phoenix-gw, cinder, or "the HUJI/CS cluster", when writing an sbatch script or #SBATCH header for it, choosing a GPU there, debugging a pending/killed job (Reasons, AssocGrpGRES), or moving a training run off Colab onto Slurm.
---

<huji-slurm>

The HUJI CSE system team runs several Slurm clusters. **phoenix** is the main GPU cluster (62 nodes, ~370 GPUs from rtx2080 up to h200); **cinder** holds phoenix nodes older than 7 years under the same policy. Jobs are submitted only from a gateway node `<cluster>-gw` (e.g. `phoenix-gw`). Most of the Slurm here is standard, but several flags exist **only at HUJI** and will fail or mean something else on any other cluster: `--killable`, the `gg:<group>:N` and `vmem:` gres, and the helper commands `slimits`, `susage`, `ssqueue`, `ssacct`, `ssinfo`.

**Status: derived from the official wiki (fetched 2026-10-31), not yet exercised on a real account.** Until someone runs [First-Login-Checklist] and records the results, treat anything marked *verify* as unconfirmed.

Sources: [Slurm](https://wiki.cs.huji.ac.il/wiki/Slurm), [Phoenix cluster policy](https://wiki.cs.huji.ac.il/wiki/Phoenix_cluster_policy), [Disk space](https://wiki.cs.huji.ac.il/wiki/Disk_space), [Python](https://wiki.cs.huji.ac.il/wiki/Python), [Connecting Remotely](https://wiki.cs.huji.ac.il/wiki/Connecting_Remotely), [Containers](https://wiki.cs.huji.ac.il/wiki/Containers), and the phoenix lab guide [AudioDeepLearningLab](https://wiki.cs.huji.ac.il/openspace/AudioDeepLearningLab) (source of `#SBATCH --killable` in scripts, the ≤ 8 CPU / 32 G per GPU rule, and the array launcher). The Slurm commands apply to every CS cluster (e.g. `hm`); the hardware and policy parts are phoenix/cinder only. HURCS (`wiki.rcs.huji.ac.il`, `/sci/labs`, the university-wide cluster) is a **different cluster with a different wiki**; nothing here applies to it.

### Topics Covered
- **Use [Access-and-SSH]** to log in (VPN vs bava jump host, OTP) and to set up a reusable SSH connection an agent can use.
- **Use [Storage-and-Environment]** before installing anything: home quota is 6–9 GB, so uv, HF, W&B and torch caches must live on `/cs/labs`.
- **Use [Requesting-Resources]** to size CPU, RAM, time and GPUs, and to choose a GPU type or group on phoenix.
- **Use [Accounts-Limits-and-Killable]** to understand lab limits, fairshare priority, QOS, and when to use `--killable --requeue`.
- **Use [Training-Job-Pattern]** for long training: checkpoint, resume after requeue, logs, secrets.
- **Use [Agent-Driven-Runs]** to submit and monitor jobs from Claude Code without loading the scheduler.
- **Use [First-Login-Checklist]** on first access to confirm the facts this skill could not verify.
- **Use [Anti-Patterns-and-Common-Mistakes]** before submitting anything.
- Reference [Phoenix Hardware](references/phoenix-hardware.md) for nodes, GPU types, VRAM and groups.
- Reference [Job Templates](references/job-templates.md) for copy-paste sbatch/srun scripts.
- Reference [Commands](references/commands.md) for every command, flag and pending Reason.

Related skills: `colab-cli` is the alternative (and fallback) GPU target. Whatever workflow the project uses to decide *what* runs (e.g. `experiment-lab-loop`) hands off here for *where and how* it runs. Use `code-as-tools` for the training code itself.

</huji-slurm>

<Access-and-SSH>

Two ways in ([Connecting Remotely](https://wiki.cs.huji.ac.il/wiki/Connecting_Remotely)):

- **On campus (Eduroam) or on the HUJI VPN** (log in to the VPN as `<ra-user>@huji.ac.il`): `ssh <login>@phoenix-gw` directly (the lab wiki also uses `phoenix.cs.huji.ac.il`). Only the CS (UNIX) password is needed.
- **From outside:** jump through `bava.cs.huji.ac.il` (alias `gw.cs.huji.ac.il`). `bava` asks for a **one-time password (OTP)**, then the target host asks for the CS password.
  ```bash
  ssh -J <login>@bava.cs.huji.ac.il <login>@phoenix-gw
  ```
  OTPs come from Google Authenticator (register at `registrar.cs.huji.ac.il`) or by SMS ([Password and OTP](https://wiki.cs.huji.ac.il/wiki/Password_and_OTP)).

**An agent cannot type an OTP.** The human opens one long-lived master connection, and the agent's commands reuse it. Local `~/.ssh/config`:

```sshconfig
Host bava
  HostName bava.cs.huji.ac.il
  User <login>
Host phoenix
  HostName phoenix-gw
  User <login>
  ProxyJump bava
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 12h
  ServerAliveInterval 60
```

The human runs `ssh -fN phoenix` once (types OTP + password). After that, `ssh phoenix '<cmd>'` runs with no prompt until the master exits. Check it with `ssh -O check phoenix`. If it is gone, the agent stops and asks the human to reopen it; it never retries in a loop (each failure at bava can burn an OTP). An SSH key in `~/.ssh/authorized_keys` on the CS side may remove the password step but not the OTP at bava — *verify*.

Do not run heavy work on `phoenix-gw` itself; it is a submission node. Public servers (`river`) cap CPU time at 40 min.

</Access-and-SSH>

<Storage-and-Environment>

| Path | Quota | Snapshots | Use for |
|---|---|---|---|
| `~` = `/cs/usr/<login>` | 6 G (stud) / 7 G (grad) / 9 G (phd) | 6 hourly, 14 daily, 4 weekly | dotfiles, small code only |
| `/cs/labs/<supervisor>/<login>` | lab share (~2 TB per faculty member) | 24 hourly, 7 daily, 4 weekly | repos, venvs, caches, checkpoints |
| `/cs/snapless/<supervisor>` | if the lab has one | none | large volatile data (heavy writes) |

**Nothing is backed up**; snapshots live on the same storage. Keep code in git and copy final results off the cluster. Check quota with `nquota`. Snapshots handle heavy writes badly: ask the system team before IO-heavy jobs, and prefer `/cs/snapless` for checkpoints if the lab has it.

The wiki teaches `virtualenv` + `pip`. This skill uses **uv**, so the same rule — everything big goes on lab storage — becomes these variables. Put them in one small file, `~/lab_env.sh`, and `source ~/lab_env.sh` at the top of every job script and every remote command. (CS accounts often default to tcsh — the wiki's examples use `setenv` — so do not rely on `~/.bashrc` being read; check with `echo $SHELL`.)

```bash
# ~/lab_env.sh
export LAB=/cs/labs/<supervisor>/<login>          # placeholder: fill in on first login
export PATH=$HOME/.local/bin:$PATH                # uv
export XDG_CACHE_HOME=$LAB/.cache
export UV_CACHE_DIR=$LAB/.cache/uv
export UV_PYTHON_INSTALL_DIR=$LAB/.local/share/uv/python
export HF_HOME=$LAB/.cache/huggingface
export TORCH_HOME=$LAB/.cache/torch
export WANDB_DIR=$LAB/wandb WANDB_CACHE_DIR=$LAB/.cache/wandb
export PIP_CACHE_DIR=$LAB/.cache/pip
```

Clone repos under `$LAB` so `uv sync` creates `.venv` there. Install uv itself with the official installer into `~/.local/bin` (one small binary). The system Python is 3.13 on debian13-5787; uv-managed Pythons avoid depending on it. A venv only works on the same Debian major release it was built on, so rebuild (`uv sync`) after an OS migration. If `~/.cache` already filled the home quota, move it to `$LAB` and symlink it back, as the wiki shows.

**CUDA:** PyTorch wheels installed by uv bundle their own CUDA runtime and need only the node's NVIDIA driver. `module load cuda/...` (lmod; see `module avail`) is needed only for compiling CUDA code (e.g. flash-attn from source). *Verify* the driver's CUDA version with `nvidia-smi` on a GPU node before pinning a torch build.

**Containers:** Docker does not run; Singularity does (`module load singularity`, `singularity exec --nv docker://<image> <cmd>`). Building images needs root, so build elsewhere. Shared images are in `/cs/containers`. Prefer uv; use a container only when a dependency cannot be installed with uv.

</Storage-and-Environment>

<Requesting-Resources>

Every job declares CPUs, RAM, time and GPUs. Too little gets the job killed or swapping; too much delays its start (backfill) and lowers the priority of all your and your lab's jobs.

- **CPUs (`-c N`):** rounded up to even (hyper-threading). Threads beyond N share the N CPUs. Rule of thumb from a phoenix lab: ≤ 8 CPUs and ≤ 32 G RAM per GPU. Set `num_workers` in the DataLoader to match `-c`.
- **RAM (`--mem=32g`):** per node. `--mem` and `--mem-per-cpu` are mutually exclusive.
- **Time (`--time=1-12` = 1 day 12 h, `2:0:0` = 2 h):** ask for a realistic bound, not the maximum. Jobs under ~5 min should be batched into one job.
- **GPUs on phoenix — HUJI-specific.** Since 2025-03-18 GPUs are grouped, and a generic `--gres=gpu:N` or `--gres=gg:N` **does not work**. Ask for either:
  - an exact type: `--gres=gpu:l40s:1`, or
  - any GPU from a group: `--gres=gg:g4:1`.

  | Group | VRAM | Types (count) |
  |---|---|---|
  | g0 | ≤ 40 G | rtx2080 10G (53), a10 22G (24), l4 23G (32), a5000 24G (64), rtx6000 24G (16) |
  | g4 | 40–100 G | a40 45G (16), l40s 45G (136), a6000 48G (8), rtxpro6000 96G (16) |
  | g10 | > 100 G | h200 140G (8) |

  The lab's limit is counted against the group it contributed to; a lab may have no quota in some groups (check `slimits`). The older `gpu:1,vmem:24g` form appears in older guides; whether `vmem` still combines with `gg:` is unknown — *verify*. Multi-GPU jobs must fit on one node (8 GPUs per node) and wait longer, especially as killable. Request more than one GPU only if the code actually uses them (DDP/FSDP).
- **bf16 trap:** g0 also holds rtx2080 (10 G) and rtx6000 (24 G), both Turing with no bf16/FlashAttention-2. For bf16 training on g0 ask for a type (`gpu:a5000:1`, `gpu:l4:1`, `gpu:a10:1`).
- **Sizing for LLM fine-tuning (estimate):** LoRA/QLoRA on a 7–8B model fits one 24 G Ampere g0 card; bf16 LoRA on 8B, or anything 13B+, wants g4 (l40s 45G); 70B or full fine-tuning needs g10 or multiple g4 cards. Measure peak memory with a short `srun` before a long run.

</Requesting-Resources>

<Accounts-Limits-and-Killable>

- **Account = lab.** Each PI's lab has a Slurm account limited to the CPUs/RAM/GPUs the lab contributed (e.g. 2 nodes × 2 g0 GPUs → at most 4 g0 GPUs in use at once). `slimits` shows usage vs limit; `susage` shows the cluster and per-user usage.
- **Priority** is separate from limits. It is mostly fairshare (past CPU time, 7-day half-life), plus job age and QOS. All labs have equal priority; paying more buys higher limits, not priority.
- **QOS:** `normal` (default), `high` (max 5 jobs per lab — don't abuse), `low` (runs only when idle). Do not set `killable*` QOS by hand.
- **Killable jobs** (`--killable`, HUJI-only): no lab limit, lowest priority, can be killed at any time by a normal job. Courses, projects and labs that contributed nothing run **only** as killable. `--killable` sets the account and QOS itself, so do not also pass `-A`/`--qos`. Add `--requeue` so a killed job goes back to the queue — and then the script must resume from a checkpoint ([Training-Job-Pattern]).
- **Lab etiquette:** one non-killable job for the run that matters, killable for sweeps and debugging; vacate resources when lab-mates ask.

</Accounts-Limits-and-Killable>

<Training-Job-Pattern>

A training job on Slurm must survive being killed and restarted. Templates are in [Job Templates](references/job-templates.md).

1. **Header:** `#SBATCH` lines go right after `#!/bin/bash`, before any command. Use `--job-name`, `--output=/cs/labs/<supervisor>/<login>/logs/%x_%j.out` (`%x` = job name; `%A_%a` for arrays; variables are not expanded in `#SBATCH` lines). **The logs directory must exist before `sbatch`**, or the job fails with no log.
2. **Environment:** `source ~/lab_env.sh` (cache variables from [Storage-and-Environment]), `cd` into the repo, run with `uv run --env-file .env ...` (no `source activate`).
3. **Checkpoint and resume:** save every N steps (and at the end) to `$LAB/checkpoints/<run-name>/`, with a stable run name (not the job id) so a requeued job finds it. Names such as `bert-lr-sweep`, `qlora-8b` or `0a-myrepo-rl/grpo` are examples only, not a naming recommendation. A `/` in the name breaks `--job-name` and the `%x` log path (it points into a missing directory), so use a sanitized form there (`${RUN_NAME//\//-}` → `0a-myrepo-rl-grpo`). On start, resume from the latest checkpoint if one exists (HF Trainer: `resume_from_checkpoint=True`; W&B: `id=<run-name>, resume="allow"`). `SLURM_RESTART_COUNT` tells the script it was requeued.
4. **Secrets:** put a `.env` at `$LAB/<repo>/.env` with `chmod 600`, created by hand on the cluster (`scp` it, never commit it). Lab directories are usually readable by lab members, and snapshots keep old copies, so use narrowly scoped tokens. Never echo secrets into the job log.
5. **Background processes:** all processes end when the batch script ends; if the script starts something with `&`, finish with `wait`.
6. **Many runs:** use one `--array=0-N%P` job, picking the config by `$SLURM_ARRAY_TASK_ID` — never a loop of `sbatch`.
7. **Results back home:** copy metrics and small outputs to your machine (`rsync` through the SSH master, e.g. into `./outputs/<run-name>/`), then run your evaluation/post-processing step locally. Leave large checkpoints on `/cs/labs` unless needed.

</Training-Job-Pattern>

<Agent-Driven-Runs>

The scheduler is shared; HUJI asks that no one loop over `sbatch` or `squeue`/`watch`.

Send each remote step as a script on stdin to `bash -s`. This works whatever the login shell is (tcsh included), and a quoted heredoc (`<<'EOF'`) keeps `$LAB` for the cluster side.

```bash
# 1. sync code (<branch> already pushed to the git remote) and submit; --parsable prints only the job id
JOB=$(ssh phoenix bash -s <<'EOF'
{ source ~/lab_env.sh && cd "$LAB/<repo>" && mkdir -p "$LAB/logs"
  git fetch -q && git checkout -q <branch> && git pull -q && uv sync -q; } >&2   # setup output -> stderr
cd "$LAB/<repo>" && sbatch --parsable jobs/train.sbatch                # only the job id -> stdout
EOF
)
# 2. check rarely (every 20-30 min, via ScheduleWakeup/Monitor, not a tight loop)
ssh phoenix "sacct -j $JOB -X --format=JobID,State,Elapsed,ExitCode -n"
ssh phoenix bash -s <<EOF
source ~/lab_env.sh && tail -n 50 "\$LAB/logs/<run-name>_$JOB.out"
EOF
```

`sbatch --parsable` may print `<id>;<cluster>`; keep the part before `;`. For end-of-job notice use `--mail-type=END,FAIL` and for pipelines `--dependency=afterok:$JOB` instead of polling. `sbatch --wait` blocks until the job ends and returns its exit code; it suits short jobs only, because a dropped SSH session loses the wait (the job keeps running). States to act on: `PENDING` (read the Reason — see [Commands](references/commands.md)), `PREEMPTED`/`REQUEUED` (killable, normal), `OUT_OF_MEMORY`, `TIMEOUT`, `FAILED`. Cluster outages, OOM from a wrong `--mem`, or a missing `.env` are infrastructure failures: fix and rerun, never report them as a result of the run.

</Agent-Driven-Runs>

<First-Login-Checklist>

Run once when access arrives, then remove the *verify* marks in this skill and record the answers wherever the project keeps infrastructure notes:

1. Can log in through bava with OTP; the ControlMaster from [Access-and-SSH] works for `ssh phoenix hostname`.
2. Lab path: `ls -ld /cs/labs/<supervisor>/<login>` exists and is writable; note its quota (`nquota`). Ask the system team (system@cs.huji.ac.il) for the directory and phoenix access if missing.
3. `slimits` — which account, which GPU groups the lab has quota in (maybe none → killable only).
4. `sinfo -o '%P %l %G' | head` — partitions, time limits, gres names as actually spelled.
5. `srun --killable -c2 --mem=8g --time=0:15:0 --gres=gg:g0:1 --pty bash`, then `nvidia-smi` (driver CUDA version) and check `--gres=gpu:1,vmem:24g` is accepted or rejected.
6. `echo $SHELL`; create `~/lab_env.sh`; install uv; `uv sync` a repo under `$LAB` with the cache variables set; confirm `du -sh ~` did not grow.
7. Submit a 5-minute `--killable --requeue` test of the train template; `scontrol requeue <id>` it and confirm it resumes from its checkpoint.
8. Whether killed jobs get a warning signal before termination (affects checkpoint frequency).

</First-Login-Checklist>

<Anti-Patterns-and-Common-Mistakes>

- **`--gres=gpu:2` on phoenix** → rejected. Use `gpu:<type>:2` or `gg:<group>:2`.
- **pip/uv/HF caches in `~`** → "Disk quota exceeded" in minutes (6–9 G home). Set the cache variables first.
- **`--output=logs/...` with no `logs/` dir** → job fails silently. `mkdir -p` first.
- **Max time "just in case"** → starts days later. Estimate from a short run.
- **`for i in ...; do sbatch ...`** or `watch squeue` → loads the scheduler. Use `--array`, `--dependency`, `--mail-type`, rare `sacct`.
- **Killable without checkpoints** → a requeued job restarts from step 0, forever.
- **`--killable` plus `-A`/`--qos`** → conflicts; `--killable` sets both.
- **Overnight idle `srun --pty` shell** holding a GPU → hurts lab fairshare and blocks others.
- **Odd `-c`** gets rounded up; asking 1 CPU means 2.
- **Training on `phoenix-gw` or `river`** → killed, and against policy.
- **Applying these flags on HURCS or another university's cluster** → `--killable`, `gg:`, `slimits` are HUJI CSE-only.

</Anti-Patterns-and-Common-Mistakes>

<huji-slurm-reference>

- [references/phoenix-hardware.md](references/phoenix-hardware.md) — full phoenix and cinder node tables, GPU totals per type and group, policy dates. Read when choosing a GPU type or a node feature.
- [references/job-templates.md](references/job-templates.md) — `train.sbatch` (single GPU, killable, resumable), job-array sweep, interactive debug `srun`, CPU-only preprocessing. Copy and fill in placeholders.
- [references/commands.md](references/commands.md) — sbatch/srun flags, monitoring commands (`squeue`, `sacct`, `sstat`, HUJI `ss*` helpers), hold/release/cancel, pending Reasons and what to do about each.

No scripts: every action is one Slurm or SSH command, documented in the references.

</huji-slurm-reference>

<examples>

**Moving a QLoRA fine-tuning run from Colab to phoenix (after the checklist passed).**

1. The run: QLoRA on an 8B model, ~10 h. That fits one 24 G card → `--gres=gg:g0:1 -c8 --mem=32g --time=16:0:0`. `slimits` shows the lab has g0 quota, so the main run is non-killable; the 3-seed sweep goes as a killable array.
2. Copy `references/job-templates.md` → `jobs/train.sbatch` in the repo; set `--job-name=qlora-8b`, `RUN_NAME=qlora-8b`, `uv run --env-file .env python -m train --run-name $RUN_NAME --resume auto`.
3. `ssh -O check phoenix` fails → ask the human to run `ssh -fN phoenix`. Do not retry.
4. Push `<branch>`; over the master run `git fetch && git checkout <branch> && uv sync && mkdir -p $LAB/logs` in the cluster clone; submit with `--parsable`, keep the id.
5. Thirty minutes later `sacct` shows `PENDING (AssocGrpGRES)`: the lab's g0 GPUs are all in use. Options: wait, or resubmit with `--killable --requeue` (safe, since the script resumes).
6. Mistake caught: the first job died with `OUT_OF_MEMORY` at 20 min — a resource error, not evidence about the method. Rerun with `--mem=48g`.
7. When `COMPLETED`, `rsync -a phoenix:/cs/labs/<supervisor>/<login>/checkpoints/qlora-8b/metrics/ ./outputs/qlora-8b/` and run your evaluation step locally. (A non-interactive `ssh` does not source `~/lab_env.sh`, so write the full path rather than `$LAB`.)

</examples>
