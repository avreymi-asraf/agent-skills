---
name: cortex
description: Build and maintain a cortex - an LLM-maintained knowledge base in three layers (immutable sources, atomic claims each anchored to a quote or an experiment, synthesis pages that cite claims), in the spirit of Karpathy's LLM wiki. Use when adding papers, articles, notes or experiment results to a knowledge base, investigating an open question from outside sources, answering from compiled knowledge, fusing claims into concept or findings pages, recording a tension between sources, or reviewing and linting a knowledge base. Also when the user mentions cortex, llm wiki, wiki-llm, karpathy wiki, or a persistent alternative to RAG. One skill for every operation - add, investigate, ask, review - e.g. `/cortex add <source>`. Each cortex states its own purpose, layout and anchors in a profile, so the same skill serves a reading knowledge base and a research lab's memory.
argument-hint: "[add <source> | investigate <question> | ask <question> | review | init]"
---

<cortex>

# Cortex

A cortex is knowledge that is compiled once and kept. Instead of re-reading raw documents for every question, an agent reads a source once, writes down what it establishes, and fuses that into pages that get better with every addition. Two things go wrong when an LLM does this unguarded: prose that is rewritten from prose drifts toward the model's own voice and loses the rare details, and grounding gets invented ("as the paper shows"). A cortex is built so that both are visible and checkable.

Use a cortex for a focused domain that keeps accumulating material and needs fused understanding. For a broad or fast-changing corpus, plain retrieval over the raw files is the better tool.

This one skill carries every operation on a cortex. Invoked with arguments, the first word names the operation: `/cortex add <source>`, `/cortex investigate <question>`, `/cortex ask <question>`, `/cortex review`, `/cortex init`. A request in plain words ("add this paper", "what do we know about X") maps to the same operations.

- **[Three-layers]**: sources, claims, synthesis, and why each has different rules. Read this first.
- **[Profile]**: what each cortex says about itself. This is where one cortex differs from another.
- **[Claims]**: the atomic layer: one sentence, an anchor, its conditions, a status.
- **[Synthesis]**: pages, tensions and questions, written on top of claims.
- **[Where-it-runs]**: which operations get a fresh context of their own, and the brief that starts one.
- **[Add]**: from a source to claims to fusion.
- **[Investigate]**: starting from an open question and going out to find what could answer it.
- **[Ask]**: answering from the cortex.
- **[Review]**: the periodic pass: well built, well linked, still true.
- **[Scripts]**, **[Connecting-Skills]**, **[Common-mistakes]**, **[Example]**, **[References]**.

</cortex>

<Three-layers>

```
synthesis   pages, tensions, questions          rewritten freely; every load-bearing sentence cites a claim
    │
claims      one sentence + anchor + conditions  added, never rewritten; a wrong one is marked, not deleted
    │
sources     originals, experiments              never edited
```

**Trust sits in the claims.** A claim is small enough to check against its anchor, by a script and by a reader who sees nothing else. Because the truth is held there, the synthesis above it may be rewritten as often as understanding changes. A sentence in a page with no claim under it is exactly where to look for drift.

Each half fails when it is alone, and the two failures are opposite:

- **Claims without synthesis** pile up. Adding one more claim is always easier than fusing, so a cortex can hold a hundred verified claims and no understanding. Fusion therefore has fixed moments ([Add] step 5, [Review]) and is never left for "later".
- **Synthesis without claims** is prose rewritten from prose. It reads well and nobody can say which sentence a source supports.

Rules between the layers:

1. A source is never edited. A claim is never rewritten: when it turns out wrong or too wide, a new claim is added and the old one is marked `superseded` or `withdrawn` with the reason. Nothing is deleted, because the history of what was once believed is evidence too.
2. A claim states only what its anchor supports. What the agent concludes from several claims is synthesis and lives in a page.
3. A page cites claims, not sources. If a page needs something no claim says, the claim is written first.

</Three-layers>

<Profile>

The skill fixes the three layers and the rules between them. Everything else is this cortex's own, and is written once in `profile.md` at the root of the cortex. **Read the profile before any operation.** Where it and this skill differ on a name or a place, the profile wins.

A profile says:

