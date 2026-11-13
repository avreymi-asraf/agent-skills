# {{FILL: lab name}} Research Lab

A research control repository: the knowledge and the tools for running experiments on external experiment repos, without storing their code here and without losing what was learned between sessions.

Agents start from `AGENTS.md`. The experiment loop is in the `experiment-lab-loop` skill (`.agents/skills/`).

Python here is `uv` only.

```bash
uv sync
uv run scripts/lab.py init           # create .repos/ and the cortex folders
uv run scripts/lab.py sync-repos     # clone or fetch the repos in repos.yaml
uv run scripts/lab.py --help         # all commands
```
