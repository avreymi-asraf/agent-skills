# Cortex Profile (`profile.md`)

> What this cortex is: the lab's knowledge base of its field. Read it before writing anything under `cortex/`. The operations (`add`, `investigate`, `ask`, `verify`, `review`) and the forms of a claim and a page are in the `cortex` skill. Where this file and the skill differ on a name or a place, this file wins.

## 1. What the Cortex Is For

**Knowing the field of the research as widely as the lab can, so that the research advances.** The cortex is the most comprehensive collection the lab can build of what is known about its field (`purpose.md` §1 names the field). It is a general knowledge base. It is not the record of the lab's experiments.

What it gathers, from any source:

- methods and how they work; results others report, with the conditions they were obtained under;
- data: which datasets exist, what is in them, their limits, licenses and known flaws;
- tools, libraries, benchmarks and evaluation practice;
- background that the field takes for granted, and neighbouring fields a good idea may come from;
- disagreements between sources, and questions nobody has answered;
- and what the lab's own experiments showed.

The last item is one among the others. Most of the cortex comes from outside the lab, and that is how it should be: almost everything known about a field was found by someone else. A claim from an experiment of ours is not more important than a claim from a paper. The anchor of a claim says where it comes from and how it can be checked (§3), never how much it matters.

**The reader** comes with any question about the field: looking for a direction, planning an experiment, stuck in a round, or simply needing to understand a topic. They may never have seen an experiment of this lab.

**The cortex is not the journal.** `JOURNAL.md` is the path of the research: which directions the lab took, from which earlier work, what each concluded, what is best now and what is next. It grows like a tree, in the direction of the research, and holds only what the lab did and decided. The cortex has no direction. It is organised by topic and it grows wherever the field has something to know.

**What is worth writing**, by where it comes from:

- **From outside:** anything about the field that could inform the research, now or later. No gap, Spark or experiment has to ask for it first. Store the source, then write the claims that carry what it establishes (not one per sentence). When in doubt, add it: a source that is stored and noted can be found again; one that was only read is lost.
- **From an experiment:** what holds beyond that experiment. The test is the loop's: **would someone working on a different idea do their work differently if they knew this?** (`experiment-lab-loop` → What-to-tell-the-lab.) Most of what a round teaches is about that try's own code and settings, and stays in the try's log.

## 2. Layout

The cortex is the `cortex/` folder. Where the `cortex` skill says *page*, read a topic page here; where it says *question*, read a row of `gap_map.md`.

