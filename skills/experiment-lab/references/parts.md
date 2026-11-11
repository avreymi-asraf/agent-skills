# Parts of a lab

Each part is listed with what it must hold and the failure that shows when it does not. Paths are the scaffold's; a lab may rename them, as long as each name means one thing.

## `AGENTS.md` (always loaded)

Holds the picture and nothing procedural:

1. What the lab is, in one paragraph, and a pointer to `wiki-llm/purpose.md`.
2. How far to go comes with the request: small stays small, wide is carried through and ends with a report.
3. Vocabulary: target repo, experiment, plan, round, experiment log, conclusion, Spark, Experiment Language, experiment name. One meaning each, with an example where a word could be read two ways.
4. Where things live, as one table.
5. A pointer to the loop skill, and when not to load it.
6. What always holds: a short list, each item with its reason. The Experiment Language comes first. The last items are this lab's own (evaluation, where runs go, data).
7. Attention: what to keep in the main context, what to hand to a subagent, what a brief must carry.

Every line here is read on every request, including "fix this label". A line that only matters during an experiment belongs in the loop skill.

*Shows when wrong:* the loop is described here and in the skill, and the copies disagree. A rule without a reason is followed where its sentence fits and nowhere else. The file grows by one line per incident.

## `wiki-llm/purpose.md`

What the lab is for, the far goal, and how results are judged. The far goal is in the user's words. How results are judged is this lab's own answer and is the place for its view of measurement: what a number has to measure to matter, how cheap a measurement must be, when simpler wins.

*Shows when wrong:* an agent on a wide task optimizes the nearest thing (finishing, a number going up). Template text left in place reads as an answer and is obeyed.

## The lab's `experiment-lab-loop` skill

The only description of the loop. Its topics: find a direction (the one fixed step is crossing the idea with what the lab knows), write the plan, work in rounds, what to tell the lab, conclusions (interim and final, provisional claims settled at close), close the experiment, the evaluation as this lab does it, the CLI's commands with what each does not do, and one worked example.

It lives in `.agents/skills/experiment-lab-loop/` with a relative link from `.claude/skills/`, and `new-exp` copies it into each worktree so an agent working inside the target repo has it too.

*Shows when wrong:* agents load it for requests that are not about an experiment (the description is too wide), or do not load it at all (`AGENTS.md` does not point to it).

## The lab's `review-wiki` skill

One pass over `wiki-llm/` and `JOURNAL.md`, run from time to time in a fresh context: is the knowledge well built, well linked and still true. It fixes what the lab's evidence settles and reports what needs the user. Every experiment starts by reading this knowledge, so a wrong claim there steers all of them and nobody sees it happen.

## Templates (`experiments/_TEMPLATE/`)

- `notes/plan.md`, copied into the worktree: the idea (stable), what we know and how we will do it (rewritten), the Experiment Language block (extension point, shared components used, what stays fixed, what is added to the shared set), open questions, stopping point, and the `data_source` line.
- `notes/log.md`, copied into the worktree: one entry per round with Tried, Run plan, Saw, Decided, Told the lab. The run plan is written before the run, because running is the expensive part of a round.
- `postmortem.md`, in the lab folder: verdict, the final conclusion and why we stopped, why it went this way, what happened to each provisional claim, what happened to the Experiment Language, Sparks.
- `results.json`, in the lab folder: written by the CLI.

A section in a template is a behavior. "Told the lab" in every round entry is what makes the agent ask the question every round. When a behavior is wanted, look for the template field first.

*Shows when wrong:* agents invent structure (an `attempt-1-oom/` folder, a second plan file) because the work they are doing has no place in the templates.

## `scripts/lab.py`

Mechanical steps only. It creates the branch, the worktree and both folders with the right names; runs a command in the worktree with `.env`, `$LAB_ROOT` and `$EXP_DIR` set; runs the final evaluation and records what it measured; adds the matrix row. It does not choose a direction, fill a plan, compare with the baseline, or write to the Frontier, the Sparks or the Banlist: those carry judgment and are written by hand.

When adding a command, keep to that line. A command that refuses to continue until a condition holds is a gate, and belongs to the mistake in [What-the-loop-needs] 1.

*Shows when wrong:* the docs promise what a command does not do, and the journal goes stale because everyone assumed the tool updated it.

## System page per target (`wiki-llm/systems/<repo>.md`)

Overview, then the Experiment Language: the mental model, the vocabulary, a table of shared components (data, run entry and config, runner, observation and analysis, evaluation) with where each lives, the extension points where an idea goes in, what a run leaves behind, commands, data source and rules. Then checks and measurements, and known limits. This is the page a lab's experiments depend on most ([One-code-language-per-target] in the skill); write it with the care of an interface many people will build on, and keep it true to the code. The header lines (`> Repo: ... | Fingerprint: git:<sha>`, `> Monitored:`, optional `> Branch:`) let `check-drift` report when the code moved since the page was written.

*Shows when wrong:* each experiment brings its own loader, loop and file layout; an experiment's diff is mostly plumbing; the analysis tool from one experiment does not open the runs of another; nobody can tell whether a difference in results came from the idea.

## `JOURNAL.md`

The routing page: Current Frontier (best verified baseline per target and task), Active Sparks, the experiment matrix, the Anti-Repeat Banlist. Only a clean run puts an idea on the Banlist, and each entry says under which condition it would be worth trying again.

## The rest of the wiki

`gap_map.md` (open questions), `findings/` (lessons by topic, each claim with its source experiment and whether it is provisional), `literature/`, `index.md`, `log.md`. Built and maintained with the `wiki-llm` skill.

## The two homes of an experiment

| | Next to the code | In the lab |
|---|---|---|
| Where | Target repo, branch `exp/<exp-name>`, `notes/<exp-name>/` | `experiments/<exp-name>/` |
| Holds | `plan.md`, `log.md`, `runs/` | `postmortem.md`, `results.json`, `evaluate.log`, `patch.diff` |
| For | Whoever continues this experiment | Whoever does a different one |
| Changes | Every round, committed with the code | Written at close, then fixed |

The folders have different names on purpose, so that `experiments/` means the lab's folder only.

## `.grow-autonomy/rejects.md`

The reject journal. Nothing in the lab's instructions links to it, and its entries never become rules. Before changing an area of the lab's content, read the entries for that area: they say which paragraphs are there because of a root that was once found.

## `repos.yaml`, `.env.example`

`repos.yaml`: one entry per target repo (`name`, `url`, `short_name`, `default_branch`). HTTPS urls, so the lab clones the same way on a laptop and in a cloud session. `.env.example`: the name and purpose of every variable experiments read; values live in `.env` or in the platform's secret store.
