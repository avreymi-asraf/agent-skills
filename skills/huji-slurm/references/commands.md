# Commands

Source: [HUJI CS Slurm wiki](https://wiki.cs.huji.ac.il/wiki/Slurm) plus standard Slurm man pages (`man sbatch`, etc.). Commands marked **HUJI** are local helpers that do not exist on other clusters. Each call loads the shared scheduler: one call is fine, a loop is not.

## Submitting

| Command | Purpose |
|---|---|
| `sbatch [opts] script.sh` | Queue a batch script (text script with shebang; not a binary). |
| `sbatch [opts] --wrap "cmd"` | Queue a one-line command without a script file. |
| `sbatch --parsable ...` | Print only the job id (may be `id;cluster`). |
| `sbatch --wait ...` | Block until the job ends; exit code = job's exit code. |
| `srun [opts] --pty bash` | Interactive shell on a compute node; blocks until resources are free. |
| `srun ... xterm` | GUI program (needs `ssh -X` to the gw); fragile, avoid. |

## Resource and placement flags (sbatch and srun)

| Flag | Meaning |
|---|---|
| `-c N` | CPUs per task (rounded up to even). |
| `--mem=32g` / `--mem-per-cpu=4g` | RAM per node / per CPU (pick one). |
| `-t, --time=D-HH` or `HH:MM:SS` | Time limit, e.g. `2-0`, `1-12`, `2:0:0`. |
| `--gres=gpu:<type>:N` | N GPUs of a type, e.g. `gpu:a5000:1`. |
| `--gres=gg:<group>:N` | **HUJI** — N GPUs from a GPU group (`g0`, `g4`, `g10`). |
| `--gres=gpu:1,vmem:24g` | **HUJI** — GPU with at least 24G VRAM (older form; check with groups). |
| `-n N` | N tasks (MPI-style multi-process); default 1. |
| `-M <cluster>[,<cluster>]` | Target cluster(s); a list picks the earliest start. |
| `--array=0-49%5` | 50 tasks, ≤ 5 at once; index in `$SLURM_ARRAY_TASK_ID`. |
| `--killable` | **HUJI** — preemptable job outside the lab limit; sets account + QOS. |
| `--requeue` | Put the job back in the queue if preempted. |
| `--qos=high\|normal\|low` | QOS; `high` ≤ 5 jobs per lab. |
| `--dependency=afterok:<id>` | Start only after job `<id>` succeeds. |
| `--mail-type=END,FAIL` | Email on end/failure instead of polling. |
| `-J, --job-name`, `-o, --output` | Name and log path (`%x` name, `%j` id, `%A`/`%a` array id/task). |

## Monitoring

| Command | Purpose |
|---|---|
| `squeue -M phoenix -u $USER` | Your queued and running jobs. |
| `ssqueue` | **HUJI** — squeue in a friendlier format. |
| `sacct -j <id> -X --format=JobID,State,Elapsed,ExitCode,MaxRSS` | Finished/running job state (`-X` = main step only). |
| `sacct -S 2026-10-01` / `sacct -l` / `sacct -a` | Since a date / long format / all users. |
| `ssacct`, `ssacct --res` | **HUJI** — sacct shortcuts; `--res` shows resources. |
| `sstat -j <id>` | Live memory/CPU of a running job. |
| `sinfo` / `ssinfo` | Partitions and nodes / **HUJI** per-node detail. |
| `susage` (`susage -a`) | **HUJI** — cluster resources and usage per user. |
| `slimits` | **HUJI** — your lab account's usage vs limits. Run before submitting. |
| `sprio` | Priority factors of pending jobs. |
| `nquota` | Disk quota (home). |

## Controlling

| Command | Purpose |
|---|---|
| `scancel <id>` / `scancel <id>_<task>` | Cancel a job / one array task. |
| `scontrol hold <id>` / `scontrol release <id>` | Keep a pending job from starting / let it start. |
| `scontrol requeue <id>` | Requeue a job (useful to test resume). |
| `scontrol show job <id>` | Full job record, including the pending Reason. |

## Pending Reasons (`squeue` NODELIST(REASON) column)

Only one reason is shown even if there are several. On some clusters jobs are submitted to all partitions, so a reason can come from a partition the job would never run on.

| Reason | Meaning | What to do |
|---|---|---|
| `Priority` | Higher-priority jobs are ahead. | Wait; smaller/shorter requests backfill sooner. |
| `Resources` | Waiting for free CPUs/RAM/GPUs. | Wait, or ask for a more common GPU (`gg:g0`). |
| `PartitionTimeLimit` | `--time` exceeds a partition's limit. | Lower `--time` (often harmless if another partition fits). |
| `AccountNotAllowed` | Account cannot use one of the partitions. | Usually harmless; if the job never starts, ask the system team. |
| `AssocGrpGRES` | The lab hit its simultaneous GPU limit. | Wait, or resubmit with `--killable --requeue`. |
| `AssocGrpLicense` | Too many simultaneous interactive jobs. | Close other `srun` shells or use `sbatch`. |

## Job states to act on (`sacct` State)

`COMPLETED` (done), `FAILED` (non-zero exit: read the log), `OUT_OF_MEMORY` (raise `--mem`), `TIMEOUT` (raise `--time` or resume), `PREEMPTED`/`REQUEUED` (killable, expected), `CANCELLED`, `NODE_FAIL` (infra; resubmit).

## Login and files

| Command | Purpose |
|---|---|
| `ssh -J <login>@bava.cs.huji.ac.il <login>@phoenix-gw` | Login from outside (OTP at bava, then CS password). |
| `ssh -fN phoenix` / `ssh -O check phoenix` / `ssh -O exit phoenix` | Open / check / close the SSH master (see SKILL [Access-and-SSH]). |
| `rsync -av phoenix:/cs/labs/<supervisor>/<login>/<path> ./` | Copy results back through the master. |
| `snapshot`, or `cd .snapshot` | Recover deleted/changed files from snapshots. |
| `module avail` / `module load <name>/<ver>` / `module load spack` | lmod software modules (CUDA, singularity, spack packages). |

Help: system@cs.huji.ac.il (lab directory, cluster access, global installs, IO-heavy jobs).
