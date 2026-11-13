# Operations

How each operation is done. Every operation is written as what it **finds**, the **steps**, and what it **leaves**, so that a person or an agent can do it, and so that the next operation can be done by someone else who reads only the lab's records and the branches. Terms: [glossary.md](glossary.md). Why it is built this way: [system-guide.md](system-guide.md).

Working a try (§3) needs only the experiment repo and is given in plain git. Every other operation is done in the lab, with the experiment repo at hand, and uses `uv run scripts/lab.py` ([commands.md](commands.md)).

The examples use experiment `observe/02-probes` in `model-repo`. In the commands, `E=observe/02-probes`.

## 0. Writing the lab's records

The map of tries, the lab step records, the cortex and the journal are the lab's **records**. Everyone reads them from the lab's default branch, so a record that is not there does not exist for anyone else.

- Do lab operations from a checkout of the lab's default branch.
- Write, commit, then publish at once: `git pull --rebase origin <default branch>` and `git push origin HEAD:<default branch>`. If the push is rejected, pull and push again.
- Two writers at the same time touch different files (one file per try record, one per claim), so they rarely collide. When they do collide on an experiment id or a try name, the second one takes another id or name. This is why `new-exp` and `new-try` publish the lab's record **before** they create the branch.
- Changes to how the lab works (skills, `lab.py`, `AGENTS.md`, templates) are a different thing: they go on a branch of their own and are merged when the user says so.

## 1. Open an experiment (lab)

**Finds:** an idea crossed with what the lab knows, and a base: the try branch named by `> Branch:` on the system page, or any other try branch or start branch.

```bash
uv run scripts/lab.py new-exp --repo model-repo --name observe/probes --base observe/01-training/first
```

It gives the id, writes the lab folder and the journal row (`OPEN`) and publishes them, which reserves the id. Then it creates the start branch `observe/02-probes/main` from the base in a local worktree, with the lab kit and `notes/$E/{plan.md, log.md}` in it.

Then, by hand:

1. Write the first plan in `notes/$E/plan.md`: the idea, why it is worth trying, the stopping point, what stays fixed for every try (data, split, the measurement tries will be compared on), and the realisation as far as it is honestly known. It may be short. Leave `This try` empty.
2. Commit it on the start branch together with what `new-exp` wrote, and push.

**Leaves:** a start branch that tries start from and that nothing enters again; a lab folder and an `OPEN` row that let any later session find the experiment.

A base that belongs to an earlier experiment carries that experiment's notes folder with it. Leave it: it is where to read how the inherited code came to be.

## 2. Open a try (lab)

**Finds:** an open experiment and a brief: what to try and what makes this try different, whether it competes or cooperates with which tries, how far to go, when to stop and flag.

```bash
uv run scripts/lab.py new-try --exp 02 --name trl-fix-lr --brief-file <file> [--base <branch>]
```

1. It writes the try record `tries/trl-fix-lr.md` in the lab folder (status `live`, the base, the brief) and publishes it, which reserves the try name.
2. It creates the try branch `observe/02-probes/trl-fix-lr` from the base (default: the start branch), makes its first commit (the current lab kit, and the brief written into `notes/$E/plan.md` under `This try`), and pushes it.

