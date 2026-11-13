---
name: experiment-lab-loop
description: Run an experiment in this research lab (cortex, JOURNAL.md, a map of tries, experiment repos whose branches are tries). An experiment is one direction, saved in the lab and worked through tries, each on its own try branch and recorded in the lab's map of tries. A lab session opens experiments and tries, reduces several tries into one, runs a lab step on a chosen try (review, evaluation, conclusions into the cortex) and closes; a try session works one try in rounds. Use when the user asks to find a research direction, open, plan, continue or close an experiment, open or work a try, reduce, merge or drop tries, run a lab step or an evaluation, manage many tries from one long-running session, decide what belongs in the cortex or journal, or work from Claude Code cloud sessions. Also when a term of the lab (experiment repo, start branch, try, map of tries, reduce, lab step, note to the lab, lab kit) needs its exact meaning.
---

<experiment-lab-loop>

# Experiment lab loop

The lab searches by keeping many directions alive and reducing them. An **experiment repo** is one big idea. An **experiment** is one direction in it: a start branch and try branches in that repo, and a lab folder and a journal row in the lab. A **try** is one attempt at the experiment, on its own branch, recorded in the lab's **map of tries**. A **reduce** turns several tries into one. A **lab step** takes one try, reviews it, evaluates it when it can, and writes what it shows into the lab. What moves up is always smaller than what was below it.

```
        LAB  (cortex, journal, lab folders with the map of tries, lab.py)            EXPERIMENT REPO
find a direction ─▶ open the experiment ───────────────────────────▶ 02-probes/main   start branch (a template)
                    open a try ──── a line in tries.md: live ──────▶   ├─ …/trl-fix-lr   rounds: implement → run → analyze
                    open a try ──── a line in tries.md: live ──────▶   ├─ …/trl-d-lr
                    reduce ──────── records: merged / dropped ─────▶   └─ …/trl          the one that remains
claims, topics   ◀─ lab step on a chosen try ◀── notes to the lab, evaluation ◀── any try branch
close ◀──────────── the lab step records, aggregated
```

There are two levels of sessions. A **try session** works one try and sees only its branch. A **lab session** does everything else, in the lab: it is the one that draws connections between tries and between experiments, and the lab's records are what it thinks with. Every operation can be done by a person or by an agent of any kind, and the next one by someone else on another machine. So the state is read from the lab's records and from the branches, never from a conversation, and every word below has one meaning.

- **[The-system]**: the parts, the names, and who may write what.
- **[Find-a-direction]**: choosing the idea, crossed with what the lab knows.
- **[Open-the-experiment]**: the start branch and the first plan.
- **[Work-in-rounds]**: opening a try, and what a try does.
- **[Reduce]**: several tries become one; the others leave the map.
- **[What-to-tell-the-lab]**: what stays in a log and what every other experiment needs. The hardest judgment in the loop.
- **[Lab-step]**: one try reviewed, evaluated and told to the lab; how knowledge is asked for.
- **[Manage-many-tries]**: the long-running session that holds the process and not the content.
- **[Close-the-experiment]**: a decision made in the lab, from the lab step records.
- **[References]**: the system guide, the operations, cloud sessions, the evaluation API, the commands.
- **[Example]**: one experiment from idea to close.

How far to carry a request (one operation, guided step by step, or a whole experiment) is set by the request; see the lab's `AGENTS.md` §1, which also holds the rules that always hold. Companion skills: `cortex` for the operations on the lab's knowledge base (`add`, `investigate`, `ask`, `verify`, `review`), with this lab's layout and statuses in `cortex/profile.md`; `code-as-tools` when writing experiment code; `grow-autonomy` when the user rejects how the lab worked or the way it works has to change. Where heavy runs go, and the skill for it, is in `AGENTS.md`.

</experiment-lab-loop>

<The-system>

The terms, with their exact forms, are in the glossary: §3 of the lab's `AGENTS.md`. A try branch carries the terms a try meets, in §5 of its own `AGENTS.md`. Use them as written; a synonym is read as a different thing. The short form, with the running example (experiment repo `model-repo`, short name `model`):

