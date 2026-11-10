# Agent Workflows with the Colab CLI

Patterns for agents and unattended pipelines. All commands are CLI 0.8.0. `<run-name>` is whatever the project calls a run (`bert-lr-sweep`, `0a-myrepo-rl/grpo`, `run-2026-01-15` are only examples); `S` is the session name derived from it with only `[a-z0-9-]`.

---

## 1. Pick the shape of the job

| Job | Use | Why |
|---|---|---|
| Short, self-contained, no secrets, one script | `colab run` | One command, VM always released |
| Needs secrets, repo code, or several steps | `colab new` → `upload`/`ssh` → `exec` → `download` → `stop` | Only a session can receive `.env` and files |
| Longer than a few minutes of silence, or hours | Session + background launch + poll (SKILL.md → Training-Runs) | Survives idle timeouts and dropped connections |
| Iterative probing of in-memory state | Session + repeated `colab exec` | Kernel state persists between calls |

---

## 2. Fire-and-forget: `colab run`

```bash
colab run --gpu T4 --timeout 600 batch_eval.py --limit 100 > ./outputs/<run-name>/eval.json 2> ./outputs/<run-name>/run.log
status=$?        # the script's own exit code
```

The script installs what it needs itself, because the VM is fresh:

```python
import subprocess, sys
subprocess.check_call(["uv", "pip", "install", "--system", "-q", "transformers", "datasets"])
```

Nothing on the VM survives: print the result to stdout (as JSON) or push it to remote storage. Use `--keep -s <name>` to inspect afterwards, then `colab stop -s <name>`.

---

## 3. Persistent session

```bash
S=eval-$(date +%Y%m%d-%H%M)
trap 'colab stop -s "$S" || true' EXIT
colab new -s "$S" --gpu T4

tar cz -C ./data . | colab ssh -s "$S" -- 'mkdir -p /content/data && tar xz -C /content/data'
colab install -s "$S" -r requirements.txt
colab upload -s "$S" .env /content/.env

colab exec -s "$S" -f phase1_load.py --timeout 300      # loads model/data into kernel memory
colab exec -s "$S" -f phase2_probe.py --timeout 300     # reuses phase-1 variables
echo 'print(len(dataset), dataset[0])' | colab exec -s "$S"

colab download -s "$S" /content/results.json ./outputs/<run-name>/results.json
```

`colab exec -f` sends the local file each time, so edit locally and re-run without uploading.

---

## 4. Notebooks against a persistent kernel

```bash
colab exec -s "$S" -f notebooks/01_explore.ipynb --timeout 300
# writes notebooks/01_explore_output.ipynb with all outputs
colab url -s "$S"            # a human can attach the browser to the same kernel
```

Cells that call slow APIs or download data stay silent for a while: raise `--timeout` (idle limit) or use `0`.

---

## 5. Bash template

```bash
#!/usr/bin/env bash
set -euo pipefail

RUN=${1:?usage: $0 <run-name>}
S=$(printf '%s' "$RUN" | tr -c 'a-z0-9-' '-')
OUT=./outputs/$RUN
GPU=${GPU:-T4}
mkdir -p "$OUT"

cleanup() { colab stop -s "$S" >/dev/null 2>&1 || true; }
trap cleanup EXIT

colab new -s "$S" --gpu "$GPU"
git archive HEAD | gzip | colab ssh -s "$S" -- 'mkdir -p /content/code && tar xz -C /content/code'
colab upload -s "$S" .env /content/.env
colab ssh -s "$S" -- 'cd /content/code && uv sync -q' </dev/null
colab ssh -s "$S" -- 'cd /content/code && nohup uv run python train.py --out /content/out > /content/train.log 2>&1 & echo $! > /content/train.pid' </dev/null

while colab ssh -s "$S" -- 'kill -0 $(cat /content/train.pid) 2>/dev/null' </dev/null; do
  colab ssh -s "$S" -- 'tail -1 /content/train.log' </dev/null || true
  sleep 60
done

colab ssh -s "$S" -- 'tar cz -C /content/out .' </dev/null | tar xz -C "$OUT"
colab download -s "$S" /content/train.log "$OUT/train.log"
```

Notes:
- The poll loop ends when the process exits *or* the VM is gone; check that the expected outputs exist before trusting the run.
- Pull only small files (metrics, logs, result JSON) back; push checkpoints and weights to the Hub from the training script.
- With no local `ssh` client, replace each `colab ssh -s "$S" -- 'X'` with `echo '!X' | colab exec -s "$S"` and the tar streams with `upload`/`download` of a `.tgz`. `exec` does not return the shell command's exit code, so print a marker (`&& echo OK`) and grep for it.

---

## 6. Parallel runs

```bash
colab --config /tmp/colab-a.json new -s sweep-lr-1e-4 --gpu T4
colab --config /tmp/colab-b.json new -s sweep-lr-3e-4 --gpu T4
```

Separate `--config` files keep session state apart; names must still be distinct because history is shared in `~/.config/colab-cli/history/`. Check `colab usage` for the compute-unit burn rate before launching many.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Backend rejected accelerator ...` (400) | No quota/entitlement for that GPU/TPU | `--gpu T4` or CPU |
| `Allocation refused (precondition failed)` | Too many sessions or temporary capacity limit | `colab sessions`, stop old ones, retry later |
| `TimeoutError: ... no message from the kernel for Ns` | Silent code longer than `--timeout` | Raise `--timeout`, `0`, or background launch |
| `Session ... appears to be lost (404/401)` | VM reclaimed | `colab new`, resume from the last pushed checkpoint |
| `colab ssh` 400 | No ed25519/ecdsa key, or RSA key | `ssh-keygen -t ed25519`, or `-i KEY` |
| `colab ssh` 404 | Runtime created without SSH support | New session |
| `colab ssh` 429 | SSH session limit (another shell/IDE attached) | Disconnect it, or use `!` lines via `exec` |
| `Local file 'dir' not found` on upload | Directories are not supported | tar stream over ssh |
| `Could not read the OAuth token from the OS keyring` | No keyring backend (headless Linux) | Harmless if commands work; or use ADC |
| CLI waits for `Enter the authorization code:` | Not logged in | A human logs in; headless: [Remote Machines](remote-machines.md) |
| Files missing on the VM | Relative path resolved elsewhere | Use absolute `/content/...` paths |
