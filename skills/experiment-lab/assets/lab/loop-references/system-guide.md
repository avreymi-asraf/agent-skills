# System guide

What the lab is made of, why it is built this way, and how information moves through it. The terms are defined in [glossary.md](glossary.md); how each operation is done is in [operations.md](operations.md).

## 1. The idea behind it

The lab searches the way a breeder does. It keeps many directions alive, starts new ones from whichever earlier one looks best, lets several attempts at the same thing run side by side, and then keeps a small part of what they produced.

```
experiment repo   one big idea or method                           (model-repo)
└─ experiment     one direction, started from any earlier try      (02-probes)
   └─ try         one attempt, in parallel with others             (trl-fix-lr, trl-d-lr, ...)
      └─ round    implement → run → analyze
```

Eight principles follow from this. Each one explains rules that appear elsewhere; when a case is not covered by a rule, decide by the principle.

1. **Mess below, small above.** A try may be as messy as it needs to be: its plan changes, its log holds dead ends, two tries contradict each other. What moves up is always smaller than what was below it. A reduce turns several tries into one. A lab step turns a try into a short record and a few claims. Nobody saves every direction of every try, and nobody should try to.
2. **Two levels of saving.** An experiment is saved: the lab knows it, and it ends with a conclusion others can use. A try is recorded, on the map, but it is not saved for its own sake: it exists to find out, and it ends by being reduced into another try or by a lab step that keeps what it showed.
3. **Two levels of sessions.** A try session works one try and sees only its own branch of the experiment repo. A lab session works in the lab: it opens experiments and tries, reduces, runs lab steps, closes. Drawing connections between tries and between experiments, and carrying a lesson from one to another, is the lab session's work, and the lab's records are what it thinks with.
4. **The lab says what exists.** Which experiments are open and which tries are live is written in the lab: the journal and the map of tries. A branch in an experiment repo proves nothing by existing, by being merged or by being old. This is why a try is opened through the lab, and why it ends by its line in the map and not by anything git does.
5. **The state is in git, in the lab's records and in the notes.** Nothing a later reader needs may stay only in a conversation or in one agent's context. This is what lets a person do one operation and an agent the next, on different machines, in any order.
6. **Every operation is defined by what it finds and what it leaves**, never by who does it. A person or an agent, of any kind and on any model, can do any of them. The same instructions serve all.
7. **A try branch is a whole system.** A fresh checkout of it, with nothing else attached, holds the code, the notes with the brief, the Experiment Language and the lab kit. The one thing it does not hold is the lab's records, which have a single live copy, on the lab's default branch.
8. **An experiment is judged as a direction.** Its conclusion is what its lab step records show together: whether an effective approach was found, and what the next direction should be. A number is part of that when the experiment repo has an evaluation; it is never the whole of it.

The rules are meaning, not locks. The hosting does not stop anyone from pushing to a start branch, to another try's branch or to a default branch. The rules hold because whoever acts knows what each branch is for.

## 2. The parts

| Part | Where | What it is for | Who writes it |
|---|---|---|---|
| Cortex | Lab, `cortex/` | The knowledge base of the field, as wide as the lab can make it: sources (mostly from outside), claims, topic pages, tensions, the gap map, system pages. The experiments are one source among the others | The cortex operations at any time (`add`, `investigate`, `review`); lab steps and the close for what an experiment showed |
| Journal | Lab, `JOURNAL.md` | The path of the research, growing like a tree: the baselines, the Sparks, every experiment's row, the Anti-Repeat Banlist. Only what the lab did and decided | `lab.py` (rows), lab steps, and whoever closes an experiment |
| Lab folder | Lab, `experiments/<repo short name>/<experiment name>/` | The experiment as the lab sees it: `results.json` (who it is, its verdict, its kept try), `postmortem.md` at close, and the map of tries | `lab.py`, lab steps, and whoever closes |
| Map of tries | Lab, `<lab folder>/tries.md` | One line per try: try branch, status, a comment of at most 100 characters | `new-try`, reduces, lab steps, the close |
| Lab step records | Lab, `<lab folder>/lab-steps.md` | One entry per lab step: what a try showed, the evaluation, the answers to its questions. Lab step files (`evaluate.log`, `patch.diff`) are in `steps/` | Lab steps |
| Tools | Lab, `scripts/lab.py`, `.agents/skills/` | Opening, listing, evaluating; the skills | Changed as a change to the lab |
| Start branch | Experiment repo, `<experiment name>/main` | The template tries start from: lab kit, first plan, empty log | `new-exp` and the opening commit, once |
| Try branch | Experiment repo, `<experiment name>/<try name>` | One attempt: its code and its notes | `new-try` (first commit), whoever works the try, a reduce into it |
| Experiment Language | Experiment repo, `EXPERIMENT_LANGUAGE.md` | The shared code language every experiment on the repo uses | A try whose experiment's idea changes it |
| Lab kit | Experiment repo, `AGENTS.md`, `.agents/skills/` | Makes a checkout self-sufficient | The lab only (`new-exp`, `new-try`) |