| Thing | Name | Example |
|---|---|---|
| Experiment | `<id>-<idea>` | `02-probes` |
| Start branch | `<experiment name>/main` | `02-probes/main` |
| Try branch | `<experiment name>/<try name>` | `02-probes/trl-fix-lr` |
| Notes, on a branch | `notes/<experiment name>/` | `plan.md`, `log.md`, `runs/` |
| Lab folder | `experiments/<repo short name>/<experiment name>/` | `experiments/model/02-probes/` |
| Map of tries, in the lab folder | `tries.md` | a line: `02-probes/trl-fix-lr` · `live` · a comment of at most 100 characters |
| Lab step records, in the lab folder | `lab-steps.md` | an entry: ``## `trl-fix-lr` · Lab step 2 · <date> · commit `<sha>` `` |

The id is two hex digits, unique in the lab, so `--exp 02` names the experiment everywhere. The name is the topic; which code an experiment starts from is its **base**, and it can be any earlier try branch.

**The start branch is only a template.** It holds the lab kit, the first plan and an empty log. Tries start from it, and nothing enters it afterwards. An experiment's result is never "on main": it is on try branches, and what the lab concluded from them is in the lab folder.

**The lab says what exists.** A try exists from the moment the lab records it, and it is live as long as its line in the map of tries (`tries.md`) says `live`. It stops being live when a reduce takes it into another try (`merged` or `dropped`), when a lab step ends it (`dropped`), or when its experiment closes (`closed`). Git decides none of this: a branch that exists, is old, or was merged somewhere proves nothing. Branches of tries that left the map stay as history; nobody works or reads them again.

**Who may write what.** Reading is open everywhere. Writing is not:

| What | Written by | Never by |
|---|---|---|
| A try branch: code and its notes | `new-try` (its first commit), whoever works that try, a reduce into it | Another try |
| The start branch | `new-exp` and the opening commit, once | Anyone afterwards |
| The lab: the map of tries, the cortex, the journal | A lab session: opening, reduce, lab step, close | A try session |
| The experiment repo's default branch | Nobody | Any experiment |

These are not locks; the hosting allows the pushes. They hold because the branch means something to whoever reads it next.

**A try branch is a whole system.** A fresh checkout of it holds the code, the notes with the brief, `EXPERIMENT_LANGUAGE.md` and the **lab kit** (`AGENTS.md`, the skills), so a try session needs nothing else. The one thing it does not hold is the lab's records. They have a single live copy, on the lab's default branch, and every working copy reads them from there.

Why it is built this way, and how information moves through it: [system-guide.md](references/system-guide.md).

</The-system>

<Find-a-direction>

This is a stage of its own and the one where research is won or lost. There are a hundred ways to do it: read papers, look for a technique in a neighbouring field, ask why a bottleneck exists, look again at a surprising round of an old experiment, argue for the opposite of the obvious move. Pick the way that fits; none is required.

What is required is to **cross the idea with what the lab already knows**, because an idea that ignores it either repeats old work or misses the reason the last attempt failed:

```bash
uv run scripts/lab.py context-pack   # writes cortex/query_pack.md: purpose, gap map, journal, cortex index
```

The pack is a first look, not the sources: a part that did not fit ends at a line marked **[CUT]** that names the file to open.

- `cortex/purpose.md`: does the idea serve what the lab is for?
- `cortex/gap_map.md` and `JOURNAL.md` → Active Sparks: is it one of the open questions, or does it open a better one?
- `JOURNAL.md` → Experiment Matrix: is an experiment on this idea already open (`OPEN` in the Verdict column)? Then open a try in it; do not open a second experiment.
- `JOURNAL.md` → Anti-Repeat Banlist: was it already refuted? Under which conditions?
- `cortex/topics/`, `cortex/tensions/`, and the postmortems and lab step records in `experiments/`: what did earlier work learn that changes this idea? Follow a topic page down to the claims it cites: each says whether the lab saw it (`experiment`) or someone else reports it (`quote`), and under which conditions. `uv run .agents/skills/cortex/scripts/cortex.py claims --grep <term>` searches all claims by a word.
- `EXPERIMENT_LANGUAGE.md` on the kept try branch (the system page `cortex/systems/<repo>.md` names it): can the idea be said in the repo's Experiment Language? Which extension point does it go into, and which shared components does it use? Creativity belongs in the idea, not in a new vocabulary or a new codebase. If the idea does not fit, that is the first thing to settle: either changing the language is the idea, or that change is an experiment of its own that comes first. An experiment repo with no Experiment Language yet gets one from its first experiment, whose one job is to connect the pipeline end to end.

