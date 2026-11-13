---
type: system
anchor: code           # this page is grounded in the experiment repo's code (Fingerprint below), not in claims
repo: <target-repo>
status: fresh
updated: YYYY-MM-DD
---
# System Profile: `<target-repo>`

> Repo: <target-repo> | Fingerprint: git:<sha>
> Monitored: <paths, comma separated>

> Add `> Branch: <experiment name>/<try name>` when the shared components below live on a kept try branch and not on the default branch. Later experiments then start from that branch with `new-exp --base`.

## 1. Overview
[What this repo is for in the research, and a short diagram of how data moves through it.]

## 2. Experiment Language (Shared by Every Experiment on This Repo)
> Every experiment on this repo is a small change on top of what this section describes: the idea goes in at an extension point and uses the shared components as they are. Change the Experiment Language only when that change is the idea of an experiment, and update this section when that experiment is kept.
>
> An experiment repo that is new or empty has no Experiment Language yet. Then write here "Not written yet", and the first experiment on this repo has one job: connect the pipeline end to end (data in, one short run, results back, a way to watch a run) and write this section from what it built. Its claim is narrow ("the pipeline is connected") and its numbers are not a baseline.

* **Mental model:** [One or two sentences: what a run is, what an idea is allowed to change, what stays as it is so that two runs differ only by the idea.]
* **Vocabulary (one concept, one name):** [The repo's terms, as used in code, plans, logs and the cortex.]

### Shared components
Used by every experiment, reimplemented by none. Fix one here, for everyone; never fork one into an experiment.

| Component | Where | What it does | Notes |
|---|---|---|---|
| Data | [file] | [load, view, split] | |
| Run entry and config | [file] | [one run from one config object; a variant is a config value or a flag] | |
| Runner | [file] | [sends a run to a machine and brings the run folder back] | |
| Observation and analysis | [file] | [watching a run while it goes; comparing runs after] | |
| Final evaluation | [file] | [see section 3] | |

### Extension points
Where an idea goes in. If an idea fits none of these, that is the first thing to settle.

* [Name, file or interface, what kind of idea belongs here.]

### What a run leaves behind
[Run folder layout, file names and key names. Keep them stable so rounds and experiments can be compared.]

### Commands
[How a round's command is run through `uv run scripts/lab.py run --exp <id> -- '<command>'`, with repo-relative paths and `.env` variables only.]

### Data
[Where the data comes from (`<repo>@<ref>:<path>`). What data may leave the machine, what may appear in logs, what is not leak-free.]

## 3. Checks & Measurements
[The cheap checks a round can run, and the final evaluation if the repo has one.]

## 4. Known Quirks & Environment Notes
[Limits every experiment on this repo will hit.]
