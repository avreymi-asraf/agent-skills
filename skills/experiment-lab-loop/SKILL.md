---
name: experiment-lab-loop
description: Run a disciplined, compounding experimentation loop (Evaluate -> Plan -> Implement -> Distill) from a dedicated control repository that keeps a research wiki, a lab journal, and per-experiment evidence folders while running each experiment in an isolated git worktree of an external target repository. Use whenever the user asks to plan, run, evaluate, document, or distill experiments, update the research wiki or lab journal, check wiki pages for code drift, or iterate on an external codebase with hypothesis-driven changes (ML, NLP, agents, or any measurable software).
---
# Experiment Lab Loop

Run hypothesis-driven experiments across external codebases without polluting them, and without losing lessons between sessions. A separate **control repository** (the lab) holds the memory; the target code is only touched inside throwaway worktrees.

## When to Use

- Setting up or operating a lab repository that experiments on other repositories.
- Reading accumulated knowledge to pick the next high-leverage experiment.
- Implementing one atomic hypothesis in an isolated worktree and gating it with a regression check and a metric check.
- Distilling an outcome into a postmortem, journal entry, and wiki update.

Not for a one-off tweak with no baseline or metric; just make the change.

## Layout of the Lab Repository

Adapt names to the repo, but keep the three layers separate.

| Layer | Location | Role |
|---|---|---|
| Evidence (immutable) | `experiments/<exp-name>/` | `plan.md`, `execution.md`, `results.json`, `patch.diff`, `postmortem.md`. Never rewrite past results. |
| Episodic / routing | `JOURNAL.md` | Current frontier (best verified baseline per target), active Sparks queue, experiment matrix, Anti-Repeat Banlist. |
| Semantic (compiled) | `wiki-llm/` | `index.md`, `purpose.md`, `gap_map.md`, `systems/`, `findings/`, `literature/`, `log.md`. Compile lessons into existing pages, not raw logs. Build and maintain it with the `wiki-llm` skill. |
| Sandboxes (git-ignored) | `.targets/repos/<repo>`, `.targets/worktrees/<exp-name>/` | Base clones and per-experiment worktrees. |

- `wiki-llm/systems/<repo>.md` describes a target: `> Repo: <name> | Fingerprint: git:<sha>`, monitored paths, and an **Experiment Language** section (see below).
- `findings/` pages mark overturned claims `Status: Superseded by [[<exp-name>]]`; never delete history.
- Experiment names: `<id>-<repo-short>-<worktree-name>` (for example `0a-api-rl/grpo`): a unique short id, the target's short name, and 1-3 short `/`-separated levels from broad to specific. The same name is used for the evidence folder, the worktree, and the branch `exp/<exp-name>`.

A small lab CLI (for example `scripts/lab.py`) is worth having for the mechanical steps: create an experiment (folder + worktree + branch), check drift, build a context pack, evaluate (scope check, guard, verify, patch, results), record a verdict, and clean up a worktree. The commands below use that shape; if the lab has no CLI, do the same steps by hand with git.

## Invariants

1. **Never edit the base clone.** Every experiment runs in its own worktree on branch `exp/<exp-name>`. One experiment = one branch + one worktree.
2. **Do not merge experiment branches** into the target's default branch unless the user explicitly asks. Push every experiment branch to the target's `origin` so evidence survives a fresh clone. A follow-up that builds on an earlier experiment branches from it (`--base-branch exp/<earlier-exp-name>`, recorded in `plan.md`).
3. **Two mechanical checks per experiment:** a `guard_cmd` (regression suite that must stay green) and a `verify_cmd` (benchmark or metric script that prints JSON). Never modify files in `forbidden_scope` (evaluation scripts, benchmark data, tests) to move a metric.
4. **Capture hygiene.** Separate infrastructure failures (`INFRA_INCONCLUSIVE`: OOM, missing credentials, typo) from scientific refutations (`HYPOTHESIS_REFUTED`). Never record an infra crash as a failed idea in `findings/` or the banlist; only a clean run can refute.
5. **Shared experiment language.** Every experiment on a target uses the same concepts, vocabulary, file layout, and flow as the ones before it, so a metric delta is attributable to the idea and a reader of experiment `0a` understands `0b` at a glance. The canonical frame lives in the `Experiment Language` section of the system page. Change the frame only when that change *is* the hypothesis; say so in `plan.md`, and update the section if the change is kept.
6. **Portable.** No absolute or machine-specific paths in docs, plans, configs, or the wiki. Use repo-relative paths and variables the evaluate step provides (for example `$LAB_ROOT`, `$EXP_DIR`, plus data locations from `.env`). Declare data in `plan.md` as `data_source: <repo>@<ref>:<path>`, not a local path. Secrets come from environment variables named in `.env.example`, never from git, logs, results, or the wiki.
7. **Protect the orchestrator's context.** Reserve it for choosing hypotheses, reviewing evidence, and deciding verdicts. Delegate bulk work (source gathering, implementation, long evaluations, wiki ingestion) to subagents with a narrow written brief, then review their output instead of redoing it.

