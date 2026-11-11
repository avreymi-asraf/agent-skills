# Running anywhere

A wide request is often handed to a session that is not the user's laptop: a cloud session, a CI job, a cluster login. That session has the repo and nothing else. A lab that depends on anything outside it cannot take such a request, and the failure is silent: the agent works from a thinner picture and does not know it.

## Everything an agent needs is in the repo

- **Instructions:** `AGENTS.md`, with one-line pointer files (`CLAUDE.md`, `GEMINI.md`) for tools that do not read it by themselves.
- **Skills:** a static copy of each skill in `.agents/skills/<skill>/` (the lab's own `experiment-lab-loop`, and `cortex` and `grow-autonomy`, which `new_lab.py` copies in), and a relative link from `.claude/skills/<skill>` to it, so every agent tool reads the same copy. Skills installed in the user's home directory do not exist in a cloud session. With `npx skills`, install into the project and commit the lock file; skills written for this lab live in the same folders.
- **Worktrees:** `lab.py new-exp` and `mount-exp` copy the lab's skills into each worktree and keep them out of the experiment's diff, so an agent working inside the target repo has them too.
- **Tool settings** that the lab relies on are committed, not kept in a personal profile.

## One Python tool: `uv`

Every Python command in the lab and in its target repos is `uv run`, `uv add` or `uv sync`. `scripts/lab.py` runs as `uv run scripts/lab.py`, the final evaluation as `uv run evaluate.py`, a round's command as `uv run ...` inside `lab.py run`. No `pip install`, no bare `python`, no hand-made virtual environment. A dependency added with `uv add` is in the lock file and therefore in the next session; one installed by hand exists on one machine until it is recycled.

## Nothing machine-specific in tracked files

No absolute paths in docs, plans, configs or the cortex. Commands use repo-relative paths and variables: `$LAB_ROOT` and `$EXP_DIR` (set by `lab.py run` and `evaluate`) and the names in `.env.example`. Data is declared as `data_source: <repo>@<ref>:<path>`; the variable that points at a local copy of it is named in `.env.example`.

## Secrets

Code reads secrets only from environment variables, with the same names everywhere. Only the source of the values changes:

| Runtime | Where the values live |
|---|---|
| Local | `.env` at the lab root (git-ignored); `lab.py run` and `evaluate` load it, and variables already set win |
| Cloud agent session | The environment's variables or secret store, set once in its settings |
| CI | The CI's secret store, passed as environment variables |
| Remote GPU or cluster job | A `.env` copied there by hand with restricted permissions, or the platform's secret store |

Experiment code runs headless: a missing value fails fast with a clear message and never prompts. A missing credential is a technical failure of a round, never a result. Values never appear in git, logs, results, patches or the cortex; print names only.

## Git access

- Target repos are registered with HTTPS urls; a cloud runtime has no SSH key.
- A cloud agent session usually reaches only the repositories attached to it. The lab repo and every target repo it will touch must be attached when the session starts. Put the lab's setup (`uv sync`, `lab.py sync-repos`) in the environment's setup script.
- A session elsewhere sees only what is pushed. Push the experiment branch after every round that matters, and the lab repo after every change to the cortex or the journal. `mount-exp` then brings the worktree back from the pushed branch.
- The frame later experiments build on lives on a kept, pushed experiment branch that the system page names (`> Branch:`). The target's default branch is not merged into unless the user asks.

## Test it

Clone the lab into an empty folder, with no `.env` and no home-directory skills, and run the cold read and the CLI pass from [Checking](checking.md). What fails there is what a cloud session will hit.
