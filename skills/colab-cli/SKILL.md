---
name: colab-cli
description: Rents Google Colab CPU/GPU/TPU runtimes from the terminal with the official Google Colab CLI (`colab`, package `google-colab-cli`) and runs code on them - sessions, `colab exec`/`colab run`, notebooks, `colab ssh` shell commands, file transfer, packages, secrets via an uploaded .env, and background training runs. Covers headless login for machines without a browser (Claude Code cloud sessions, CI runners, remote VMs). Use when running training or evaluation on Colab GPUs/TPUs (T4, L4, A100, H100, v5e1, v6e1), when the user mentions Colab, colab-cli, or `colab new`/`exec`/`run`/`ssh`, or when an agent needs a cloud GPU without a local one.
---

<colab-cli>

The Google Colab CLI (`colab`, PyPI `google-colab-cli`, source `github.com/googlecolab/google-colab-cli`) rents a Colab VM and drives it from a terminal: a **session** is a live Jupyter kernel on a billable VM. `colab new` allocates it, `exec`/`ssh`/`upload`/`download` work on it, `colab stop` releases it. Kernel state persists between `colab exec` calls of the same session. Everything runs in `/content` on the VM.

Written against **CLI 0.8.0** (Nov 2026). Commands marked *(live)* were run against a real runtime; the rest are checked against `colab <cmd> --help` or the upstream docs. The CLI also ships its own short guide: `colab skill` and `colab readme`.

### Topics Covered
- **Use [Installation-and-Auth]** to install, log in (OAuth2 or ADC), and check the login.
- **Use [Runtime-Management]** for sessions, accelerators, high-RAM, liveness, timeouts, and compute units.
- **Use [Running-Code]** to pick between `exec`, `run`, notebooks, `ssh -- CMD`, and `repl`.
- **Use [Files-and-Packages]** for single-file upload/download, moving directories with tar over `colab ssh`, and `colab install`.
- **Use [Secrets]** to get API keys onto the VM (uploaded `.env`; Colab UI secrets do not work from the CLI).
- **Use [Notebook-Bootstrapping]** for notebooks a human opens in the Colab web UI.
- **Use [Training-Runs]** for long jobs: upload → background launch → poll → download → stop.
- **Use [Headless-and-Cloud]** when the agent runs where no browser exists (Claude Code cloud, CI, VMs).
- **Use [Agent-Automation-Patterns]** for exit codes, streams, teardown traps, and parallel runs.
- **Use [Anti-Patterns-and-Common-Mistakes]** and **[Examples]** before a first run.
- References: [Command Reference](references/command-reference.md), [Secrets Guide](references/secrets-and-credentials.md), [Agent Workflows](references/agent-workflows.md), [Remote Machines](references/remote-machines.md).

</colab-cli>

<Installation-and-Auth>

Install: `uv tool install google-colab-cli` (or `pipx`/`pip`). Upgrade: `uv tool upgrade google-colab-cli`; `colab update` only checks (`--install` runs `pip install -U`, Linux only). Version: `colab version`. Linux and macOS only.

The global `--auth {oauth2,adc}` flag goes **before** the subcommand (`colab --auth=adc sessions`). Default: `oauth2`. (The bundled `colab skill`/`readme` still say `adc`; `--help` and the code say `oauth2`.)

1. **OAuth2 (default)**: the first command prints a Google URL; the user opens it in any browser, approves, and pastes the code back into the terminal (copy-paste flow, no localhost callback). The token is saved in the **OS keyring** (service `google-colab-cli`, user `oauth_token`). Where no keyring exists (WSL, containers, CI) every command prints two `Could not ... OS keyring` warnings and the token stays in the legacy file `~/.config/colab-cli/token.json`. *(live)*
2. **ADC**: `colab --auth=adc ...` uses Google Application Default Credentials: `GOOGLE_APPLICATION_CREDENTIALS`, the `gcloud` ADC file, or a metadata server. User credentials need these scopes:
   ```bash
   gcloud auth application-default login --scopes=openid,\
   https://www.googleapis.com/auth/cloud-platform,\
   https://www.googleapis.com/auth/userinfo.email,\
   https://www.googleapis.com/auth/colaboratory
   ```
3. **Check**: `colab whoami` (hidden command: provider, email, scopes, expiry) and `colab sessions`. A 401/403 is almost always a missing login or scope.