## 3. Who does what, and where

| Operation | Done in | Leaves behind |
|---|---|---|
| Open an experiment | Lab | The start branch; the lab folder; an `OPEN` row |
| Open a try | Lab | A line in the map (`live`); the pushed try branch, with the brief in its plan |
| Work a try | Experiment repo, in a try session; the lab is read, never written | Commits and notes on the try branch, pushed; a signal |
| Reduce | Lab | One live try with the chosen code and the synthesized notes; the others `merged` or `dropped` in the map |
| Lab step | Lab | A lab step record; claims, topic pages, gap map, journal |
| Close | Lab | The postmortem, the verdict, settled claims, the kept try, no live tries |
| Manage many tries | Lab, in a managing session | The map, kept current |
| Delete branches of tries that left the map | Hosting, by a person (a cloud agent cannot) | A shorter branch list |

"Lab" means the lab with the experiment repo at hand: a local clone of the lab (which keeps the experiment repos under `.repos/`), or a cloud session attached to both.

How far a lab session goes without asking is set by the request it was given, like everything in the lab: one operation, guided step by step, or a whole experiment. Two things do not depend on the request. A try session never does a lab operation. A pull request is opened only when the user asks for one.

## 4. How information moves

**Up, by getting smaller.**

```
round ──▶ log entry on the try branch ──▶ [lab step on that try] ──▶ lab step record ──▶ claim ──▶ topic page
          (everything)             │                                  (a few lines)      (one sentence)
                                   └──▶ [reduce] ──▶ one entry in the remaining try's log
                                                      (unread notes to the lab carried, word for word)
```

- A try writes everything a continuer of that try needs, and marks the few things someone else needs as notes to the lab.
- A lab step reads one try and writes what it shows into the lab. The record names the commit it read up to, so the next lab step on that try reads only what is new.
- A reduce keeps what the remaining try needs from the others and drops the rest on purpose. It carries the notes to the lab that no lab step has read yet, unchanged, and keeps two tries' contradicting lessons side by side when the evidence does not decide between them.
- The close aggregates the lab step records into the experiment's conclusion.

**In, from outside.** The cortex is not filled by the experiments alone, or mainly. Whatever is known about the field and may advance the research is added to it at any time (`cortex add`), by a lab session or by a person, with no gap or experiment behind it. What a try reads from outside reaches it as a `source` note.

**Down, by reading the lab.** Anyone, in any working copy, reads the lab from its default branch: the cortex, the journal, the map, the lab step records of its experiment. Nothing is copied into experiment repos, so nothing goes stale there. Three cases when a try needs to know something:

1. The cortex knows. Use it, and cite the claim in the log.
2. The cortex does not know and the outside world may. Investigate, and write what was found as a `source` note to the lab. Do not write it into the cortex.
3. Only the user knows, or it is a decision. Write a `question` note, state the assumption the try continues under, and continue or stop as the brief says. The answer comes back in a lab step record, under `Answers`.

**Sideways, between tries.** A try does not read other tries unless its brief says so. Competing tries stay independent so that their results can be told apart; what lets them be compared is what the first plan fixes for all of them. Cooperating tries are told in their briefs which try branch to read or start from. Bringing two tries together is a reduce, done in the lab.

**To the managing session.** Only the map and the short reports of reduces and lab steps. The content of a try stays inside the operation that processes it.

## 5. What is not enforced

Known limits of the hosting, so that nobody relies on a lock that is not there:

- A session can push to any branch of a repository it can write to, including a start branch, another try's branch and a default branch.
- A pull request opened without naming its base is offered against the repository's default branch. In an experiment repo that is always wrong.
- A cloud agent cannot delete a branch. Nothing in the lab depends on a branch being deleted.
- The lab's default branch is the one live copy of its records. What is not pushed to it does not exist for anyone else.
