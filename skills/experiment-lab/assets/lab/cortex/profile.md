# Cortex Profile (`profile.md`)

> What this cortex is: the lab's memory. Read it before writing anything under `cortex/`. The operations (add, investigate, ask, review) and the forms of a claim and a page are in the `cortex` skill. Where this file and the skill differ on a name or a place, this file wins.

## 1. What the Synthesis Is For

Choosing and doing the next experiment. The reader comes here with an idea, or looking for one, and has not seen the experiments that came before. What the lab is for and how results are judged: `purpose.md`.

The test for writing anything here is the experiment loop's: **would someone working on a different idea do their work differently if they knew this?** (`experiment-lab-loop` → What-to-tell-the-lab explains the judgment.) Most of what a round teaches fails that test and stays in the experiment's log. A source from outside is held to the same test: a claim is written because it bears on a gap, a Spark or a choice of direction, not because the paper says it.

## 2. Layout

| Layer | Where | Holds |
|---|---|---|
| Sources | `experiments/<exp-name>/` and the experiment's branch | What the lab did. This is what an `experiment` anchor points at. |
| | `cortex/sources/<source-id>.md`, `cortex/sources/text/` | What was read from outside: the note, and the text that was actually read |
| Claims | `cortex/claims/` | One claim per file |
| Synthesis | `cortex/findings/<topic>.md` | What the lab knows about a topic, citing claims |
| | `cortex/tensions/` | Two claims that disagree, and what would settle it |
| | `cortex/gap_map.md` | The open questions, one row each |
| | `JOURNAL.md` (lab root) | Frontier, Sparks, Banlist |
| | `cortex/systems/<repo>.md` | A target's Experiment Language. Anchored to the code (`anchor: code`, `Fingerprint`), not to claims. |
| Map | `cortex/index.md`, `cortex/log.md` | One line per page; one line per operation |

Templates: `claims/_TEMPLATE.md`, `findings/_TEMPLATE.md`, `sources/_TEMPLATE.md`, `systems/_TEMPLATE.md`. A tension uses the skill's template.

## 3. Anchors

| Anchor | What it earns in this lab |
|---|---|
| `experiment` | **The lab saw it.** Names the experiment, the round and the commit. Its Conditions name the model, the data and split, and the evaluation version, so a reader can tell whether it applies to their experiment. |
| `quote` | **Someone else reports it.** For this lab it is a hypothesis until an experiment tests it. It can open a gap or a Spark and shape a plan. It cannot put an idea on the Banlist or a number on the Frontier. |
| `stated` | **The user said it.** For facts about the data, the environment or the goal that nothing else records. |

A findings page says which kind it rests on (the first line of its template). "The literature reports" and "we found" are different sentences here.

## 4. Status

- `provisional`: an `experiment` claim while its experiment is open; a `quote` claim until an experiment of ours tests it or a second, independent source reports the same.
- `confirmed`: the experiment closed and its postmortem confirms the claim.
- `withdrawn`: the experiment closed and the claim did not hold, or a later experiment showed it was an artifact. The `withdrawn::` line says after which experiment and round, and why.
- `superseded`: a later claim says it more exactly or under corrected conditions.

A technical failure (crash, out-of-memory, missing credential) produces no claim at all.

## 5. Moments

Fusion here is driven by the experiment loop, not by a schedule.

| Moment in the loop | What happens in the cortex |
|---|---|
| Finding a direction | Read (`ask`): findings, tensions, the gap map, the Banlist. Reading from outside to answer a gap is `investigate`: it starts from the gap's row and ends by updating that row. |
| A round ends with something to tell the lab | Write the claim (`provisional`, `experiment` anchor), then work it into the findings page it changes, citing it. If it disagrees with a claim the lab holds, write the tension. Update the gap it touches. |
| The experiment closes | List its open claims and settle each one, `confirmed` or `withdrawn`. Revise the pages that cited a withdrawn claim. |
| From time to time, and before a wide request that will choose a direction | `review`, with the additions in section 7. |

A source added with no question behind it yields claims and tensions only. A findings page is built when a gap or an experiment needs one.

## 6. Checking

From the lab root, before every commit that touches `cortex/`:

```bash
uv run .agents/skills/cortex/scripts/cortex.py check --also experiments
uv run .agents/skills/cortex/scripts/cortex.py claims --from <exp-name> --status provisional   # what a closing experiment still owes
uv run .agents/skills/cortex/scripts/cortex.py links claims/<claim>                            # what rests on a claim
```

Blind verification (a fresh agent sees only the sentence and its evidence): for every `quote` claim, when it is added. An `experiment` claim is checked by the experiment itself, at close.

## 7. Review, in This Lab

In addition to the skill's checklist. Mechanical state first:

```bash
uv run scripts/lab.py sync-repos     # so system pages can be compared with the code
uv run scripts/lab.py check-drift    # system pages whose monitored code changed
```

Read, besides `cortex/`: `JOURNAL.md`, and every `experiments/*/postmortem.md` and `results.json`. Then check:

- **Closed experiments.** Every experiment in the journal's matrix has no `provisional` claim left, and the pages its postmortem says it changed show it.
- **Numbers.** Frontier numbers match `results.json`, and numbers that are compared were measured with the same `eval_script_sha`.
- **Basis.** No findings page presents as seen by the lab something that rests only on `quote` claims. No Banlist entry rests on a `quote` claim or on a technical failure.
- **Gaps.** A gap listed as open that an experiment has answered; a question an experiment revealed that is on no list.
- **Sparks and Banlist.** A Spark already done or made pointless; a Banlist entry whose "unless" condition has since changed.
- **System pages.** Read the diff `check-drift` points at and see what on the page is no longer so.
- **One experiment's detail.** Settings and debugging of a single experiment in a findings page. They belong in that experiment's log.

Experiment folders are evidence: do not edit them. To check a claim against its experiment, read the postmortem; the plan and the log are in `notes/<exp-name>/` on the experiment's branch (`uv run scripts/lab.py mount-exp --exp <id>`). Append one line to `cortex/log.md`: `## [YYYY-MM-DD HH:MM] review | cortex — <what was fixed, how many items reported>`.
