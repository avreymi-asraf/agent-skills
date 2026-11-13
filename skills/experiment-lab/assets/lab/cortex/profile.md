# Cortex Profile (`profile.md`)

> What this cortex is: the lab's knowledge base of its field. Read it before writing anything under `cortex/`. The operations (add, investigate, ask, review) and the forms of a claim and a page are in the `cortex` skill. Where this file and the skill differ on a name or a place, this file wins.

## 1. What the Cortex Is For

Knowing the field of the research as widely as the lab can, so that the research advances. The cortex is the most comprehensive collection the lab can build of what is known about its field (`purpose.md` §1 names it): methods, results, data, tools, background, neighbouring fields, and what the lab's own experiments showed. Most of it comes from outside the lab, and that is how it should be. The lab's experiments are one kind of source among the others; a claim from an experiment is not more important than a claim from a paper. The anchor of a claim says where it comes from and how it can be checked (§3), never how much it matters.

The reader comes with any question about the field: looking for a direction, planning an experiment, stuck in a round, or wanting to understand a topic. They may never have seen an experiment of this lab.

The cortex is not the journal. `JOURNAL.md` is the path of the research: which directions the lab took, from which earlier work, what each concluded, what is best now and what is next. It grows like a tree, in the direction of the research, and holds only what the lab did and decided. The cortex has no direction: it is organised by topic and it grows in every direction the field has.

What is worth writing, by where it comes from:

- **From outside:** anything about the field that could inform the research, now or later. No gap, Spark or experiment has to ask for it first. Write the claims that carry what the source establishes, not one per sentence.
- **From an experiment:** what holds beyond that experiment. The test is the loop's: **would someone working on a different idea do their work differently if they knew this?** (`experiment-lab-loop` → What-to-tell-the-lab.) Most of what a round teaches is about that try's own code and settings; it stays in the try's log.

## 2. Layout

The cortex is the `cortex/` folder. One of its layers also reaches outside it: the lab's experiments are one of its sources. Where the `cortex` skill says *page*, read a findings page here; where it says *question*, read a row of `gap_map.md`.

