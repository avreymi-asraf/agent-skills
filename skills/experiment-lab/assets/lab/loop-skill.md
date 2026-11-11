---
name: experiment-lab-loop
description: Run an experiment in this research lab (cortex, JOURNAL.md, isolated git worktrees on external target repos). An experiment is one idea worked in rounds of implement, run, analyze, with a living plan and a round log kept next to the code, until a conclusion is reached, then closed with a final evaluation. Use when the user asks to find a new research direction, plan, start, continue, analyze or close an experiment, decide what from an experiment belongs in the lab's cortex or journal, or run or re-run the final evaluation of a target repo.
---

<experiment-lab-loop>

# Experiment lab loop

An experiment here is a line of inquiry: one idea, pursued until there is a conclusion. Most of the work is a loop of rounds (implement, run, analyze) in which the plan keeps getting more exact. It is a semantic loop. No tool decides when a round taught something or when the idea is exhausted; you do, and sometimes many rounds pass before there is anything to conclude.

The lab exists so that this work compounds. What a round teaches the whole lab goes into the cortex (`cortex/`, the lab's memory), where the next experiment will find it. The terms used below (experiment, plan, round, conclusion, baseline, Spark) are defined in the lab's `AGENTS.md`, together with the rules that always hold.

```
find a direction ─▶ write the plan ─▶ ┌─ implement ─▶ run ─▶ analyze ─┐ ─▶ close: final evaluation,
 (cross-check with                    │  update the plan              │    postmortem, journal, cortex
  what the lab knows)                 └─ interim conclusion ─▶ cortex ◀┘
```

- **[Find-a-direction]**: choosing the idea. The only fixed part is checking it against what the lab already knows.
- **[Write-the-plan]**: the plan as a living description of how to realise the idea, and its stopping point.
- **[Work-in-rounds]**: the loop itself, and the experiment log.
- **[What-to-tell-the-lab]**: what stays in the experiment's own log and what every other experiment needs. The hardest judgment in the loop.
- **[Conclusions]**: interim and final, and how each reaches the cortex.
- **[Close-the-experiment]**: final evaluation, verdict, journal, branch.
- **[Evaluation-API]**: the one contract the tools enforce.
- **[Commands]**: what `scripts/lab.py` does and does not do.
- **[Example]**: one experiment from idea to close.

How far to carry a request (one round, or the whole experiment without checking in) is set by the request; see `AGENTS.md` §1. Companion skills: `cortex` for every operation on the lab's memory (the form of a claim and a page, `investigate` for reading from outside, `review` for the periodic check), with this lab's own layout and anchors in `cortex/profile.md`; `iterative-deep-researcher` for a long search inside an investigation; `code-as-tools` when writing experiment code, `grow-autonomy` when the user rejects how the lab worked or the way it works has to change. Where heavy runs go, and the skill for it, is in `AGENTS.md`.

</experiment-lab-loop>

<Find-a-direction>

This is a stage of its own and the one where research is won or lost. There are a hundred ways to do it: read papers, look for a technique in a neighbouring field, ask why a bottleneck exists, look again at a surprising round of an old experiment, argue for the opposite of the obvious move. Pick the way that fits; none is required.

What is required is to **cross the idea with what the lab already knows**, because an idea that ignores it either repeats old work or misses the reason the last attempt failed:

```bash
uv run scripts/lab.py context-pack   # writes cortex/query_pack.md: purpose, gaps, journal, cortex index
```

- `cortex/purpose.md`: does the idea serve what the lab is for?
- `cortex/gap_map.md` and `JOURNAL.md` → Active Sparks: is it one of the open questions, or does it open a better one?
- `JOURNAL.md` → Anti-Repeat Banlist: was it already refuted? Under which conditions?
- `cortex/findings/`, `cortex/tensions/` and earlier `experiments/*/postmortem.md`: what did earlier rounds learn that changes this idea? Follow a findings page down to the claims it cites: each says whether the lab saw it (`experiment`) or someone else reports it (`quote`), and under which conditions. `uv run .agents/skills/cortex/scripts/cortex.py claims --grep <term>` finds claims no page uses yet.
- `cortex/systems/<repo>.md`: can it be said in the repo's Experiment Language? Which extension point does it go into, and which shared components does it use? Creativity belongs in the idea, not in a new vocabulary or a new codebase. If the idea does not fit, that is the first thing to settle: either changing the frame is the idea, or the frame change is an experiment of its own that comes first.

Run `uv run scripts/lab.py check-drift` when the base branch may have moved. It reports whether the code a system page describes has changed since the page was written; it updates nothing.

**Going outside is part of this stage.** An open gap is often answered faster by reading than by running. Reading for a gap is `cortex investigate`: it starts from the gap's row, brings back sources and `quote` claims, and ends by updating that row. What comes back is what someone else reports. For this lab it is a hypothesis, and often the best source of the next idea: it can open a Spark and shape a plan, and an experiment is what turns it into something the lab has seen. Reading with no gap behind it is fine too; it leaves claims in the cortex and no findings page.

Ideas you considered and dropped are candidate Sparks; keep them in the plan.

</Find-a-direction>

<Write-the-plan>

Open the experiment:

```bash
uv run scripts/lab.py new-exp --repo <target-repo> --name <worktree-name> [--base-branch exp/<earlier-exp-name>]
```

This creates the branch `exp/<exp-name>` and its worktree `.targets/worktrees/<exp-name>/`, puts `plan.md` and `log.md` in the worktree under `notes/<exp-name>/`, and creates the lab folder `experiments/<exp-name>/` for the closing record. The two folders have different names on purpose: `notes/` is the experiment's own working memory inside the target repo, and `experiments/` exists only in the lab. Use `--base-branch` when the idea builds on an earlier experiment's code, for example the branch named by `> Branch:` on the system page; the new branch then also carries that experiment's plan and log, which is where to read how its code came to be. The default base is the repo's `default_branch`.

Plan and log live next to the code because they change with it: one commit holds a round's code and what the round taught. Commit them on the experiment branch, starting with the first version of the plan.

`plan.md` describes **how to realise the idea, as far as is known right now**. Write it as exactly as present knowledge allows, and no more exactly than that. On day one it may say little more than "try GRPO on the base model", with a list of what is unknown: which reward, which library, whether it fits the GPU we have. After each round that teaches something, rewrite the plan in place so that it is again the best current description. A reader should be able to open `plan.md` at any moment and see where the experiment stands, without reading the history.

The plan holds:

- **The idea** and why it is worth trying. This part is stable. If it has to be replaced, the experiment is over (see [Conclusions]).
- **What we know and how we will do it**: the realisation, at whatever level of detail is honest today.
- **Open questions**: what the next rounds have to find out.
- **Stopping point**, in free text: what result would be enough, and what would make it not worth continuing (a budget of GPU hours or rounds, a sign that the idea is exhausted). Reaching it does not stop the work mechanically. It is the moment to decide: conclude, or go on with a reason. On a wide request you make that decision and report it; otherwise you bring it to the user.
- **Experiment Language**: the extension point the idea goes into, the shared components it uses, what stays fixed, and anything it adds to the shared set.
- `data_source: <repo>@<ref>:<path>` in the frontmatter, never a local path.

</Write-the-plan>

<Work-in-rounds>

Each round, in the worktree `.targets/worktrees/<exp-name>/` on branch `exp/<exp-name>` (in a new session or a fresh clone, `uv run scripts/lab.py mount-exp --exp <id>` brings the worktree back from the pushed branch):

1. **Implement** the next step of the plan, in the repo's Experiment Language: put the idea in at its extension point, use the shared components as they are, and make a variant a config value, not a copied script. When you need something the shared set lacks (a metric, a view of the data, a plot), write it as a shared component in the shared style, not as a one-off inside the experiment. When a shared component is wrong, fix it there and note it in the plan. Read your diff against the base before committing: it should read as the idea and nothing else. Commit to the experiment branch; remote runners ship committed code only.
2. **Run** it. During rounds you are free to measure however is useful: a short training run, a probe, a notebook, the repo's own checks. The final evaluation script is not required here. `uv run scripts/lab.py run --exp <id> -- '<command>'` runs a command in the worktree with the lab's `.env`, `$LAB_ROOT` and `$EXP_DIR` set. Heavy runs go where `AGENTS.md` says. Running is the expensive part of a round, so get the most out of each run: before starting, write in the log what question the run answers, what you will look at while it runs, and what would make you stop it early. Then watch it while it runs, with the target's own observation tools (system page), and stop a run that has already answered its question or cannot.
3. **Analyze** what came back. Look at cases and traces, not only at the number, and ask why it moved or did not.
4. **Write the round into the experiment log** (`notes/<exp-name>/log.md` in the worktree): what was tried, what was seen, what was decided, and where the run's files are (`notes/<exp-name>/runs/<nn>-<short-name>/`, small files only). A failed round is logged like any other; say whether the failure was technical or a real result.
5. **Update the plan** if the round changed what we know. Commit code, log and plan together and push the branch, so the round survives the session.
6. **Is there something to tell the lab?** ([What-to-tell-the-lab]) Often not yet. Then start the next round.

A long stretch of implement-and-analyze without a conclusion is normal. Check it against the plan's stopping point from time to time so that it does not go on unnoticed.

A long implementation or debugging session is a good piece to hand to a subagent. Give it the relevant part of `plan.md`, the Experiment Language, the data rules, what to hand back, and when to stop and flag.

</Work-in-rounds>

<What-to-tell-the-lab>

An experiment writes in two places, for two different readers.

- **The experiment log, next to the code**, is for whoever continues *this* experiment: you tomorrow, or another agent picking up the branch. It holds everything, including what turned out not to matter: settings, dead ends, debugging, partial numbers, why the plan changed.
- **The lab** (the cortex, the journal, and the postmortem at the end) is for whoever does a *different* experiment and will never open this branch. Their attention is scarce, and every line written there is read by all of them.

Most of what happens in a round stays in the log. The question for each thing you learned is: **would someone working on a different idea do their work differently if they knew this?** If yes, it leaves the log.

| Learned in a round | Where it goes | Why |
|---|---|---|
| The reward parser in this implementation rejects free-text answers | Log only | It is about this experiment's code. |
| Learning rate 2e-5 diverged, 1e-5 is stable for this recipe | Log only | A setting of this idea. It becomes a lab matter only if it says something about the model or the data in general. |
| The patient record contains outcome fields, so any prediction trained on it leaks | Lab: a claim, cited from `findings/`, and the gap map | Every experiment that trains on records is affected. |
| Full fine-tuning of the base model does not fit the lab's GPU above batch 4 | Lab: the system page (environment notes) | Every experiment on this repo will hit it. It is a fact about the system, not a research finding. |
| GRPO did not improve held-out reward in three reward designs | Lab, when the experiment closes: postmortem and Banlist | It decides whether anyone tries it again. One bad round does not say this yet. |
| The run crashed on a missing token | Log only | A technical failure says nothing about the idea. |

Two ways to get this wrong, and both cost the lab. Telling too little: the lesson stays in a branch nobody opens and the next experiment repeats it. Telling too much: the cortex fills with one experiment's details, and the few things that matter to everyone get buried. When unsure, write the lesson in the log now and mark it "candidate for the lab"; decide at the next round, when it is clearer whether it holds.

What is told to the lab is written for a reader who has not seen the experiment: say what was found, on what evidence, and under which conditions, and name the experiment and round so they can go to the branch for more.

</What-to-tell-the-lab>

<Conclusions>

A conclusion is what [What-to-tell-the-lab] selects: something a different experiment should know.

**Interim conclusion.** We learned something that matters and the experiment goes on. Share it now, before the context is gone:

- Write it as a claim in `cortex/claims/` (from `claims/_TEMPLATE.md`): one sentence, `status: provisional`, the anchor `experiment::` with this experiment's name, the round and the commit, and the conditions it was seen under.
- Work it into the `cortex/findings/<topic>.md` page it changes, citing it: `(provisional, [[claims/<claim>]])`. If it disagrees with a claim the lab already holds, write the tension; do not overwrite the older claim.
- If it changes an open gap, update `cortex/gap_map.md`. Update `cortex/index.md` when a page is added.
- Run the cortex check (`cortex/profile.md` §6), and note in the experiment log which claim was written ("Told the lab").

Then go back to the top of the loop.

**Final conclusion.** There is no point trying further: the result was reached, or the idea is exhausted. Close the experiment ([Close-the-experiment]). If what you found is that a different idea is the right one, that is also a final conclusion: close this experiment and write the new idea as a Spark, or open it as a new experiment.

The cortex is only useful while its claims can be trusted. A provisional claim is a promise to come back to it: when the experiment closes, each one becomes `confirmed` or `withdrawn` (with a `withdrawn::` line that names the round and the reason). An older claim that this experiment overturned is not edited: write the new claim and mark the old one `superseded`. Nothing is deleted, and the findings pages are then rewritten freely to say what the lab now knows.

A technical failure (OOM, missing credential, typo) is never a conclusion about the idea.

</Conclusions>

<Close-the-experiment>

1. **Final evaluation**, if the target repo has an `evaluate.py`:
   ```bash
   uv run scripts/lab.py evaluate --exp <id>
   ```
   Compare the metrics with the repo's baseline in `JOURNAL.md` → Current Frontier, and check that both were measured with the same evaluation version (`eval_script_sha` in `results.json`). If the repo has no evaluation yet, the experiment closes with its conclusion and no number; say so in the postmortem.
2. **Write `postmortem.md`** in the lab folder `experiments/<exp-name>/`: the verdict, why things went the way they did (cite rounds from the log), what happened to each provisional claim, and one or two Sparks.
   - `HYPOTHESIS_SUPPORTED`: the idea worked. The result improved, or it held equal within noise while the code or prompt got simpler (Simplicity Criterion, `cortex/purpose.md`).
   - `HYPOTHESIS_REFUTED`: the idea ran cleanly and did not work. Add it to the Anti-Repeat Banlist as `[pattern] -> [why it failed] -> [unless condition X changes]`.
   - `INFRA_INCONCLUSIVE`: a technical blocker prevented a real test. Nothing goes to findings or the Banlist.
3. **Record it**:
   ```bash
   uv run scripts/lab.py record-verdict --exp <id> --verdict <VERDICT> --metric-delta "<delta or 'no metric'>" --summary "<one-line lesson>"
   ```
   This adds the row to the experiment matrix and a line to `cortex/log.md`. By hand: copy the Sparks into `JOURNAL.md` → Active Sparks, and update Current Frontier if this is a new best number, with the evaluation version beside it.
4. **Settle the cortex**: `uv run .agents/skills/cortex/scripts/cortex.py claims --from <exp-name> --status provisional` lists what this experiment still owes. Confirm or withdraw each claim, revise the findings pages that cited a withdrawn one (`cortex.py links claims/<claim>` shows them), update `gap_map.md` and `index.md`, and run the cortex check. Then the Experiment Language: if the experiment is kept and it added a shared component, fixed one, or changed the frame, update the system page (components table, extension points, vocabulary) and point the page at the branch (`> Branch: exp/<exp-name>`, `Fingerprint: git:<sha>`), so the next experiment starts from it. If it left the language as it was, say so in the postmortem.
5. **Push the branch**, whatever the verdict, with the final plan and log on it, and do not merge it:
   ```bash
   git -C .targets/repos/<repo> push -u origin exp/<exp-name>
   ```
6. Optionally `uv run scripts/lab.py cleanup-worktree --exp <id>`. The branch and the experiment folder stay.

After closing, the lab folder does not change, except for a re-evaluation added to `results.json` ([Evaluation-API]).

</Close-the-experiment>

<Evaluation-API>

The one thing the tools enforce is that every final evaluation of a target repo is run the same way:

- The script is **`evaluate.py` at the root of the target repo**. It is part of the repo's code and travels with the experiment branch.
- `lab.py evaluate` runs `uv run evaluate.py` in the experiment's worktree, with no arguments. The script reads what it needs from the environment: `$EXP_DIR` (this experiment's folder, for outputs), `$LAB_ROOT`, and the lab's `.env` variables (names in `.env.example`).
- **The last line of stdout is one JSON object of metrics.** Progress goes to stderr or to earlier lines. Exit code 0 means the evaluation ran.
- When the script calls an external benchmark, it adds that benchmark's name and version to the JSON as `"eval_version"`.

