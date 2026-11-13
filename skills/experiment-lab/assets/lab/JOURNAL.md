# Lab Journal (`JOURNAL.md`)

> The lab's routing page: the best verified baselines, the ideas waiting to be tried (Sparks), the index of all experiments, open and closed, and the Anti-Repeat Banlist of refuted ideas. Terms: `AGENTS.md` §2.

## 1. Current Frontier (Best Verified Baselines)

> One baseline per experiment repo and task, shared by all experiments. A number is written with the evaluation version it was measured with (`evaluation_version` from that experiment's `results.json`).

| Experiment Repo | Task / Benchmark | Best Branch / Commit | Metric | Evaluation Version | Provenance Experiment |
| :--- | :--- | :--- | :--- | :--- | :--- |

## 2. Active Sparks (Ideas Waiting to Be Tried)

> `* **[SPARK-nn] (from [[<exp-name>]], a claim from outside, or the user; Priority; Gap):** the idea, and why it is worth an experiment.`

## 3. Experiment Matrix (Chronological Index)

> One row per experiment, written by `scripts/lab.py`: `new-exp` adds it with **OPEN** in the Verdict column, `record-verdict` completes it. A row that says OPEN is an experiment someone may be working on.

| Exp | Opened | Closed | Experiment Repo (`Branch`) | Idea | Metric vs. Baseline | Verdict | One-Line Takeaway |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

## 4. Anti-Repeat Banlist

> An idea that ran cleanly and did not work (`HYPOTHESIS_REFUTED`): `[pattern] -> [why it failed] -> [unless condition X changes] ([[claims/<claim>]])`. The claim is the experiment's final conclusion. A crash is never listed here, and neither is something only a paper reports.
