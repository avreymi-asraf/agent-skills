---
name: experiment-lab-loop
description: Run an experiment in a research lab repository (a wiki, a journal, and isolated git worktrees on external target repos). An experiment is one idea worked in rounds of implement, run, analyze, with a living plan and a round log kept next to the code, until a conclusion is reached, then closed with a final evaluation. Use when the user asks to find a new research direction, plan, start, continue, analyze or close an experiment, decide what from an experiment belongs in the research wiki or lab journal, or run or re-run the final evaluation of a target repo.
---

# Experiment lab loop

An experiment is a line of inquiry: one idea, pursued until there is a conclusion. Most of the work is a loop of rounds (implement, run, analyze) in which the plan keeps getting more exact. No tool decides when a round taught something or when the idea is exhausted; you do, and many rounds may pass before there is anything to conclude.

The lab exists so this work compounds: what a round teaches goes into the wiki, where the next experiment finds it. Take the lab's own terms and standing rules (usually in its `AGENTS.md`) as binding; this skill describes the working method.

```
find a direction ─▶ write the plan ─▶ ┌─ implement ─▶ run ─▶ analyze ─┐ ─▶ close: final evaluation,
 (cross-check with                    │  update the plan              │    postmortem, journal, wiki
  what the lab knows)                 └─ interim conclusion ─▶ wiki ◀─┘
```

## Lab layout (adapt names to the repo)

| Part | Role |
|---|---|
| `experiments/<exp-name>/` | Closing record per experiment: `postmortem.md`, `results.json`, `patch.diff`. Not rewritten after closing, except a re-evaluation added to `results.json`. |
| `JOURNAL.md` | Routing: current frontier (best verified baseline per target), active Sparks, experiment matrix, Anti-Repeat Banlist. |
| `wiki-llm/` | Compiled knowledge: `index.md`, `purpose.md`, `gap_map.md`, `systems/`, `findings/`, `literature/`, `log.md`. Build and maintain it with the `wiki-llm` skill. |
| `.targets/repos/<repo>`, `.targets/worktrees/<exp-name>/` | Git-ignored base clones and per-experiment worktrees. |

- Experiment names: `<id>-<repo-short>-<worktree-name>`, with a unique short id, the target's short name, and 1-3 short `/`-separated levels from broad to specific. The same name is used for the lab folder, the worktree, and the branch `exp/<exp-name>`.
- A system page (`wiki-llm/systems/<repo>.md`) records `> Repo`, `Fingerprint: git:<sha>`, monitored paths, and the target's **Experiment Language**: the concepts, file layout, extension points, and naming that every experiment on that repo reuses, so a metric delta is attributable to the idea and a reader of one experiment understands the next. Change the language only when that change *is* the hypothesis, and say so in the plan.
- A small lab CLI (shown below as `lab`, e.g. `scripts/lab.py`) is worth having for the mechanical steps. Without one, do the same steps with plain git.

## Standing rules

1. Never edit a base clone. One experiment = one branch + one worktree. Push the experiment branch to the target's `origin` after every round that matters, and never merge it into the default branch unless the user asks. A follow-up built on earlier code branches from it (`--base-branch exp/<earlier>`).
2. A technical failure (OOM, missing credential, typo) says nothing about the idea. Only a clean run can refute; never record a crash in `findings/` or the banlist.
3. Do not edit the evaluation to move a number. What keeps numbers honest is the recorded evaluation version (see Evaluation contract).
4. No absolute or machine-specific paths in docs, plans, configs, or the wiki; use repo-relative paths and variables the tooling provides. Declare data as `data_source: <repo>@<ref>:<path>`. Secrets come from environment variables named in `.env.example`, never from git, logs, results, or the wiki.
5. Keep the orchestrator's context for judgment (choosing ideas, reviewing evidence, deciding verdicts). Delegate bulk work (source gathering, long implementation or debugging, long runs, wiki ingestion) to subagents with a narrow written brief, then review the output instead of redoing it.
6. Commit code, log, and plan together, so one commit holds a round's code and what it taught.

## 1. Find a direction

Choosing the idea is a stage of its own, and where research is won or lost. Use any method that fits: papers, techniques from neighbouring fields, asking *why* a bottleneck exists, a surprising round of an old experiment, arguing for the opposite of the obvious move. The `iterative-deep-researcher` skill suits the literature work. Keep several competing hypotheses alive before committing, at least one contrarian.

