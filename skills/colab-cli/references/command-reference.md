# Google Colab CLI Command Reference

Every subcommand and flag of `google-colab-cli` **0.8.0**, taken from `colab <cmd> --help`. The **Checked** column says how each command was confirmed:

- **live**: run against a real Colab runtime with 0.8.0 (CPU session).
- **run**: executed locally (no runtime needed).
- **help**: flags confirmed from `--help` and the source, not run (GPU/TPU, human-only, or billing commands).

Re-check after upgrading: `colab version`, then `colab <cmd> -h`. `colab help <cmd>` works too.

---

## 1. Global Options

They go **before** the subcommand: `colab [GLOBAL_OPTIONS] COMMAND [ARGS...]`.

| Option | Description | Default |
|---|---|---|
| `--auth {oauth2,adc}` | `oauth2`: copy-paste browser login, token in the OS keyring (fallback `~/.config/colab-cli/token.json`). `adc`: Application Default Credentials. | `oauth2` |
| `-c, --client-oauth-config PATH` | OAuth client config JSON (falls back to the bundled client) | `~/.colab-cli-oauth-config.json` |
| `--config PATH` | Session state file (isolate parallel runs with it) | `~/.config/colab-cli/sessions.json` |
| `--logtostderr` | Debug logging to stderr (the debug log is `~/.config/colab-cli/colab.log`) | off |
| `--install-completion` / `--show-completion` | Shell completion | |

Environment variables read by the CLI: `GOOGLE_APPLICATION_CREDENTIALS` (ADC), `COLAB_CLI_ASSIGN_RETRIES` (default 3), `COLAB_CLI_RETRY_BACKOFF` (seconds, default 10), `COLAB_CLI_REQUEST_TIMEOUT`.

Local files: `~/.config/colab-cli/sessions.json` (sessions), `settings.json` (update check), `history/<session>.jsonl` (every executed code block and its output), `colab.log` (debug).

---

## 2. Sessions

| Command | Flags | Checked |
|---|---|---|
| `colab new` | `-s/--session NAME`, `--gpu {T4,L4,G4,H100,A100}`, `--tpu {V5E1,V6E1}` (case-insensitive; unknown values are rejected before allocation), `--high-mem` (Pro/Pro+; ignored for L4 and TPUs). No accelerator = CPU. | live (CPU) |
| `colab sessions` | none. Lists server assignments, prunes stale local entries; unknown ones show as `[?]`. | live |
| `colab status` | `-s`. Hardware, shape, variant, IDLE/BUSY, last execution. | live |
| `colab restart-kernel` | `-s`. Resets kernel state, keeps the VM. | help |
| `colab stop` | `-s`. Releases the VM. | live |
| `colab url` | `-s`, `--host ORIGIN` (default `https://colab.research.google.com`), `--open`. Prints a URL that attaches the web UI to the CLI's kernel. | live |
| `colab usage` | none. Compute-unit balance, burn rate, active assignments. | live |
| `colab pay` | none. Opens the Colab signup/compute-units page. | help |

---

## 3. Running Code

### `colab exec`
```bash
colab exec [-s NAME] [-f FILE] [--timeout SECS] [--env KEY=VALUE ...] [--output-image PATH]
```
- Code from `-f file.py`, `-f notebook.ipynb`, or stdin. The file is read locally; no upload needed. *(live)*
- Notebooks: code cells run in order; results go to `<name>_output.ipynb` next to the input; `# @title X` names a cell in progress output. *(live)*
- `--timeout`: seconds allowed **without output** (default 30, `0` = no limit). On expiry: exit 1, `TimeoutError: Timeout waiting for output: no message from the kernel for Ns`. The kernel stays usable. *(live)*
- `--env KEY=VALUE` (repeatable): prepends `os.environ[...] = ...` to each code block. Values persist in the kernel and are written to the history file. *(live)*
- IPython syntax works: `!cmd` lines, `%%bash` cells, `%cd`. *(live: `!nproc`)*

### `colab run`
```bash
colab run [-s NAME] [--gpu G | --tpu T] [--high-mem] [--keep] [--timeout SECS] [--env KEY=VALUE ...] SCRIPT [ARGS...]
```
- Fresh VM → run → stop (even when the script fails). `--keep` keeps the VM for `colab exec -s NAME`. *(live)*
- `sys.argv = [script, *ARGS]`, `__name__ == "__main__"`. Exit code = the script's (`sys.exit(3)` → 3, uncaught exception → 1). *(live)*
- stdout = script output only; stderr = `[colab] ...` status. *(live)*
- Missing script path fails before a VM is allocated.
- Shebang: `#!/usr/bin/env -S colab run --gpu T4`, then `chmod +x job.py && ./job.py`.
- Auto name `run-<6 hex>` when `-s` is omitted.

