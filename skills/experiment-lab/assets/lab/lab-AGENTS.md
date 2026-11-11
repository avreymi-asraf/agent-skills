# {{FILL: lab name}} Research Lab (`AGENTS.md`)

This repository is a **research lab**: it holds the memory and the tools for running experiments on external target repositories. The target's code is never stored here. What is stored here is what was tried, what was learned, and what to try next, so that each experiment starts from everything the earlier ones found.

What the lab is for, and the far goal it is growing toward: `cortex/purpose.md`. Read it before any task that leaves you a choice of direction.

## 1. How Far to Go Comes With the Request

Requests of every size arrive here, in any order: "rename this function", "fix this line in the cortex", "think of a new direction and run it to a conclusion". The lab has no automation level and no stages.

- **Read the size from the request itself**, not from the previous request and not from how the lab usually works. If the request does not say how far to go and the readings lead to different work, ask with a concrete case.
- **Small request:** do that thing. Do not start an experiment, a cortex review, or a redesign that was not asked for. If you notice a problem outside the request, mention it and leave it.
- **Wide request:** carry it through. Do not come back for approval at each step. Use the stopping point in the experiment's `plan.md` to decide when to stop. At the end, report what you decided along the way, what you assumed, what you did not check, and where you are unsure.
- **When work is rejected, or the way the lab works has to change:** use the `grow-autonomy` skill. It fixes what agents understand, at the root, and records the reject in `.grow-autonomy/rejects.md`.

## 2. Vocabulary (One Concept, One Name)

- **Target repo:** a git repository outside the lab that experiments run on, registered in `repos.yaml`. Each of its experiments is a branch in it. A stage or theme of the research usually has its own target repo.
- **Experiment:** one idea, pursued through as many rounds as it takes to reach a conclusion. It is a line of inquiry, not a single run. "Try GRPO on the base model" is an experiment. One training run is a round inside it. If the idea itself is replaced (GRPO turns out unsuitable and PPO looks right), close the experiment with that conclusion and open a new one.
- **Plan (`plan.md`, next to the code):** the current best description of how to realise the idea. It starts as detailed as present knowledge allows, which may be quite high-level, and is rewritten in place after every round that teaches something. It is never a signed contract.
- **Round:** one pass of implement → run → analyze. A round can be long.
- **Experiment log (`log.md`, next to the code):** append-only, one entry per round: what was tried, what was seen, what was decided. The plan says where we are; the log says how we got there. "The log" always means this file; `cortex/log.md`, where `lab.py` adds a line per operation, is called by its path. Plan and log are the experiment's **notes**, its own working memory: they live on the experiment's branch in the target repo, in `notes/<exp-name>/`, and are committed with the code they describe. The folder is called `notes` so that `experiments/` means one thing only: the lab's folder.
- **Conclusion:** something learned that a *different* experiment should know. It is what leaves the experiment's own log and is told to the whole lab. *Interim*: the experiment continues; the lesson goes to the cortex now, as a provisional claim. *Final*: there is no point trying further (the result was reached, or the idea is exhausted); the experiment closes.
- **Cortex (`cortex/`):** the lab's memory, in three layers. *Sources*: the experiments themselves, and what was read from outside. *Claims*: what a source establishes, one sentence each. *Synthesis*: findings pages, tensions and the gap map, written on top of claims and rewritten whenever understanding changes.
- **Claim:** one sentence that can be true or false, in its own file in `cortex/claims/`, with an anchor and the conditions it holds under. The anchor says what kind of knowledge it is: `experiment` (a round of ours, with its commit: the lab saw it), `quote` (the words of an outside source: someone else reports it, and for this lab it is a hypothesis) or `stated` (the user said it). A claim is never rewritten; it is confirmed, withdrawn or superseded. An interim conclusion enters the cortex as a provisional claim.
- **Findings page:** a page in `cortex/findings/` about one topic, saying what the lab knows about it by citing claims. One result is a claim; "finding" here always means the page.
- **Final evaluation:** one run of the target repo's `evaluate.py` when the experiment closes. Its number is recorded with its **evaluation version** (`evaluation_version` in `results.json`: which script produced it, and which version of an external benchmark) and is compared with the baseline only when the two versions are the same.
- **Baseline:** the best verified number per target repo and task, shared by all experiments. It lives in `JOURNAL.md` → Current Frontier. A repo may have no baseline yet; then experiments close with a conclusion and no number.
- **Spark:** an idea worth an experiment that has not been opened yet, written down while the context is fresh (`JOURNAL.md`).
- **Experiment Language:** the shared code language of one target repo: its concepts and names, its shared components (the code every experiment uses and none reimplements), and its extension points (where an idea goes in). Recorded in `cortex/systems/<repo>.md`. An experiment is a small change on top of it.
- **Experiment name:** `<id>-<repo-short>-<worktree-name>`, e.g. `0a-model-rl/grpo`. `<id>` is two hex digits, unique in the lab (`new-exp` picks it). `<repo-short>` is `short_name` in `repos.yaml`. `<worktree-name>` is 1-3 short `/`-separated levels, broad to specific. The same name is used for the lab folder `experiments/<exp-name>/`, the notes folder `notes/<exp-name>/`, the worktree `.targets/worktrees/<exp-name>/` and branch `exp/<exp-name>`. Commands take the id (`--exp 0a`) or the full name.

