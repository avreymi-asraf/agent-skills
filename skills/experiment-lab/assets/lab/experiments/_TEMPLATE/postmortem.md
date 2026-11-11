# Postmortem: `<exp-name>`

* **Verdict:** `[HYPOTHESIS_SUPPORTED | HYPOTHESIS_REFUTED | INFRA_INCONCLUSIVE]`
* **Plan and log:** `notes/<exp-name>/` on branch `exp/<exp-name>` of `<target-repo>`, at commit `[sha]`
* **Branch:** `[Kept: exp/<exp-name> pushed, base for follow-ups via --base-branch | Not kept: exp/<exp-name> pushed as a record]` (never merged into the target's default branch unless the user explicitly asks)

## 1. The Final Conclusion
* **What we conclude about the idea:** [One paragraph.]
* **Why we stopped here:** [The result was reached, or the idea is exhausted. Refer to the plan's stopping point.]
* **Final evaluation:** [Metrics from `results.json` next to the baseline in `JOURNAL.md` → Current Frontier, and whether both were measured with the same `eval_script_sha`. Or: this repo has no evaluation yet.]

## 2. Why It Went This Way
[The mechanism. Cite rounds from the experiment log and specific cases or traces.]

## 3. What Went Into the Cortex and the Journal
* **Claims from this experiment:** [Each one by file name: confirmed or withdrawn, and why. None may stay provisional. The claim that states the final conclusion, if the idea ran cleanly. Older claims this experiment's result disagrees with, and what happened to each: tension, withdrawn or superseded.]
* **Experiment Language:** [Unchanged | shared components added or fixed, extension points or vocabulary changed, and where the system page was updated. Does the diff in `patch.diff` read as the idea only? If not, what else is in it and why.]
* **Other cortex changes:** [`findings/`, `gap_map.md`, the system page's Experiment Language if the frame changed.]
* **Anti-Repeat Banlist entry (if refuted):** [`[pattern] -> [why it failed] -> [unless condition X changes] ([[claims/<claim>]])`]

## 4. Sparks
* **[SPARK-NEW]:** [The follow-up idea this experiment makes most worth trying, written while the context is fresh.]
