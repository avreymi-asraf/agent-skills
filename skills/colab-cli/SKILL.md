---
name: colab-cli
description: Provision Google Colab cloud runtimes, manage secrets/credentials, execute remote Python scripts and notebooks, manage files, open SSH sessions, and run compute tasks directly from the terminal via the official Google Colab CLI. Use when running code on Google Colab GPUs/TPUs, managing Colab secrets, provisioning remote environments, streaming outputs, or using colab-cli in agentic workflows.
---

<colab-cli>

Google Colab CLI (`google-colab-cli`) connects local terminals and autonomous agents directly to Google Colab cloud runtimes. It enables allocating CPU, GPU (T4, L4, G4, A100, H100), or TPU (v5e1, v6e1) instances, managing secrets via Colab `userdata`, exploring data interactively, executing Python scripts/notebooks remotely with real-time output streaming, transferring files, and managing VM lifecycles without opening a browser.

### Topics Covered
- **Use [Installation-and-Auth]** for installing `google-colab-cli` and configuring ADC / OAuth2 scopes.
- **Use [Runtime-Management]** for provisioning (`new`), listing (`sessions`), inspecting (`status`), and stopping sessions.
- **Use [Interactive-Exploration]** for interactive data probing via REPL, console shell, and Colab web UI attachment (`url`).
- **Use [Execution-Modes]** for ephemeral jobs (`run`), persistent kernel execution (`exec`), and shebang scripts.
- **Use [File-and-Package-Management]** for transferring datasets, editing remote files (`edit`), and installing packages (`install`).
- **Use [Colab-Secrets-and-Credentials]** for getting API keys onto the VM: Colab UI secrets vs an uploaded `.env` for CLI runs.
- **Use [Colab-Notebook-Bootstrapping]** for self-cloning, secret loading, and setting up repository dependencies in Colab web-UI notebooks.
- **Use [Training-Runs]** for long model training from the CLI: background launch, polling, checkpoints, and result download.
- **Use [Agent-Automation-Patterns]** for headless scripts, stdout/stderr streams, error codes, and session isolation.
- **Use [Anti-Patterns-and-Common-Mistakes]** to avoid auth traps, scope errors, missing secrets, and idle resource costs.
- **Use [Examples]** for practical, end-to-end interactive and batch recipes.
- Reference [Command Reference](references/command-reference.md), [Secrets Guide](references/secrets-and-credentials.md), and [Agent Workflows](references/agent-workflows.md) for full details.

</colab-cli>

<Installation-and-Auth>

### Package Installation
```bash
# Recommended installation via uv
uv tool install google-colab-cli
```

### Authentication Strategies
The CLI supports two authentication modes via the global flag `--auth={oauth2,adc}` (default is `oauth2`, a one-time browser login cached locally). Both work headless once logged in; check with `colab whoami`. The user logs in, never the agent — no token needs to be handed to the agent.

1. **Application Default Credentials (ADC) — alternative for machines with `gcloud`**:
   Log in once with `gcloud` providing the 4 required Colab scopes, then pass `--auth=adc`:
   ```bash
   gcloud auth application-default login \
     --scopes=openid,\
   https://www.googleapis.com/auth/cloud-platform,\
   https://www.googleapis.com/auth/userinfo.email,\
   https://www.googleapis.com/auth/colaboratory
   ```
   - `userinfo.email`: Required for session backend (`colab.research.google.com`).
   - `colaboratory`: Required for keep-alive RPCs (`colab.pa.googleapis.com`).

2. **Verify Auth**:
   - `colab sessions`: Read-only check for server connectivity.
   - `colab whoami`: Displays active email, audience, scopes, and token expiration.

> [!NOTE]
> `colab auth` is for injecting *VM-side* GCP credentials into the running kernel for BigQuery/GCS. It is **not** used to authenticate the local CLI itself.

</Installation-and-Auth>

<Runtime-Management>

### 1. Persistent Session Management (`colab new` / `colab stop`)
Maintains runtime state and kernel memory across multiple commands:
```bash
# Provision named session (always specify -s to avoid random IDs)
colab new -s explore --gpu T4
# Provision with TPU
colab new -s tpu-run --tpu v5e1
# List active sessions and prune stale backend records
colab sessions
# Show hardware, memory, and kernel status
colab status -s explore
# Restart Jupyter kernel while keeping the VM allocated
colab restart-kernel -s explore
# Stop and release VM resources
colab stop -s explore
```
Supported accelerators: `--gpu` (`T4`, `L4`, `G4`, `A100`, `H100`), `--tpu` (`v5e1`, `v6e1`).

