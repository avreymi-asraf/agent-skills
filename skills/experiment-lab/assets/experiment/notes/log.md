# Log: `<exp-name>`

* **Experiment repo:** `<target-repo>` (start branch `<exp-name>/main`, base `<base-branch>` at `<base-sha>`)
* **Opened:** `YYYY-MM-DD HH:MM`

> Empty on the start branch. On a try branch it is that try's log: append-only, newest last, one entry per round, and one entry per try taken in by a reduce. Write here everything someone continuing **this try** needs: settings, dead ends, debugging, partial numbers. A failed round is an entry too; say whether the failure was technical or a real result.
> What a **different** experiment would need to know is written under **For the lab**, and enters the cortex in a lab step (`experiment-lab-loop` → What-to-tell-the-lab). The last entry's **Signal** tells the lab where the try stands.

## <try name> · Round 1 · YYYY-MM-DD · [short name]
* **Tried:** [What was implemented. Commit sha.]
* **Run plan:** [Written before the run: the question it answers, what to watch while it runs, what would stop it early. Settings, where it ran.]
* **Saw:** [What came back: numbers, and the cases or traces behind them. Run files: `runs/01-<short-name>/`.]
* **Decided:** [What this changes. Plan updated? Next step?]
* **For the lab:** [None | one item per line: `lesson` | `source` | `correction` | `question` — one sentence — anchor — conditions.]
* **Signal:** working | ready | failed | blocked

## <try name> · Reduced `<other try>` · YYYY-MM-DD · merged | dropped
* **Tried:** [What that try attempted, in two or three sentences. Its last commit sha.]
* **Saw:** [What it found, with the numbers that matter. Technical failure or a real result.]
* **Decided:** [What entered and why; what was left out and why; what changed in the plan.]
* **For the lab:** [That try's notes to the lab that no lab step has read yet, carried over word for word.]
* **Signal:** working
