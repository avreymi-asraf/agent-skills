# Google Colab Secrets and Credentials Management

This guide details how to securely access, manage, and inject credentials and API keys in Google Colab environments across interactive notebooks, CLI sessions, and autonomous agent workflows.

---

## 1. Google Colab Secrets Architecture (`google.colab.userdata`)

Google Colab provides a secure Secrets store accessible via the **🔑 Secrets** tab in the notebook sidebar. When secrets are stored:
1. They are encrypted and associated with the user's Google account.
2. Notebooks request access per secret via the "Notebook access" toggle.
3. In Python, secrets are accessed through the `google.colab.userdata` module.

### Core Retrieval Pattern in Python
```python
import os

# Standard pattern: try Colab userdata first, then fall back to os.environ / .env
def get_secret(key: str, default: str | None = None) -> str | None:
    try:
        from google.colab import userdata
        try:
            val = userdata.get(key)
            if val:
                return val
        except Exception:
            pass
    except ImportError:
        pass
    return os.environ.get(key, default)
```

---

## 2. Syncing Colab Secrets to `os.environ` for Third-Party Libraries

Most LLM and ML libraries (`litellm`, `huggingface_hub`, `openai`, `google-genai`, `wandb`, `transformers`) read API keys directly from `os.environ`. Colab secrets are **not** automatically injected into `os.environ`.

### Automatic Environment Synchronization
Run this snippet during initialization in Colab notebooks or remote scripts:

```python
import os
import sys

IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

if IN_COLAB:
    try:
        from google.colab import userdata
        # Common AI/ML secrets to auto-sync
        SYNC_KEYS = [
            "HF_TOKEN",
            "HUGGINGFACE_TOKEN",
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "DEEPSEEK_API_KEY",
            "MISTRAL_API_KEY",
            "WANDB_API_KEY",
            "GITHUB_TOKEN",
        ]
        for k in SYNC_KEYS:
            try:
                val = userdata.get(k)
                if val and k not in os.environ:
                    os.environ[k] = val
            except Exception:
                pass
        print("🔑 Colab secrets synchronized to os.environ.")
    except ImportError:
        pass
```

---

## 3. Common Secret Keys & Provider Map

| Secret Name | Intended Service | Used By |
|---|---|---|
| `HF_TOKEN` / `HUGGINGFACE_TOKEN` | Hugging Face Hub | `huggingface_hub`, `transformers`, `datasets` |
| `GEMINI_API_KEY` | Google Gemini API | `google-genai`, `litellm` |
| `OPENAI_API_KEY` | OpenAI API | `openai`, `litellm` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API | `anthropic`, `litellm` |
| `DEEPSEEK_API_KEY` | DeepSeek API | `litellm`, `openai` |
| `WANDB_API_KEY` | Weights & Biases | `wandb`, `transformers.Trainer` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | `git clone`, repository operations |

---

## 4. Handling Missing Secrets Gracefully

When a secret is missing or access is not granted in the Colab UI:
- `userdata.get(key)` raises `google.colab.userdata.SecretNotFoundError` or `google.colab.userdata.NotebookAccessError`.
- Catching general `Exception` or `userdata.SecretNotFoundError` ensures execution proceeds cleanly with local environment variables or prompts the user with an actionable message.

```python
from google.colab import userdata

try:
    hf_token = userdata.get('HF_TOKEN')
except userdata.SecretNotFoundError:
    print("⚠️ 'HF_TOKEN' not found in Colab Secrets. Set it under the 🔑 Secrets tab.")
    hf_token = os.environ.get('HF_TOKEN')
except userdata.NotebookAccessError:
    print("⚠️ Notebook access not granted for 'HF_TOKEN'. Enable toggle in Secrets tab.")
    hf_token = None
```

---

## 5. Secrets in Headless & CLI Execution (`colab-cli`)

Verified on CLI 0.6.0:
1. **`userdata` is unavailable to CLI-started code.** In `colab run` / `colab exec`, `userdata.get(key)` raises `TimeoutException: Requesting secret <key> timed out. Secrets can only be fetched when running from the Colab UI.` Do not call it in unattended runs.
2. **Upload a `.env` file instead.** `colab upload -s <name> .env /content/.env`, then parse it into `os.environ` at the top of the script (loader in SKILL.md → Colab-Secrets-and-Credentials). The session log records the upload path only, not the file contents.
3. **Never inline a secret into code sent to `colab exec`.** `colab log` stores every executed snippet verbatim (`event_type: execution`, `code: ...`) under `~/.config/colab-cli/`, so `echo "os.environ['HF_TOKEN']='$HF_TOKEN'" | colab exec` writes the token to disk. Never print secret values either; outputs are logged too.
4. **`colab run` cannot receive secrets**, because it creates a fresh VM with no upload step. Use `colab new` → `upload` → `exec` → `stop` whenever a job needs a key.