Run `uv run scripts/lab.py sync-repos` and then `check-drift` when the base may have moved.

**Going outside is part of this stage, and of the lab's work at any time.** The cortex is the lab's knowledge base of its whole field, not a record of its experiments: most of what it holds comes from outside, and a claim from a paper matters as much as a claim from a round of ours. So read widely around the idea and add what you read (`cortex add`), whether or not a gap asked for it. An open gap is often answered faster by reading than by running: that is `cortex investigate`, which starts from the gap's row and ends by updating it. A `quote` claim says what a source reports under the source's conditions; whether it holds in this lab's setting is a question an experiment can answer.

On a wide request, when experiments have closed since the cortex was last reviewed (`cortex/log.md`), hand a `cortex review` to a subagent before choosing: a direction chosen from a stale cortex is chosen badly.

Ideas you considered and dropped are written in the first plan, under Alternatives considered. One that is worth an experiment of its own is also written as a Spark in `JOURNAL.md` → Active Sparks, now, while the reason is fresh.

</Find-a-direction>

<Open-the-experiment>

Only through the lab, whoever does it, person or agent:

```bash
uv run scripts/lab.py new-exp --repo <experiment repo> --name <idea> [--base <branch>]
```

It gives the id, writes the lab folder and the journal row (`OPEN`) and publishes them to the lab's default branch, which is what reserves the id and lets any other session find the experiment. Then it creates the start branch from the base and writes the experiment template on it: the lab's `start-branch/` folder (the try `AGENTS.md`, the first plan, an empty log) and the lab's skills. This is the only time the template is copied; every try starts from the start branch and carries it. Write the first plan, commit it on the start branch and push ([operations.md](references/operations.md) §1). After that the start branch is not touched again.

The first plan describes **how to realise the idea, as far as is known right now**. Write it as exactly as present knowledge allows, and no more exactly than that. On day one it may say little more than "try GRPO on the base model", with a list of what is unknown. Every try starts from it and carries it; a try rewrites its own copy as it learns.

The first plan holds:

- **The idea** and why it is worth trying. This part is stable. If it has to be replaced, the experiment is over.
- **What we know and how we will do it**: the realisation, at whatever level of detail is honest today.
- **Open questions**: what the tries have to find out.
- **Stopping point**, in free text: what result would be enough, and what would make it not worth continuing (a budget of GPU hours or rounds, a sign that the idea is exhausted). Reaching it does not stop the work mechanically. It is the moment to decide: conclude, or go on with a reason. On a wide request you make that decision and report it; otherwise you bring it to the user.
- **Experiment Language**: the extension point the idea goes into, the shared components it uses, **what stays fixed for every try** (the data and split, and the measurement competing tries will be compared on), and anything it adds to the shared set.
- `data_source: <repo>@<ref>:<path>` in the frontmatter, never a local path.
- **This Try**: empty on the start branch. Each try's brief is written here when the try is opened.

</Open-the-experiment>

<Work-in-rounds>

**Opening a try** is done in the lab, with a **brief**: what to try and what makes this try different, whether it competes or cooperates with which tries, how far to go, when to stop and flag.

```bash
uv run scripts/lab.py new-try --exp <id> --name <try name> --brief-file <file> [--base <branch>]
```

It writes the try's line in `tries.md` (the try branch, `live`, a comment of at most 100 characters saying what it tries) and publishes it, then creates the try branch from the start branch (which already holds the lab kit and the notes), writes the brief in the plan's `This Try` section, and pushes it. So whoever works the try **starts on the try branch and pushes to the same branch**: a local worktree (`lab.py mount`), or a try session in the cloud ([claude-code-cloud.md](references/claude-code-cloud.md)). An experiment with one try is normal, especially at the beginning. Competing tries do not read each other, so their results can be told apart.