## 3. Where Things Live

| Place | Holds | Rule |
|---|---|---|
| Target repo, branch `exp/<exp-name>`: `notes/<exp-name>/` | The experiment's notes, next to its code: `plan.md` (current state), `log.md` (round log), `runs/` | While open, the plan is rewritten and the log grows, committed together with the code. A branch that starts from an earlier experiment carries that experiment's notes with it. |
| Lab: `experiments/<exp-name>/` | What the experiment tells everyone when it closes: `postmortem.md`, `results.json`, `evaluate.log`, `patch.diff`, and any file the final evaluation wrote there | Created by `new-exp`, filled at close. After it closes, nothing changes except a re-evaluation added to `results.json`. |
| `JOURNAL.md` | Current Frontier (baselines), Active Sparks, the matrix of all experiments (open and closed), the Anti-Repeat Banlist | The routing page: what is best, what is next, what is under way, what not to repeat. |
| `cortex/` | The lab's memory, in three layers: `sources/` (what was read from outside), `claims/` (one sentence each, anchored to an experiment round or to a quote), and the synthesis on top (`findings/`, `tensions/`, `gap_map.md`, `systems/`). Also `purpose.md`, `profile.md`, `index.md`, `log.md` | A findings page is rewritten freely and cites claims. A claim is never rewritten: it is confirmed, withdrawn or superseded. Read `cortex/profile.md` before writing here. Never dump raw logs. |
| `.targets/` (git-ignored) | Clones of target repos (`repos/`) and one worktree per experiment (`worktrees/<exp-name>/`) | Managed by `scripts/lab.py`. |
| `.grow-autonomy/rejects.md` | The reject journal | For the user and for whoever maintains this content. Not instructions. |

## 4. Running an Experiment, and Working on the Cortex

Load the `experiment-lab-loop` skill. It is the only place the loop is described: find a direction, write the plan, work in rounds, tell the lab what others need, close with a final evaluation. Do not load it for requests that are not about an experiment.

The cortex has its own operations, and they are the `cortex` skill: adding a source, investigating a gap from outside sources, answering from what the lab knows, the periodic review. This lab's layout and rules for them are in `cortex/profile.md`. Two things need the profile and not the skill: writing a claim during an experiment (the loop skill says when; the form is `cortex/claims/_TEMPLATE.md`), and a small edit to a page. After either, run the check in `cortex/profile.md` §6.

## 5. What Always Holds

Each of these holds for every request, whatever its size.

