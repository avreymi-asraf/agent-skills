---
name: cortex
description: Build and maintain a cortex - an LLM-maintained knowledge base in three layers (immutable sources, atomic claims each anchored to a quote or an experiment, synthesis pages that cite claims), in the spirit of Karpathy's LLM wiki. Use when adding papers, articles, notes or experiment results to a knowledge base, investigating an open question from outside sources, answering from compiled knowledge, fusing claims into concept or findings pages, recording a tension between sources, or reviewing and linting a knowledge base. Also when the user mentions cortex, llm wiki, wiki-llm, karpathy wiki, or a persistent alternative to RAG. One skill for every operation - add, investigate, ask, verify, review - e.g. `/cortex add <source>`. Each cortex states its own purpose, layout and anchors in a profile, so the same skill serves a reading knowledge base and a research lab's memory.
argument-hint: "[add <source> | investigate <question> | ask <question> | verify | review | init]"
---

<cortex>

# Cortex

A cortex is knowledge that is compiled once and kept. Instead of re-reading raw documents for every question, an agent reads a source once, writes down what it establishes, and fuses that into pages that get better with every addition. Two things go wrong when an LLM does this unguarded: prose that is rewritten from prose drifts toward the model's own voice and loses the rare details, and grounding gets invented ("as the paper shows"). A cortex is built so that both are visible and checkable.

Use a cortex for a focused domain that keeps accumulating material and needs fused understanding. For a broad or fast-changing corpus, plain retrieval over the raw files is the better tool.

This one skill carries every operation on a cortex. Invoked with arguments, the first word names the operation: `/cortex add <source>`, `/cortex investigate <question>`, `/cortex ask <question>`, `/cortex verify`, `/cortex review`, `/cortex init`. A request in plain words ("add this paper", "what do we know about X") maps to the same operations.

- **[Three-layers]**: sources, claims, synthesis, and why each has different rules. Read this first.
- **[Profile]**: what each cortex says about itself. This is where one cortex differs from another.
- **[Claims]**: the atomic layer: one sentence, an anchor, its conditions, a status.
- **[Synthesis]**: pages, tensions and questions, written on top of claims.
- **[Where-it-runs]**: which operations get a fresh context of their own, the brief that starts one, and what to do when you cannot start one.
- **[Add]**: from a source to claims to fusion.
- **[Verify]**: a blind verdict on each new claim, and what happens to a claim that does not pass.
- **[Investigate]**: starting from an open question and going out to find what could answer it.
- **[Ask]**: answering from the cortex.
- **[Review]**: the periodic pass: well built, well linked, still true.
- **[Scripts]**, **[Connecting-Skills]**, **[Common-mistakes]**, **[Example]**, **[References]**.

</cortex>

<Three-layers>

```
synthesis   pages, tensions, questions          rewritten freely; every load-bearing sentence cites a claim
    │
claims      one sentence + anchor + conditions  corrected in place until verified; after that marked, never rewritten
    │
sources     originals, experiments              never edited
```

**Trust sits in the claims.** A claim is small enough to check against its anchor, by a script and by a reader who sees nothing else. Because the truth is held there, the synthesis above it may be rewritten as often as understanding changes. A sentence in a page with no claim under it is exactly where to look for drift.

Each half fails when it is alone, and the two failures are opposite:

- **Claims without synthesis** pile up. Adding one more claim is always easier than fusing, so a cortex can hold a hundred verified claims and no understanding. Fusion therefore has fixed moments ([Add] step 5, [Review]) and is never left for "later".
- **Synthesis without claims** is prose rewritten from prose. It reads well and nobody can say which sentence a source supports.

Rules between the layers:

1. A source is never edited. A claim is a draft until a verifier passes it, and fixed after: the whole rule is in [Claims], under *Correcting a claim*.
2. A claim states only what its anchor supports. What the agent concludes from several claims is synthesis and lives in a page.
3. A page cites claims, not sources. If a page needs something no claim says, the claim is written first.

</Three-layers>

<Profile>

The skill fixes the three layers and the rules between them. Everything else is this cortex's own, and is written once in `profile.md` at the root of the cortex. **Read the profile before any operation.** Where it and this skill differ on a name or a place, the profile wins.

