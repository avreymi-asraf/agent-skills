# Running the Colab CLI from a Remote Machine

How to drive Colab from a machine with no browser: Claude Code cloud, a CI runner, a cloud VM, or a cluster login node.

> **Status: not yet verified end-to-end.** The local parts (token file location, `.env` upload) were verified on CLI 0.6.0. Using the token on a different machine has not been tested yet. Check with `colab whoami` and `colab sessions` before relying on it, and update this note once confirmed.

## What the remote machine needs

| Need | Local machine | Remote machine |
|---|---|---|
| Colab login | Browser OAuth flow, cached in `~/.config/colab-cli/token.json` | Same file, restored from the secret `COLAB_TOKEN_JSON` |
| Project secrets | `.env` file | Platform env vars → written to a `.env` file before upload |
| Network | Open | Must reach `colab.research.google.com`, `colab.pa.googleapis.com`, `oauth2.googleapis.com` |

## One-time setup (by the user, never the agent)

1. On a machine where `colab whoami` works, copy the contents of `~/.config/colab-cli/token.json`.
2. In the remote platform's secret store, create `COLAB_TOKEN_JSON` with that content (e.g. Claude Code cloud → environment settings → environment variables; GitHub Actions → repository secrets).
3. Add `HF_TOKEN`, `WANDB_API_KEY`, and any other names from `.env.example` the same way.
4. If the platform restricts network access, allow the three hosts above.

The token holds a long-lived refresh token: treat it as a password. To revoke it, remove the app's access in the Google Account → Security → third-party connections page, then log in again locally and refresh the secret.

## Session start (every remote session)

```bash
uv tool install google-colab-cli
mkdir -p ~/.config/colab-cli
printf '%s' "$COLAB_TOKEN_JSON" > ~/.config/colab-cli/token.json
chmod 600 ~/.config/colab-cli/token.json
colab whoami && colab sessions          # fail fast if the login does not work

# build .env from platform env vars; never echo the values
for k in HF_TOKEN WANDB_API_KEY ANTHROPIC_API_KEY; do
  [ -n "${!k}" ] && echo "$k=${!k}"
done > .env
chmod 600 .env
```

From here, follow the session flow in SKILL.md → Training-Runs unchanged (`colab upload -s <s> .env /content/.env`, background launch, poll, download, stop).

## Rules

- A missing `COLAB_TOKEN_JSON`, a failed `colab whoami`, or blocked network is an infra failure (`INFRA_INCONCLUSIVE`), never a result.
- Never print `COLAB_TOKEN_JSON` or `.env`, and never commit them. `.env` is gitignored; `token.json` lives outside the repo.
- Unattended agents can rent paid GPUs: always use `trap "colab stop -s $S || true" EXIT`, and start with a short `T4` smoke test.
- If the remote machine refreshes the token, the copy in the secret store is not updated. If `colab whoami` starts failing after a long time, log in locally again and replace the secret.