**Working the try.** Start by reading `AGENTS.md` and `EXPERIMENT_LANGUAGE.md` at the root, and the plan with its brief. A try writes code and the notes on its own branch, and nothing else: not another branch, not the lab kit, not the lab. Each round:

1. **Implement** the next step, in the repo's Experiment Language: put the idea in at its extension point, use the shared components as they are, and make a variant a config value, not a copied script. When you need something the shared set lacks (a metric, a view of the data, a plot), write it as a shared component in the shared style. When a shared component is wrong, fix it there and say so in the plan. Read your diff against the base before committing: it should read as the idea and nothing else. Remote runners ship committed code only.
2. **Run** it. During rounds you are free to measure however is useful: a short training run, a probe, a notebook, the repo's own checks. Hold to what the first plan fixes for every try. Heavy runs go where the lab's `AGENTS.md` says. Running is the expensive part of a round, so before starting, write in the log what question the run answers, what you will look at while it runs, and what would make you stop it early. Then watch it with the repo's own observation tools, and stop a run that has already answered its question or cannot.
3. **Analyze** what came back. Look at cases and traces, not only at the number, and ask why it moved or did not.
4. **Write the round into the log** (`notes/<experiment name>/log.md`): what was tried, what was seen, what was decided, where the run's files are (`runs/<nn>-<short-name>/`, small files only), the notes to the lab if any, and the signal. A failed round is logged like any other; say whether the failure was technical or a real result. The entry's form is in [operations.md](references/operations.md) §3.
5. **Update the plan** if the round changed what we know. Commit code, log and plan together and push the try branch, so the round survives the session.
6. **Need to know something?** Read the lab first ([Lab-step]).

**Finishing.** Set the **signal** in the last log entry: `ready` (for a lab step or a reduce), `failed` (nothing worth keeping; technical or a real result), or `blocked` (a question must be answered first). Push, report, and stop. A try does not open tries, reduce, run a lab step, or open a pull request. If the try turned out to be a direction of its own, say so in the log and stop: the new experiment is opened through the lab, from this try branch.

A long stretch of rounds without a conclusion is normal. Check it against the stopping point from time to time. A long implementation or debugging session is a good piece to hand to a subagent, with the relevant part of the plan, the Experiment Language, the data rules, what to hand back, and when to stop and flag.

</Work-in-rounds>

<Reduce>

Tries produce a mess, and that is fine: plans that changed, logs full of dead ends, two tries that disagree. A reduce takes **two or more tries and leaves one**. It is done in the lab ([operations.md](references/operations.md) §4, with the git commands):

1. Choose the **target**: an existing try that nobody is working at that moment, or a new try opened for the reduce (so reducing into a new try is also opening a try).
2. For each other try: bring it in without committing, **decide which code enters** (all, part or none), and **synthesize the notes by meaning**, not by text: rewrite the target's plan in place, and append one entry to its log saying what that try attempted, what it saw, what entered and why.
3. Push the target, then **update the map**: each reduced try's line says `merged` or `dropped`, into which try, and in its comment how it ended.

Very often a reduce is simply dropping the weaker try and keeping its few lessons. This is how a try ends: it is not deleted, it leaves the map, and its line says where what it taught went. The lesson of a failure is often what the remaining try most needs; a technical failure gets an entry that says it was technical. When two tries reached contradicting lessons and the evidence does not decide, keep both and say so; do not pick one.

What whoever continues the target does not need is dropped on purpose. The notes to the lab that no lab step has read yet are the exception: they are carried over word for word. After a reduce the target's signal is `working`, because the combined code has not been run; running it is its next round.

</Reduce>

<What-to-tell-the-lab>

Work is written for two readers, and the second needs far less than the first.

