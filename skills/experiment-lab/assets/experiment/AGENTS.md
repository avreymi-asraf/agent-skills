<!-- Lab kit of `<experiment name>`, written by the lab at commit `<lab-sha>`. Owned by the lab: a try never edits this file or `.agents/skills/`. -->
# Working a Try of `<experiment name>` (`AGENTS.md`)

You are in an **experiment repo**, on a branch of the experiment `<experiment name>`. This file tells whoever works here what the branch is, what may be written on it, and what every term means. It was written once, on the start branch, when the experiment was opened; every try branch starts from the start branch and carries it.

The experiment belongs to a **research lab**, a separate repository that holds the knowledge (the cortex), the path of the research (the journal) and the record of this experiment (its map of tries and its lab step records). You do not need the lab to work a try. You may read it; you never write it.

## 1. Which Branch You Are On

| Branch | What it is | What to do on it |
|---|---|---|
| `<experiment name>/main` | The **start branch**: a template. This file, the lab's skills, the first plan, an empty log. | Nothing. It is written once and never worked on. If you are here and were asked to work, stop and say so: a try is opened by the lab, on its own branch. |
| `<experiment name>/<try name>` | A **try branch**: one attempt at the experiment. | Work it, in rounds. Push to this branch only. |

A try exists because the lab opened it: its line is in the lab's map of tries and its branch was pushed. Do not create a try branch yourself.

## 2. Structure

```text
this branch
├── AGENTS.md                      this file          ┐ the lab kit: owned by the lab,
├── .agents/skills/                the lab's skills   ┘ never edited in a try
├── EXPERIMENT_LANGUAGE.md         the repo's shared code language; read it before writing code
├── <the code>
└── notes/<experiment name>/
    ├── plan.md                    how the idea is realised now; the brief of this try under `This Try`
    ├── log.md                     append-only: one entry per round
    └── runs/<nn>-<short-name>/    the files of each run
```

What reaches the lab from here is only what is written in `log.md` under `For the lab`, and only when the lab comes for it in a **lab step**. The lab also reads the **signal** of the last log entry to know where the try stands.

## 3. How a Try Is Worked

Start by reading `EXPERIMENT_LANGUAGE.md` and `notes/<experiment name>/plan.md`: the plan, and under `This Try` the **brief** (what to try, what makes this try different from the others, how far to go, when to stop and flag). Then work in **rounds**; the `experiment-lab-loop` skill → Work-in-rounds and What-to-tell-the-lab describe them in full.

Each round:

1. **Implement** the next step of the plan, in the Experiment Language.
2. **Run** it. Write the run plan in the log first: the question the run answers, what to watch, what would stop it early.
3. **Analyze** what came back: the numbers, and the cases behind them.
4. **Write it down:** one entry in `log.md` (tried, saw, decided, notes to the lab, signal), and rewrite `plan.md` in place if the round taught something.
5. **Commit and push** the try branch. What is not pushed does not exist for anyone else.

How far to go comes with the brief. A small request inside a try ("fix this function") stays small.

## 4. What You May Write

- **Yes:** the code, in the Experiment Language; `notes/<experiment name>/` on this branch.
- **No:** another branch; the start branch; the default branch; this file and `.agents/skills/`; anything in the lab. No pull request unless the user asks; nothing is merged into the default branch or the start branch.
- **Something is wrong outside what you may write** (a skill misleads, a term is missing, a shared component of another try needs a fix): write it as a note to the lab, or say it in your report. Do not fix it here.

## 5. Glossary (One Concept, One Name)

The terms a try meets. Use each word exactly as written; a synonym is read as a different thing. The whole glossary, which is the authority, is §3 of the lab's `AGENTS.md`.