1. **What the synthesis is for**: the question a reader brings to this cortex. It is the test for what is worth writing. A reading knowledge base: "understand the field well enough to explain it and compare approaches". A research lab: "choose and do the next experiment". The same paper yields different claims and different pages under each.
2. **Layout**: where sources, claims and synthesis live and what the page types are called.
3. **Anchors**: which kinds of anchor this cortex accepts and what each one earns ([Claims]).
4. **Checking**: what must pass before a write counts: the script, and when a blind verification is required.
5. **Moments**: when fusion happens here and who does it. In a knowledge base it is the end of each `add`. In a lab it is set by the experiment loop.

A new cortex (`init`) starts from the default profile in [Templates](references/templates.md) and this layout:

```
<root>/
├── sources/           # raw/ originals, text/ what was extracted from them, <source-id>.md notes
└── cortex/
    ├── profile.md
    ├── index.md       # map of the synthesis: one line per page, open tensions and questions
    ├── claims/
    ├── pages/
    ├── tensions/
    └── questions/
```

A folder that already holds compiled knowledge and has no profile is not migrated. Write a profile that describes it as it is, and add the claims layer from the next operation on.

</Profile>

<Claims>

A claim is one thing that can be true or false, written as one sentence, in a file of its own under `claims/`. The sentence is the title. Template in [Templates](references/templates.md).

```md
---
type: claim
status: provisional
verified: pass
created: 2026-11-11
description: PPO vs GRPO, convergence speed, reward collapse, Search-R1
---
# In Search-R1 training, GRPO converges faster than PPO but can collapse in reward after many steps, while PPO stays stable.

## Evidence
- quote::[[sources/search-r1]] — section 5.1
  > GRPO converges faster than PPO across all cases.
  > [...] GRPO leads to reward collapse after training for many steps, whereas PPO remains stable.

## Conditions
Qwen2.5 3B and 7B, NQ and HotpotQA, training reward (not evaluation EM).

## Relations
- supports::[[claims/reinforce-outperforms-ppo-and-grpo-with-fewer-search-actions]] — independent evidence for "GRPO least stable" only
```

- **Atomic.** If "and" joins two things that could be false separately, write two claims.
- **With its conditions.** Model, data, metric, population, date: whatever the statement was true under. A claim stripped of its conditions gets fused with things it cannot be compared to.
- **Anchored.** Every evidence item is `<anchor kind>::<what it points at>`. The kinds:

| Anchor | Points at | Can be checked | Earns |
|---|---|---|---|
| `quote` | A source and the verbatim words | By script: the words are in the source text | "The source says this." Not "this is so". |
| `experiment` | An experiment, a round, a commit | By re-running | "We observed this, under these conditions." |
| `stated` | Who said it and when | No | "We were told this." Use for what the user knows and nothing else records. |

  A profile may accept only some of these, or add its own kind, as long as it says what the anchor points at and how it can be checked.
- **Read before you claim.** A search snippet or an abstract is a lead. A `quote` is taken only from text that is stored under `sources/`, so it can be checked.
- **Two fields, two questions.** `verified` (`pass`, `partial`, `fail`, `unchecked`): does the evidence say what the sentence says? `status`: how far do we rely on it? `provisional` → `confirmed`, `withdrawn` or `superseded`. A profile says what moves a claim to `confirmed`: a second independent source, a closed experiment, real use.
- **Edits that are allowed:** `status`, `verified`, a new evidence item for the same statement under the same conditions, a new relation, a typo. Anything else is a new claim.
- **When a new claim disagrees with an old one**, there are three cases. It is not settled which holds, or both may hold under different conditions: write a tension ([Synthesis]) and leave both claims as they are. The old one did not hold (an error, an artifact): mark it `withdrawn`. The new one says the same thing more exactly or under corrected conditions: mark the old one `superseded`.
- **Relations** between claims name the relation and the reason: `supports::`, `contradicts::`, `refines::`, `superseded_by::`. A source that repeats another source is not independent support; say so in the reason.

</Claims>

<Synthesis>

Synthesis is where understanding lives: a page explains, compares and concludes, and may be rewritten whenever understanding changes.

