# {{FILL: lab name}} Research Lab (`AGENTS.md`)

This repository is a **research lab**: it holds the memory and the tools for running experiments on external target repositories. The target's code is never stored here. What is stored here is what was tried, what was learned, and what to try next, so that each experiment starts from everything the earlier ones found.

What the lab is for, and the far goal it is growing toward: `wiki-llm/purpose.md`. Read it before any task that leaves you a choice of direction.

## 1. How Far to Go Comes With the Request

Requests of every size arrive here, in any order: "rename this function", "fix this wiki line", "think of a new direction and run it to a conclusion". The lab has no automation level and no stages.

- **Read the size from the request itself**, not from the previous request and not from how the lab usually works. If the request does not say how far to go and the readings lead to different work, ask with a concrete case.
- **Small request:** do that thing. Do not start an experiment, a wiki pass, or a redesign that was not asked for. If you notice a problem outside the request, mention it and leave it.
- **Wide request:** carry it through. Do not come back for approval at each step. Use the stopping point in the experiment's `plan.md` to decide when to stop. At the end, report what you decided along the way, what you assumed, what you did not check, and where you are unsure.
- **When work is rejected, or the way the lab works has to change:** use the `grow-autonomy` skill. It fixes what agents understand, at the root, and records the reject in `.grow-autonomy/rejects.md`.

## 2. Vocabulary (One Concept, One Name)

- **Target repo:** one stage or theme of the research, holding many experiments as branches. Registered in `repos.yaml`.
- **Experiment:** one idea, pursued through as many rounds as it takes to reach a conclusion. It is a line of inquiry, not a single run. "Try GRPO on the base model" is an experiment. One training run is a round inside it. If the idea itself is replaced (GRPO turns out unsuitable and PPO looks right), close the experiment with that conclusion and open a new one.
- **Plan (`plan.md`, next to the code):** the current best description of how to realise the idea. It starts as detailed as present knowledge allows, which may be quite high-level, and is rewritten in place after every round that teaches something. It is never a signed contract.
- **Round:** one pass of implement → run → analyze. A round can be long.
- **Experiment log (`log.md`, next to the code):** append-only, one entry per round: what was tried, what was seen, what was decided. The plan says where we are; the log says how we got there. Plan and log are the experiment's **notes**, its own working memory: they live on the experiment's branch in the target repo, in `notes/<exp-name>/`, and are committed with the code they describe. The folder is called `notes` so that `experiments/` means one thing only: the lab's folder.
- **Conclusion:** something learned that a *different* experiment should know. It is what leaves the experiment's own log and is told to the whole lab. *Interim*: the experiment continues; the lesson goes to the wiki now, marked provisional. *Final*: there is no point trying further (the result was reached, or the idea is exhausted); the experiment closes.
- **Final evaluation:** one run of the target repo's `evaluate.py` when the experiment closes. Its number is compared with the baseline.
- **Baseline:** the best verified number per target repo and task, shared by all experiments. It lives in `JOURNAL.md` → Current Frontier. A repo may have no baseline yet; then experiments close with a conclusion and no number.
- **Spark:** an idea worth an experiment that has not been opened yet, written down while the context is fresh (`JOURNAL.md`).
- **Experiment Language:** the concepts, structure and names that all experiments on one target repo share (`wiki-llm/systems/<repo>.md`).
- **Experiment name:** `<id>-<repo-short>-<worktree-name>`, e.g. `0a-model-rl/grpo`. `<id>` is two hex digits, unique in the lab (`new-exp` picks it). `<repo-short>` is `short_name` in `repos.yaml`. `<worktree-name>` is 1-3 short `/`-separated levels, broad to specific. The same name is used for the lab folder `experiments/<exp-name>/`, the notes folder `notes/<exp-name>/`, the worktree `.targets/worktrees/<exp-name>/` and branch `exp/<exp-name>`. Commands take the id (`--exp 0a`) or the full name.

## 3. Where Things Live