| Term | Meaning | Is not |
|---|---|---|
| **Lab** | The repository that holds the cortex, the journal, the records of every experiment and the tools. It holds no experiment code. | A place a try writes to. |
| **Experiment repo** | This repository. It stands for one big idea or method and holds every experiment on it as branches. | The lab. A single experiment. |
| **Experiment** | One direction inside an experiment repo, pursued through tries until there is a conclusion. Its name is `<id>-<idea>`. | One try. One run. |
| **Start branch** | `<experiment name>/main`: the template tries start from. Nothing enters it after the experiment is opened. | The place where the experiment's result is. The default branch. |
| **Try** | One attempt at realising the experiment, on its own try branch, recorded in the lab's map of tries. Several run side by side, mostly competing. | An experiment: it has no verdict. A round. |
| **Try branch** | `<experiment name>/<try name>`. | |
| **Map of tries** | The lab's file `tries.md` for this experiment: one line per try (branch, status, short comment). It alone says whether a try is live or done. | Something git shows. Something a try writes. |
| **Brief** | What the opener of a try tells whoever works it. Written in the plan under `This Try`. | Something said only in a prompt. |
| **Base** | The branch and commit a try or an experiment starts from. | Something the name shows. |
| **Round** | One pass of implement → run → analyze. One log entry per round. | A try. |
| **Notes** | `notes/<experiment name>/`: the plan, the log and `runs/`, committed with the code they describe. | The lab's folder for the experiment. |
| **Plan** (`plan.md`) | The current best description of how to realise the idea, rewritten in place. | A contract. A history. |
| **Log** (`log.md`) | Append-only: one entry per round, and one per try taken in by a reduce. | The plan. |
| **Signal** | The last line of the last log entry: `working`, `ready` (for a lab step or a reduce), `failed` (nothing worth keeping; say whether technical or a real result), `blocked` (a question must be answered first). | The status in the map, which the lab owns. |
| **Note to the lab** | One item under `For the lab` in a log entry: `lesson` (seen in a round), `source` (found outside), `correction` (a claim of the cortex looks wrong), `question`. One sentence, its anchor, its conditions. | A claim. It becomes one only in a lab step. |
| **Lab step** | What the lab does on one chosen try: review it, evaluate it when that is possible, write the conclusions into the lab. | Part of working a try. |
| **Reduce** | The lab's operation that turns two or more tries into one: the chosen code and the conclusions, in one try. The others leave the map as `merged` or `dropped`. It is how a try ends. | A plain `git merge`. |
| **Cortex** | The lab's knowledge base of its field, from every source; most of it from outside the lab. Read it when the try needs to know something. | A record of experiments. Something a try writes. |
| **Journal** | The lab's `JOURNAL.md`: the path of the research. | A knowledge base. |
| **Experiment Language** | The shared code language of this repo: its concepts, its shared components, its extension points. `EXPERIMENT_LANGUAGE.md` at the root, changed like code. | The lab kit. |
| **Lab kit** | This file and `.agents/skills/`: what the lab committed on the start branch so that a checkout is a whole system. | Part of a try's code change. |
| **Evaluation** | One run of the repo's `evaluate.py` on one commit of a try, done by the lab in a lab step. | A measurement inside a round, which a try makes however is useful. |
| **Technical failure** | A crash, out-of-memory, missing credential or typo. | A result about the idea. |
| **Session** | One person or agent working in one working copy. A **try session** works one try and has only this repo. | A runtime. A conversation. |

## 6. What Always Holds

1. **The Experiment Language.** An idea goes in at an extension point named in `EXPERIMENT_LANGUAGE.md`; a variant is a config value or a flag, not a copied script. Use the shared components as they are. If one is wrong or too narrow, fix it as a shared component and say so in the plan. The test: this try's diff against its base reads as the idea and nothing else. *Why:* a difference between two tries can then be attributed to the idea.
2. **A technical failure is not a result.** Say so in the log entry and in the signal. Never write a `lesson` saying an idea failed before it ran cleanly. *Why:* a false refutation stops everyone after you from trying a good idea.
3. **Push after every round that matters.** The state of the work is read from the branch, never from a conversation; the next round may be done by someone else.
4. **No machine-specific paths** in code, configs or notes. Repo-relative paths only. Data is declared in the plan as `data_source: <repo>@<ref>:<path>`.
5. **Secrets come only from environment variables**, the ones the lab names in its `.env.example` and gives to the session's environment. Never a value in git, logs or notes.
6. **Python is `uv`, and only `uv`:** `uv run`, `uv add`, `uv sync`.
7. **Where heavy runs go:** {{FILL: the same answer as item 10 of §5 in the lab's `AGENTS.md`.}}
8. **Data:** {{FILL: the same answer as item 11 of §5 in the lab's `AGENTS.md`.}}

## 7. What You Learned Goes Somewhere

- **True for this try:** the log and the plan.
- **True for a different experiment, or found outside:** a note to the lab in the log entry (`lesson`, `source`).
- **True for how the lab works:** a `question` or `correction` note, or your report. The lab changes itself.