1. **Experiments on one target repo share one code language and one set of components: its Experiment Language** (`cortex/systems/<repo>.md`). Read it before writing any experiment code.
   - An idea goes in at an extension point named there. A variant is a config value or a flag, not a copied script.
   - Use the shared components (data loading, run entry and config, runner, observation and analysis tools, evaluation) as they are. Do not reimplement or fork one inside an experiment. If one is wrong or too narrow, fix it as a shared component and say so in `plan.md`: every later experiment inherits it.
   - Something new that other experiments will need is written as a shared component and added to the system page when the experiment is kept.
   - Change the language itself only when that change is the idea. If an idea does not fit the language, stop and decide which it is; do not code around it.
   - The test: the experiment's diff against its base reads as the idea and nothing else.

   *Why:* this is what makes the lab's experiments add up. A difference between two results can be attributed to the idea, someone who understood experiment `0a` opens `0b` and sees only what changed, and the tools and findings of one experiment work for the next.
2. **Experiment code lives in its own worktree and branch.** Never edit `.targets/repos/<repo>` (the base clone). `uv run scripts/lab.py new-exp` creates `.targets/worktrees/<exp-name>/` on branch `exp/<exp-name>`. *Why:* experiments stay independent and each can be reproduced alone.
3. **Experiment branches are pushed and never merged** into the target's default branch unless the user explicitly asks. An experiment that builds on an earlier one starts from it (`new-exp --base-branch exp/<earlier-exp-name>`). *Why:* every result must survive a fresh clone, and no experiment may silently change the ground under another.
4. **A technical failure is not a scientific result.** A crash, out-of-memory, missing credential or typo is `INFRA_INCONCLUSIVE`, or simply a round that failed. Never write a claim, a line in a findings page or an Anti-Repeat Banlist entry saying that an idea failed before it actually ran cleanly. *Why:* a false refutation stops every later agent from trying a good idea.
5. **Everything runs from a fresh clone, anywhere** (a laptop, a cloud session, CI, a cluster). Whatever an agent needs is in this repo: instructions, skills, tools. A session elsewhere sees only what is pushed, in both repositories: push the experiment branch after every round that matters, and commit and push this repo whenever it changed (an experiment opened or closed, a claim, the journal). `mount-exp` in a fresh clone finds an experiment through its folder here. Never write absolute or machine-specific paths into docs, code, configs, plans or the cortex. Use repo-relative paths, or the variables `lab.py run` and `lab.py evaluate` provide: `$LAB_ROOT`, `$EXP_DIR`, and the `.env` variables. Data is declared in `plan.md` as `data_source: <repo>@<ref>:<path>`.
6. **Secrets come only from environment variables named in `.env.example`.** Never write a value into git, logs, results or the cortex.
7. **Python is `uv`, and only `uv`.** `uv run`, `uv add`, `uv sync`, in the lab and in every target repo. Never `pip install`, a bare `python`, or a hand-made virtual environment. *Why:* a fresh clone on any machine reaches the same environment with one command, and a dependency added in one round is there in the next session.
8. **Never edit a skill for one experiment.** `new-exp` copies the lab's skills into every worktree; a change to a skill is a change to the lab.
9. **Final evaluation:** {{FILL: how this lab measures an experiment when it closes, and why that way. The scaffold's default: the script `evaluate.py` at the target repo's root, run by `uv run scripts/lab.py evaluate`, which records the script's version with every result so that numbers from different versions are not compared by mistake. Details in the `experiment-lab-loop` skill.}}
10. **Where heavy runs go:** {{FILL: the machines or services GPU and long runs may use, and the skill for each.}}
11. **Data:** {{FILL: where the data comes from (repo and path), which data may leave the machine and what may appear in logs, or "in each target's system page".}}

## 6. Attention

No agent can hold the whole lab in view. Keep your own context for judgment: choosing a direction, reading evidence, deciding what a round taught. Hand heavy-reading work with a small result to subagents: a long implementation or debugging session, an investigation of a gap from outside sources, a cortex review.

A subagent sees none of this conversation. Its brief must carry what the piece is for, what good looks like, the reasons it could not guess (the relevant part of `plan.md`, the data rules), the target's Experiment Language (a subagent that has not seen it will write its own loader and its own loop), what to hand back, and when to stop and flag instead of finishing. Review what comes back; do not redo it.