The **user** logs in, never the agent: an agent must not run the login flow and wait on the paste. For machines without a browser see [Headless-and-Cloud].

`colab auth -s <name>` is unrelated: it gives the *VM's* kernel GCP credentials (BigQuery/GCS), needs a human at a TTY, and never fixes CLI auth errors.

</Installation-and-Auth>

<Runtime-Management>

```bash
colab new -s <session> --gpu T4          # CPU if neither --gpu nor --tpu (live: CPU, ~4 s)
colab new -s <session> --tpu v6e1
colab new -s <session> --gpu A100 --high-mem   # high-RAM shape, Colab Pro/Pro+ only
colab sessions                           # server-side list; prunes stale local entries (live)
colab status -s <session>                # hardware, shape, IDLE/BUSY (live)
colab restart-kernel -s <session>        # reset kernel state, keep the VM
colab stop -s <session>                  # release the VM (live)
colab usage                              # compute-unit balance, burn rate, active assignments (live)
```

- Accelerators: `--gpu` `T4`, `L4`, `G4`, `A100`, `H100`; `--tpu` `v5e1`, `v6e1`. Availability depends on the Colab plan. A 400 on an accelerator means no quota/entitlement: retry with `T4` or CPU. A "precondition failed" refusal means too many sessions or a temporary capacity limit.
- **Always pass `-s <session>`**; omitted names become random hex. Use `[a-z0-9-]` only: the name becomes a file name under `~/.config/colab-cli/history/`, so derive it from a run name: `S=$(printf '%s' "$RUN" | tr -c 'a-z0-9-' '-')`.
- With exactly one active session, `-s` may be omitted. With several, it is required.
- **Liveness**: the CLI runs no keep-alive daemon any more (removed Sep 2026); the backend keeps a VM alive while its kernel is active and reclaims it after inactivity or the plan's maximum runtime lifetime (Colab policy, often quoted as up to 24 h; not verified). An idle but allocated VM still burns compute units until `colab stop`.
- **Timeouts**: `--timeout` on `exec`/`run` is an **idle** limit, the seconds allowed *without output* (default 30, `0` = no limit). On expiry the CLI exits 1 with `TimeoutError: ... no message from the kernel for Ns`, while the code may keep running on the kernel. *(live)*

</Runtime-Management>

<Running-Code>

| Need | Command | Notes |
|---|---|---|
| Python on a live kernel | `colab exec -s S -f job.py` or `echo 'code' \| colab exec -s S` | File is read locally and sent; no upload needed. State persists. *(live)* |
| Notebook | `colab exec -s S -f nb.ipynb` | Runs code cells in order, writes `nb_output.ipynb` next to it; `# @title X` labels a cell. *(live)* |
| One-off job on a fresh VM | `colab run --gpu T4 job.py --lr 0.1` | new → exec → stop. Args go to `sys.argv`, `__name__ == "__main__"`, script exit code is returned. *(live)* Shebang: `#!/usr/bin/env -S colab run --gpu T4`. `--keep` keeps the VM. |
| Shell command | `colab ssh -s S -- 'nvidia-smi \| head -5'` | Runs in `/content`, returns the command's exit code, stdin/stdout piped byte-exact. *(live)* Needs local `ssh` + ed25519/ecdsa key (`-i KEY`; RSA rejected). |
| Shell without ssh | `echo '!df -h /content' \| colab exec -s S` | Each `!` line is its own shell; start multi-line scripts with `%%bash`. *(live)* |
| Interactive shell / IDE | `colab ssh -s S` (human) or `ProxyCommand colab ssh --proxy-mode -s S` in `~/.ssh/config` | `colab console` was **removed** in 0.8.0. |
| Python REPL | `colab repl -s S` (human) | Agents pipe stdin to it or use `exec`. |
| Browser on the same kernel | `colab url -s S` (`--open` to launch) | Human inspection of the CLI's VM. |

- `--env KEY=VALUE` (repeatable) on `exec`/`run` sets `os.environ` in the kernel by prepending Python code. That code is stored verbatim in the session history: **never pass secrets with `--env`** ([Secrets]).
- `colab ssh -- CMD` never creates a runtime. Bare `colab ssh` with no session **creates a billable one**: agents always pass `-s` and `-- CMD`.
- One argument after `--` is a shell line; several arguments are an exact argv. Pass untrusted values as separate arguments, never inside a shell line or `!` line.
- `--output-image PATH` on `exec`/`repl` saves plotted PNG/JPEG output.