| Layer | Where | Holds |
|---|---|---|
| Sources | `cortex/sources/<source-id>.md`, `cortex/sources/text/` | What was read, of any kind: paper, article, documentation, dataset description, code, talk, discussion, a note from the user. The note, and the text that was actually read, stored by `cortex.py store` as it was fetched. The original stays where it was published (the note's `location`); a file that exists nowhere else goes to `cortex/sources/raw/`. A source whose text could not be obtained is a note with `read: not obtained`: a lead, with no claims. |
| | `experiments/<repo short name>/<experiment name>/` and the experiment's try branches | The lab's own experiments, as one more kind of source. This is what an `experiment` anchor points at. |
| Claims | `cortex/claims/` | One claim per file: one sentence, its evidence, its conditions |
| Synthesis | `cortex/topics/<topic>.md` | A **topic page**: what is known about one topic of the field, citing claims of every anchor. Its `kind` says what sort of topic it is (concept, method, result, dataset, tool, comparison, background). |
| | `cortex/tensions/` | Two claims that disagree, and what would settle it |
| | `cortex/gap_map.md` | What the cortex should know and does not, one row each |
| Map | `cortex/index.md` | The map of the field: its areas, and under each the topic pages. An area with nothing under it shows where the cortex is thin. Kept by hand, in the same commit as the page. |
| | `cortex/log.md` | One line per operation on the cortex, and per experiment opened, evaluated or closed |
| Beside the knowledge | `cortex/purpose.md`, `cortex/systems/<repo>.md` | What the lab is for; and one system page per experiment repo (its Experiment Language, anchored to the code). They live here so that everything a reader needs is in one place; they are about the lab, not about the field. |

Templates: `sources/_TEMPLATE.md`, `claims/_TEMPLATE.md`, `topics/_TEMPLATE.md`, `systems/_TEMPLATE.md`. A tension uses the skill's template.

## 3. Anchors

| Anchor | Where the claim comes from, and how it can be checked |
|---|---|
| `quote` | **A source reports it.** Checked against the source's stored text. Its Conditions are the source's own setting. |
| `experiment` | **The lab saw it.** Checked by re-running. Names the experiment, the try, the round and the commit. Its Conditions name the model, the data and split, and the evaluation version. |
| `stated` | **The user said it.** For facts about the data, the environment or the goal that nothing else records. |

**The kinds are not ranks.** Every claim is knowledge and is used the same way: it answers questions, fills a topic page, opens a gap or a Spark, shapes a plan. A result reported by a careful study on much data can deserve more trust than one round of ours; what decides is the evidence and the conditions, and whether they match the reader's case. The kinds are kept apart only so that a reader can tell where a sentence comes from: a topic page says which kinds it rests on, and "the literature reports" and "we found" are different sentences here.

One place takes only what the lab did: the journal. A number on the Frontier and an entry on the Banlist are records of the lab's own path, so each rests on an `experiment` claim.

## 4. Status and Corrections

`status` says how far a claim is relied on; `verified` says whether its evidence was checked by someone other than its writer. `verified` is never set by the writer.

**A `quote` claim:**

- Verified blindly when it is added (§6). At that moment it is still a draft and nothing has been concluded from it: a `partial` is narrowed in place to what the stored text carries and verified again; a `fail` is deleted. Whoever does it corrects the pages that cite it in the same commit (`cortex.py links`).
- `provisional` until a second, independent source reports the same; then `confirmed`, which means "well reported".
- An experiment of ours never changes the status of a `quote` claim, because the source still says what it says. The experiment writes its own claim, with `supports::` or `contradicts::` pointing at the quoted one, and a contradiction gets a tension: what held there, what held here, and the difference in conditions.

**An `experiment` claim:**

- `provisional` while its experiment is open.
- `confirmed` when the experiment closes and its postmortem confirms it, with `verified: pass`. The close is its check.
- `withdrawn` when it did not hold: at close, or when a later experiment shows it was an error or an artifact. The `withdrawn::` line names the experiment and round, and says why.

**Every claim, once checked** (a `quote` claim after its verification; an `experiment` or `stated` claim from the start, because others act on it as soon as it is written): its sentence, evidence and conditions do not change and it is not deleted, even when a later source, experiment or re-check contradicts it. What the lab once held, and why it stopped, is part of the knowledge. It changes status instead: `withdrawn`, or `superseded` when a later claim says the same thing more exactly or under corrected conditions (`superseded_by::`).

When two claims disagree and it is not yet clear which holds: a tension, and both stay. A technical failure (crash, out-of-memory, missing credential) produces no claim at all.

## 5. How the Cortex Grows

Mostly by its own operations, at any time. The experiment loop adds to it at fixed moments.

| When | What happens in the cortex |
|---|---|
| **Any time:** something about the field was read, found, or handed over by the user | `add`: store the source, write its claims, and work them into the topic pages they change. No gap or experiment has to ask for it. Gathering knowledge about the field is work of the lab in its own right, and a lab session with nothing else to do does this. |
| A topic has claims and no page, or a page no longer says what its claims say | Write or rewrite the topic page, and put it under its area in `index.md`. A page is built as soon as a topic has enough claims to say something, whichever sources they come from. |
| An area of the field in `index.md` is empty or thin | Read into it (`add`), or write the gap. |
| A question the cortex cannot answer | A row in `gap_map.md`; `investigate` starts from the row and ends by updating it. |
| Finding a direction for an experiment | `ask`: topic pages, tensions, the gap map; and the journal for the path so far. Read widely around the idea and `add` what was read. |
| A round of a try ends with something to tell the lab | The try writes a note to the lab in its log and nothing in the cortex. |
| A lab step on a try | For each `lesson` note: the claim (`provisional`, `experiment` anchor), worked into the topic page it changes; a tension if it disagrees with a claim the cortex holds; the gap it touches. A `source` note is an `add`; a `correction` is settled as §4 says; a `question` is an `ask`, then an `investigate`. |
| An experiment closes | Its open claims are settled, `confirmed` or `withdrawn`, and the pages that cited them revised. If the idea ran cleanly, its final conclusion is written as a claim too. |
| From time to time, and before a wide request that will choose a direction | `review`, with the additions in §7. |

## 6. Checking

From the lab root, before every commit that touches `cortex/`:

```bash
uv run .agents/skills/cortex/scripts/cortex.py check --also experiments
uv run .agents/skills/cortex/scripts/cortex.py links claims/<claim>                                    # what rests on a claim
uv run .agents/skills/cortex/scripts/cortex.py claims --from <experiment name> --status provisional   # what a closing experiment still owes
```

Blind verification: for every `quote` claim, when it is added: `/cortex verify`, which says who starts it when the agent that wrote the claims cannot. Until then the claim is `verified: unchecked`, and `check` prints how many claims wait.

## 7. Review, in This Lab

In addition to the skill's checklist.

**The knowledge base:**

- **Breadth.** Go through the areas in `index.md` against the field as `purpose.md` §1 names it. An area that is missing, empty, or holds only what the lab's own experiments showed is reported, with what to read. A cortex that knows only what the lab tried is the main failure this review looks for.
- **Pages.** Claims that sit in no topic page; a page about one source instead of one topic; a page that no longer says what its claims say.
- **Basis.** No topic page presents as seen by the lab something that rests only on `quote` claims, or the other way round.
- **Gaps.** A gap listed as open that a source or an experiment has answered; a question that is on no list.
- **One experiment's detail.** Settings and debugging of a single experiment in a topic page. They belong in that try's log.

**Against the lab's own path.** Read `JOURNAL.md` and every `experiments/<repo short name>/<experiment name>/postmortem.md` and `results.json`, and run:

```bash
uv run scripts/lab.py sync-repos     # so system pages can be compared with the code
uv run scripts/lab.py check-drift    # system pages whose monitored code changed
```

- **Closed experiments.** No closed experiment (a row with a verdict in the journal's matrix) has a `provisional` claim left, and the pages its postmortem says it changed show it.
- **Frontier and Banlist.** Frontier numbers match the `metrics.json` of the lab step they name, and numbers that are compared were measured with the same `evaluation_version`. Every Banlist entry names the `experiment` claim it rests on; none rests on a `quote` claim or on a technical failure. A Banlist entry whose "unless" condition has since changed; a Spark already done or made pointless.
- **System pages.** Read the diff `check-drift` points at and see what on the page is no longer so.

Experiment folders are evidence: do not edit them. To check a claim against its experiment, read the postmortem and the lab step records in its lab folder; the plan and the log are in `notes/<experiment name>/` on the try branch the claim names (`uv run scripts/lab.py mount --exp <id> --try <try name>`). Append one line to `cortex/log.md`: `## [YYYY-MM-DD HH:MM] review | cortex — <what was fixed, how many items reported>`.