`lab.py evaluate` saves the full output to `evaluate.log`, the metrics, the commit and the git hash of `evaluate.py` (`eval_script_sha`) to `results.json`, and the branch's diff to `patch.diff`. It exits non-zero when the script is missing, fails, times out or prints no JSON line, and then writes no metrics.

Nothing protects the evaluation code; it is often external anyway. What keeps numbers honest is the recorded version: two results are comparable only when their `eval_script_sha` (and `eval_version`) match.

**When the evaluation changes, the experiments are measured again.** `evaluate.py` lives on experiment branches, so a change made in one experiment does not reach the others by itself. Say in the log and the postmortem that the evaluation changed, then re-run it on every experiment whose number is still being compared (at least the Frontier's):

```bash
uv run scripts/lab.py mount-exp --exp <older-id>          # if its worktree was cleaned up
uv run scripts/lab.py evaluate --exp <older-id> --eval-from exp/<exp-with-the-new-evaluation>
```

`--eval-from` runs that branch's `evaluate.py` on the older experiment's code without committing it there. The earlier measurement is kept in `results.json` under `earlier_evaluations`. Update Current Frontier with the new numbers and version. If the new script needs code the older branch does not have, the run fails; say so in the journal, and do not compare that experiment's old number with new ones.

Building or changing the evaluation of a repo is itself an experiment.

</Evaluation-API>

<Commands>

All commands run from the lab root as `uv run scripts/lab.py <command>`.

| Command | Does | Does not |
|---|---|---|
| `sync-repos [--repo <name>]` | Clones or fetches the repos in `repos.yaml` into `.targets/repos/` | |
| `context-pack` | Compiles `cortex/query_pack.md` | Choose a direction |
| `check-drift` | Reports system pages whose monitored code changed since their `Fingerprint` | Update any page |
| `new-exp --repo <r> --name <n> [--base-branch <b>] [--title <t>] [--id <hh>]` | Creates the branch and worktree with `notes/<exp-name>/{plan.md, log.md}` in it, the lab folder `experiments/<exp-name>/`, and copies the lab's skills into the worktree | Fill the plan, commit |
| `mount-exp --exp <id>` | Re-creates the worktree of an existing experiment from its branch | |
| `run --exp <id> -- '<command>'` | Runs a round's command in the worktree with `.env`, `$LAB_ROOT` and `$EXP_DIR` set; output is shown as it comes | Record anything |
| `evaluate --exp <id> [--eval-from <branch>] [--timeout <sec>]` | Runs the target's `evaluate.py`; writes `evaluate.log`, `results.json`, `patch.diff` (the diff is saved even when the repo has no evaluation yet) | Check scopes, run tests, compare with the baseline |
| `record-verdict --exp <id> --verdict <V> --metric-delta "<d>" --summary "<s>"` | Sets the verdict in `results.json`, adds the matrix row and a log line | Update Frontier, Sparks or the Banlist |
| `cleanup-worktree --exp <id>` | Removes the worktree | Delete the branch or the experiment folder |

The experiment log, the plan, the cortex and the journal's Frontier, Sparks and Banlist are edited by hand. They carry judgment, so no command writes them.

</Commands>

<Example>

A request: "try reinforcement-learning fine-tuning on the base model and see if it gets anywhere."

1. **Direction.** `context-pack`, then read the gap map and the target's system page. The lab has a Spark asking for a leak-free prediction task; an RL objective needs a reward, and the reward needs that task. The cortex also holds a `quote` claim from a paper: GRPO converged faster than PPO there and collapsed in reward after many steps. Nobody in the lab has seen that, so it goes into the plan as something to watch for, not as a known fact. Two alternatives are noted and dropped (supervised answer-token loss only; a tabular baseline first), and kept as Sparks.
2. **Plan.** `new-exp --repo model-repo --name rl/grpo --base-branch exp/01-model-init/pipeline` creates `02-model-rl/grpo`; the branch carries experiment 01's code. Day-one plan, committed on the branch: the idea (GRPO on the base model), what is known (the frame from experiment 01, the GPU's memory limit), open questions (reward definition, group size, library or plain PyTorch), stopping point ("enough: a reward curve that rises on held-out patients. Not worth more: three reward designs with no movement, or about 10 GPU hours").
3. **Round 1.** Implement a reward from the 24-month outcome, run 50 steps. Reward is flat. Analysis shows the model answers in free text the reward parser rejects. Log the round; update the plan: constrain the answer format. This is about this experiment's code, so nothing is told to the lab.
4. **Round 2.** Reward rises on train and not on held-out patients. Analysis: the record still contains outcome fields. Every experiment that trains on records is affected, so this leaves the log as an **interim conclusion**: a provisional claim in `cortex/claims/`, anchored to this experiment, round 2 and its commit, cited from the `findings/` page on training data; gap map updated. Plan rewritten: render only fields known at prediction time.
5. **Rounds 3-5.** Held-out reward now rises slowly. The stopping point's budget is reached; the decision to continue for two more rounds, and why, goes into the log.
6. **Final conclusion.** The result is reached. `evaluate` runs the repo's `evaluate.py`; the metrics are compared with the Frontier baseline measured at the same `eval_script_sha`. Postmortem, `record-verdict`, Sparks and Frontier updated, the provisional leakage claim confirmed, branch pushed.

Had round 2 shown that GRPO cannot work on this model at all, the experiment would have closed there as `HYPOTHESIS_REFUTED`, with "try PPO" as a Spark for a new experiment.

</Example>
