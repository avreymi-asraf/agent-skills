# Experiment Language of `<experiment repo>`

> Not written yet: this is the form, put here by the lab because the repo had none when `<experiment name>` was opened. The first experiment on this repo has one job: connect the pipeline end to end (data in, one short run, results back, a way to watch a run) and write this file from what it built. Replace every bracket, and remove this note.

* **Mental model:** [One or two sentences: what a run is, what an idea is allowed to change, what stays as it is so that two runs differ only by the idea.]
* **Vocabulary (one concept, one name):** [The repo's terms, as used in code, plans, logs and the cortex.]

## Shared components
Used by every experiment, reimplemented by none. Fix one here, for everyone; never fork one into an experiment.

| Component | Where | What it does | Notes |
|---|---|---|---|
| Data | [file] | [load, view, split] | |
| Run entry and config | [file] | [one run from one config object; a variant is a config value or a flag] | |
| Runner | [file] | [sends a run to a machine and brings the run folder back] | |
| Observation and analysis | [file] | [watching a run while it goes; comparing runs after] | |
| Final evaluation | `evaluate.py` | [what it measures, or "none yet"] | |

## Extension points
Where an idea goes in. If an idea fits none of these, that is the first thing to settle.
* [Name, file or interface, what kind of idea belongs here.]

## What a run leaves behind
[Run folder layout, file names and key names. Keep them stable so rounds and experiments can be compared.]

## Commands
[How a round's command is run, with `uv run`, repo-relative paths and environment variables only.]