| Place | Holds | Rule |
|---|---|---|
| Target repo, branch `exp/<exp-name>`: `notes/<exp-name>/` | The experiment's notes, next to its code: `plan.md` (current state), `log.md` (round log), `runs/` | While open, the plan is rewritten and the log grows, committed together with the code. A branch that starts from an earlier experiment carries that experiment's notes with it. |
| Lab: `experiments/<exp-name>/` | What the experiment tells everyone when it closes: `postmortem.md`, `results.json`, `evaluate.log`, `patch.diff` | After it closes, nothing changes except a re-evaluation added to `results.json`. |
| `JOURNAL.md` | Current Frontier (baselines), Active Sparks, the matrix of all experiments, the Anti-Repeat Banlist | The routing page: what is best, what is next, what not to repeat. |
| `wiki-llm/` | Compiled knowledge: `purpose.md`, `gap_map.md`, `systems/`, `findings/`, `literature/`, `index.md`, `log.md` | Work lessons into existing pages. Every claim names its source experiment and whether it is provisional. Never dump raw logs. |
| `.targets/` (git-ignored) | Clones of target repos (`repos/`) and one worktree per experiment (`worktrees/<exp-name>/`) | Managed by `scripts/lab.py`. |
| `.grow-autonomy/rejects.md` | The reject journal | For the user and for whoever maintains this content. Not instructions. |

## 4. Running an Experiment

Load the `experiment-lab-loop` skill. It is the only place the loop is described: find a direction, write the plan, work in rounds, tell the lab what others need, close with a final evaluation. Do not load it for requests that are not about an experiment.

## 5. What Always Holds

Each of these holds for every request, whatever its size.

1. **Experiment code lives in its own worktree and branch.** Never edit `.targets/repos/<repo>` (the base clone). `uv run scripts/lab.py new-exp` creates `.targets/worktrees/<exp-name>/` on branch `exp/<exp-name>`. *Why:* experiments stay independent and each can be reproduced alone.
2. **Experiment branches are pushed and never merged** into the target's default branch unless the user explicitly asks. An experiment that builds on an earlier one starts from it (`new-exp --base-branch exp/<earlier-exp-name>`). *Why:* every result must survive a fresh clone, and no experiment may silently change the ground under another.
3. **A technical failure is not a scientific result.** A crash, out-of-memory, missing credential or typo is `INFRA_INCONCLUSIVE`, or simply a round that failed. Never write to `wiki-llm/findings/` or the Anti-Repeat Banlist that an idea failed before it actually ran cleanly. *Why:* a false refutation stops every later agent from trying a good idea.
4. **Experiments on one repo share one Experiment Language.** Reuse the terms, files, extension points and patterns recorded in `wiki-llm/systems/<repo>.md`, so that someone who understood experiment `0a` opens `0b` and sees that only the idea changed. Change the language only when that change is the idea. Say so in `plan.md`, and update the system page when the experiment is kept. *Why:* readability across experiments, and results that can be attributed to the idea.
5. **Everything runs from a fresh clone, anywhere** (a laptop, a cloud session, CI, a cluster). Never write absolute or machine-specific paths into docs, code, configs, plans or the wiki. Use repo-relative paths, or the variables `lab.py run` and `lab.py evaluate` provide: `$LAB_ROOT`, `$EXP_DIR`, and the `.env` variables. Data is declared in `plan.md` as `data_source: <repo>@<ref>:<path>`.
6. **Secrets come only from environment variables named in `.env.example`.** Never write a value into git, logs, results or the wiki.
7. **Never edit a skill for one experiment.** `new-exp` copies the lab's skills into every worktree; a change to a skill is a change to the lab.
8. **Final evaluation:** {{FILL: how this lab measures an experiment when it closes, and why that way. The scaffold's default: the script `evaluate.py` at the target repo's root, run by `uv run scripts/lab.py evaluate`, which records the script's version with every result so that numbers from different versions are not compared by mistake. Details in the `experiment-lab-loop` skill.}}
9. **Where heavy runs go:** {{FILL: the machines or services GPU and long runs may use, and the skill for each.}}
10. **Data rules:** {{FILL: which data may leave the machine and what may appear in logs, or "in each target's system page".}}

## 6. Attention

No agent can hold the whole lab in view. Keep your own context for judgment: choosing a direction, reading evidence, deciding what a round taught. Hand heavy-reading work with a small result to subagents: gathering sources, a long implementation or debugging session, working a lesson into the wiki.

A subagent sees none of this conversation. Its brief must carry what the piece is for, what good looks like, the reasons it could not guess (the relevant part of `plan.md`, the Experiment Language, the data rules), what to hand back, and when to stop and flag instead of finishing. Review what comes back; do not redo it.
