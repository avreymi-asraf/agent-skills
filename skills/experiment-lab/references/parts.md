# Parts of a lab

Each part is listed with what it must hold and the failure that shows when it does not. Paths are the scaffold's; a lab may rename them, as long as each name means one thing.

## `AGENTS.md` (always loaded)

Holds the picture and nothing procedural:

1. What the lab is, in one paragraph, and a pointer to `cortex/purpose.md`.
2. How far to go comes with the request: small stays small, wide is carried through and ends with a report.
3. Vocabulary, in short form: experiment repo, experiment, try, start branch, map of tries, session, reduce, note to the lab, lab step, lab kit, plan, round, log, conclusion, cortex, claim, evaluation and evaluation version, baseline, kept, Spark, Experiment Language, experiment name. One meaning each. The full glossary, with what each term is not, is the loop skill's `references/glossary.md`, and it is the authority.
4. Where things live, as one table.
5. A pointer to the loop skill, and when not to load it; a pointer to the `cortex` skill for work on the lab's knowledge base.
6. What always holds: a short list, each item with its reason. The Experiment Language comes first. The last items are this lab's own (evaluation, where runs go, data).
7. Attention: what to keep in the main context, what to hand to a subagent, what a brief must carry.
8. Where what was learned is written, by who it is true for: the experiment's notes, the cortex, the lab's own files, or a proposal for the source of an outside skill. Short lines; the reasoning is in `grow-autonomy`.

Every line here is read on every request, including "fix this label". A line that only matters during an experiment belongs in the loop skill.

*Shows when wrong:* the loop is described here and in the skill, and the copies disagree. A rule without a reason is followed where its sentence fits and nowhere else. The file grows by one line per incident.

## `cortex/purpose.md`

What the lab is for, the far goal, and how results are judged. The far goal is in the user's words. How results are judged is this lab's own answer and is the place for its view of measurement: what a number has to measure to matter, how cheap a measurement must be, when simpler wins.

*Shows when wrong:* an agent on a wide task optimizes the nearest thing (finishing, a number going up). Template text left in place reads as an answer and is obeyed.

## The lab's `experiment-lab-loop` skill

The only description of the loop. Its topics: the system (names, who may write what), find a direction (the one fixed step is crossing the idea with what the lab knows), open the experiment, open a try and work it in rounds, reduce, what to tell the lab, the lab step, managing many tries, close the experiment, and one worked example. Its `references/` hold the glossary, the system guide, each operation as what it finds and what it leaves, working from Claude Code cloud sessions, the evaluation as this lab does it, and the CLI's commands with what each does not do.

It lives in `.agents/skills/experiment-lab-loop/` with a relative link from `.claude/skills/`, and the lab commits it on every try branch as part of the lab kit, so a try session working inside the experiment repo has it too.

*Shows when wrong:* agents load it for requests that are not about an experiment (the description is too wide), or do not load it at all (`AGENTS.md` does not point to it).

## Templates (`experiments/_TEMPLATE/`)

- `notes/plan.md`, written on the start branch and carried by every try: the idea (stable), what we know and how we will do it (rewritten), the Experiment Language block (extension point, shared components used, what stays fixed for every try, what is added to the shared set), open questions, stopping point, the `data_source` line, and `This Try`, where a try's brief is written when it is opened.
- `notes/log.md`, on a try branch: one entry per round with Tried, Run plan, Saw, Decided, For the lab, Signal, and one entry per try taken in by a reduce. The run plan is written before the run, because running is the expensive part of a round.
- `tries.md`, in the lab folder: the map of tries. One line per try: the try branch, its status, a comment of at most 100 characters. Kept this small on purpose: it is what a managing session reads, and a file per try grew into a second copy of the try's notes.
- `lab-steps.md`, in the lab folder: one lab step record per lab step, with the answers to a try's questions.
- `postmortem.md`, in the lab folder: verdict, the final conclusion as the lab step records show it together and why we stopped, why it went this way, what happened to each provisional claim, what happened to the Experiment Language, Sparks.
- `results.json`, in the lab folder: written by the CLI. Its `verdict` is `OPEN` until `record-verdict`, and `evaluation_version` is what makes two numbers comparable.

A section in a template is a behavior. "For the lab" in every round entry is what makes the agent ask the question every round. When a behavior is wanted, look for the template field first.

*Shows when wrong:* agents invent structure (an `attempt-1-oom/` folder, a second plan file) because the work they are doing has no place in the templates.

## `scripts/lab.py`

