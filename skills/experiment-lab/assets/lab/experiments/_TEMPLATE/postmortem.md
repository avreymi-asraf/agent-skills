# Postmortem: `<experiment name>`

* **Verdict:** `[HYPOTHESIS_SUPPORTED | HYPOTHESIS_REFUTED | INFRA_INCONCLUSIVE]`
* **Tries:** [Each try that had a lab step, with the commit of its last lab step (`lab-steps.md`). Tries that were merged or dropped, and into what.]
* **Kept:** `[Kept, because <what later experiments get by starting from it>: the try branch <experiment name>/<try name> is named by the system page's "> Branch:" line | Not kept, because <why none of its tries is a base for others>]` (no branch is merged into the experiment repo's default branch)

## 1. The Final Conclusion
* **What we conclude about the idea:** [One paragraph: what the lab step records show together.]
* **Why we stopped here:** [The result was reached, or the idea is exhausted. Refer to the plan's stopping point.]
* **Evaluation:** [The metrics of the lab step the conclusion rests on (try and commit), next to the baseline in `JOURNAL.md` → Current Frontier, and whether both were measured with the same evaluation version. Or: this repo has no evaluation yet.]

## 2. Why It Went This Way
[The mechanism. Cite lab step records, and through them rounds of a try's log and specific cases or traces.]

## 3. What Went Into the Cortex and the Journal
* **Claims from this experiment:** [Each one by file name: confirmed or withdrawn, and why. None may stay provisional. The claim that states the final conclusion, if the idea ran cleanly. Older claims this experiment's result disagrees with, and what happened to each: tension, withdrawn or superseded.]
* **Experiment Language:** [Unchanged | shared components added or fixed, extension points or vocabulary changed, and where the system page was updated. Does the kept try's `patch.diff` (its code change against the experiment's base) read as the idea only? If not, what else is in it and why.]
* **Other cortex changes:** [`topics/`, `gap_map.md`, the system page, if the Experiment Language changed.]
* **Anti-Repeat Banlist entry (if refuted):** [`[pattern] -> [why it failed] -> [unless condition X changes] ([[claims/<claim>]])`]

## 4. Sparks
* **[SPARK-NEW]:** [The follow-up idea this experiment makes most worth trying, written while the context is fresh.]