- **A page is about an idea or a question, never about a source.** A page that summarizes one source is that source's claims in worse form. Page types and their names come from the profile (concept, method, comparison, finding, ...).
- **Every load-bearing sentence cites its claim**: `... collapses after many steps ([[claims/grpo-converges-faster-...]])`. Reasoning that goes beyond the claims is allowed and wanted; label it `Inference:` or `Hypothesis:` so a reader can tell it from what is anchored.
- **A page inherits the weakness of its anchors.** A page that rests only on `quote` claims says what the literature reports, and says so. It is not something this cortex's owner has seen happen.
- **Create a page** when an idea is asked about repeatedly, is needed to explain other things, or is where several claims meet. **Merge** into an existing page when the new material sharpens the same idea. **Split** when a page answers independent questions. Check for the idea under another name before creating.
- **A tension is a node of its own.** When two claims disagree, do not average them and do not quietly pick one. Write a tension: the question in dispute, the claims on each side, the difference in conditions that might explain it, and what evidence would settle it. A tension is the most valuable thing an `add` can produce, because it says where the next reading or experiment should go.
- **A question** is something the cortex should know and does not: what was asked, which claims bear on it, what is missing. Some cortexes keep questions as files, some as rows in one table; the profile says.
- **Links carry meaning.** Write `relation::[[target]]` with the reason on the same line. A link that only marks a shared word helps nobody.

Before finishing a new or heavily revised page, run it through the gate in [Quality gate](references/quality-gate.md).

</Synthesis>

<Where-it-runs>

Some operations read a great deal and return little, and their draft should not be colored by whatever the conversation was about. Those run in a fresh context: a subagent, a forked skill, or a session of their own. The agent that received the request writes the brief and reads the report; it does not read the source itself.

| Operation | Runs | Why |
|---|---|---|
| `add` | Fresh context | A whole source is read. The claims should come from the source, not from what the caller hopes it says. |
| `investigate` | Fresh context for the search and each `add`; the caller keeps the question and writes what changed | The reading is heavy, the judgment about the question is the caller's. |
| `review` | Fresh context | It reads the whole cortex. |
| Blind verification of a claim | Its own fresh context, never the one that wrote the claim | The verifier must see only the sentence and the evidence. |
| `ask` | In the conversation | The answer is for the conversation. |
| Writing one claim from work already at hand (a round of an experiment just analyzed) | In the conversation | The evidence is already in front of the agent. |

The brief is the worker's whole picture, so it carries:

```
Load the `cortex` skill and carry out `add` on <source path or URL>, in the cortex at <path>.
You are the worker: do every step of the operation yourself. Read `profile.md` first.
Why this source: <the question, gap or request it was brought for, or "no question behind it">.
Return the "Cortex update" report and nothing else.
```

"Why this source" is the part a worker cannot guess, and it decides which claims are worth writing. When the user wants the fresh context guaranteed by the tool and not by this instruction, see [Scripts].

</Where-it-runs>

<Add>

`/cortex add <source>`: one source in, the cortex changed. With no argument, take the next source that has no claims yet. It runs in a fresh context ([Where-it-runs]); the steps below are the worker's.

1. **Orient.** Read `profile.md`, then `index.md`. Search for the source's central terms among claims and pages, so that what is already known is in front of you: `cortex.py claims --grep <term>`.
2. **Store the source.** The original goes to `sources/raw/` and its extracted text to `sources/text/` (use `pdf-to-markdown-mcp` for a PDF). Write the source note `sources/<source-id>.md` from the template: what it is, where it came from, how reliable, and **how much of it was actually read**.
3. **Write the claims** that could change what a reader of this cortex understands or decides, as the profile defines its reader. Not one per sentence. For each: is it already there? The same statement under the same conditions gets a new evidence item on the existing claim. A statement that disagrees gets its own claim and a `contradicts::` relation.
4. **Check.** `cortex.py check` must pass. When the profile asks for a blind verification, hand each new claim to a fresh agent that gets only the sentence and its evidence, not the draft and not your reasoning, and record its answer in `verified`. `partial` or `fail` means the sentence is rewritten to what the evidence carries, as a new claim.
5. **Fuse.** For each new claim ask: which page does this change? Three honest answers:
   - *It contradicts a claim we hold.* Write a tension, unless the new evidence settles which one holds ([Claims]).
   - *It changes a page.* Revise the affected part of that page and cite the claim. Keep what is still right.
   - *Nothing yet.* The claim stays a claim. Do not build a page that no question asked for.
