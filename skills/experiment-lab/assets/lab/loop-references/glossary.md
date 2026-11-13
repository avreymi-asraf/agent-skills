# Glossary

Every term of the lab, with one meaning each. Use the word exactly as written here, in plans, logs, briefs, records, reports, code and the cortex. A new word is read as a new thing, so do not use a synonym: say "experiment repo" and never "target repo", "try" and never "feature" or "sub-experiment", "start branch" and never "the experiment's main".

The running example: experiment repo `model-repo` (short name `model`), idea `probes`, id `02`.

## 1. Places

| Term | Meaning | Is not |
|---|---|---|
| **Lab** | The repository that holds the knowledge and the tools: the cortex, the journal, the lab folders with the map of tries, `scripts/lab.py`, the skills. It holds no experiment code. | A place where experiment code is written. |
| **Experiment repo** | A git repository outside the lab, registered in `repos.yaml`. It stands for one big idea or method and holds every experiment on it as branches. | The lab. A single experiment. |
| **Default branch** | The branch a repository gives to a plain clone. In an experiment repo nothing is merged into it and no work is done on it. In the lab it is the one live copy of the lab's records: the cortex, the journal and the map of tries are read from it by everyone. | A start branch, even though both may end in `main`. |
| **Working copy** | One checkout of one branch in which a person or an agent works: a local worktree under `.repos/worktrees/`, or the checkout of a cloud session. | A branch. Two working copies never share a branch at the same time. |
| **Session** | One person or one agent working in one working copy, from start to stop. A **try session** works one try and has only the experiment repo. A **lab session** works in the lab with the experiment repo at hand, and does the lab's operations. A **managing session** is a long-running lab session that runs many tries of one experiment. | A Colab runtime (always called a runtime). A conversation: what a session knows is lost when it ends, unless it is in git. |

## 2. The work

| Term | Meaning | Is not |
|---|---|---|
| **Experiment** | One direction inside an experiment repo, pursued until there is a conclusion. It is saved: it has a lab folder, a row in the journal, a first plan, a map of its tries, lab step records, claims and a postmortem. An experiment with a single try is normal. | One run. One try. If the idea itself is replaced, the experiment closes and a new one opens. |
| **Idea** | The topic part of an experiment's name (`<id>-<idea>`). Which code an experiment starts from is its base, not its name. | A parent-child link. |
| **Try** | One attempt at realising an experiment, on its own try branch, recorded in the map of tries from the moment it is opened. Several tries of one experiment run at the same time, mostly competing, sometimes cooperating. What makes a try different from its siblings is written in its plan. | An experiment: it has no journal row and no verdict. A round. |
| **Round** | One pass of implement → run → analyze inside a try. A round can be long. One log entry per round. | A try (a try has many rounds). |
| **Reduce** | The operation that takes two or more tries and leaves one: the chosen code, and the conclusions synthesized by meaning, in one try (an existing one, or a new one opened for it). Every other try leaves the map, as `merged` (some of its code entered) or `dropped` (only its lessons entered). Dropping a weaker try and keeping its few lessons is the most common reduce, and it is how a try ends. | A plain `git merge`. A deletion of a branch: the branches stay in git as history. |
| **Lab step** | The operation done in the lab on one chosen try: review it, run the evaluation on it when one is possible, and write the conclusions into the lab (a lab step record, the cortex, the journal). It can be done on any try, at any time, and several times in one experiment. The only way anything from an experiment repo enters the cortex. | Part of working a try. Something reserved for one special branch or for the end. |
| **Close** | The decision, made in the lab, that an experiment has reached its conclusion. The experiment's conclusion is the aggregation of its lab step records. | Something git shows. An experiment can close while tries are still on the map; closing takes them off it. |
| **Base** | The branch and commit an experiment or a try starts from. An experiment can start from any try branch or start branch of its repo. A try starts from its experiment's start branch or from another try branch. | Something the name shows. The base of a pull request, which is always called "the pull request's base". |
| **Brief** | What whoever opens a try tells whoever works it: what to try and what makes it different, whether it competes or cooperates with which tries, how far to go, when to stop and flag. It is written in the try's plan, under `This Try`, when the try is opened; the map holds only a short comment. | Something said only in a prompt or a conversation. |
| **Kept** | An experiment is kept when one of its try branches becomes the base later experiments start from; the system page's `> Branch:` line names that try branch. Decided at close, apart from the verdict. | The verdict. A refuted experiment can be kept for a component it added. |

## 3. Branches and names

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

## 4. Notes and records