| Layer | Where | Holds |
|---|---|---|
| Sources | `cortex/sources/<source-id>.md`, `cortex/sources/text/` | What was read from outside, of any kind (paper, article, documentation, dataset, code, talk, conversation): the note, and the text that was actually read, stored by `cortex.py store` as it was fetched. The original stays where it was published (the note's `location`); a file that exists nowhere else goes to `cortex/sources/raw/`. A source whose text could not be obtained is a note with `read: not obtained`: a lead, with no claims. |
| | `experiments/<repo short name>/<experiment name>/` (with its try records) and the experiment's try branches | What the lab did. This is what an `experiment` anchor points at. |
| Claims | `cortex/claims/` | One claim per file |
| Synthesis | `cortex/findings/<topic>.md` | What is known about a topic, citing claims of every anchor |
| | `cortex/tensions/` | Two claims that disagree, and what would settle it |
| | `cortex/gap_map.md` | The open questions, one row each |
| | `cortex/systems/<repo>.md` | An experiment repo's system page: what it is for, the kept try branch, data and environment notes, and a pointer to `EXPERIMENT_LANGUAGE.md` on that branch. Anchored to the code (`anchor: code`, `Fingerprint`), not to claims. |
| Map | `cortex/index.md`, `cortex/log.md` | `index.md`: one line per page, kept by hand. `log.md`: appended by `lab.py` when an experiment is opened, evaluated or closed, and by a review. |

Templates: `claims/_TEMPLATE.md`, `findings/_TEMPLATE.md`, `sources/_TEMPLATE.md`, `systems/_TEMPLATE.md`. A tension uses the skill's template.

## 3. Anchors

| Anchor | Where the claim comes from, and how it can be checked |
|---|---|
| `experiment` | **The lab saw it.** Checked by re-running. Names the experiment, the try, the round and the commit. Its Conditions name the model, the data and split, and the evaluation version, so a reader can tell whether it applies to their experiment. |
| `quote` | **A source reports it.** Checked against the source's stored text. Its Conditions are the source's own setting. It is knowledge like any other claim: it answers questions, fills a findings page, opens a gap or a Spark, shapes a plan. |
| `stated` | **The user said it.** For facts about the data, the environment or the goal that nothing else records. |

The kinds are not ranks. A result reported by a careful outside study on much data can deserve more trust than one round of ours; what decides is the evidence and the conditions, and whether they match the reader's case. The kinds are kept apart so that a reader can tell where a sentence comes from: a findings page says which kinds it rests on (the first line of its template), and "the literature reports" and "we found" are different sentences here.

One place takes only what the lab did: the journal. A number on the Frontier and an entry on the Banlist are records of the lab's own path, so each rests on an `experiment` claim.

## 4. Status and Corrections

How a claim may be corrected depends on whether it has been checked. This is the rule for every claim in the lab:

- **At its blind verification** (a `quote` claim, §6) it is still a draft, and nothing has been concluded from it yet. A `partial` is narrowed in place to what the stored text carries and verified again; a `fail` is deleted. Whoever does it corrects the pages that cite it in the same commit (`cortex.py links`).
- **After it passes**, and from the start for an `experiment` or `stated` claim (an interim conclusion is acted on by other experiments as soon as it is written), its sentence, evidence and conditions do not change and it is not deleted, even when a later experiment, source or re-check contradicts it: what the lab once believed, and why it stopped, is part of the record. It changes status instead, as below.

`verified` is never set by the claim's writer. A `quote` claim gets it from a blind verifier. An `experiment` claim gets it from its experiment's close, which is its check.

An `experiment` claim:

- `provisional` while its experiment is open.
- `confirmed` when the experiment closes and its postmortem confirms it, with `verified: pass`.
- `withdrawn` when it did not hold: at close, or when a later experiment shows it was an error or an artifact. The `withdrawn::` line names the experiment and round, and says why.
- `superseded` when a later claim says the same thing more exactly or under corrected conditions (`superseded_by::`).

A `quote` claim is `provisional` until a second, independent source reports the same; then `confirmed` means "well reported", and its anchor still says it comes from a source. An experiment of ours never changes the status of a `quote` claim, because the source still says what it says. The experiment writes its own claim, with `supports::` or `contradicts::` pointing at the quoted one, and a contradiction gets a tension: what held there, what held here, and the difference in conditions.

When a new result disagrees with an older `experiment` claim and it is not yet clear which holds: a tension, and both claims stay. Once it is clear, the loser is withdrawn or superseded as above.

A technical failure (crash, out-of-memory, missing credential) produces no claim at all.

## 5. Moments

The cortex is written at any time, by its own operations, and at fixed moments of the experiment loop.

| Moment | What happens in the cortex |
|---|---|
| Any time: something about the field was read, found or handed over by the user | `add`: the source, its claims, and the findings pages they change. No gap or experiment has to ask for it. Gathering knowledge about the field is work of the lab in its own right. |
| A topic has claims and no page, or a page no longer says what its claims say | Write or rewrite the findings page. |
| Finding a direction | Read (`ask`): findings, tensions, the gap map; and the journal for the path so far. Reading from outside to answer a gap is `investigate`: it starts from the gap's row and ends by updating that row. Reading widely around the idea, with no gap behind it, is `add`. |
| A round ends with something to tell the lab | The try writes a note to the lab in its log and nothing in the cortex. |
| A lab step on a try | For each `lesson` note: write the claim (`provisional`, `experiment` anchor), then work it into the findings page it changes, citing it. If it disagrees with a claim the lab holds, write the tension. Update the gap it touches. A `source` note is an `add`; a `correction` is settled as section 4 says; a `question` is an `ask`, then an `investigate`. |
| The experiment closes | List its open claims and settle each one, `confirmed` or `withdrawn`. Revise the pages that cited a withdrawn claim, and drop "provisional" from the citations of confirmed ones. If the idea ran cleanly, its final conclusion is written as a claim too: it is what a findings page and a Banlist entry cite. |
| From time to time, and before a wide request that will choose a direction | `review`, with the additions in section 7. |

A findings page is built as soon as a topic has enough claims to say something, whichever sources they come from. It does not wait for a gap or an experiment.

## 6. Checking

From the lab root, before every commit that touches `cortex/`:

```bash
uv run .agents/skills/cortex/scripts/cortex.py check --also experiments
uv run .agents/skills/cortex/scripts/cortex.py claims --from <exp-name> --status provisional   # what a closing experiment still owes
uv run .agents/skills/cortex/scripts/cortex.py links claims/<claim>                            # what rests on a claim
```

Blind verification: for every `quote` claim, when it is added: `/cortex verify`, which says who starts it when the agent that wrote the claims cannot. Until then the claim is `verified: unchecked`, and `check` prints how many claims wait. An `experiment` claim is checked by the experiment itself, at close (§4).

## 7. Review, in This Lab

In addition to the skill's checklist. Mechanical state first:

```bash
uv run scripts/lab.py sync-repos     # so system pages can be compared with the code
uv run scripts/lab.py check-drift    # system pages whose monitored code changed
```

Read, besides `cortex/`: `JOURNAL.md`, and every `experiments/<repo short name>/<experiment name>/postmortem.md` and `results.json`. Then check:

- **Closed experiments.** Every closed experiment (a row with a verdict in the journal's matrix) has no `provisional` claim left, and the pages its postmortem says it changed show it.
- **Numbers.** Frontier numbers match `results.json`, and numbers that are compared were measured with the same `evaluation_version`.
- **Breadth.** Topics of the field (`purpose.md` §1) on which the cortex holds nothing, or only what the lab's own experiments showed. List them as gaps or as reading to do.
- **Basis.** No findings page presents as seen by the lab something that rests only on `quote` claims. Every Banlist entry names the `experiment` claim it rests on; none rests on a `quote` claim or on a technical failure.
- **Gaps.** A gap listed as open that an experiment has answered; a question an experiment revealed that is on no list.
- **Sparks and Banlist.** A Spark already done or made pointless; a Banlist entry whose "unless" condition has since changed.
- **System pages.** Read the diff `check-drift` points at and see what on the page is no longer so.
- **One experiment's detail.** Settings and debugging of a single experiment in a findings page. They belong in that experiment's log.

Experiment folders are evidence: do not edit them. To check a claim against its experiment, read the postmortem; the try records are in its lab folder, and the plan and the log are in `notes/<experiment name>/` on the try branch the claim names (`uv run scripts/lab.py mount --exp <id> --try <try name>`). Append one line to `cortex/log.md`: `## [YYYY-MM-DD HH:MM] review | cortex — <what was fixed, how many items reported>`.