6. **Close.** Update `index.md` for pages, tensions and questions that were added or changed. Commit the whole operation as one commit (`add: <source-id>`), so it can be read, or reverted, as a unit.

Report what was captured, what it changed, and the tensions it opened.

</Add>

<Investigate>

`/cortex investigate <question>`: reading as an active step. It starts from a named question, tension or gap, and its job is to change that node.

1. State what would count as an answer, and what kind of source could give it: a primary paper, official documentation, a dataset, an independent measurement.
2. Search for those sources. For a disputed point, look deliberately for the evidence against the side the cortex currently leans to. Use `iterative-deep-researcher` or `gemini-deep-research` for a long search.
3. Run each source that is worth it through [Add].
4. Return to the node that started it and write what changed: answered (by which claims), narrowed (what is now known, what remains), or still open (what was looked for and not found, so the next agent does not repeat the search).

The difference from a plain `add`: a source that is dropped in without a question yields claims and tensions, and changes pages only where it touches them. A page gets built when a question pulls claims together. Collecting first and asking later produces a large page of other people's results that nothing rests on.

</Investigate>

<Ask>

`/cortex ask <question>`: answer from what the cortex holds.

1. Read `profile.md` and `index.md`; open the smallest set of pages that covers the question.
2. For each load-bearing point, open the claim it cites and look at its status, its conditions and its anchor.
3. Answer with citations to claims. Say plainly where the cortex has nothing, where it has only `quote` claims, and where a tension is open.
4. If the pages do not cover it and the claims do, answer from the claims. That answer is a candidate page.

Persist only what is reusable: a recurring explanation, a comparison, a sharpened tension. When the task was only a question, answer it and propose the page; do not grow the cortex silently. A question the cortex could not answer is recorded as a question node.

</Ask>

<Review>

`/cortex review`: one pass over the whole cortex, from time to time, after a batch of additions, and before a decision that will lean on it. It runs in a fresh context ([Where-it-runs]).

1. **Mechanical first:** `cortex.py check` and `cortex.py claims --status provisional`, with the options the profile gives for this cortex.
2. **Built.** Does every page pass the gate? Is a page one source's summary? Is something stated as seen that is only quoted?
3. **Linked.** Does `index.md` match the pages on disk? Are there claims no page uses that a page should? Pages that say the same thing in two wordings?
4. **True.** This is the part that needs judgment: claims left `provisional` after the thing that should have settled them; pages that still lean on a withdrawn or superseded claim (`check` lists them); two pages that disagree with no tension written; a tension that later claims have settled; a question that has been answered.

**Fix** what the evidence in the cortex settles: links, index lines, a status that the record clearly decides, a duplicate (keep the better-anchored wording, link from the other). **Report and leave** what needs a decision: a contradiction with no clear loser, a claim whose anchor cannot be found, anything about what the cortex is for. Never delete a claim. Commit the fixes as one commit.

The full checklist and the report format: [Quality gate](references/quality-gate.md). A profile may add checks of its own; run them in the same pass.

</Review>

<Scripts>

`scripts/cortex.py`, standard library only, run with `uv` from the folder that contains the cortex. It reads the files and decides nothing about content.

```bash
uv run <this-skill>/scripts/cortex.py check  [--cortex cortex] [--sources DIR] [--also DIR] [--strict]
uv run <this-skill>/scripts/cortex.py claims [--status S] [--anchor K] [--from TEXT] [--grep TEXT]
uv run <this-skill>/scripts/cortex.py links <node>
```