- **The log and the plan on the try branch** are for whoever continues *this try*, or reduces it. They hold everything, including what turned out not to matter: settings, dead ends, debugging, partial numbers.
- **The lab** (the lab step records, the cortex, the journal, and the postmortem at the end) is for whoever does a *different* try or a *different* experiment and will never open this branch. Their attention is scarce, and every line written there is read by all of them.

Most of what happens in a round stays in the log. The question for each thing you learned is: **would someone working on a different idea do their work differently if they knew this?** If yes, write it as a **note to the lab**, under `For the lab` in the log entry.

| Learned in a round | Where it goes | Why |
|---|---|---|
| The reward parser in this implementation rejects free-text answers | Log only | It is about this try's code. |
| Learning rate 2e-5 diverged, 1e-5 is stable for this recipe | Log; a sibling learns it at a reduce | A setting of this idea. It becomes a lab matter only if it says something about the model or the data in general. |
| The patient record contains outcome fields, so any prediction trained on it leaks | A `lesson` note → a claim, cited from `topics/`; the gap map; the system page's Data section | Every experiment that trains on records is affected. |
| Full fine-tuning of the base model does not fit the lab's GPU above batch 4 | A `lesson` note → the system page (environment notes) | Every experiment on this repo will hit it. A fact about the system, not a research finding. |
| A paper reports that GRPO collapses in reward after many steps | A `source` note → a source and a `quote` claim | Knowledge about the field, whoever found it. The claim says what the source reports, under the source's conditions. |
| A claim in the cortex does not match what this round saw | A `correction` note, with the evidence | The claim is settled in the lab, never edited from a try. |
| GRPO did not improve held-out reward in three reward designs | The lab step records, then the close: postmortem and Banlist | It decides whether anyone tries it again. One bad round does not say this yet. |
| The run crashed on a missing token | Log only | A technical failure says nothing about the idea. |

Two ways to get this wrong, and both cost the lab. Telling too little: the lesson stays in a branch nobody opens and the next experiment repeats it. Telling too much: the cortex fills with one try's details, and the few things that matter to everyone get buried. When unsure, write the lesson in the log now and mark it "candidate for the lab"; decide at the next round, when it is clearer whether it holds.

A note to the lab is written for a reader who has not seen the try: one sentence saying what was found, the anchor (commit and run, or link and quoted words, or the claim it corrects), and the conditions.

</What-to-tell-the-lab>

<Lab-step>

A **lab step** is done in the lab on **one chosen try** ([operations.md](references/operations.md) §5). It can be any live try, not only the newest or the best, and one try can have several. It is the only way anything from an experiment repo enters the lab.

1. **Read what is new**: `lab.py inbox --exp <id> --try <try name>` shows the try's signal and the notes to the lab added since its last lab step.
2. **Review the try**: its plan, its log, its code change against the experiment's base. Does the diff read as the idea? Did it run cleanly? Do the runs support what the log says?
3. **Evaluate, when one is possible**: `lab.py evaluate --exp <id> --try <try name>` ([evaluation.md](references/evaluation.md)). With no `evaluate.py` in the repo the lab step has no number, and says so.
4. **Write the conclusions into the lab**: a **lab step record** in the lab folder's `lab-steps.md` (the try, the commit, the evaluation's result, what this try shows about the idea and what it does not), and one change in the cortex per note:
   - `lesson`: an **interim conclusion**. A claim in `cortex/claims/`: one sentence, `status: provisional`, anchor `experiment::` with the experiment, the try, the round and the commit, and the conditions. Work it into the topic page it changes, citing it; write a tension if it disagrees with a claim the lab holds; update the gap it touches.
   - `source`: the source and its `quote` claims (`cortex add`).
   - `correction`: what `cortex/profile.md` §4 says for the case: a tension, or the older claim withdrawn or superseded.
   - `question`: try to answer it, from the cortex and then from outside (`cortex investigate`), and write the answer in the lab step record, under `Answers`. Only what stays open goes to the user, and to the gap map.
5. Run the cortex check (`cortex/profile.md` §6) and publish the lab to its default branch at once: what is not there does not exist for anyone else.