### 2. Ephemeral Job Runner (`colab run`)
Provisions a fresh VM, runs the script, streams output, and terminates the VM (everything on it is lost unless `--keep`):
```bash
colab run --gpu T4 --timeout 600 smoke_test.py
```
`colab run` has no upload step, so the script gets **no secrets** and no repo files. Use it only for short, self-contained, secret-free jobs; train with the session flow in [Training-Runs].

### 3. Timeouts and Limits
- `--timeout` on `run`/`exec` defaults to **30 s**. When it expires the CLI exits with `TimeoutError`, but the code **keeps running** on the kernel. Never rely on a huge `--timeout` for training — launch it in the background (see [Training-Runs]).
- A session lives at most **24 h** (keep-alive cap); idle sessions still burn compute units until `colab stop`.
- GPU availability depends on the Colab subscription tier; `colab new` fails if the tier lacks the accelerator.

</Runtime-Management>

<Interactive-Exploration>

Colab CLI bridges autonomous agents and human researchers across two complementary modalities:
- **For Agents (CLI/REPL Execution)**: `colab exec` and `colab repl` provide the fastest, headless vehicle to execute cells, inspect persistent in-memory variables, stream logs, and verify code directly on cloud GPUs without browser overhead.
- **For Humans (Visual Web Notebooks)**: `colab url -s <name> --open` connects the browser Web UI directly to that same persistent VM and kernel, allowing humans to visually inspect interactive HTML diffs, markdown narrative, and tables.
- **Interactive Probing Modes**:
  - **Interactive Python REPL (`colab repl`)**: Live Python shell on remote VM keeping variables/data in kernel memory: `colab repl -s explore --output-image ./plot.png`
  - **Remote Shell Console (`colab console`)**: Interactive tmux/bash session in `/content`: `colab console -s explore`
  - **Attach Colab Web Notebook (`colab url`)**: Connects browser UI directly to the CLI VM: `colab url -s explore --open`
  - **Step-by-Step Code Probing (`colab exec`)**: Runs code/scripts against persistent kernel memory: `echo "print(len(dataset))" | colab exec -s explore`

</Interactive-Exploration>

<Execution-Modes>

| Mode | Command | Behavior |
|---|---|---|
| **Ephemeral Run** | `colab run --gpu T4 script.py [args]` | Full lifecycle: new VM → execute → teardown |
| **Session Exec** | `colab exec -s <name> -f script.py` | Transmits local file to remote kernel; keeps state |
| **Piped Exec** | `echo "print(1)" \| colab exec -s <name>` | Executes piped code on remote kernel |
| **Notebook Exec** | `colab exec -s <name> -f notebook.ipynb` | Runs cells, writes output to `notebook_output.ipynb` |
| **Shell Console** | `colab console -s <name>` | Raw interactive TTY / tmux shell on remote VM |
| **Interactive REPL** | `colab repl -s <name>` | Python REPL on remote kernel |

</Execution-Modes>

<File-and-Package-Management>

Working directory on remote VMs is always `/content`.

```bash
# Install packages using high-performance uv inside VM
colab install -s explore torch transformers datasets
colab install -s explore -r requirements.txt
# Upload single files only — directories fail ("Local file not found"); tar them first
tar czf code.tgz -C ./local_dir . && colab upload -s explore code.tgz /content/code.tgz
echo 'import subprocess; subprocess.run("mkdir -p /content/code && tar xzf /content/code.tgz -C /content/code", shell=True, check=True)' | colab exec -s explore
# Download remote artifacts or checkpoints
colab download -s explore /content/checkpoint.pt ./checkpoints/checkpoint.pt
# List and delete remote files
colab ls -s explore /content
colab rm -s explore /content/temp_data.csv
```

</File-and-Package-Management>

<Colab-Secrets-and-Credentials>

Secrets reach the VM by one of two paths, depending on who started the kernel. Secret names follow the project's `.env.example` (e.g. `HF_TOKEN`, `WANDB_API_KEY`, `ANTHROPIC_API_KEY`).

| Started from | Secret source | How |
|---|---|---|
| **Colab web UI** (browser notebook) | 🔑 Secrets tab → `google.colab.userdata` | Bootstrap cell syncs `userdata` into `os.environ` |
| **CLI** (`colab new`/`exec`, agents) | Local gitignored `.env` | `colab upload` the file, load it on the VM |

