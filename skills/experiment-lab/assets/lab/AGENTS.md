# {{FILL: lab name}} Research Lab (`AGENTS.md`)

This repository is a **research lab**: it holds the knowledge and the tools for running experiments in external experiment repos. Experiment code is never stored here. What is stored here is what is known about the field of the research, from any source (the cortex), and the path of the research: what was tried, what it concluded and what to try next (the journal and the experiments' records). Each experiment starts from all of it.

What the lab is for, and the far goal it is growing toward: `cortex/purpose.md`. Read it before any task that leaves you a choice of direction.

## 1. How Far to Go Comes With the Request

Requests of every size arrive here, in any order: "rename this function", "fix this line in the cortex", "think of a new direction and run it to a conclusion". The lab has no automation level and no stages.

- **Read the size from the request itself**, not from the previous request and not from how the lab usually works. If the request does not say how far to go and the readings lead to different work, ask with a concrete case.
- **Small request:** do that thing. Do not start an experiment, a cortex review, or a redesign that was not asked for. If you notice a problem outside the request, mention it and leave it.
- **Wide request:** carry it through. Do not come back for approval at each step. Use the stopping point in the experiment's `plan.md` to decide when to stop. At the end, report what you decided along the way, what you assumed, what you did not check, and where you are unsure.
- **When work is rejected, or the way the lab works has to change:** use the `grow-autonomy` skill. It fixes what agents understand, at the root, and keeps the record of rejects.

## 2. Structure

Two kinds of repository, and nothing else:

- **The lab** (this repository): the knowledge, the records and the tools. No experiment code.
- **Experiment repos** (outside, listed in `repos.yaml`): the code. Each stands for one big idea or method, and every experiment on it is a set of branches in it.

```text
the lab
├── AGENTS.md              this file: structure, glossary, what always holds
├── JOURNAL.md             the journal: the path of the research
├── cortex/                the knowledge base of the field
│   ├── purpose.md, profile.md, index.md, gap_map.md, log.md
│   ├── sources/  claims/  topics/  tensions/
│   └── systems/<repo>.md  one system page per experiment repo
├── experiments/<repo short name>/<experiment name>/     the lab folder of one experiment
│   ├── tries.md           the map of tries
│   ├── lab-steps.md       the lab step records
│   ├── steps/<try name>-<short commit>/                 the files of one lab step
│   ├── results.json
│   └── postmortem.md      written at close
├── experiments/_TEMPLATE/ the template of a lab folder
├── start-branch/          the experiment template: what a start branch is given (try AGENTS.md, first plan, empty log)
├── repos.yaml             the experiment repos
├── scripts/lab.py         the lab's command line
├── .agents/skills/        the loop skill, `cortex`, `grow-autonomy`, and the skills for where runs go
└── .repos/                clones and local worktrees (git-ignored)

an experiment repo
├── <default branch>                   nothing is merged into it, no work is done on it
├── <experiment name>/main             the start branch: a template, written once
└── <experiment name>/<try name>       a try branch, one per try
    ├── EXPERIMENT_LANGUAGE.md         the repo's shared code language
    ├── AGENTS.md, .agents/skills/     the lab kit
    ├── <the code>
    └── notes/<experiment name>/       plan.md, log.md, runs/
```

**How the work moves.** An experiment is opened in the lab: a lab folder, a row in the journal, a start branch in the experiment repo. Tries are opened from the lab, each on its own try branch and with its own line in the map of tries. A try is worked in rounds, on its branch only; what it has to tell the lab it writes in its log as notes to the lab. The lab comes to a try: a **reduce** turns several tries into one, and a **lab step** reviews one try, evaluates it when that is possible, and writes the conclusions into the lab. At some point the experiment is **closed** in the lab, with a postmortem and a verdict.

**How knowledge moves.** The cortex is filled from every source, at any time, and most of it comes from outside the lab (`cortex add`). From an experiment, the only way in is a lab step. Everyone reads the cortex and the journal before choosing a direction and while planning.

**Where things live:**


| Place | Holds | Rule |
|---|---|---|
| Experiment repo, start branch `<experiment name>/main` | The template of an experiment: the lab kit, `EXPERIMENT_LANGUAGE.md`, and `notes/<experiment name>/` with the first plan and an empty log | Written once, when the experiment is opened. Nothing enters it afterwards. |
| Experiment repo, try branch `<experiment name>/<try name>`: `notes/<experiment name>/` | The try's code and its notes: `plan.md` (the first plan, the brief under `This try`, rewritten as the try learns), `log.md` (one entry per round), `runs/` | Written by `new-try` (first commit), by whoever works that try, and by a reduce into it. Pushed after every round that matters. A branch that starts from another try or an earlier experiment carries its notes with it. |
| Lab: `experiments/<repo short name>/<experiment name>/` | The experiment as the lab sees it: `results.json` (who it is, its verdict, its kept try), `postmortem.md` at close, the map of tries `tries.md` (one line per try: branch, status, short comment), and `lab-steps.md` (one lab step record per lab step, with the answers to a try's questions), with each lab step's files in `steps/<try name>-<short commit>/` (`evaluate.log`, `patch.diff`, `metrics.json`) | Created by `new-exp`; lines of the map by `new-try`; written by reduces, lab steps and the close. After the experiment closes, nothing changes except a later evaluation added as a new lab step record. |
| Lab: `start-branch/` | The experiment template: the try `AGENTS.md`, and `notes/` with the first plan and an empty log | Copied to a start branch when an experiment is opened, and nowhere else: tries take it from the start branch. Changing it is a change to how the lab works. |
| `JOURNAL.md` | Current Frontier (baselines), Active Sparks, the matrix of all experiments (open and closed), the Anti-Repeat Banlist | The path of the research: what the lab did and decided, growing like a tree in the direction of the research. Not a knowledge base; that is the cortex. |
| `cortex/` | The lab's knowledge base of its field, in three layers: `sources/` (what was read from outside), `claims/` (one sentence each, anchored to an experiment round or to a quote), and the synthesis on top (`topics/`, `tensions/`, `gap_map.md`, `systems/`). Also `purpose.md`, `profile.md`, `index.md`, `log.md` | A topic page is rewritten freely and cites claims. A claim is corrected only as `cortex/profile.md` §4 says. Read `cortex/profile.md` before writing here. Never dump raw logs. |
| `.repos/` (git-ignored) | Clones of experiment repos (`clones/`) and local worktrees, one per try (`worktrees/<repo short name>/<experiment name>/<try name>/`) | Managed by `scripts/lab.py`. A cloud session needs neither: its own checkout is the working copy. |

The lab's **records** (the map of tries, the lab step records, the cortex, the journal) have one live copy, on the lab's default branch. Everyone reads them from there, and a record that is not pushed there does not exist for anyone else. Lab operations are done from a checkout of the default branch and published to it at once. Changes to how the lab works (skills, `lab.py`, this file, templates) are a different thing: they go on their own branch and are merged when the user says so.

## 3. Glossary (One Concept, One Name)

Every term of the lab, with one meaning each. This is the authority. Use the word exactly as written here, in plans, logs, briefs, records, reports, code and the cortex. A new word is read as a new thing, so do not use a synonym: say "experiment repo" and never "target repo", "try" and never "feature" or "sub-experiment", "start branch" and never "the experiment's main". When a term is missing or misleads, that is a change to the lab: fix it here, with `grow-autonomy`.

The running example: experiment repo `model-repo` (short name `model`), idea `probes`, id `02`.

### 3.1 Places

| Term | Meaning | Is not |
|---|---|---|
| **Lab** | The repository that holds the knowledge and the tools: the cortex, the journal, the lab folders with the map of tries, `scripts/lab.py`, the skills. It holds no experiment code. | A place where experiment code is written. |
| **Experiment repo** | A git repository outside the lab, registered in `repos.yaml`. It stands for one big idea or method and holds every experiment on it as branches. | The lab. A single experiment. |
| **Default branch** | The branch a repository gives to a plain clone. In an experiment repo nothing is merged into it and no work is done on it. In the lab it is the one live copy of the lab's records: the cortex, the journal and the map of tries are read from it by everyone. | A start branch, even though both may end in `main`. |
| **Working copy** | One checkout of one branch in which a person or an agent works: a local worktree under `.repos/worktrees/`, or the checkout of a cloud session. | A branch. Two working copies never share a branch at the same time. |
| **Session** | One person or one agent working in one working copy, from start to stop. A **try session** works one try and has only the experiment repo. A **lab session** works in the lab with the experiment repo at hand, and does the lab's operations. A **managing session** is a long-running lab session that runs many tries of one experiment. | A Colab runtime (always called a runtime). A conversation: what a session knows is lost when it ends, unless it is in git. |
| **Runtime** | A rented machine a heavy run goes to (for example a Colab runtime), reached through the experiment repo's runner. | A session. |
| **`lab.py`** (`scripts/lab.py`) | The lab's command line: opens experiments and tries, prints the map, mounts a try, runs and evaluates, closes. What each command does and does not do: the loop skill's `references/commands.md`. | The loop. It does the mechanical part of an operation; the judgment is in the skill. |
| **`repos.yaml`** | The list of experiment repos the lab works on, each with its `short_name`. | |
| **Reject journal** (`.grow-autonomy/rejects.md`) | The record of work the user rejected and what was changed at the root because of it. Kept with the `grow-autonomy` skill. | The journal. |

### 3.2 The work

| Term | Meaning | Is not |
|---|---|---|
| **Experiment** | One direction inside an experiment repo, pursued until there is a conclusion. It is saved: it has a lab folder, a row in the journal, a first plan, a map of its tries, lab step records, claims and a postmortem. An experiment with a single try is normal. "Try GRPO on the base model" is an experiment; one training run is a round inside one of its tries. | One run. One try. If the idea itself is replaced, the experiment closes and a new one opens. |
| **Idea** | The topic part of an experiment's name (`<id>-<idea>`). Which code an experiment starts from is its base, not its name. | A parent-child link. |
| **Try** | One attempt at realising an experiment, on its own try branch, recorded in the map of tries from the moment it is opened. Several tries of one experiment run at the same time, mostly competing, sometimes cooperating. What makes a try different from its siblings is written in its plan. | An experiment: it has no journal row and no verdict. A round. |
| **Round** | One pass of implement → run → analyze inside a try. A round can be long. One log entry per round. | A try (a try has many rounds). |
| **Reduce** | The operation that takes two or more tries and leaves one: the chosen code, and the conclusions synthesized by meaning, in one try (an existing one, or a new one opened for it). Every other try leaves the map, as `merged` (some of its code entered) or `dropped` (only its lessons entered). Dropping a weaker try and keeping its few lessons is the most common reduce, and it is how a try ends. | A plain `git merge`. A deletion of a branch: the branches stay in git as history. |
| **Lab step** | The operation done in the lab on one chosen try: review it, run the evaluation on it when one is possible, and write the conclusions into the lab (a lab step record, the cortex, the journal). It can be done on any try, at any time, and several times in one experiment. The only way anything from an experiment repo enters the cortex. | Part of working a try. Something reserved for one special branch or for the end. |
| **Close** | The decision, made in the lab, that an experiment has reached its conclusion. The experiment's conclusion is the aggregation of its lab step records. | Something git shows. An experiment can close while tries are still on the map; closing takes them off it. |
| **Base** | The branch and commit an experiment or a try starts from. An experiment can start from any try branch or start branch of its repo. A try starts from its experiment's start branch or from another try branch. | Something the name shows. The base of a pull request, which is always called "the pull request's base". |
| **Brief** | What whoever opens a try tells whoever works it: what to try and what makes it different, whether it competes or cooperates with which tries, how far to go, when to stop and flag. It is written in the try's plan, under `This Try`, when the try is opened; the map holds only a short comment. | Something said only in a prompt or a conversation. |
| **Kept** | An experiment is kept when one of its try branches becomes the base later experiments start from; the system page's `> Branch:` line names that try branch. Whoever closes the experiment decides it, apart from the verdict: keep it when later experiments should start from its code (it added or fixed a shared component, changed the Experiment Language, or holds the new best result), judged by `cortex/purpose.md` §3. The reason is written in the postmortem. | The verdict. A refuted experiment can be kept for a component it added. |

### 3.3 Branches and names

| Term | Form | Example |
|---|---|---|
| **Experiment name** | `<id>-<idea>` | `02-probes` |
| **Id** | Two lowercase hex digits, unique in the whole lab, given by `new-exp` | `02` |
| **Start branch** | `<experiment name>/main` | `02-probes/main` |
| **Try name** | One segment, lowercase words joined by hyphens, never `main`, never a `/` | `trl-fix-lr` |
| **Try branch** | `<experiment name>/<try name>` | `02-probes/trl-fix-lr` |
| **Notes** | `notes/<experiment name>/` on a branch | `notes/02-probes/plan.md` |
| **Lab folder** | `experiments/<repo short name>/<experiment name>/` in the lab | `experiments/model/02-probes/` |
| **Map of tries** | `<lab folder>/tries.md` | `experiments/model/02-probes/tries.md` |
| **Lab step records** | `<lab folder>/lab-steps.md` | `experiments/model/02-probes/lab-steps.md` |
| **Lab step files** | `<lab folder>/steps/<try name>-<short commit>/` | `…/steps/trl-fix-lr-3f9a2c1/evaluate.log` |
| **Local worktree** | `.repos/worktrees/<repo short name>/<experiment name>/<try name>/` in the lab's folder (git-ignored) | `.repos/worktrees/model/02-probes/trl-fix-lr/` |

Rules for names:

- `<idea>` is one segment: lowercase words joined by hyphens, never a `/`.
- Commands take the id alone (`--exp 02`) or the full name (`--exp 02-probes`).
- The experiment repo is not part of the name; it is the folder level `<repo short name>` in the lab (`short_name` in `repos.yaml`).
- No prefix such as `exp/`. Everything under `<experiment name>/` in the experiment repo is that experiment: its start branch and its try branches.
- A try that is the result of a reduce is named like any try. When it takes tries that share a prefix, that prefix is a natural name (`trl` for `trl-fix-lr` and `trl-d-lr`).

**Start branch.** A template: the lab kit, the first plan and an empty log, on top of the experiment's base. `new-exp` writes it, and nothing enters it afterwards. Tries start from it. It is never worked on, never evaluated, and never the place where an experiment's result is.

**Map of tries.** One file per experiment, `tries.md` in its lab folder, with one line per try: the try branch, the status, and a comment of at most 100 characters (while live: what it tries; afterwards: how it ended). Nothing else is kept per try in the lab: the brief and the base are in the try's plan, and what lab steps concluded is in `lab-steps.md`. It says which tries exist and where each stands, and it is the only definition of a try being live or done: git ancestry and the existence of a branch decide nothing. `lab.py tries` prints it.

**Status** (of a try, in its line of the map). Owned by the lab:

| Status | Meaning |
|---|---|
| `live` | The try is in play: being worked, waiting for a lab step or a reduce, or waiting for an answer. |
| `merged` | A reduce took code from it into the try the line names (`merged → <try>`). |
| `dropped` | A reduce took only its lessons into the try the line names (`dropped → <try>`); or, with no try named, a lab step recorded its conclusion and it was ended. |
| `closed` | Its experiment closed while it was live. |

A try that is not `live` is never worked, reduced or read again. Its branch stays in git as history and may be deleted by a person; nothing depends on it.

### 3.4 Notes and records

| Term | Meaning | Is not |
|---|---|---|
| **Notes** | A plan, a log and a `runs/` folder, in `notes/<experiment name>/`, kept next to the code and committed with it. On the start branch they are the first plan and an empty log. On a try branch they are that try's notes. A branch started from another try carries that try's notes and continues them. | The lab folder. The folder is called `notes` so that `experiments/` means one thing only: the lab's folder. |
| **Plan** (`plan.md`) | The current best description of how to realise the idea, rewritten in place. The first plan is written when the experiment is opened. On a try branch the plan also says, under `This try`, what makes this try different; `new-try` writes the brief there. | A signed contract. A history: the plan says where we are, the log says how we got there. |
| **Log** (`log.md`) | Append-only: one entry per round, and one entry per try taken in by a reduce. Every entry's heading carries the try name. "The log" is this file; `cortex/log.md` is always called by its path. | The plan. |
| **Signal** | The line of a try log's last entry by which the try tells the lab where its work stands: `working`, `ready` (for a lab step or a reduce), `failed` (nothing worth keeping; say whether technical or a real result), `blocked` (a question must be answered first). `lab.py tries` reads it from the branch and shows it next to the status. | The status, which the lab owns. A message in a conversation. |
| **Note to the lab** | One item under the heading `For the lab` in a log entry, written for a lab step. Four kinds: `lesson` (seen in a round; anchor: commit and run), `source` (found outside; anchor: link and the quoted words), `correction` (a claim the cortex holds looks wrong; anchor: the claim and the evidence), `question` (something neither the cortex nor the round could answer). Form: one sentence, the anchor, the conditions. | A claim. It becomes one, or changes one, only in a lab step. |
| **Line of the map** | The lab's whole record of one try: its try branch, its status, and a comment of at most 100 characters. Written only in the lab. | A file per try. The try's notes, which live on its branch. |
| **Lab step record** | An entry in the experiment's `lab-steps.md`, one per lab step, headed by the try name: the commit that was reviewed, the evaluation's result or why none was run, the conclusions, the answers to the try's questions, and what was written to the cortex and the journal. | A claim. A log entry. |
| **Experiment template** (`start-branch/`) | The lab's folder that holds what a start branch is given when an experiment is opened: the try `AGENTS.md`, and `notes/` with the first plan and an empty log. Copied once per experiment, to its start branch; tries take it from there. A change to it reaches experiments opened afterwards. | The template of the lab folder (`experiments/_TEMPLATE/`). The start branch itself. |
| **Lab kit** | The files the lab commits on a start branch, once, when the experiment is opened; every try branch starts from the start branch and carries them, so that a working copy is a whole system with nothing else attached: `AGENTS.md` (how a try is worked, what it may write, and the glossary of the terms a try meets; written from `start-branch/AGENTS.md` in the lab; its first line names the lab commit it came from) and the lab's skills (`.agents/skills/`, linked from `.claude/skills/`). Owned by the lab, never edited in a try, not part of a try's code change. | The Experiment Language page, which belongs to the experiment repo's code. |

### 3.5 Knowledge

| Term | Meaning | Is not |
|---|---|---|
| **Cortex** (`cortex/`) | The lab's knowledge base of its field: the widest collection the lab can build of what is known that may advance the research. Most of it comes from outside; the lab's experiments are one kind of source among the others, with no higher rank. Three layers: *sources* (what was read from outside, and the experiments), *claims*, and *synthesis* (topic pages, tensions, the gap map, system pages). Added to at any time (`cortex add`), with no gap or experiment needed to ask for it. Read by everyone, from the lab's default branch. Written only in the lab. | A record of the experiments. The journal. A copy: no branch of an experiment repo carries one. |
| **Journal** (`JOURNAL.md`) | The path of the research: Current Frontier, Active Sparks, the matrix of experiments, the Anti-Repeat Banlist. It grows like a tree, each experiment starting from earlier work, in the direction of the research, and holds only what the lab did and decided. | A knowledge base. What is known about the field is in the cortex. |
| **Claim** | One sentence that can be true or false, in its own file in `cortex/claims/`, with an anchor and conditions. Anchors: `experiment` (the lab saw it: experiment, try, round, commit), `quote` (an outside source reports it), `stated` (the user said it). The anchor says where a claim comes from, not how much it matters. Corrected only as `cortex/profile.md` §4 says. | A note to the lab. A topic page. |
| **Topic page** | A page in `cortex/topics/` about one topic of the field, saying what is known by citing claims of every anchor. Rewritten freely. Most of what it cites comes from outside the lab. | A claim; a page about one source; a record of the lab's experiments (that is the journal). |
| **Conclusion** | Something a *different* experiment should know. *Interim*: the experiment goes on; it leaves a try as a `lesson` note and becomes a provisional claim in a lab step. *Final*: no point trying further; the experiment closes. | Everything a round taught. Most of that stays in the log. |
| **Source** | Anything the cortex takes knowledge from: a paper, an article, documentation, a dataset description, code, a talk, a note from the user; and the lab's own experiments. An outside source has a note in `cortex/sources/` and its stored text. | A claim. A reason to rank a claim higher or lower. |
| **Anchor** | The part of a claim that says where it comes from and how it can be checked: `quote`, `experiment` or `stated`. | A rank. |
| **Tension** | A page in `cortex/tensions/`: two claims that disagree, and what would settle it. Both claims stay. | A correction of either claim. |
| **Gap** | A row in `cortex/gap_map.md`: something the cortex should know and does not, about anything in the field. Adding knowledge needs no gap. | A Spark: a gap is a question, a Spark is an idea for an experiment. |
| **Index** (`cortex/index.md`) | The map of the field: its areas, with the topic pages under each. An empty area shows where the cortex is thin. | A list of experiments. |
| **Profile** (`cortex/profile.md`) | What this lab's cortex is for, its layout, its anchors and statuses, how it grows and how it is checked. Read before writing anything under `cortex/`. | The `cortex` skill, which holds the operations for any cortex. |
| **Experiment Language** | The shared code language of one experiment repo: its concepts and names, its shared components (the code every experiment uses and none reimplements), its extension points (where an idea goes in). An experiment is a small change on top of it. Written in `EXPERIMENT_LANGUAGE.md` at the root of the experiment repo, on every branch, and changed like code. | The lab kit. A per-experiment document. |
| **System page** | `cortex/systems/<repo>.md` in the lab: what the experiment repo is for, the kept try branch (`> Branch:`), data and environment notes, and a pointer to `EXPERIMENT_LANGUAGE.md` on that branch. | A second copy of the Experiment Language. A topic page: it is about the lab's repo, not about the field. |
| **Evaluation** | One run of the experiment repo's `evaluate.py` on one commit of one try, inside a lab step. Recorded in the lab step record with its **evaluation version**; two numbers are compared only when their versions are equal. A lab step with no evaluation is normal while the repo has none. The outcome of an experiment is whether an effective approach was found; the number is evidence for that, not its definition. | A measurement inside a round, which a try makes however is useful. |
| **Baseline** | The best verified number per experiment repo and task (`JOURNAL.md` → Current Frontier), with the experiment and try it came from. A repo may have none yet. | |
| **Verdict** | `HYPOTHESIS_SUPPORTED`, `HYPOTHESIS_REFUTED` or `INFRA_INCONCLUSIVE`, set for the experiment at close. | Kept or not kept. The result in one lab step record. |
| **Spark** | An idea worth an experiment that has not been opened yet, written down while the context is fresh (`JOURNAL.md` → Active Sparks). | An open experiment. |
| **Purpose** (`cortex/purpose.md`) | What the lab is for, the far goal, and how results are judged. | |
| **Frontier** | `JOURNAL.md` → Current Frontier: the baselines, per experiment repo and task. Rests on `experiment` claims. | What the literature reports as best. |
| **Matrix** | `JOURNAL.md` → the table of all experiments, open and closed, one row each, with the verdict of the closed ones. | The map of tries: tries have no row here. |
| **Banlist** | `JOURNAL.md` → Anti-Repeat Banlist: directions the lab ran cleanly and should not repeat, each with the `experiment` claim it rests on and an "unless" condition. | A place for something only a source reports, or for a technical failure. |
| **Postmortem** (`postmortem.md`) | Written in the lab folder at close: the experiment's final conclusion, the verdict, whether it is kept and why, what changed in the cortex. | A lab step record. |
| **Technical failure** | A crash, out-of-memory, missing credential or typo. It produces no claim, no line in a topic page and no Banlist entry. | A result about the idea. |

## 4. Running an Experiment, and Working on the Cortex

Load the `experiment-lab-loop` skill. It is the only place the loop is described: find a direction, open the experiment, open tries and work them in rounds, reduce several tries into one, run a lab step on a chosen try, manage many tries from one long-running session, close. Its references hold the system guide, each operation step by step, and how to work from Claude Code cloud sessions. Do not load it for requests that are not about an experiment.

The cortex has its own operations, and they are the `cortex` skill: adding a source (at any time: whatever is known about the field and may advance the research belongs there), investigating a gap from outside sources, answering from what the lab knows, the periodic review. This lab's layout and rules for them are in `cortex/profile.md`. Two things need the profile and not the skill: writing a claim in a lab step (the loop skill says when; the form is `cortex/claims/_TEMPLATE.md`), and a small edit to a page. After either, run the check in `cortex/profile.md` §6.

## 5. What Always Holds

Each of these holds for every request, whatever its size.

1. **Experiments on one experiment repo share one code language and one set of components: its Experiment Language** (`EXPERIMENT_LANGUAGE.md` on the branch). Read it before writing any experiment code.
   - An idea goes in at an extension point named there. A variant is a config value or a flag, not a copied script.
   - Use the shared components (data loading, run entry and config, runner, observation and analysis tools, evaluation) as they are. Do not reimplement or fork one inside an experiment. If one is wrong or too narrow, fix it as a shared component and say so in `plan.md`: every later experiment inherits it.
   - Something new that other experiments will need is written as a shared component and added to `EXPERIMENT_LANGUAGE.md` in the same change.
   - Change the language itself only when that change is the idea. If an idea does not fit the language, stop and decide which it is; do not code around it.
   - The test: the experiment's diff against its base reads as the idea and nothing else.

   *Why:* this is what makes the lab's experiments add up. A difference between two results can be attributed to the idea, someone who understood experiment `0a` opens `0b` and sees only what changed, and the tools and findings of one experiment work for the next.
2. **A try exists when the lab records it, and it has its own branch and its own working copy.** A try is opened only through the lab (`lab.py new-try`), which writes its line in the map of tries and pushes its try branch; whoever works it starts on that branch and pushes to the same branch. A try session writes only its own try branch, and never the lab. A try is live or done by what the map of tries says, never by what git shows. The start branch is a template and is not touched after the experiment is opened. Never edit `.repos/clones/<repo>` (the base clone). *Why:* tries stay independent, so their results can be told apart, and anyone can see from the lab what is in play without reading a branch.
3. **Nothing is merged into an experiment repo's default branch or into a start branch, and a pull request is opened only when the user asks.** Tries come together only through a reduce, in the lab; experiments are never merged into each other. An experiment that builds on earlier work starts from it (`new-exp --base <branch>`: any try branch). A pull request names its base explicitly. The hosting enforces none of this. *Why:* every result must survive a fresh clone, and no experiment may silently change the ground under another.
4. **A technical failure is not a scientific result.** A crash, out-of-memory, missing credential or typo is `INFRA_INCONCLUSIVE`, or simply a round that failed. Never write a claim, a line in a topic page or an Anti-Repeat Banlist entry saying that an idea failed before it actually ran cleanly. *Why:* a false refutation stops every later agent from trying a good idea.
5. **Everything runs from a fresh clone, anywhere** (a laptop, a cloud session, CI, a cluster). Whatever an agent needs is in this repo: instructions, skills, tools. A session elsewhere sees only what is pushed, in both repositories: push the try branch after every round that matters, and publish the lab's records whenever they changed (an experiment or a try opened, a reduce, a lab step, a close). `mount` in a fresh clone finds a try through its line in the map here and its pushed branch. The state of the work is read from the lab's records and from the branches, never from a conversation: any operation may be done by a person or by an agent, and the next one by someone else. Never write absolute or machine-specific paths into docs, code, configs, plans or the cortex. Use repo-relative paths, or the variables `lab.py run` and `lab.py evaluate` provide: `$LAB_ROOT`, `$EXP_DIR`, and the `.env` variables. Data is declared in `plan.md` as `data_source: <repo>@<ref>:<path>`.
6. **Secrets come only from environment variables named in `.env.example`.** Never write a value into git, logs, results or the cortex.
7. **Python is `uv`, and only `uv`.** `uv run`, `uv add`, `uv sync`, in the lab and in every experiment repo. Never `pip install`, a bare `python`, or a hand-made virtual environment. *Why:* a fresh clone on any machine reaches the same environment with one command, and a dependency added in one round is there in the next session.
8. **Never edit a skill for one experiment.** The lab commits its skills on the start branch and on every try branch as part of the lab kit; a change to a skill is a change to the lab, and a try never edits the lab kit.
9. **Evaluation:** {{FILL: how this lab measures a try in a lab step, and why that way. The scaffold's default: the script `evaluate.py` at the experiment repo's root, run on a try by `uv run scripts/lab.py evaluate`, which records the script's version with every result so that numbers from different versions are not compared by mistake. Details in the `experiment-lab-loop` skill.}}
10. **Where heavy runs go:** {{FILL: the machines or services GPU and long runs may use, and the skill for each.}}
11. **Data:** {{FILL: where the data comes from (repo and path), which data may leave the machine and what may appear in logs, or "in each experiment repo's system page".}}

## 6. Attention

No agent can hold the whole lab in view. Keep your own context for judgment: choosing a direction, reading evidence, deciding what a round taught. Hand heavy-reading work with a small result to subagents: a long implementation or debugging session, an investigation of a gap from outside sources, a cortex review.

A subagent sees none of this conversation. Its brief must carry what the piece is for, what good looks like, the reasons it could not guess (the relevant part of `plan.md`, the data rules), the repo's Experiment Language (a subagent that has not seen it will write its own loader and its own loop), what to hand back, and when to stop and flag instead of finishing. Review what comes back; do not redo it.

## 7. What You Learned Goes Somewhere

A conversation is not memory. Before you finish any piece of work, place each thing you learned at the level it is true for, and tell the user what you wrote where:

- **True for this try:** its log and plan, on the try branch.
- **True for this experiment:** the lab step record of the try that showed it, in the lab folder's `lab-steps.md`; at a reduce, the log of the try that remains.
- **True for the field** (something you read or found outside, at any moment): the cortex, with `cortex add`; from a try, a `source` note to the lab.
- **True for the research** (a different experiment should know it): from a try, a note to the lab in the log; in a lab step, the claim it becomes and the page or gap it changes.
- **True for how this lab works** (a term that misled, a template with no place for something, a step that came out wrong): the lab's own files, at the root, with `grow-autonomy`. On a small request, say it and leave the change to the user.
- **True for anyone who uses a skill that came from outside** (`cortex`, `grow-autonomy`, the skills for where runs go): do not edit the copy in `.agents/skills/`. Propose the change to the user, with what happened here that showed it, so it is made at the skill's source. What is true only here goes in `cortex/profile.md` or in this file.
- **True for any lab:** the same, for the scaffold this lab was made from (`experiment-lab`).