A profile says:

1. **What the synthesis is for**: the question a reader brings to this cortex. It is the test for what is worth writing. A reading knowledge base: "understand the field well enough to explain it and compare approaches". A research lab: "know the field of the research as widely as possible, so the research advances". The same paper yields different claims and different pages under each.
2. **Layout**: where sources, claims and synthesis live and what the page types are called.
3. **Anchors**: which kinds of anchor this cortex accepts and what each one earns ([Claims]).
4. **Checking**: what must pass before a write counts: the script, and when a blind verification is required.
5. **Moments**: when fusion happens here and who does it. In a knowledge base it is the end of each `add`. In a lab it is also at fixed moments of the experiment loop.

A new cortex (`init`) starts from the default profile in [Templates](references/templates.md) and this layout:

```
<root>/
├── sources/           # raw/ originals, text/ the text read (written by `cortex.py store`), <source-id>.md notes
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
- **Read before you claim.** A search snippet or an abstract is a lead. A `quote` is taken only from the source's text stored in `sources/text/` ([Add] step 2), so it can be checked. The source note is your description of the source, not its words, and quotes are never checked against it.
- **Two fields, two questions.** `verified` (`pass`, `partial`, `fail`, `unchecked`): does the evidence say what the sentence says? `status`: how far do we rely on it? `provisional` → `confirmed`, `withdrawn` or `superseded`. A profile says what moves a claim to `confirmed`: a second independent source, a closed experiment, real use.
- **`verified` is never the writer's own verdict.** A new claim is `unchecked`. Its writer, rereading it, sees the sentence it meant and not the one it wrote, so the verdict comes from someone else: for a `quote` claim, a blind verifier ([Verify]); for another anchor, the check the profile names (an experiment's own close, for instance).
- **Correcting a claim** depends on whether it has passed verification:
  - *At verification* it is still a draft, and nothing has been concluded from it. A claim returned `partial` is narrowed in place to what its evidence carries and verified again; one returned `fail` is deleted. Whoever does it fixes the pages and relations that cite it in the same change.
  - *Once it has passed*, and from the start for a claim whose anchor gets no blind verification, its sentence, evidence and conditions stay as they are, because pages cited that wording and what was once believed is evidence too. The edits still allowed: `status`, `verified`, a new evidence item for the same statement under the same conditions, a new relation, a typo. When later evidence (a source, an experiment, a later re-check) shows it wrong or too wide, it is never rewritten or deleted; one of the three cases below applies.
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
| `verify`: the blind verdict on a claim | Its own fresh context, never the one that wrote the claim | The verifier must see only the sentence and the evidence. |
| `ask` | In the conversation | The answer is for the conversation. |
| Writing one claim from work already at hand (a round of an experiment just analyzed) | In the conversation; its `verify`, if the profile asks for one, still in a fresh context | The evidence is already in front of the agent. |

The brief is the worker's whole picture, so it carries:

```
Load the `cortex` skill and carry out `add` on <source path or URL>, in the cortex at <path>.
You are the worker: do every step of the operation yourself, except a step the skill gives a fresh
context of its own; for that, follow "When you cannot start one" in [Where-it-runs]. Read `profile.md` first.
Why this source: <the question, gap or request it was brought for, or "no question behind it">.
Return the "Cortex update" report and nothing else.
```

"Why this source" is the part a worker cannot guess, and it decides which claims are worth writing.

**When you cannot start one.** A step that has a fresh context of its own is never done in your context instead, not even as a stand-in: that is how a writer ends up verifying its own claims, or a caller reading the source it hoped would agree. If you can start an agent, start it with the brief. If you cannot (you are yourself a delegated agent, or the session has no way to start one), do the rest of your work, leave that step undone, and list it under **Pending** in your hand-back with its brief written out. The session that delegated your work starts it; a session that cannot either passes it up the same way, and at the top it goes to the user. Leave what depends on the step in the state that says so: a claim waiting for its verdict stays `unchecked`.

</Where-it-runs>

<Add>

`/cortex add <source>`: one source in, the cortex changed. With no argument, take the next source that has no claims yet. It runs in a fresh context ([Where-it-runs]); the steps below are the worker's.

1. **Orient.** Read `profile.md`, then `index.md`. Once the source's text is stored (step 2), `cortex.py similar sources/text/<source-id>.md` lists the claims and pages closest to it; read those, so that what is already known is in front of you. `cortex.py claims --grep <term>` finds more.
2. **Store the text.** A quote is checked against the stored text, so that text has to be the source's own words as a tool delivered them, never typed out by an agent: a retyped passage checks against the agent's memory of the source. Take the first route this session has:
   1. *The original as a file*: it is local, or the session can download it. Keep it in `sources/raw/` when it exists nowhere stable, convert it to text with whatever converter the session has, and store that text: `cortex.py store <source-id> --file <text file>`.
   2. *A tool that writes what it fetched or converted to a file*: store that file the same way.
   3. *A tool that returns the text into the conversation and cannot write a file*: here the text has to pass through you. Pipe each passage you need to `cortex.py store <source-id>` on standard input, copied whole from the tool's result: not from memory, not reworded, reflowed or repaired, with `[...]` between passages that are not adjacent and section headings as the source writes them. Then fetch the source again and pipe the second copy to `cortex.py store <source-id> --compare`: it names every stored passage the second copy does not contain. Store again, under `--part`, anything it names.

   Store each passage with the sentences that carry its conditions (the model, the data and population, the setting), even when they stand in another section: a verifier sees only the stored text around a quote. A long copyrighted text stays out of a public repo; store the passages claims will quote.

   If no route gives the text (blocked hosts, a paywall, a format nothing here reads), the source is a lead. Write its note with `read: not obtained` and the routes tried, with their dates, and stop: no claims come from a lead, and `check` lists it until a route works.

   Write the source note `sources/<source-id>.md` from the template: what it is, where it came from, how reliable, the route its text came by, and **how much of it was actually read**.
3. **Write the claims** that could change what a reader of this cortex understands or decides, as the profile defines its reader. Not one per sentence. For each: is it already there? The same statement under the same conditions gets a new evidence item on the existing claim. A statement that disagrees gets its own claim and a `contradicts::` relation. A condition the sentence names that is not in the quoted passage (the model, named in the methods) gets a quote of its own, so the verifier sees it. Each new claim is `verified: unchecked`.
4. **Check and verify.** `cortex.py check` must pass. When the profile asks for a blind verification, the new claims go through [Verify]: start the verifier if you can, and list it under Pending if you cannot ([Where-it-runs]).
5. **Fuse.** For each new claim ask: which page does this change? A page may cite a claim still waiting for its verdict; if [Verify] narrows or deletes the claim, the page is corrected with it. Three honest answers:
   - *It contradicts a claim we hold.* Write a tension, unless the new evidence settles which one holds ([Claims]).
   - *It changes a page.* Revise the affected part of that page and cite the claim. Keep what is still right.
   - *Nothing yet.* The claim stays a claim. Do not build a page that no question asked for.
6. **Close.** Update `index.md` for pages, tensions and questions that were added or changed. Commit the whole operation as one commit (`add: <source-id>`), so it can be read, or reverted, as a unit.

Report what was captured, what it changed, the tensions it opened, and what is pending.

</Add>

<Verify>

`/cortex verify`: each claim that waits for a blind verdict gets one. `cortex.py check` says how many wait. The session that wrote the claims starts the verifier if it can; otherwise the session it hands back to does ([Where-it-runs]).

1. Start a fresh agent whose whole brief is:

   ```
   From <the folder that contains the cortex>, run `uv run <this-skill>/scripts/cortex.py pairs` and judge
   each claim from its output alone. Open no other file. Return one line per claim: file, verdict, reason.
   ```

   `pairs` prints each waiting claim's sentence, its quotes and the stored text around each, so nothing of the writer's draft, reasoning or source note reaches the verifier.
2. Record each verdict in `verified` as the verifier gave it.
3. On `partial`, narrow the sentence in place to what the printed text carries, using the verifier's reason. If the stored text carries the missing part in a passage the verifier was not shown, add that passage as a second quote instead. Set `verified: unchecked` and go back to step 1 with a new fresh agent. On `fail`, or when nothing worth keeping is left after narrowing, delete the claim. Before narrowing or deleting, run `cortex.py links claims/<claim>` and correct, in the same change, the pages and relations that cite it.

Narrowing and deleting are for this moment only. A claim that has passed is corrected as [Claims] says, by a new claim or a status, never in place.

</Verify>

<Investigate>

`/cortex investigate <question>`: reading as an active step. It starts from a named question, tension or gap, and its job is to change that node.

1. State what would count as an answer, and what kind of source could give it: a primary paper, official documentation, a dataset, an independent measurement.
2. Search for those sources. For a disputed point, look deliberately for the evidence against the side the cortex currently leans to. Use `gemini-deep-research` for a long search.
3. Run each source that is worth it through [Add].
4. Return to the node that started it and write what changed: answered (by which claims), narrowed (what is now known, what remains), or still open (what was looked for and not found, and the leads whose text could not be obtained, so the next agent does not repeat the search).

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

**Fix** what the evidence in the cortex settles: links, index lines, a status that the record clearly decides, a duplicate (keep the better-anchored wording, link from the other). **Report and leave** what needs a decision: a contradiction with no clear loser, a claim whose anchor cannot be found, anything about what the cortex is for. Never delete a claim that has passed verification. Claims still waiting for a verdict go to [Verify], started or listed as pending like any fresh-context step. Commit the fixes as one commit.

The full checklist and the report format: [Quality gate](references/quality-gate.md). A profile may add checks of its own; run them in the same pass.

</Review>

<Scripts>

`scripts/cortex.py`, standard library only, run with `uv` from the folder that contains the cortex. It reads the files and decides nothing about content.

```bash
uv run <this-skill>/scripts/cortex.py store   <source-id> [--file PATH] [--part NAME]   # text from the file, or stdin
uv run <this-skill>/scripts/cortex.py store   <source-id> --compare [--file PATH]       # check a copy against a second fetch
uv run <this-skill>/scripts/cortex.py check   [--cortex cortex] [--sources DIR] [--also DIR] [--strict]
uv run <this-skill>/scripts/cortex.py claims  [--status S] [--anchor K] [--from TEXT] [--grep TEXT]
uv run <this-skill>/scripts/cortex.py links   <node>
uv run <this-skill>/scripts/cortex.py similar <text file>
uv run <this-skill>/scripts/cortex.py pairs   [--all] [--context N]
```

- `store` writes a source's text to `sources/text/<source-id>.md` exactly as it was given, from a file or standard input, and refuses to overwrite: more text of the same source goes in as `--part <name>`. With `--compare` it reads a second copy instead and names each stored passage the copy does not contain.
- `check` fails on: a claim with no status, no evidence or an unknown anchor; a `quote` whose words are not in the source's stored text in `sources/text/` (whitespace, hyphens and typography are ignored, `[...]` marks an omission; the source note does not count); a `quote` of a source whose text was not obtained; an `experiment` anchor without a round and a commit; a `superseded` or `withdrawn` claim that does not say by what or why; a live claim marked `verified: fail`; a file under `sources/raw/` or `sources/text/` that changed after it was committed (git is the record); a `[[link]]` that leads nowhere. It lists for review, without failing: claims marked `verified: partial`, pages that cite a withdrawn or superseded claim, typed pages that cite no claim, tensions with fewer than two claims, pages missing from `index.md`, sources no claim quotes yet (the backlog of `add`), and sources whose text was not obtained (leads). `--strict` fails on those too. Its last line says how many quoted claims wait for a blind verdict. `--also DIR` adds a folder that links may point into (a lab's `experiments/`).
- `claims` prints the claims as a table, filtered by status, anchor kind, the source or experiment they come from, or a word in the title and description. It is the way to find what is already known before writing, and what is still provisional.
- `links <node>` prints what a node points to and what points to it. Run it before withdrawing a claim, to see which pages rest on it.
- `similar <text file>` lists the claims and pages that share a source's most frequent words. It is the orientation step of `add`, done the same way every time.
- `pairs` prints, for each live quoted claim still `unchecked`, the sentence, the quote and the lines of stored text around it. It is the whole input of a blind verifier ([Verify]).

A typed page that is grounded in something other than claims says so in its frontmatter (`anchor: code` on a page that describes a codebase), and `check` does not ask it for claims.

</Scripts>

<Connecting-Skills>

- **Prerequisites:** a way to read sources: a download in the shell, or a fetch or reader tool. A converter such as `pdf-to-markdown-mcp`, where it is installed, turns a PDF into text that can be stored. [Add] step 2 says what to do with whichever the session has.
- **Companions:** `gemini-deep-research` for the search inside [Investigate]. `experiment-lab`: a lab built with it keeps its knowledge base of its field as a cortex, with its own profile; there the experiment loop decides when an experiment's claims are written and settled, and this skill gives the form and the operations.
- **Prerequisites:** `pdf-to-markdown-mcp` when a source is a PDF: a quote can only be checked against extracted text.
- **Companions:** `gemini-deep-research` for the search inside [Investigate]. `experiment-lab`: a lab built with it keeps its knowledge base of its field as a cortex, with its own profile; there the experiment loop decides when an experiment's claims are written and settled, and this skill gives the form and the operations.
- **Successors:** `manage-skills` when this skill itself has to change. `grow-autonomy` when agents keep writing to a cortex in a way the user rejects: the cause is in what they understood, usually in the profile, not in the pages.

</Connecting-Skills>

<Common-mistakes>

- **A claim per sentence.** The test is the profile's reader: would this change what they understand or decide?
- **A claim that says more than its anchor.** The quote reports a result on one benchmark; the sentence says "is better". Narrow the sentence.
- **Synthesis written into a claim.** "Therefore RL needs a warm start" is a conclusion from several claims. It belongs in a page, labeled as inference.
- **Editing a verified claim to make it right.** Once it has passed, its wording is what pages cited. Supersede it.
- **A page with citations to sources.** Then nothing can be checked sentence by sentence. Write the claims first.
- **Averaging a disagreement.** "Results are mixed" hides the one thing worth knowing. Write the tension with the conditions on each side.
- **Skipping fusion.** An `add` that ends at step 4 leaves the cortex larger and no wiser.
- **Quoting what was not read.** An abstract supports claims about the abstract.
- **Keeping a `partial`.** A claim known to say more than its evidence, left as it is, gets cited like any other. Narrow it and verify again.

</Common-mistakes>

<Example>

A reading cortex on training search agents. The profile says the reader wants to choose a training recipe.

1. `/cortex add sources/raw/search-r1.pdf`. The PDF is converted, the text is stored with `cortex.py store`, and the source note says the full paper was read. Seven claims are written, `unchecked`, among them the GRPO claim shown in [Claims]. `check` passes, and a fresh agent judges the seven from `pairs`. Fusion: the page `pages/rl-algorithms-for-search-agents.md` gets a paragraph on stability, citing the claim.
2. `/cortex add sources/raw/research.pdf`. One new claim says that starting from an instruction-tuned model gives a better final result. An existing claim from Search-R1 says the final reward is similar. They disagree, so a tension is written: `tensions/does-instruct-initialization-beat-base.md`, with both claims, the differences in conditions (GRPO vs PPO, 7B and 32B vs 3B and 7B, evaluation metric vs training reward), and what would settle it (the same algorithm and metric on both starts).
3. `/cortex ask "should we start from the instruct model?"`. The answer cites both claims and the open tension, and says that the cortex holds only quoted results on this.
4. `/cortex investigate tensions/does-instruct-initialization-beat-base`. A third paper measures both starts with one metric. Its claim is added; the tension is rewritten as narrowed: the gap appears on evaluation metrics and not on training reward.
5. A month later, `/cortex review` finds a page that still cites a claim since superseded, and two pages that describe the same reward design under different names. The first is fixed, the second is merged, and one contradiction with no clear loser is reported to the user.

**A mistake, and what it looked like:** in step 1 the first draft of a claim read "GRPO is unstable". The blind verification returned `partial`: the quote reports collapse in this paper's runs, after many steps. The claim was narrowed in place to those conditions and passed a second blind verification before anything cited it.

</Example>

<References>

- [Templates](references/templates.md): the default profile, the claim, the source note, the page, the tension, the question, the index. Read when starting a cortex or writing a node of a kind for the first time.
- [Quality gate](references/quality-gate.md): the tests a page must pass, the review checklist, and the report format. Read before finishing a substantial `add` and during `review`.

</References>