**`userdata` does not work for CLI-started code.** `userdata.get()` raises `TimeoutException: ... Secrets can only be fetched when running from the Colab UI` (verified on CLI 0.6.0). `colab run` has no upload step, so it gets no secrets at all.

### CLI path: upload `.env`, load it on the VM
```bash
colab upload -s exp01 .env /content/.env      # the log records only the path, not the contents
```
```python
# first lines of the training script (or a separate load step via `colab exec -f`)
import os
if os.path.exists("/content/.env"):
    for line in open("/content/.env"):
        k, _, v = line.strip().partition("=")
        if k and v and not k.startswith("#"):
            os.environ.setdefault(k, v)
missing = [k for k in ("HF_TOKEN",) if not os.environ.get(k)]
if missing:
    raise SystemExit(f"missing secrets: {missing}")   # an infra failure, not a result
```
**Never put a secret value in code sent to `colab exec`** (`echo "os.environ['HF_TOKEN']='$HF_TOKEN'" | colab exec ...`): `colab log` stores every executed snippet verbatim in `~/.config/colab-cli/`. Never `print` a secret either — stdout is logged too.

Reference [Secrets Guide](references/secrets-and-credentials.md) for error handling and the provider map.

</Colab-Secrets-and-Credentials>

<Colab-Notebook-Bootstrapping>

When a notebook is opened in the **Colab web UI**, put this cell first. It clones the repo, installs it, and syncs UI secrets (the browser path only — CLI runs use the `.env` path above):

```python
import os, sys
IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
if IN_COLAB:
    REPO_DIR = "/content/<repo-name>"
    if not os.path.exists(REPO_DIR):
        !git clone https://github.com/<owner>/<repo-name>.git {REPO_DIR}
    %cd {REPO_DIR}
    !uv pip install --system -q -e .
    from google.colab import userdata
    for k in ["HF_TOKEN", "WANDB_API_KEY", "ANTHROPIC_API_KEY"]:  # match .env.example
        try:
            os.environ.setdefault(k, userdata.get(k))
        except Exception:
            print(f"secret {k} not set or not granted in the Secrets tab")
```

</Colab-Notebook-Bootstrapping>

<Training-Runs>

Training outlives any `--timeout` and the VM is disposable, so a training run is: **upload → launch in background → poll → download → stop**. Verified on CLI 0.6.0: background processes survive between `exec` calls; directory upload does not work.

```bash
S=exp-007-train
trap "colab stop -s $S || true" EXIT                    # guaranteed teardown
colab new -s $S --gpu L4
git -C .targets/worktrees/EXP-007 archive -o /tmp/code.tgz HEAD   # committed code only, no .env
colab upload -s $S /tmp/code.tgz /content/code.tgz
colab upload -s $S .env /content/.env
echo 'import subprocess; subprocess.run("mkdir -p /content/code && tar xzf /content/code.tgz -C /content/code && cd /content/code && uv sync -q", shell=True, check=True)' \
  | colab exec -s $S --timeout 900
# launch detached; the script loads /content/.env itself (see [Colab-Secrets-and-Credentials])
echo 'import subprocess; subprocess.Popen("cd /content/code && nohup uv run python train.py --out /content/out > /content/train.log 2>&1 & echo $! > /content/train.pid", shell=True)' \
  | colab exec -s $S
# poll (repeat until the process is gone)
echo 'import subprocess; print(subprocess.run("tail -5 /content/train.log; kill -0 $(cat /content/train.pid) && echo RUNNING || echo EXITED", shell=True, capture_output=True, text=True).stdout)' \
  | colab exec -s $S
colab download -s $S /content/out/metrics.json ./experiments/EXP-007/metrics.json  # destination is a file path, not a dir
colab download -s $S /content/train.log ./experiments/EXP-007/train.log
```

Rules for training runs:
- **`uv sync` builds a fresh venv** and re-downloads large wheels like torch (several minutes on first run). If it exceeds `--timeout`, the install keeps going on the VM — poll for `/content/code/.venv` before launching. Pin a CUDA build that matches the Colab GPU.
- **Checkpoint often and push off the VM.** A VM can be reclaimed mid-run (24 h cap, quota, preemption). Save checkpoints every N steps and push them to the Hugging Face Hub (`HF_TOKEN` with write access) so a new session can resume with `resume_from_checkpoint`. `colab drivemount` needs a human at a TTY, so agents cannot use Drive.
- **Small files home, large files to the Hub.** `colab download` takes one file at a time — bring back metrics, logs, and `results.json`; leave weights on the Hub.
- **Track live with W&B** (`WANDB_API_KEY` in `.env`); use the `wandb-for-trl` skill for TRL/SFTTrainer setup.
- **Smoke-test first**: run 20 steps on the cheapest GPU (`T4`) before renting `A100`/`H100`.
- **Record the run**: GPU type, wall-clock, CLI version, and the Hub checkpoint revision go into the experiment's `results.json` / `execution.md`.
- A missing secret, OOM, or reclaimed VM is an infra failure (`INFRA_INCONCLUSIVE`), never evidence against the hypothesis.

