---
type: system
repo: <target-repo>
status: fresh
updated: YYYY-MM-DD
---
# System Profile: `<target-repo>`

> Repo: <target-repo> | Fingerprint: git:<sha>
> Monitored: <paths, comma separated>

> Add `> Branch: exp/<exp-name>` when the frame below lives on a kept experiment branch and not on the default branch. Experiments that use the frame then start from it with `new-exp --base-branch`.

## 1. Overview
[What this repo is for in the research, and a short diagram of how data moves through it.]

## 2. Experiment Language (Must Stay Consistent)
> Change this frame only when the frame itself is the idea of an experiment, and update this section when that experiment is kept.

* **Mental model:** [One or two sentences: what a run is, what an idea is allowed to change, what stays as it is so that two runs differ only by the idea.]
* **Vocabulary (one concept, one name):** [The repo's terms.]
* **Structure:** [The shared tools every experiment uses, and the extension points where an idea goes.]
* **Commands:** [How a round's command is run through `lab.py run`, with repo-relative paths and `.env` variables only.]
* **Data rules:** [What data may leave the machine, what may appear in logs, what is not leak-free.]

## 3. Checks & Measurements
[The cheap checks a round can run, and the final evaluation if the repo has one.]

## 4. Known Quirks & Environment Notes
[Limits every experiment on this repo will hit.]
