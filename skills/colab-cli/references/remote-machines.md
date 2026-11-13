# Running the Colab CLI on a Machine Without a Browser

For agents and jobs that run where nobody can open a login page: Claude Code cloud sessions, CI runners (GitHub Actions, GitLab), cloud VMs, cluster login nodes.

> **Status (CLI 0.8.0):** the ADC recipe below was run end-to-end in an empty `HOME` with a fresh ssh key: `whoami`, `sessions`, `usage`, `new`, `upload .env`, `exec`, `ssh -- CMD` with a piped `git archive`, `stop`. It has not yet been run on a specific cloud platform; the platform notes (secret stores, network allowlists) come from those platforms' docs.

## How the login travels

The CLI's OAuth login is a refresh token plus the OAuth client id/secret. Saved as an `authorized_user` JSON, Google's standard Application Default Credentials (ADC) loader accepts it through `GOOGLE_APPLICATION_CREDENTIALS`, and `colab --auth=adc` uses it. No keyring, no `gcloud`, and no browser are needed on the remote machine.

| Need | User's machine | Remote machine |
|---|---|---|
| Colab login | `colab whoami` works | `COLAB_TOKEN_JSON` secret → file → `GOOGLE_APPLICATION_CREDENTIALS`, `--auth=adc` |
| Project secrets | `.env` file | Platform env vars → `.env` → `colab upload` |
| `colab ssh` key | `~/.ssh/id_ed25519` | Throwaway key made per session |
| Network | open | Outbound HTTPS + WebSocket to `colab.research.google.com`, `*.colab.dev`, `oauth2.googleapis.com`, `www.googleapis.com` (+ `pypi.org` for the update check and installs) |

## One-time setup (the user does this, not the agent)

1. On the user's own machine, log in once: `colab sessions` (follow the URL, paste the code) and check with `colab whoami`.
2. Export the login as an `authorized_user` JSON. The CLI keeps it in the OS keyring, or in `~/.config/colab-cli/token.json` where no keyring exists; this reads either:
   ```bash
   umask 077
   "$(uv tool dir)/google-colab-cli/bin/python" - <<'EOF' > colab-token.json
   import json, os, keyring
   try:
       raw = keyring.get_password("google-colab-cli", "oauth_token")
   except Exception:
       raw = None
   raw = raw or open(os.path.expanduser("~/.config/colab-cli/token.json")).read()
   d = json.loads(raw); d["type"] = "authorized_user"
   print(json.dumps(d))
   EOF
   ```
   (Installed with `pipx`/`pip` instead of `uv tool`: run the same script with that environment's Python.) Alternative: `gcloud auth application-default login --scopes=...` (scopes in SKILL.md → Installation-and-Auth) and use `~/.config/gcloud/application_default_credentials.json` as is.
3. Store the file's contents as a secret named `COLAB_TOKEN_JSON`, then delete the local copy (`rm colab-token.json`):
   - **Claude Code cloud**: the environment's settings → environment variables. Set network access to allow the hosts above (custom allowlist or full access).
   - **GitHub Actions**: repository/environment secret, exposed as `env: COLAB_TOKEN_JSON: ${{ secrets.COLAB_TOKEN_JSON }}`.
   - **VM / cluster**: a `chmod 600` file outside any repo, or the site's secret manager.
4. Add the project's secrets (`HF_TOKEN`, `WANDB_API_KEY`, ...) the same way, using the names the project's `.env.example` lists.

The JSON holds a long-lived refresh token with access to the user's Colab account (it can spend compute units): treat it as a password. To revoke it, remove the app's access at Google Account → Security → Third-party connections, log in again, and replace the secret. Prefer a platform secret store that is scoped to one repo/environment.

## Session start (every remote session)

```bash
uv tool install google-colab-cli
umask 077
mkdir -p ~/.config/colab-cli ~/.ssh
printf '%s' "$COLAB_TOKEN_JSON" > ~/.config/colab-cli/adc.json
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/colab-cli/adc.json
colab() { command colab --auth=adc "$@"; }          # every call needs --auth=adc
colab whoami >/dev/null && colab sessions            # fail fast if the login does not work

[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/id_ed25519
KEY=~/.ssh/id_ed25519                                 # pass -i "$KEY" to every colab ssh

for k in HF_TOKEN WANDB_API_KEY; do                   # the project's secret names
  [ -n "${!k:-}" ] && printf '%s=%s\n' "$k" "${!k}"
done > .env                                           # never echo the values
```

Pass `-i "$KEY"` explicitly: `ssh` looks up `~/.ssh` from the user's passwd home, not `$HOME`, so in containers where they differ the default key and the key the CLI sends do not match (`Permission denied (publickey)`).

If `ssh` is not installed and cannot be, skip the key and use `colab upload`/`download` with `.tgz` files plus `!` lines through `colab exec` (SKILL.md → Files-and-Packages).

## End-to-end cloud recipe

```bash
RUN=run-2026-01-15                                    # example name only
S=$(printf '%s' "$RUN" | tr -c 'a-z0-9-' '-')
OUT=./outputs/$RUN; mkdir -p "$OUT"
trap 'colab stop -s "$S" || true' EXIT

colab new -s "$S" --gpu T4
git archive HEAD | gzip | colab ssh -s "$S" -i "$KEY" -- 'mkdir -p /content/code && tar xz -C /content/code'
colab upload -s "$S" .env /content/.env
colab ssh -s "$S" -i "$KEY" -- 'cd /content/code && uv sync -q' </dev/null
colab ssh -s "$S" -i "$KEY" -- 'cd /content/code && nohup uv run python train.py --out /content/out > /content/train.log 2>&1 & echo $! > /content/train.pid' </dev/null
while colab ssh -s "$S" -i "$KEY" -- 'kill -0 $(cat /content/train.pid) 2>/dev/null' </dev/null; do sleep 60; done
colab ssh -s "$S" -i "$KEY" -- 'tar cz -C /content/out .' </dev/null | tar xz -C "$OUT"
colab download -s "$S" /content/train.log "$OUT/train.log"
```

Cloud sessions and CI jobs have their own time limits: when a run may outlast the agent's session, launch it in the background (as above), push checkpoints to the Hub, and let a later session reattach with the same `-s` name (`colab sessions` lists it; the VM keeps running until `colab stop` or reclaim) instead of keeping a `trap` that stops the VM on exit.

## Alternative: restore the token file (oauth2)

On Linux without a keyring, 0.8.0 still reads the legacy file `~/.config/colab-cli/token.json` (the CLI's token JSON, `type` field optional), so `printf '%s' "$COLAB_TOKEN_JSON" > ~/.config/colab-cli/token.json` with the default `--auth=oauth2` also works (verified with `whoami`/`sessions`). Every command then prints two keyring warnings. This path is the CLI's migration code for old installs and may be removed; prefer ADC.

## Rules

- A missing `COLAB_TOKEN_JSON`, a failed `colab whoami`, or blocked network is a setup failure, never a result. Stop and report it; do not try to log in interactively.
- Never print `COLAB_TOKEN_JSON`, `adc.json`, or `.env`, and never commit them.
- Unattended agents rent paid GPUs: smoke-test on `T4`, keep a teardown `trap` for short jobs, and check `colab usage`.
- The token refreshes in memory; the stored secret does not change. If `whoami` starts failing (password change, revoked access, token expiry policy), the user logs in again locally and replaces the secret.
