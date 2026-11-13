# Lab Journal (`JOURNAL.md`)

> The path of the research: which directions the lab took and what each concluded (the matrix), what is best now (Frontier), where it may go next (Sparks), and where not to go again (Banlist). It grows like a tree, each experiment starting from earlier work, in the direction of the research, and it holds only what the lab did and decided. What is known about the field, from any source, is in `cortex/`. Terms: `AGENTS.md` §3.

## 1. Current Frontier (Best Verified Baselines)

> One baseline per experiment repo and task, shared by all experiments. A number is written with the evaluation version it was measured with (`evaluation_version` in that lab step's `metrics.json`).

| Experiment Repo | Task / Benchmark | Best Branch / Commit | Metric | Evaluation Version | Provenance Experiment |
| :--- | :--- | :--- | :--- | :--- | :--- |

## 2. Active Sparks (Ideas Waiting to Be Tried)

> `* **[SPARK-nn] (from [[<experiment name>]], a claim from outside, or the user; Priority; Gap):** the idea, and why it is worth an experiment.`

## 3. Experiment Matrix (Chronological Index)

> One row per experiment, written by `scripts/lab.py`: `new-exp` adds it with **OPEN** in the Verdict column, `record-verdict` completes it, with the kept try branch or `none`. Base is the branch and commit the experiment started from. A row that says OPEN is an experiment someone may be working on.

| Experiment | Opened | Closed | Experiment Repo | Base | Idea | Metric vs. Baseline | Verdict | Kept Try | One-Line Takeaway |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

## 4. Anti-Repeat Banlist

> An idea that ran cleanly and did not work (`HYPOTHESIS_REFUTED`): `[pattern] -> [why it failed] -> [unless condition X changes] ([[claims/<claim>]])`. The claim is the experiment's final conclusion. A crash is never listed here, and neither is something only a paper reports.