## The Loop

### 1. Evaluate and orient (architect)

1. Check drift and build the context pack:
   ```bash
   lab check-drift
   lab context-pack
   ```
2. For any system page flagged `DRIFTED`, inspect the diff in the base clone, update the page, and bump its fingerprint.
3. Read the pack (purpose, gap map, journal), then the specific findings and system pages tied to the current bottleneck.

### 2. Ideate and plan (architect)

This step decides whether the research is any good; spend real effort here.

1. Use the `iterative-deep-researcher` skill on the target gap: gather, read, think, update. Look for prior art and adjacent fields, ask *why* the bottleneck exists, and keep **at least 3 competing hypotheses** alive (one contrarian) before committing. Delegate source gathering; save notes to `wiki-llm/literature/`.
2. Pick one testable hypothesis tied to an open gap or a high-priority Spark. Record the rejected alternatives in `plan.md`; they are future Sparks.
3. Check the Anti-Repeat Banlist, and confirm the idea fits the target's Experiment Language.
4. Scaffold: `lab new-exp --repo <target> --name <worktree-name> [--base-branch exp/<earlier>]`.
5. Complete `plan.md` so it works as a self-contained brief for an implementation subagent: hypothesis and linked gap, `editable_scope`, `forbidden_scope`, `guard_cmd`, `verify_cmd`, `data_source`, expected metric direction, falsification criteria, and the experiment-language statement. In human-in-the-loop mode, pause here for approval.

### 3. Implement and verify (technician)

1. Work only from `plan.md` inside the worktree. Prefer an implementation subagent; the orchestrator reviews the diff and `results.json`.
2. If no baseline exists for the base commit, run `lab evaluate --exp <id> --baseline` first.
3. Make the smallest atomic change, in the established experiment language, and commit it to the experiment branch.
4. Run `lab evaluate --exp <id>`: it checks scope, runs guard and verify, saves `patch.diff`, and writes `results.json`.
5. On a setup or syntax failure, fix and retry up to 3 times before declaring `INFRA_INCONCLUSIVE`.

### 4. Distill and compound (wiki maintainer)

1. Write `postmortem.md` with a verdict:
   - `HYPOTHESIS_SUPPORTED`: guard passed and the metric improved, or held within noise while the code got simpler.
   - `HYPOTHESIS_REFUTED`: clean run, guard passed, metric did not improve, nothing got simpler.
   - `INFRA_INCONCLUSIVE`: a blocker prevented a valid test.
   Explain *why* the metric moved or did not, citing concrete cases or traces, and add the mandatory **Spark** section with 1-2 concrete follow-up hypotheses while context is fresh.
2. Record the verdict: `lab record-verdict --exp <id> --verdict <VERDICT> --metric-delta "<delta>" --summary "<one-line lesson>"`. Update the frontier if there is a new best, add refuted patterns (with their boundary conditions) to the banlist, and copy the Sparks into the queue.
3. Update `wiki-llm/`: weave the lesson into the right `findings/` page, update `gap_map.md` and `index.md`, append to `log.md`. Delegate to a wiki-maintainer subagent with `postmortem.md` and `results.json`, then review its edits.
4. Push the branch for every verdict: `git -C .targets/repos/<repo> push -u origin exp/<exp-name>`. A kept branch becomes the base for follow-ups; if it changed the frame, point the system page at it (`> Branch: exp/<exp-name>`, new fingerprint).
5. Optionally remove the worktree (the branch and evidence stay): `lab cleanup-worktree --exp <id>`.

## Gotchas

- **Self-poisoning:** logging an infra crash as a refutation bans a good idea forever.
- **Reward hacking:** touching evaluation code or labels to raise a metric invalidates the experiment.
- **Simplicity bias:** 150 lines of complexity for a gain within noise is a discard; record the trade-off.
- **Language drift:** renaming concepts or swapping frameworks makes results incomparable.
- **Shallow ideation:** jumping to the most obvious tweak yields redundant experiments.
- **Context exhaustion:** an orchestrator that gathers, codes, and edits the wiki itself loses the overview it needs to judge results.

## Companions

`wiki-llm` (build and maintain the semantic layer), `iterative-deep-researcher` (ideation), `code-as-tools` and `notebook-observability` (experiment code and inspection), `colab-cli` (run on Colab GPUs), `testing` (keep guard suites small and meaningful).