**Asking, from a try.** Any working copy reads the lab from its default branch (locally the lab's folder, after a pull; in a cloud session the lab is attached for reading). The cortex knows: use it, and cite the claim in the log. The cortex does not know and the outside world may: investigate, and write what was found as a `source` note, not into the cortex. Only the user knows, or it is a decision: write a `question` note, state the assumption the try continues under, and continue or stop as the brief says; the answer arrives in a lab step record (`lab-steps.md` in the experiment's lab folder).

A lab step adds the try's part to the cortex; it is not the cortex's main supply, which is `cortex add` at any time. The cortex is only useful while its claims can be trusted. A provisional claim is a promise to come back to it: when the experiment closes, each one becomes `confirmed` or `withdrawn`. Nothing is deleted, and the topic pages are rewritten freely to say what the lab now knows. A technical failure (OOM, missing credential, typo) is never a conclusion about the idea.

</Lab-step>

<Manage-many-tries>

When an experiment has more tries than one session can hold in view, a long-running lab session, the **managing session**, runs them ([operations.md](references/operations.md) §8). It holds the process and not the content:

- It reads the **map** (`lab.py tries`: each try's status, signal, last commit, comment and last lab step) and decides the next move: open tries and start a try session for each, ask for a lab step, ask for a reduce, answer a blocked try, close.
- It **never loads a try's log, plan or code** into its own context. Reduces and lab steps are handed to a clean context (a subagent, or another lab session) with a brief, and come back as a few lines. That report and the map are all the managing session knows of a try.
- Everything it decides is written in the map before the next move. If it ends, another one continues from the map.

A try session that died leaves a `live` try whose signal is still `working`: start a new try session on the same try branch. Only work that was never pushed is lost.

</Manage-many-tries>

<Close-the-experiment>

Closing is a decision made in the lab: the stopping point was reached, or the idea is exhausted. The experiment's conclusion is **the aggregation of its lab step records**: whether an effective approach was found and which direction to take next. A number is evidence for that when the repo has an evaluation; it is not the definition of it. Nothing in git forces or forbids a close, and live tries do not block it ([operations.md](references/operations.md) §6).

1. **Every live try first**: a lab step, when it holds something the conclusion should rest on; otherwise its comment in the map says why it needs none.
2. **Write `postmortem.md`** in the lab folder, from the lab step records: what each try showed, what they show together, the verdict, why things went the way they did, what happened to each provisional claim, and one or two Sparks.
   - `HYPOTHESIS_SUPPORTED`: the idea worked, by this lab's own measure, `cortex/purpose.md` §3.
   - `HYPOTHESIS_REFUTED`: the idea ran cleanly and did not work. Add it to the Anti-Repeat Banlist as `[pattern] -> [why it failed] -> [unless condition X changes] ([[claims/<claim>]])`.
   - `INFRA_INCONCLUSIVE`: a technical blocker prevented a real test. Nothing is written about the idea: no claim, no line in a topic page, no Banlist entry. Claims from rounds that ran cleanly are still settled on their own evidence.
3. **Settle the cortex.** `cortex.py claims --from <experiment name> --status provisional` lists what this experiment still owes: confirm or withdraw each, revise the topic pages that cited a withdrawn one, and drop "provisional" from the citations of confirmed ones. When the idea ran cleanly, write its final conclusion as a claim as well (`confirmed`, anchored to the try and commit it rests on): without it the experiment's main result is in no page. Update `gap_map.md` and `index.md`, and run the cortex check.
4. **Kept or not.** Decide which try branch later experiments should start from (it added or fixed a shared component, changed the Experiment Language, or holds the new best result), apart from the verdict, and write the reason in the postmortem. If kept, point the system page at it (`> Branch: <experiment name>/<try name>`, `Fingerprint: git:<sha>`).
5. **Record it**: `uv run scripts/lab.py record-verdict --exp <id> --verdict <VERDICT> --kept <try name|none> --metric-delta "<delta or 'no metric'>" --summary "<one-line lesson>"`. It completes the journal row, sets every try that is still `live` to `closed`, and publishes, together with whatever else was written in the lab's records and not published yet (the postmortem, the claims). A verdict is recorded once. By hand, and then `lab.py publish`: copy the Sparks into Active Sparks, and update Current Frontier if a lab step gave a new best number.

After closing, the lab folder does not change, except for a later evaluation added as a new lab step record. No branch is merged into the experiment repo's default branch.

</Close-the-experiment>

<References>

- The glossary is not here: it is §3 of the lab's `AGENTS.md` (on a try branch, §5 of the branch's `AGENTS.md`), every term with one meaning and the exact forms of names and paths. Read it before writing a plan, a log, a brief, a record or a report, and whenever a word could be read two ways.
- [system-guide.md](references/system-guide.md): the idea behind the lab, its parts, who does what where, how information moves, and what the hosting does not enforce. Read it when a case is not covered by a rule.
- [operations.md](references/operations.md): each operation as what it finds, its steps, and what it leaves; how the lab's records are published. Read it before opening a try, reducing, running a lab step, closing, or managing tries.
- [claude-code-cloud.md](references/claude-code-cloud.md): try sessions, lab sessions and managing sessions in Claude Code cloud: the settings, the opening message, reading the lab, what was checked.
- [evaluation.md](references/evaluation.md): the contract of `evaluate.py`, evaluation versions, re-evaluating after a change.
- [commands.md](references/commands.md): what each `lab.py` command does and does not do.