### `colab ssh`
```bash
colab ssh [-s NAME] [-i KEY] [--gpu G | --tpu T] [--high-mem] [--rm] [--proxy-mode] [-- CMD [ARGS...]]
```
- `-- CMD`: runs in `/content` on an **existing** session (never creates one), returns CMD's exit status, piped stdin/stdout byte-exact, PTY only when both ends are terminals. One argument = shell line; several = exact argv. *(live: exit 7 propagated, tar streamed both ways)*
- Bare `colab ssh`: interactive shell in `/content` on the only session, or **auto-creates** one (`--gpu/--tpu/--high-mem` size it, `--rm` stops it on exit). For humans.
- `--proxy-mode`: OpenSSH `ProxyCommand` bridge (for `ssh`, `scp`, `rsync`, VS Code Remote-SSH):
  ```
  Host colab-<session>
    ProxyCommand /abs/path/to/colab ssh --proxy-mode -s <session>
    User root
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
  ```
  `-s` creates the session on first connect; `--rm` stops it on disconnect. *(help/docs)*
- `-i KEY`: `.pub` or private key path. Default: `~/.ssh/id_ed25519.pub`, then `id_ecdsa.pub`. RSA keys are rejected. *(live with a fresh ed25519 key)*
- Errors: 400 bad key, 401 token expired, 404 runtime has no SSH (create a new one), 429 SSH session limit (depends on plan), 502 sshd unhealthy.
- The ssh environment is minimal: `python3`, `pip`, `uv`, `nvidia-smi` are on `PATH`; tools like `gcloud`/`node` may not be.

### `colab repl`
```bash
colab repl [-s NAME] [--output-image PATH]
```
Interactive Python on the kernel; exits on EOF when stdin is piped. *(help)*

### Removed
- `colab console` (removed in 0.8.0): use `colab ssh -s NAME [-- CMD]`, or `!` lines through `colab exec`.

---

## 4. Files and Packages

All remote paths are absolute or relative to `/content`.

| Command | Notes | Checked |
|---|---|---|
| `colab upload [-s NAME] LOCAL REMOTE` | Single file only; a directory gives `Local file 'X' not found.` | live |
| `colab download [-s NAME] REMOTE LOCAL` | Single file; LOCAL must be a file path (a directory gives `Is a directory`); a remote directory gives `Cannot download a directory`. | live |
| `colab ls [-s NAME] [PATH]` | Default path `content` | live |
| `colab rm [-s NAME] PATH` | Deletes a remote file | help |
| `colab edit [-s NAME] PATH` | Opens in local `$EDITOR`, writes back on change | help |
| `colab install [-s NAME] [PKG...] [-r FILE]` | `uv pip install --system`, falls back to `pip` | live |
| `colab drivemount [-s NAME] [PATH]` | Mounts Drive (default `/content/drive`); needs a human at a TTY | help |
| `colab auth [-s NAME]` | Hidden. GCP credentials *for the VM* (BigQuery/GCS); needs a human. Not CLI login. | help |

Directories: stream a tar through `colab ssh` (see SKILL.md → Files-and-Packages).

---

## 5. History: `colab log`

```bash
colab log [-s NAME] [-n LINES] [-t TYPE] [-o OUTPUT]
```
- No `-s`: lists sessions that have logs.
- `-t`: `execution`, `file_operation`, ...
- `-o`: format by suffix: `.ipynb`, `.md`, `.txt`, `.jsonl`. *(live: `-n`, `-t execution`, `-o .md`)*

---

## 6. Utility

| Command | Notes | Checked |
|---|---|---|
| `colab whoami` | Hidden. Auth provider, email, OAuth client, expiry, scopes. | live |
| `colab version` | Installed version | run |
| `colab update [--install]` | Checks PyPI; `--install` runs `pip install -U` (Linux). With `uv tool`, prefer `uv tool upgrade google-colab-cli`. | help |
| `colab skill` / `colab readme` | Print the bundled agent skill / README | run |
| `colab help [CMD]` | Same as `-h` | help |