Mechanical steps only. It gives ids and names; writes the lab folder, the journal row and the lines of the map of tries and publishes them before it creates the start branch or a try branch; prints the map of tries; runs a command in a try's worktree with `.env`, `$LAB_ROOT` and `$EXP_DIR` set; saves a try's code change, runs the evaluation on it and records what it measured; completes the matrix row with the verdict. (The shipped `lab.py` still implements the earlier single-branch form; the loop skill's `references/commands.md` says what it has to do.) It does not choose a direction, fill a plan, compare with the baseline, or write to the Frontier, the Sparks or the Banlist: those carry judgment and are written by hand.

When adding a command, keep to that line. A command that refuses to continue until a condition holds is a gate, and belongs to the mistake in [What-the-loop-needs] 1. A command may say what it noticed (an experiment repo with no system page, a part cut from the context pack, the lab repo left to push): a printed line reaches the agent at the moment it matters and blocks nothing.

*Shows when wrong:* the docs promise what a command does not do, and the journal goes stale because everyone assumed the tool updated it.

## System page per experiment repo (`cortex/systems/<repo>.md`)

Overview, then the Experiment Language: the mental model, the vocabulary, a table of shared components (data, run entry and config, runner, observation and analysis, evaluation) with where each lives, the extension points where an idea goes in, what a run leaves behind, commands, data source and rules. Then checks and measurements, and known limits. This is the page a lab's experiments depend on most ([One-code-language-per-repo] in the skill); write it with the care of an interface many people will build on, and keep it true to the code. The header lines (`> Repo: ... | Fingerprint: git:<sha>`, `> Monitored:`, optional `> Branch:`) let `check-drift` report when the code moved since the page was written.

*Shows when wrong:* each experiment brings its own loader, loop and file layout; an experiment's diff is mostly plumbing; the analysis tool from one experiment does not open the runs of another; nobody can tell whether a difference in results came from the idea.

## `JOURNAL.md`

The path of the research, growing like a tree in its direction, holding only what the lab did and decided: Current Frontier (best verified baseline per experiment repo and task, each with its evaluation version), Active Sparks, the experiment matrix (one row per experiment from the moment it is opened, written by `lab.py`), the Anti-Repeat Banlist. Only a clean run puts an idea on the Banlist, and each entry says under which condition it would be worth trying again.

## The cortex (`cortex/`)

The lab's knowledge base of its field, built with the `cortex` skill: as wide a collection as the lab can build of what is known that may advance the research. Most of it comes from outside, and the lab's experiments are one kind of source among the others. Three layers, with different rules:

- **Sources.** What was read from outside, of any kind (`cortex/sources/`: a note per source and the text that was actually read), and the experiments themselves (the lab folder with its map of tries and lab step records, and the try branches).
- **Claims** (`cortex/claims/`). One sentence per file, with an anchor (`experiment`: name, try, round, commit; `quote`: the source's words; `stated`: the user), the conditions it holds under, and a status. A claim is corrected in place only at its blind verification; after that, and for an `experiment` claim from the start, it changes status and is never rewritten (the profile's §4). An interim conclusion enters here as `provisional` and is settled when its experiment closes.
- **Synthesis.** `findings/` (what is known about a topic, citing claims of every anchor), `tensions/` (two claims that disagree), `gap_map.md` (open questions). These are rewritten whenever understanding changes. Also `index.md` and `log.md`.

*Shows when wrong:* a findings page states as the lab's own result something only a paper reports. A claim is edited in place and the pages that cited it now say something nobody checked. Claims pile up and no findings page changes. The cortex holds only what the lab's experiments showed, and nothing is added unless a gap asks. Provisional claims of closed experiments are still provisional.

## `cortex/profile.md`

What makes this cortex a lab's: what it is for (knowing the field as widely as possible so the research advances; what is worth writing from outside and from an experiment), how it differs from the journal, the layout, what each kind of anchor says (where a claim comes from and how it is checked, not its rank; the journal's Banlist and Frontier rest on `experiment` claims because they record the lab's own path), when claims are written and settled, the check command, and what a review looks at in this lab beyond the skill's own list (the journal, the experiments' results, drifted system pages).

The general `cortex` skill is copied into the lab unchanged; this file is the only place where the lab's knowledge base is described as the lab's. A change to how agents write to the cortex goes here or into the templates beside it (`claims/_TEMPLATE.md`, `findings/_TEMPLATE.md`, `sources/_TEMPLATE.md`).

*Shows when wrong:* agents write to the cortex as to a general knowledge base: a claim for every sentence of a paper, a page per source. Or the profile restates the loop and the two copies drift.

## The `cortex` skill, in the lab

The operations on the lab's knowledge base: add a source (the main way the cortex grows), investigate a gap from outside sources, answer from what the lab knows, verify new claims, review. One skill for all of them (`/cortex review`, `/cortex investigate G4`), and one script, `.agents/skills/cortex/scripts/cortex.py`, that checks anchors and links and lists claims. The review pass runs from time to time in a fresh context: every experiment starts by reading this knowledge, so a wrong claim there steers all of them and nobody sees it happen.

## The two homes of an experiment's work

| | Next to the code | In the lab |
|---|---|---|
| Where | Experiment repo, try branch `<experiment name>/<try name>`, `notes/<experiment name>/` | `experiments/<repo short name>/<experiment name>/` |
| Holds | `plan.md`, `log.md`, `runs/` | `results.json`, `postmortem.md`, the map of tries `tries.md`, the lab step records `lab-steps.md`, and each lab step's files (`evaluate.log`, `patch.diff`, `metrics.json`) |
| For | Whoever continues or reduces this try | Whoever does a different try or a different experiment |
| Changes | Every round, committed with the code | Written when an experiment or a try is opened, at every reduce and lab step, and at close; then fixed |

The folders have different names on purpose, so that `experiments/` means the lab's folder only.

## `.grow-autonomy/rejects.md`

The reject journal. Nothing in the lab's instructions links to it, not even by path: an agent reaches it through `grow-autonomy`, which says where it lives. Its entries never become rules. Before changing an area of the lab's content, read the entries for that area: they say which paragraphs are there because of a root that was once found.

## `repos.yaml`, `.env.example`

`repos.yaml`: one entry per experiment repo (`name`, `url`, `short_name`, `default_branch`). HTTPS urls, so the lab clones the same way on a laptop and in a cloud session. `.env.example`: the name and purpose of every variable experiments read; values live in `.env` or in the platform's secret store.