- `check` fails on: a claim with no status, no evidence or an unknown anchor; a `quote` whose words are not in the source text (whitespace and typography are ignored, `[...]` marks an omission); an `experiment` anchor without a round and a commit; a `superseded` or `withdrawn` claim that does not say by what or why; a `[[link]]` that leads nowhere. It lists for review, without failing: pages that cite a withdrawn or superseded claim, typed pages that cite no claim, tensions with fewer than two claims, pages missing from `index.md`. `--strict` fails on those too. `--also DIR` adds a folder that links may point into (a lab's `experiments/`).
- `claims` prints the claims as a table, filtered by status, anchor kind, the source or experiment they come from, or a word in the title and description. It is the way to find what is already known before writing, and what is still provisional.
- `links <node>` prints what a node points to and what points to it. Run it before withdrawing a claim, to see which pages rest on it.

A typed page that is grounded in something other than claims says so in its frontmatter (`anchor: code` on a page that describes a codebase), and `check` does not ask it for claims.

**Making the fresh context a property of the tool.** This skill asks for a fresh context in words, which works in every agent tool and depends on the agent following it. Claude Code can enforce it, in one of two ways, and both are the owner's choice for their own repo:

- Add `context: fork` to this skill's frontmatter in that repo. Every `/cortex ...` then runs in a subagent that gets this file and the arguments as its task. It suits a repo that is only a knowledge base. It does not suit a repo where an agent writes claims in the middle of other work (a lab), because the skill then never loads into the working agent's own context.
- Define one subagent in `.claude/agents/` that preloads this skill (`skills: [cortex]`), and delegate `add` and `review` to it. The skill stays as it is.

</Scripts>

<Connecting-Skills>

- **Prerequisites:** `pdf-to-markdown-mcp` when a source is a PDF: a quote can only be checked against extracted text.
- **Companions:** `iterative-deep-researcher` and `gemini-deep-research` for the search inside [Investigate]. `experiment-lab`: a lab built with it keeps its memory as a cortex, with its own profile; there the experiment loop decides when a claim is written and settled, and this skill gives the form and the operations.
- **Successors:** `manage-skills` when this skill itself has to change. `grow-autonomy` when agents keep writing to a cortex in a way the user rejects: the cause is in what they understood, usually in the profile, not in the pages.

</Connecting-Skills>

<Common-mistakes>

- **A claim per sentence.** The test is the profile's reader: would this change what they understand or decide?
- **A claim that says more than its anchor.** The quote reports a result on one benchmark; the sentence says "is better". Narrow the sentence.
- **Synthesis written into a claim.** "Therefore RL needs a warm start" is a conclusion from several claims. It belongs in a page, labeled as inference.
- **Editing a claim to make it right.** The old wording is what pages cited. Supersede it.
- **A page with citations to sources.** Then nothing can be checked sentence by sentence. Write the claims first.
- **Averaging a disagreement.** "Results are mixed" hides the one thing worth knowing. Write the tension with the conditions on each side.
- **Skipping fusion.** An `add` that ends at step 4 leaves the cortex larger and no wiser.
- **Quoting what was not read.** An abstract supports claims about the abstract.

</Common-mistakes>

<Example>

A reading cortex on training search agents. The profile says the reader wants to choose a training recipe.

1. `/cortex add sources/raw/search-r1.pdf`. The text is extracted, the source note says the full paper was read. Seven claims are written, among them the GRPO claim shown in [Claims]. `check` passes. Fusion: the page `pages/rl-algorithms-for-search-agents.md` gets a paragraph on stability, citing the claim.
2. `/cortex add sources/raw/research.pdf`. One new claim says that starting from an instruction-tuned model gives a better final result. An existing claim from Search-R1 says the final reward is similar. They disagree, so a tension is written: `tensions/does-instruct-initialization-beat-base.md`, with both claims, the differences in conditions (GRPO vs PPO, 7B and 32B vs 3B and 7B, evaluation metric vs training reward), and what would settle it (the same algorithm and metric on both starts).
3. `/cortex ask "should we start from the instruct model?"`. The answer cites both claims and the open tension, and says that the cortex holds only quoted results on this.
4. `/cortex investigate tensions/does-instruct-initialization-beat-base`. A third paper measures both starts with one metric. Its claim is added; the tension is rewritten as narrowed: the gap appears on evaluation metrics and not on training reward.
5. A month later, `/cortex review` finds a page that still cites a claim since superseded, and two pages that describe the same reward design under different names. The first is fixed, the second is merged, and one contradiction with no clear loser is reported to the user.

**A mistake, and what it looked like:** in step 1 the first draft of a claim read "GRPO is unstable". The blind verification returned `partial`: the quote reports collapse in this paper's runs, after many steps. The claim was rewritten with those conditions before anything cited it.

</Example>

<References>

- [Templates](references/templates.md): the default profile, the claim, the source note, the page, the tension, the question, the index. Read when starting a cortex or writing a node of a kind for the first time.
- [Quality gate](references/quality-gate.md): the tests a page must pass, the review checklist, and the report format. Read before finishing a substantial `add` and during `review`.

</References>
