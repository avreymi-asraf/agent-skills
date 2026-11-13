---
type: system
anchor: code           # this page is grounded in the experiment repo's code (Fingerprint below), not in claims
repo: <experiment repo>
status: fresh
updated: YYYY-MM-DD
---
# System Profile: `<experiment repo>`

> This page is about one of the lab's experiment repos, not about the field: what the repo is for, where its Experiment Language is, its data and its limits. Knowledge about the field goes in `topics/`.

> Repo: <experiment repo> | Fingerprint: git:<sha>
> Monitored: <paths, comma separated: EXPERIMENT_LANGUAGE.md and the shared components>

> Add `> Branch: <experiment name>/<try name>` when the current Experiment Language and shared components live on a kept try branch and not on the default branch. Later experiments then start from that branch with `new-exp --base`.

## 1. Overview
[What this repo is for in the research, and a short diagram of how data moves through it.]

## 2. Experiment Language
> The Experiment Language of this repo is written in `EXPERIMENT_LANGUAGE.md` at the root of the repo, on the branch named by `> Branch:` (the default branch while there is none), and only there: a try session sees its branch, never this page. Every experiment on this repo is a small change on top of it. It changes like code, in the experiment whose idea is that change, and that experiment is kept.
>
> An experiment repo that is new or empty has no Experiment Language yet. Then write here "Not written yet", and the first experiment on this repo has one job: connect the pipeline end to end (data in, one short run, results back, a way to watch a run) and write `EXPERIMENT_LANGUAGE.md` from what it built. `new-exp` puts the form of that file on the start branch when the base has none (the lab keeps it as `start-branch/EXPERIMENT_LANGUAGE.md`). Its claim is narrow ("the pipeline is connected") and its numbers are not a baseline. A repo that has code and no such file gets one written from its code the same way.

* **File:** `EXPERIMENT_LANGUAGE.md` on `[branch]` | Not written yet
* **In one line:** [What an idea on this repo is allowed to change, and what stays as it is.]


## 3. Data
[Where the data comes from (`<repo>@<ref>:<path>`). What data may leave the machine, what may appear in logs, what is not leak-free.]

## 4. Checks & Measurements
[The cheap checks a round can run, and the final evaluation if the repo has one.]

## 5. Known Quirks & Environment Notes
[Limits every experiment on this repo will hit.]