</Running-Code>

<Files-and-Packages>

```bash
colab upload -s S ./data.csv /content/data.csv            # single files only (live)
colab download -s S /content/out/metrics.json ./outputs/<run-name>/metrics.json   # destination = file path (live)
colab ls -s S /content ; colab rm -s S /content/tmp.bin
colab install -s S torch transformers ; colab install -s S -r requirements.txt    # uv pip --system, pip fallback (live)
colab edit -s S /content/config.yaml                       # opens in local $EDITOR (human)
```

`upload` rejects directories ("Local file not found"); `download` rejects a remote directory and a local directory target. Move directories as a tar stream over `colab ssh` *(live)*:

```bash
tar cz -C ./src . | colab ssh -s S -- 'mkdir -p /content/code && tar xz -C /content/code'
colab ssh -s S -- 'tar cz -C /content/out .' </dev/null | tar xz -C ./outputs/<run-name>
```

Without ssh: `tar czf code.tgz -C ./src .`, `colab upload` the file, then `echo '!mkdir -p /content/code && tar xzf /content/code.tgz -C /content/code' | colab exec -s S`.

`colab drivemount` mounts Google Drive but needs a human at a TTY, so agents cannot use Drive.

</Files-and-Packages>

<Secrets>

| Kernel started from | Secret source | How |
|---|---|---|
| **Colab web UI** | 🔑 Secrets tab → `google.colab.userdata` | Bootstrap cell copies them into `os.environ` ([Notebook-Bootstrapping]) |
| **CLI** (`new`/`exec`/`run`/`ssh`) | A local, gitignored `.env` | `colab upload` it, load it at the top of the script |

`userdata.get()` from CLI-started code raises `TimeoutException: Requesting secret HF_TOKEN timed out. Secrets can only be fetched when running from the Colab UI.` *(live, 0.8.0)*

```bash
colab upload -s S .env /content/.env        # history records the path only, not the contents
```
```python
import os   # first lines of the job script
if os.path.exists("/content/.env"):
    for line in open("/content/.env"):
        k, _, v = line.strip().partition("=")
        if k and v and not k.startswith("#"):
            os.environ.setdefault(k, v.strip("'\""))
missing = [k for k in ("HF_TOKEN",) if not os.environ.get(k)]
if missing:
    raise SystemExit(f"missing secrets: {missing}")   # setup failure, not a result
```

**Never** put a secret in code or flags sent to the VM: `colab exec`/`run` code and `--env` values are written verbatim to `~/.config/colab-cli/history/<session>.jsonl` *(live)* and `--env` also shows in `ps` and shell history. Never print secrets: outputs are logged too. `colab run` has no upload step, so a job that needs keys uses `new` → `upload .env` → `exec` → `stop`. Details: [Secrets Guide](references/secrets-and-credentials.md).

</Secrets>

<Notebook-Bootstrapping>

For a notebook a **human opens in the Colab web UI** (not CLI runs), make the first cell set up the repo and UI secrets:

```python
import os, sys
if "google.colab" in sys.modules:
    REPO_DIR = "/content/<repo-name>"
    if not os.path.exists(REPO_DIR):
        !git clone https://github.com/<owner>/<repo-name>.git {REPO_DIR}
    %cd {REPO_DIR}
    !uv pip install --system -q -e .
    from google.colab import userdata
    for k in ["HF_TOKEN", "WANDB_API_KEY"]:          # the project's secret names
        try:
            os.environ.setdefault(k, userdata.get(k))
        except Exception:
            print(f"secret {k} not set or not granted in the Secrets tab")
```

</Notebook-Bootstrapping>

<Training-Runs>

Training outlives any idle timeout and any single connection, and the VM is disposable. A training run is **upload → background launch → poll → download → stop**. Background processes survive between `exec`/`ssh` calls *(live)*.

