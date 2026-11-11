# Lab Journal (`JOURNAL.md`)

> The lab's routing page: the best verified baselines, the follow-up ideas waiting to be tried (Sparks), the index of all experiments, and the Anti-Repeat Banlist of refuted ideas. Terms: `AGENTS.md` §2.

## 1. Current Frontier (Best Verified Baselines)

> One baseline per target repo and task, shared by all experiments. A number is written with the evaluation version it was measured with (`eval_script_sha` from `results.json`).

| Target Repo | Task / Benchmark | Best Branch / Commit | Metric | Evaluation Version | Provenance Experiment |
| :--- | :--- | :--- | :--- | :--- | :--- |

## 2. Active Sparks (Ideas Waiting to Be Tried)

> `* **[SPARK-nn] (from [[<exp-name>]], a claim from outside, or the user; Priority; Gap):** the idea, and why it is worth an experiment.`

## 3. Experiment Matrix (Chronological Index)

| Exp | Date | Target Repo (`Branch`) | Idea | Metric vs. Baseline | Verdict | One-Line Takeaway |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

## 4. Anti-Repeat Banlist

> An idea that ran cleanly and did not work (`HYPOTHESIS_REFUTED`): `[pattern] -> [why it failed] -> [unless condition X changes] ([[claims/<claim>]])`. The claim is the experiment's final conclusion. A crash is never listed here, and neither is something only a paper reports.