Whoever works the try then starts **on the try branch and pushes to the same branch**: locally `uv run scripts/lab.py mount --exp 02 --try trl-fix-lr`, in the cloud a try session ([claude-code-cloud.md](claude-code-cloud.md)). Write who works it (a person's name, or the session) in the try record's `worked_by` line.

**Leaves:** a live try on the map, with its brief in the lab and on its branch.

## 3. Work a try (experiment repo)

**Finds:** its try branch, and on it `AGENTS.md`, `EXPERIMENT_LANGUAGE.md`, and `notes/$E/plan.md` with the first plan and, under `This try`, the brief.

A try works in rounds (the skill's [Work-in-rounds]). What a try may write: code, in the Experiment Language, and the notes on its own branch. It does not write another branch, the lab kit, or anything in the lab. It may read the lab, including its own try record, where the brief and the answers to its questions are.

First, rewrite the plan's `This try` section in your own words if the brief leaves the realisation open: how this try will do it, its open questions.

One log entry per round, appended to `notes/$E/log.md`:

```markdown
## trl-fix-lr · Round 2 · 2026-11-14 · held-out split
* **Tried:** [what was implemented; commit sha]
* **Run plan:** [written before the run: the question, what to watch, what would stop it early; where it ran]
* **Saw:** [numbers, and the cases or traces behind them; run files: `runs/02-held-out/`]
* **Decided:** [what this changes; was the plan updated; next step]
* **For the lab:** [None, or one item per line:]
  * `lesson` — [one sentence] — anchor: commit `<sha>`, run `02-held-out` — conditions: [model, data and split, what was fixed]
  * `source` — [one sentence] — anchor: [link], "[the quoted words]" — conditions: [the source's own setting]
  * `correction` — [one sentence] — anchor: `claims/<claim>`, and the evidence — conditions: [...]
  * `question` — [what is missing and why it matters] — continuing under: [the assumption]
* **Signal:** working | ready | failed | blocked
```

Commit code, log and plan together and push after every round that matters.

**Finishing.** Set the signal in the last entry: `ready` when there is something for a lab step or a reduce, `failed` when nothing is worth keeping (say whether the failure was technical or a real result), `blocked` when a `question` must be answered first. Push, report, and stop. A try does not open tries, reduce, run a lab step, or open a pull request.

**Leaves:** a pushed try branch whose last log entry tells any reader where it stands.

## 4. Reduce (lab)

**Finds:** two or more live tries of one experiment, and a decision about which one is the **target**: an existing try that nobody is working at that moment, or a new try opened for the reduce. Every other try will leave the map.

1. **The target.** For a new one, open a try (§2) whose base is the try branch that holds the code to start from, and whose brief says which tries it reduces. Work in the target's working copy.
2. **One other try at a time**, here `trl-d-lr`:
   ```bash
   git fetch origin
   git merge --no-ff --no-commit origin/$E/trl-d-lr
   git restore --source=HEAD --staged --worktree -- notes/$E/plan.md notes/$E/log.md   # the notes are merged by meaning, below
   ```
3. **Decide which code enters**, by reading the diff and the two logs: all, part or none. Resolve conflicts in favour of what the target should hold now. To leave code out, put the paths back as they were before the merge:
   ```bash
   git restore --source=HEAD --staged --worktree -- <paths>     # part
   git restore --source=HEAD --staged --worktree -- .           # none: the try is dropped, only its lessons enter
   ```
4. **Synthesize the notes**, by meaning. Read the other try's notes with `git show origin/$E/trl-d-lr:notes/$E/log.md` (and `plan.md`).
   - Rewrite the target's `plan.md` in place so that it is the best current description of the one try that remains.
   - Append one entry to the target's `log.md`:
     ```markdown
     ## trl · Reduced `trl-d-lr` · 2026-11-15 · merged | dropped
     * **Tried:** [what that try attempted, in two or three sentences; its last commit sha]
     * **Saw:** [what it found, with the numbers that matter; technical failure or a real result]
     * **Decided:** [what entered and why; what was left out and why; what changed in the plan]
     * **For the lab:** [that try's notes to the lab that no lab step has read yet, carried over word for word with their anchors. Its try record says up to which commit they were read. Notes already read are not carried.]
     * **Signal:** working
     ```
   - Do not copy the other try's log. What whoever continues the target does not need is dropped here, on purpose. When two tries reached contradicting lessons and the evidence does not decide, keep both and say so.
   - Of the other try's run files, keep only those a carried lesson cites. When both tries used the same run name the files conflict: keep the target's, and cite the other try's by its branch and commit.
5. **Commit the merge**: stage what you chose by name (`git add <paths>`, never `git add -A`), then `git commit`. Go on to the next try. After the last one, push the target. Its signal is `working`: the combined code has not been run yet, and running it is the target's next round.
6. **Update the map**, in the lab: in each reduced try's record set `status: merged` or `dropped` and `into: <target>`, and add a `Reduced` section of one or two lines (what entered, which lessons were carried). A new target that was opened from one of the tries takes that try off the map too. Publish (§0).
7. **Report** in a few lines: the target, what entered from each try, what was left out and why, the lessons. This report is all a managing session reads of a reduce.

**Leaves:** one live try holding the chosen code and the synthesized notes; the others off the map, each record saying merged or dropped and into what. Their branches stay in git as history. No one works, reduces or reads them again, and a person may delete them.

## 5. Lab step (lab)

**Finds:** one chosen live try, and the commit to look at (default: the tip of its branch). Any try can be chosen, not only the newest or the best, and the same try can have several lab steps.

1. **Read what is new.**
   ```bash
   uv run scripts/lab.py inbox --exp 02 --try trl-fix-lr
   ```
   It prints the try's signal and the `For the lab` items in its log that were added after the commit recorded by this try's last lab step.
2. **Review the try**: its plan, its log, and its code change against the experiment's base. Does the diff read as the idea? Did the rounds run cleanly, or is a failure technical? Is what the log claims supported by the runs it cites?
3. **Evaluate, when one is possible.**
   ```bash
   uv run scripts/lab.py evaluate --exp 02 --try trl-fix-lr [--commit <sha>]
   ```
   ([evaluation.md](evaluation.md)). With no `evaluate.py` in the repo, or a try that cannot run, the lab step has no number, and says why.
4. **Write the conclusions into the lab.**
   - A **lab step record** in the try record:
     ```markdown
     ## Lab step 2 · 2026-11-16 · commit `3f9a2c1`
     * **Reviewed:** [what the try did, in a few sentences; whether the diff reads as the idea; technical problems]
     * **Evaluation:** [metrics and evaluation version; against the baseline, same version or not | not run, because ...]
     * **Conclusions:** [what this try shows about the experiment's idea, and what it does not show]
     * **Written to the lab:** [claims by file name; findings pages, gaps, journal lines changed | nothing]
     * **Notes read up to:** `3f9a2c1`
     ```
   - The cortex, one change per note, by kind (forms and statuses: `cortex/profile.md`):

     | Kind | What is written |
     |---|---|
     | `lesson` | A claim: `status: provisional`, anchor `experiment::` with the experiment name, the try, the round and the commit. Then the findings page it changes, citing it; a tension if it disagrees with a claim the lab holds; the gap it touches. |
     | `source` | The source (`cortex add`), and its `quote` claims. |
     | `correction` | What `cortex/profile.md` §4 says for the case: a tension while it is open which holds, or the claim withdrawn or superseded. |
     | `question` | Try to answer it: from the cortex (`ask`), then from outside (`cortex investigate`). Write the answer in the try record under `Answers`. What stays open becomes a row in `cortex/gap_map.md` and is put to the user. |

     Apply the test of [What-to-tell-the-lab] again: a note that fails it writes nothing, and the lab step record says so.
   - The journal: Current Frontier when the evaluation gives a new best number (with its evaluation version, the experiment and the try); Active Sparks for an idea worth its own experiment.
5. Run the cortex check (`cortex/profile.md` §6) and publish (§0).

**Leaves:** a lab step record that names the commit it looked at; the cortex and the journal changed and published. Nothing is written to the experiment repo.

## 6. Close an experiment (lab)

**Finds:** a decision that the experiment has reached its conclusion: the plan's stopping point was reached, or the idea is exhausted. It is a judgment made in the lab from the lab step records; git shows nothing that forces or forbids it.

1. **Every live try** gets one of two things first: a lab step, when it holds something the conclusion should rest on; or one line in its try record saying why it needs none. A try that only repeats a sibling is reduced into it (§4).
2. **Aggregate.** Write `postmortem.md` in the lab folder from the lab step records: what each try showed, what they show together, the verdict, why things went this way, one or two Sparks.
3. **Settle the cortex**: every provisional claim of this experiment becomes `confirmed` or `withdrawn`; when the idea ran cleanly, its final conclusion is written as a claim too.
4. **Kept or not**: name the try branch later experiments should start from, or say why none.
5. **Record it**: `uv run scripts/lab.py record-verdict --exp 02 ...`. It sets the verdict and the kept try, completes the journal row, and sets every try that is still `live` to `closed`. Publish (§0).

The details of each step are in the skill's [Close-the-experiment].

**Leaves:** a closed row in the journal, a lab folder that no longer changes, no live tries, and, when kept, a try branch that later experiments start from.

## 7. A try becomes an experiment (lab)

When a try turns out to be a direction of its own, it does not grow inside its experiment. Whoever works it says so in the try log, sets the signal to `ready`, pushes and stops. In the lab, a new experiment is opened with that try branch as its base (§1). The try itself gets a lab step that records why, and its status is set to `dropped`, with a line naming the new experiment.

## 8. Manage many tries (lab, a managing session)

**Finds:** an open experiment with more tries than one session can hold in view.

A managing session holds the process, not the content. It reads the map, and the short reports that reduces and lab steps hand back. It never loads a try's log, plan or code into its own context: the content of tries is processed inside reduces and lab steps, which are done in a clean context (a subagent, or another lab session) and return a few lines.

The loop:

1. `uv run scripts/lab.py tries --exp 02` prints the map: each try's status, its signal as read from its branch, the date of its last commit, who works it, and its last lab step.
2. Decide the next move from that and from the experiment's first plan: open tries (§2) and start a try session for each; ask for a lab step on a try that signals `ready`; ask for a reduce when tries have to become one; answer a `blocked` try; close.
3. Hand each reduce and each lab step to a clean context, with a brief: which tries, which target, what to hand back. Read the report, not the tries.
4. Everything decided is in the map before the next move: statuses, `into`, `worked_by`, the lab step records. A managing session that ends leaves nothing behind that another one, reading the map, cannot continue from.

Cases:

- **A try session died.** The map says `live` and the signal is still `working`, but no one works it. Start a new try session on the same try branch and update `worked_by`. Only work that was never pushed is lost. If the try is not worth continuing, reduce it into a sibling as `dropped`, or give it a lab step and end it.
- **A try is `blocked`.** Its `question` is answered in a lab step and written in its try record under `Answers`. Then a try session is started on the same branch and told to read its record.
- **How far the managing session goes by itself** (opening tries, reducing, closing) is set by the request it was given, like everything in the lab.