```bash
RUN=bert-lr-sweep                                  # any run name (see [Examples])
S=$(printf '%s' "$RUN" | tr -c 'a-z0-9-' '-')      # safe session name
OUT=./outputs/$RUN; mkdir -p "$OUT"
trap 'colab stop -s "$S" || true' EXIT             # guaranteed teardown
colab new -s "$S" --gpu L4
git archive HEAD | gzip | colab ssh -s "$S" -- 'mkdir -p /content/code && tar xz -C /content/code'  # committed code, no .env
colab upload -s "$S" .env /content/.env
colab ssh -s "$S" -- 'cd /content/code && uv sync -q' </dev/null          # long installs: no idle timeout over ssh
colab ssh -s "$S" -- 'cd /content/code && nohup uv run python train.py --out /content/out > /content/train.log 2>&1 & echo $! > /content/train.pid' </dev/null
# poll until EXITED
colab ssh -s "$S" -- 'tail -5 /content/train.log; kill -0 $(cat /content/train.pid) 2>/dev/null && echo RUNNING || echo EXITED' </dev/null
colab download -s "$S" /content/out/metrics.json "$OUT/metrics.json"
colab download -s "$S" /content/train.log "$OUT/train.log"
```

- Without ssh, run the same shell lines as `!` lines through `colab exec` (or `subprocess.Popen` in Python).
- `uv sync` builds a fresh venv and downloads large wheels like torch (minutes). Pin a CUDA build that matches the GPU.
- **Checkpoint often, off the VM.** A VM can be reclaimed mid-run. Push checkpoints to the Hugging Face Hub (or other remote storage) every N steps so a new session can resume.
- **Small files home, large files to the Hub.** Bring back metrics, logs, and result JSON; leave weights remote.
- **Smoke-test first**: a few steps on `T4` (or `colab run` for a secret-free check) before renting `A100`/`H100`.
- Record GPU type, wall-clock, CLI version, and checkpoint revision with the results.
- A missing secret, OOM, quota refusal, or reclaimed VM is a setup failure, not evidence about the idea being tested.

</Training-Runs>

<Headless-and-Cloud>

On a machine with no browser (Claude Code cloud session, CI runner, remote VM), the login is an `authorized_user` JSON the user exports once from their own logged-in CLI and stores in the platform's secret store as `COLAB_TOKEN_JSON`. Each session writes it to a file and uses ADC:

```bash
uv tool install google-colab-cli
umask 077; mkdir -p ~/.config/colab-cli ~/.ssh
printf '%s' "$COLAB_TOKEN_JSON" > ~/.config/colab-cli/adc.json
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/colab-cli/adc.json
colab() { command colab --auth=adc "$@"; }     # every call needs --auth=adc
colab whoami >/dev/null && colab sessions      # fail fast
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/id_ed25519   # for colab ssh; pass -i ~/.ssh/id_ed25519
```

- Project secrets come from the platform's env vars, written into a `.env` and uploaded as in [Secrets]; Colab UI secrets never reach CLI runs.
- Outbound HTTPS/WebSocket must reach `colab.research.google.com`, `*.colab.dev` (regional runtime proxies), `oauth2.googleapis.com`, `www.googleapis.com` (and `pypi.org` for installs).
- A missing secret or failed `whoami` is a setup failure: stop and report; never start the interactive login.

Exporting `COLAB_TOKEN_JSON`, revocation, the token-file alternative, and a full recipe: [Remote Machines](references/remote-machines.md). Verified end-to-end with CLI 0.8.0 in an empty `HOME` with a fresh key (`new`, `upload`, `exec`, `ssh`, `stop`); not yet run on a specific cloud platform.

</Headless-and-Cloud>

<Agent-Automation-Patterns>

1. **Streams**: `colab run` writes `[colab] ...` status to stderr and the script's output to stdout: `colab run job.py > out.json 2> run.log`. `colab exec` streams the program's stdout/stderr through. *(live)*
2. **Exit codes**: `run` returns the script's exit status (`sys.exit(3)` → 3) *(live)*; `ssh -- CMD` returns the command's; `exec` exits 1 on an idle timeout. 255 from `ssh` is an ssh error or a signal.
3. **Teardown**: `trap 'colab stop -s "$S" || true' EXIT` around every `colab new`. `colab run` (without `--keep`) stops its VM even when the script fails.
4. **Isolation**: parallel runs pass global `--config <path>` (separate sessions file) and distinct session names. History still goes to `~/.config/colab-cli/history/`.
5. **Debugging**: `colab log -s S -n 20 -t execution`; `colab log -s S -o run.ipynb` (`.md`, `.txt`, `.jsonl`) exports the session. "Session not found"/404/401 means the VM was reclaimed: `colab sessions`, then `colab new`.
6. **Retries**: `colab new` retries assignment `COLAB_CLI_ASSIGN_RETRIES` times (default 3) with `COLAB_CLI_RETRY_BACKOFF` seconds (default 10).

