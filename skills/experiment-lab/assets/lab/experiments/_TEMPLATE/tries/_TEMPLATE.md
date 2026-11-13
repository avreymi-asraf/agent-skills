---
experiment: <experiment name>
try: <try name>
repo: <experiment repo>
branch: <experiment name>/<try name>
base: <branch> @ <sha>
opened: YYYY-MM-DD
status: live          # live | merged | dropped | closed. Owned by the lab. A try that is not live is never worked, reduced or read again.
into:                 # for merged or dropped by a reduce: the try that took it
worked_by:            # who works it now: a person's name, or the session
---
# Try `<try name>` of `<experiment name>`

> The lab's record of one try. Written only in the lab. The try's own notes are on its branch, in `notes/<experiment name>/`.

## Brief
[What to try and what makes this try different from its siblings. Competing with or cooperating with which tries. How far to go. When to stop and flag. `new-try` also writes this into the try's plan, under This Try.]

## Answers
[Answers to this try's `question` notes, each with its date and who answered. The try reads them here.]

## Lab step 1 · YYYY-MM-DD · commit `<sha>`
* **Reviewed:** [What the try did, in a few sentences. Does its code change read as the idea? Technical problems.]
* **Evaluation:** [Metrics and evaluation version, and how they stand against the baseline (same version or not) | not run, because ...]
* **Conclusions:** [What this try shows about the experiment's idea, and what it does not show.]
* **Written to the lab:** [Claims by file name; findings pages, gaps, journal lines changed | nothing, and why.]
* **Notes read up to:** `<sha>`

## How it ended
[Reduced · YYYY-MM-DD · merged | dropped into `<try>`: what entered, which lessons were carried. | Dropped after lab step <n>: why. | Closed with the experiment: one line on why it needed no further lab step. | Kept: later experiments start from this branch.]