What is required is to **cross the idea with what the lab already knows**, because an idea that ignores it repeats old work or misses why the last attempt failed:

- `purpose.md`: does it serve what the lab is for?
- `gap_map.md` and the journal's Active Sparks: is it an open question, or does it open a better one?
- Anti-Repeat Banlist: was it refuted already, and under which conditions?
- `findings/` and earlier postmortems: what did earlier rounds learn that changes this idea?
- The target's system page: can it be said in the repo's Experiment Language?

If the lab has a drift check, run it when the base branch may have moved; it reports system pages whose monitored code changed since their fingerprint and updates nothing. Save useful paper notes to `wiki-llm/literature/`. Ideas considered and dropped are candidate Sparks; keep them in the plan.

## 2. Write the plan

```bash
lab new-exp --repo <target-repo> --name <worktree-name> [--base-branch exp/<earlier-exp-name>]
```

This creates the branch and worktree, puts `plan.md` and `log.md` in the worktree (for example under `notes/<exp-name>/`, so they travel with the code), and creates the lab folder `experiments/<exp-name>/` for the closing record.

`plan.md` describes **how to realise the idea, as far as is known right now**: as exact as present knowledge allows, no more. On day one it may be little more than "try X", with a list of what is unknown. After each round that teaches something, rewrite it in place so a reader sees where the experiment stands without reading history. It holds:

- **The idea** and why it is worth trying. Stable; if it must be replaced, the experiment is over.
- **What we know and how we will do it**, at whatever level of detail is honest today.
- **Open questions** the next rounds must answer.
- **Stopping point**, in free text: what result is enough, and what makes it not worth continuing (a budget of rounds or GPU hours, a sign the idea is exhausted). Reaching it is the moment to decide (conclude, or go on with a reason), not an automatic stop.
- **Experiment language**: which concepts and extension points of the repo it reuses.
- `data_source` in the frontmatter.

## 3. Work in rounds

Each round, inside the worktree on the experiment branch:

1. **Implement** the next step of the plan in the repo's Experiment Language. Commit it; remote runners ship committed code only.
2. **Run** it. During rounds, measure however is useful (short run, probe, notebook, the repo's own checks); the final evaluation is not required yet. Running is expensive: plan each run first and watch it while it runs. For GPUs use `colab-cli` or the cluster skill the lab provides.
3. **Analyze.** Look at cases and traces, not only the number, and ask why it moved or did not.
4. **Log the round** in the experiment log: what was tried, seen, decided, and where the run's small files live. A failed round is logged like any other, marked technical failure or real result.
5. **Update the plan** if the round changed what is known. Commit code, log, and plan together and push.
6. **Is there something to tell the lab?** Often not yet. Then start the next round.

Check a long stretch without a conclusion against the stopping point from time to time.

## 4. What to tell the lab

An experiment writes in two places for two readers:

- **The experiment log**, next to the code, is for whoever continues *this* experiment. It holds everything, including dead ends and debugging.
- **The lab** (wiki, journal, postmortem) is for whoever does a *different* experiment and will never open this branch. Every line there is read by all of them.

For each thing learned, ask: **would someone working on a different idea do their work differently if they knew this?** If yes, it leaves the log.

| Learned in a round | Goes to |
|---|---|
| A bug or quirk in this experiment's code | Log only |
| A hyperparameter that diverged for this recipe | Log only (lab only if it says something general about the model or data) |
| A data property that affects every experiment on it (e.g. label leakage) | Lab: `findings/` and gap map |
| An environment limit every experiment on the repo will hit (e.g. memory) | Lab: the system page |
| An idea that failed across several clean variants | Lab, at close: postmortem and Banlist |
| A crash from a missing credential | Log only |

Telling too little leaves lessons in a branch nobody opens; telling too much buries what matters. When unsure, write it in the log marked "candidate for the lab" and decide next round. Write lab entries for a reader who has not seen the experiment: what was found, on what evidence, under which conditions, naming the experiment and round.

## 5. Conclusions

- **Interim conclusion** (something a different experiment should know, but the experiment goes on): work it into the right `findings/` page marked `(provisional, [[<exp-name>]] round <n>)`, update `gap_map.md` (and `index.md` if a page was added), note "Told the lab" in the log, and continue.
- **Final conclusion** (result reached, or idea exhausted): close the experiment. If the finding is that a different idea is right, that is also final: close this one and write the new idea as a Spark or open a new experiment.

A provisional claim is a promise to return. At close, confirm each (remove the mark, name the experiment as source) or withdraw it (`Status: Withdrawn after [[<exp-name>]]`, with the reason). A claim an older page made and this experiment overturned gets `Status: Superseded by [[<exp-name>]]`. Never delete history silently.

## 6. Close the experiment

1. **Final evaluation**, if the target repo has one: `lab evaluate --exp <id>`. Compare with the baseline in the journal's Current Frontier, and check both used the same evaluation version. If there is no evaluation yet, close with the conclusion and no number, and say so.
2. **Write `postmortem.md`** in the lab folder: verdict, why things went the way they did (cite rounds), what happened to each provisional claim, and one or two Sparks.
   - `HYPOTHESIS_SUPPORTED`: the result improved, or held within noise while code or prompt got simpler.
   - `HYPOTHESIS_REFUTED`: ran cleanly and did not work. Add to the Banlist as `[pattern] -> [why it failed] -> [unless condition X changes]`.
   - `INFRA_INCONCLUSIVE`: a technical blocker prevented a real test. Nothing goes to findings or the Banlist.
3. **Record it:** `lab record-verdict --exp <id> --verdict <V> --metric-delta "<delta or 'no metric'>" --summary "<one-line lesson>"`. Copy Sparks into the journal and update Current Frontier on a new best, with the evaluation version beside it.
4. **Settle the wiki:** confirm or withdraw provisional claims, update `gap_map.md` and `index.md`. If a kept experiment changed the frame, update the Experiment Language and point the system page at the branch (`> Branch: exp/<exp-name>`, new fingerprint).
5. **Push the branch** whatever the verdict, with the final plan and log on it. Do not merge it.
6. Optionally remove the worktree; the branch and lab folder stay.

## Evaluation contract

Every final evaluation of a target repo should be run the same way:

- An `evaluate` script at the root of the target repo, part of its code, travelling with the experiment branch.
- The lab command runs it in the worktree with no arguments; the script reads what it needs from environment variables (experiment folder, lab root, data locations).
- **The last line of stdout is one JSON object of metrics.** Progress goes to stderr or earlier lines. Exit code 0 means it ran. External benchmarks add their name and version as `"eval_version"`.
- The lab stores the output, metrics, commit, and a hash of the script (`eval_script_sha`) in `results.json`, and the branch diff in `patch.diff`. Two results are comparable only when `eval_script_sha` (and `eval_version`) match.

**When the evaluation changes, re-measure.** The script lives on experiment branches, so a change in one does not reach the others. Note the change in the log and postmortem, then re-run the new script on every experiment still being compared (at least the Frontier's), keeping the earlier measurement under `earlier_evaluations`. If the new script needs code the older branch lacks, say so in the journal and do not compare the old number with new ones. Building or changing a repo's evaluation is itself an experiment.

## Suggested lab commands

| Command | Does |
|---|---|
| `sync-repos` | Clone or fetch target repos into `.targets/repos/` |
| `context-pack` | Compile purpose, gaps, journal, and wiki index into one reading file |
| `check-drift` | Report system pages whose monitored code changed since their fingerprint |
| `new-exp` | Create branch, worktree, plan and log, and the lab folder |
| `mount-exp` | Re-create a worktree from a pushed experiment branch (new session or fresh clone) |
| `run --exp <id> -- '<cmd>'` | Run a command in the worktree with the lab's environment set |
| `evaluate --exp <id> [--eval-from <branch>]` | Run the target's evaluation; write results and patch |
| `record-verdict` | Set the verdict, add the matrix row and a log line |
| `cleanup-worktree` | Remove the worktree only |

The log, plan, wiki, and the journal's Frontier, Sparks, and Banlist are edited by hand; they carry judgment, so no command writes them.

## Companions

`wiki-llm` (the semantic layer), `iterative-deep-researcher` (direction finding), `colab-cli` (GPU runs), `testing` and `code-as-tools` (experiment code), `grow-autonomy` (when the user rejects how the lab worked).