Patterns and a full bash template: [Agent Workflows](references/agent-workflows.md).

</Agent-Automation-Patterns>

<Connecting-Skills>

- **Prerequisites**: `code-as-tools` / `coding-principles` to shape the job script so it runs unchanged locally and on Colab; `scripts` for the driver script.
- **Companions**: `notebook-observability` for notebooks run with `colab exec -f`; `experiment-lab-loop` decides *what* to run, and this skill runs it and brings back the metrics.
- **Successors**: whatever records results (an experiment log, results file, or W&B) consumes the files in `./outputs/<run-name>/`.

</Connecting-Skills>

<Anti-Patterns-and-Common-Mistakes>

| Mistake | Why it fails | Instead |
|---|---|---|
| `userdata.get()` in CLI-started code | UI secrets only work from the web UI | Upload `.env`, load it on the VM |
| Secret in `--env`, inline `exec` code, or `print` | History stores code, flags, and output verbatim | `.env` upload |
| Training in the foreground on `exec` | Idle timeout or a dropped connection ends the CLI call | Background launch + poll ([Training-Runs]) |
| `colab upload ./dir` / `colab download /content/dir` | Single files only | tar over `colab ssh` |
| `colab console` | Removed in 0.8.0 | `colab ssh -s S -- CMD` or `!` lines via `exec` |
| Bare `colab ssh` from an agent | Creates a billable VM and opens an interactive shell | `colab ssh -s S -- CMD` |
| Agent runs the OAuth login | Blocks on a paste only a human can do | User logs in; cloud uses `COLAB_TOKEN_JSON` + ADC |
| `colab auth` to fix a CLI 401/403 | It authenticates the VM, not the CLI | `colab whoami`, re-login or fix ADC scopes |
| No `-s`, or `/` in the session name | Random hex name / broken history file path | Sanitized explicit name |
| Checkpoints only on the VM | Wiped on stop, reclaim, or `colab run` exit | Push to the Hub during training |
| No teardown trap | Idle VM burns compute units | `trap 'colab stop ...' EXIT` |

</Anti-Patterns-and-Common-Mistakes>

<Examples>

Run names in this skill (`bert-lr-sweep`, `0a-myrepo-rl/grpo`, `run-2026-01-15`) are examples only, not a naming recommendation; use whatever the project already uses. Outputs land in `./outputs/<run-name>/`, e.g. `./outputs/0a-myrepo-rl/grpo/` with session name `0a-myrepo-rl-grpo`.

Interactive probe on a GPU, then teardown:
```bash
S=probe-$(date +%Y%m%d)
colab new -s "$S" --gpu T4
colab install -s "$S" datasets transformers
tar cz src | colab ssh -s "$S" -- 'tar xz -C /content'
echo 'import sys; sys.path.insert(0, "/content"); import src; print(src.__file__)' | colab exec -s "$S"
echo 'from datasets import load_dataset; ds = load_dataset("imdb", split="test")' | colab exec -s "$S" --timeout 300
echo 'print(len(ds), ds[0]["label"])' | colab exec -s "$S"     # later calls reuse kernel state
mkdir -p ./outputs/run-2026-01-15 && colab log -s "$S" -o ./outputs/run-2026-01-15/probe.ipynb
colab stop -s "$S"
```

Secret-free smoke test in one command: `colab run --gpu T4 --timeout 600 smoke_test.py --steps 20 > smoke.json`.

</Examples>

<References>

- [Command Reference](references/command-reference.md): every subcommand and flag of CLI 0.8.0, with what was run live.
- [Secrets Guide](references/secrets-and-credentials.md): UI secrets vs uploaded `.env`, error handling, what gets logged.
- [Agent Workflows](references/agent-workflows.md): unattended pipelines, notebook runs, a bash template, troubleshooting.
- [Remote Machines](references/remote-machines.md): Claude Code cloud, CI, and VMs: creating `COLAB_TOKEN_JSON`, session start, full recipe.

</References>