| Term | Meaning | Is not |
|---|---|---|
| **Notes** | A plan, a log and a `runs/` folder, in `notes/<experiment name>/`, kept next to the code and committed with it. On the start branch they are the first plan and an empty log. On a try branch they are that try's notes. A branch started from another try carries that try's notes and continues them. | The lab folder. `experiments/` exists only in the lab. |
| **Plan** (`plan.md`) | The current best description of how to realise the idea, rewritten in place. The first plan is written when the experiment is opened. On a try branch the plan also says, under `This try`, what makes this try different; `new-try` writes the brief there. | A contract. A history. |
| **Log** (`log.md`) | Append-only: one entry per round, and one entry per try taken in by a reduce. Every entry's heading carries the try name. "The log" is this file; `cortex/log.md` is always called by its path. | The plan. |
| **Signal** | The line of a try log's last entry by which the try tells the lab where its work stands: `working`, `ready` (for a lab step or a reduce), `failed` (nothing worth keeping; say whether technical or a real result), `blocked` (a question must be answered first). `lab.py tries` reads it from the branch and shows it next to the status. | The status, which the lab owns. A message in a conversation. |
| **Note to the lab** | One item under the heading `For the lab` in a log entry, written for a lab step. Four kinds: `lesson` (seen in a round; anchor: commit and run), `source` (found outside; anchor: link and the quoted words), `correction` (a claim the cortex holds looks wrong; anchor: the claim and the evidence), `question` (something neither the cortex nor the round could answer). Form: one sentence, the anchor, the conditions. | A claim. It becomes one, or changes one, only in a lab step. |
| **Line of the map** | The lab's whole record of one try: its try branch, its status, and a comment of at most 100 characters. Written only in the lab. | A file per try. The try's notes, which live on its branch. |
| **Lab step record** | An entry in the experiment's `lab-steps.md`, one per lab step, headed by the try name: the commit that was reviewed, the evaluation's result or why none was run, the conclusions, the answers to the try's questions, and what was written to the cortex and the journal. | A claim. A log entry. |
| **Lab kit** | The files the lab commits on a start branch and refreshes at the opening of every try, so that a working copy is a whole system with nothing else attached: `AGENTS.md` (the rules for working a try; its first line names the lab commit it came from) and the lab's skills (`.agents/skills/`, linked from `.claude/skills/`). Owned by the lab, never edited in a try, not part of a try's code change. | The Experiment Language page, which belongs to the experiment repo's code. |

## 5. Knowledge

| Term | Meaning | Is not |
|---|---|---|
| **Cortex** (`cortex/`) | The lab's knowledge base of its field: the widest collection the lab can build of what is known that may advance the research. Most of it comes from outside; the lab's experiments are one kind of source among the others, with no higher rank. Three layers: *sources* (what was read from outside, and the experiments), *claims*, and *synthesis* (findings pages, tensions, the gap map, system pages). Added to at any time (`cortex add`), with no gap or experiment needed to ask for it. Read by everyone, from the lab's default branch. Written only in the lab. | A record of the experiments. The journal. A copy: no branch of an experiment repo carries one. |
| **Journal** (`JOURNAL.md`) | The path of the research: Current Frontier, Active Sparks, the matrix of experiments, the Anti-Repeat Banlist. It grows like a tree, each experiment starting from earlier work, in the direction of the research, and holds only what the lab did and decided. | A knowledge base. What is known about the field is in the cortex. |
| **Claim** | One sentence that can be true or false, in its own file in `cortex/claims/`, with an anchor and conditions. Anchors: `experiment` (the lab saw it: experiment, try, round, commit), `quote` (an outside source reports it), `stated` (the user said it). The anchor says where a claim comes from, not how much it matters. Corrected only as `cortex/profile.md` §4 says. | A note to the lab. A findings page. |
| **Findings page** | A page in `cortex/findings/` about one topic of the field, saying what is known by citing claims of every anchor. Rewritten freely. "Finding" always means the page; one result is a claim. | A claim. |
| **Conclusion** | Something a *different* experiment should know. *Interim*: the experiment goes on; it leaves a try as a `lesson` note and becomes a provisional claim in a lab step. *Final*: no point trying further; the experiment closes. | Everything a round taught. Most of that stays in the log. |
| **Experiment Language** | The shared code language of one experiment repo: its concepts and names, its shared components, its extension points. Written in `EXPERIMENT_LANGUAGE.md` at the root of the experiment repo, on every branch, and changed like code. | The lab kit. A per-experiment document. |
| **System page** | `cortex/systems/<repo>.md` in the lab: what the experiment repo is for, the kept try branch (`> Branch:`), data and environment notes, and a pointer to `EXPERIMENT_LANGUAGE.md` on that branch. | A second copy of the Experiment Language. |
| **Evaluation** | One run of the experiment repo's `evaluate.py` on one commit of one try, inside a lab step. Recorded in the lab step record with its **evaluation version**; two numbers are compared only when their versions are equal. A lab step with no evaluation is normal while the repo has none. | A measurement inside a round, which a try makes however is useful. |
| **Baseline** | The best verified number per experiment repo and task (`JOURNAL.md` → Current Frontier), with the experiment and try it came from. A repo may have none yet. | |
| **Verdict** | `HYPOTHESIS_SUPPORTED`, `HYPOTHESIS_REFUTED` or `INFRA_INCONCLUSIVE`, set for the experiment at close. | Kept or not kept. The result in one lab step record. |
| **Spark** | An idea worth an experiment that has not been opened yet (`JOURNAL.md` → Active Sparks). | An open experiment. |
