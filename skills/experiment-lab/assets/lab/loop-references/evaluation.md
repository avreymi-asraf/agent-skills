# The evaluation API

The one contract the tools enforce: every evaluation of an experiment repo is run the same way. An evaluation is run in a lab step, on one commit of one try. It can be run on any try, and on several tries of one experiment. Inside a round, a try measures however is useful; that is not an evaluation.

## The contract

- The script is **`evaluate.py` at the root of the experiment repo**. It is part of the repo's code and travels with every branch.
- `lab.py evaluate --exp <id> --try <try name>` runs `uv run evaluate.py` in a worktree of the try branch at the chosen commit, with no arguments. The script reads what it needs from the environment: `$LAB_ROOT`, the lab's `.env` variables (names in `.env.example`), `$EXP_DIR` (the experiment's lab folder) and `$STEP_DIR` (this lab step's files folder, `<lab folder>/steps/<try name>-<short commit>/`). A file the evaluation writes to `$STEP_DIR` (per-case scores, a report) becomes part of the lab step's record. Files of a round never go there; they go to the notes' `runs/` folder on the try branch.
- **The last line of stdout is one JSON object of metrics.** Progress goes to stderr or to earlier lines. Exit code 0 means the evaluation ran.
- When the script calls an external benchmark, it adds that benchmark's name and version to the JSON as `"eval_version"`, so that a new benchmark version counts as a new evaluation version.

## What `lab.py evaluate` records

In `$STEP_DIR` it saves `patch.diff`, the try's code change against the experiment's base (the diff without the notes folder and without the lab kit); `evaluate.log`, the full output; and `metrics.json`, the metrics, the commit and the **evaluation version**. The evaluation version (`evaluation_version`) is the git hash of the `evaluate.py` that ran, followed by `+<eval_version>` when the JSON has one. Whoever runs the lab step copies the result into the lab step record in `lab-steps.md`.

The command exits non-zero when the script fails, times out or prints no JSON line, and then writes no metrics. When the repo has no `evaluate.py`, it saves `patch.diff`, says that there is no evaluation yet, and exits zero: the lab step is recorded with its conclusions and no number.

Nothing protects the evaluation code; it is often external anyway. What keeps numbers honest is the recorded version: two results are comparable only when their `evaluation_version` is the same.

## When the evaluation changes

`evaluate.py` lives on branches, so a change made in one try does not reach the others by itself. Say in the try's log and in the lab step record that the evaluation changed, then re-run it on every try whose number is still being compared (at least the Frontier's):

```bash
uv run scripts/lab.py evaluate --exp <older-id> --try <try name> --eval-from <branch with the new evaluation>
```

`--eval-from` runs that branch's `evaluate.py` on the older try's code without committing it there. The result is a new lab step record on that try; the earlier one stays. Update Current Frontier with the new numbers and version. If the new script needs code the older branch does not have, the run fails, the failed attempt is recorded in the lab step record, and the old number stays under its old evaluation version. Do not compare that number with new ones; if it is the Frontier's, the Frontier row keeps the old version beside it, which is what shows the mismatch.

Building or changing the evaluation of a repo is itself an experiment.

## What the number is for

The conclusion of an experiment is what its lab step records show together: whether an effective approach was found and which direction to take next. An evaluation is evidence for that, not the definition of it. What the evaluation measures is this lab's own decision (the lab's `AGENTS.md`); until an experiment builds an `evaluate.py`, do not invent a metric and call it the lab's.