</References>

<Example>

A request: "try reinforcement-learning fine-tuning on the base model and see if it gets anywhere."

1. **Direction.** `context-pack`, then the gap map and the repo's Experiment Language. An RL objective needs a reward, and the reward needs the leak-free prediction task a Spark asks for. The cortex holds a `quote` claim: GRPO converged faster than PPO in a paper and collapsed in reward after many steps. Nobody in the lab has seen that, so it goes into the plan as something to watch for.
2. **Open.** `new-exp --repo model-repo --name grpo --base 01-pipeline/first` creates experiment `02-grpo` and its start branch `02-grpo/main`. The first plan is committed there: the idea, the open questions (reward definition, group size), what stays fixed (the held-out patients, the reward curve as the shared measurement), the stopping point ("enough: a reward curve that rises on held-out patients. Not worth more: three reward designs with no movement, or about 10 GPU hours").
3. **Tries.** `new-try` twice, with briefs: `reward-outcome` and `reward-shaped`, competing. Each has a line in `tries.md` (`live`) and a pushed try branch with its brief in the plan; a try session is started on each.
4. **`reward-outcome`.** Round 1: reward is flat, the parser rejects free text. That is about this try's code: `For the lab` says None. Round 2: reward rises on train and not on held-out patients, because the record still contains outcome fields. Every experiment that trains on records is affected, so the entry carries a `lesson` note with the commit, the run and the conditions. Signal `ready`.
5. **`reward-shaped`** crashes on memory twice, then runs and shows no movement. Signal `failed`; the log says the last result was a real one.
6. **Lab step on `reward-outcome`.** `inbox` shows the leak lesson. The repo has no `evaluate.py` yet, so the record says "evaluation: not run" and gives the conclusion. The lesson becomes a provisional claim anchored to `02-grpo`, try `reward-outcome`, round 2 and its commit, cited from the topic page on training data.
7. **Reduce.** `reward-shaped` is dropped into `reward-outcome`: no code enters, one log entry says what it tried and saw, and its line in the map says `dropped → reward-outcome`. The remaining try's plan is rewritten: render only fields known at prediction time. Its signal is `working`.
8. **More rounds** on `reward-outcome`, then a second lab step on it. The stopping point's budget is reached; the decision to go on for one more try, and why, is in the lab step record.
9. **Close.** The two lab step records are aggregated into the postmortem. `record-verdict --kept reward-outcome`: the experiment is kept for the leak-free rendering it added, the leak claim is confirmed, the system page names `02-grpo/reward-outcome`, and the lab is published.

Had `reward-outcome` shown that GRPO cannot work on this model at all, the experiment would have closed as `HYPOTHESIS_REFUTED`, with "try PPO" as a Spark. Had `reward-shaped` turned into a method of its own, it would have become a new experiment opened from its try branch.

</Example>
