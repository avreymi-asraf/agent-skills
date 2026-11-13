# Secrets and Credentials on Colab

How API keys (Hugging Face, W&B, LLM providers, GitHub) reach code running on a Colab VM. Which path works depends on **who started the kernel**:

| Kernel started from | Works | Does not work |
|---|---|---|
| Colab web UI (browser notebook) | 🔑 Secrets tab → `google.colab.userdata` | — |
| CLI (`colab new`/`exec`/`run`/`ssh`) | Uploaded `.env` file | `userdata`, `--env` for secrets (logged) |

This is separate from the CLI's own Google login (SKILL.md → Installation-and-Auth, and [Remote Machines](remote-machines.md) for headless machines).

---

## 1. CLI runs: upload a `.env`

Verified on CLI 0.8.0:

1. **`userdata` is unavailable.** From `colab exec`/`run`, `userdata.get("HF_TOKEN")` raises `TimeoutException: Requesting secret HF_TOKEN timed out. Secrets can only be fetched when running from the Colab UI.` It takes several seconds to fail, so never call it in unattended runs.
2. **Upload the project's gitignored `.env`:**
   ```bash
   colab upload -s <session> .env /content/.env
   ```
   The history records the upload as a file operation with paths only, not the contents.
3. **Load it at the top of the job** (loader in SKILL.md → Secrets), or with `python-dotenv` if the project already uses it: `load_dotenv("/content/.env")`.
4. **Fail fast** when a required key is missing: raise with the key *names*, never the values. A missing key is a setup failure.
5. **`colab run` cannot receive secrets**: it creates a fresh VM with no upload step. Use `colab new` → `upload .env` → `exec`/`ssh` → `stop`.
6. **Delete it when done** if the session is kept: `colab rm -s <session> /content/.env`. `colab stop` destroys the VM and the file with it.

### What never to do

| Pattern | What leaks |
|---|---|
| `colab exec --env HF_TOKEN=$HF_TOKEN` / `colab run --env ...` | Value written into the code block stored in `~/.config/colab-cli/history/<session>.jsonl`; also visible in `ps` and shell history |
| `echo "os.environ['HF_TOKEN']='$HF_TOKEN'" \| colab exec` | Same history file, verbatim |
| `print(os.environ["HF_TOKEN"])`, logging config dumps | Outputs are stored in the history file and in exported logs (`colab log -o`) |
| Committing `.env` or baking it into `git archive` | Repo history |

`--env` is fine for non-secret settings (`--env MODE=smoke`).

---

## 2. Web UI notebooks: `google.colab.userdata`

The 🔑 Secrets tab stores secrets per Google account; each notebook must be granted access per secret ("Notebook access" toggle). Libraries read keys from `os.environ`, so copy them over (bootstrap cell in SKILL.md → Notebook-Bootstrapping).

```python
import os
from google.colab import userdata

try:
    os.environ.setdefault("HF_TOKEN", userdata.get("HF_TOKEN"))
except userdata.SecretNotFoundError:
    print("HF_TOKEN not set: add it in the Secrets tab")
except userdata.NotebookAccessError:
    print("HF_TOKEN not granted: enable notebook access in the Secrets tab")
```

A helper that works in both places (web UI first, then environment / `.env`):

```python
import os

def get_secret(key: str, default: str | None = None) -> str | None:
    if os.environ.get(key):
        return os.environ[key]
    try:
        from google.colab import userdata
        return userdata.get(key)
    except Exception:          # not on Colab, not in the UI, missing, or not granted
        return default
```

Check `os.environ` first: in CLI runs the `.env` loader has already filled it, so the slow-failing `userdata` call is skipped.

---

## 3. Common secret names

Use the names the project already lists (e.g. in `.env.example`). Typical ones:

| Name | Service | Read by |
|---|---|---|
| `HF_TOKEN` | Hugging Face Hub | `huggingface_hub`, `transformers`, `datasets` |
| `WANDB_API_KEY` | Weights & Biases | `wandb`, `transformers.Trainer` |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` | LLM APIs | provider SDKs, `litellm` |
| `GITHUB_TOKEN` | GitHub | `git clone` of private repos |

---

## 4. GCP credentials on the VM

For BigQuery/GCS from code on the VM, `colab auth -s <session>` runs `google.colab.auth.authenticate_user()` in the kernel. It needs a human at a TTY, so agents use a service-account key uploaded like `.env` (and `GOOGLE_APPLICATION_CREDENTIALS=/content/sa.json` in `.env`) instead. *(Service-account path: standard Google auth behavior, not tested on Colab.)*