</Training-Runs>

<Agent-Automation-Patterns>

1. **Stream Separation**: `colab run` logs CLI status to **stderr** and program output to **stdout**:
   ```bash
   colab run --gpu T4 eval.py > output.json 2> run.log
   ```
2. **Exit Code Propagation**: `colab run` and `colab exec` propagate the script's exit status (`sys.exit(0)` → 0, `sys.exit(1)` → 1). Check `$?` for failures.
3. **Guaranteed Teardown with Bash Traps**:
   ```bash
   SESSION="job-$(date +%s)"
   trap "colab stop -s $SESSION || true" EXIT
   colab new -s "$SESSION" --gpu T4
   colab exec -s "$SESSION" -f eval.py --timeout 600   # short jobs only; training → [Training-Runs]
   colab download -s "$SESSION" /content/model.pt ./model.pt
   ```

</Agent-Automation-Patterns>

<Connecting-Skills>

- **Prerequisites**: Use `coding-principles` for clean code structure.
- **Companions**: Use `code-as-tools` to author modular tools before dispatching to Colab runtimes, and `wandb-for-trl` to track training metrics.
- **Lab loop**: Inside an experiment lab, `experiment-lab-loop` decides *what* to train; this skill runs it, and the downloaded metrics feed that experiment's `results.json`.
- **Successors**: Use `manage-skills` when updating or extending skill definitions.

</Connecting-Skills>

<Anti-Patterns-and-Common-Mistakes>

| Anti-Pattern | Root Cause | Correct Approach |
|---|---|---|
| Calling `userdata.get()` in a CLI-started run | Colab secrets only work from the web UI | Upload `.env` and load it on the VM |
| Passing a secret inline to `colab exec` | `colab log` stores executed code verbatim | Upload `.env`; never print secrets |
| Training in the foreground with a big `--timeout` | CLI times out (default 30 s) while the kernel keeps going | Background launch + poll ([Training-Runs]) |
| Keeping checkpoints only on the VM | VM is wiped on stop, reclaim, or `colab run` exit | Push checkpoints to the HF Hub during training |
| Running `colab auth` to fix local CLI 401/403 | Confusing VM GCP auth with CLI auth | Re-login (`colab whoami` to check); for ADC use all 4 scopes |
| Missing `-s <name>` on `colab new` | Auto-generates random 6-hex ID | Always name sessions explicitly (e.g. `-s exp01`) |
| Missing self-bootstrapping in Colab notebooks | `ModuleNotFoundError` when opened on Colab | Include the `IN_COLAB` git clone & editable install block in cell 1 |
| Leaving persistent VMs running | Incurring compute quota burn | Use `colab run` (auto-teardown) or bash `trap "colab stop" EXIT` |

</Anti-Patterns-and-Common-Mistakes>

<Examples>

### Interactive Probing & Experimentation Recipe
```bash
# 1. Provision a T4 GPU session
colab new -s probe --gpu T4
# 2. Install dependencies using uv inside VM
colab install -s probe datasets transformers torch litellm
# 3. Upload project modules
tar czf src.tgz src && colab upload -s probe src.tgz /content/src.tgz   # files only, no dirs
echo 'import subprocess; subprocess.run("tar xzf /content/src.tgz -C /content", shell=True, check=True)' | colab exec -s probe
# 4. Probing via REPL or sequential exec
echo "import sys; sys.path.append('/content'); import src" | colab exec -s probe
colab repl -s probe
# 5. Export interactive work to notebook and tear down
colab log -s probe -o exploration_session.ipynb
colab stop -s probe
```

</Examples>

<References>

- [Command Reference](references/command-reference.md): Complete list of flags, subcommands, accelerators, and options.
- [Secrets Guide](references/secrets-and-credentials.md): Managing Colab secrets (`google.colab.userdata`), permissions, and API key syncing.
- [Agent Workflows](references/agent-workflows.md): Unattended pipeline scripts, error recovery, and batch recipes.

</References>
