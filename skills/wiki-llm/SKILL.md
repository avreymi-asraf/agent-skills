---
name: wiki-llm
description: Build and maintain a compounding LLM wiki from papers, articles, notes, transcripts, code findings, or web research. Implements Karpathy's LLM Wiki pattern — pre-compile sources into interlinked markdown instead of re-reading raw files (RAG). Use when ingesting sources, connecting concepts, synthesizing knowledge, querying prior understanding, auditing wiki quality, or when the user mentions llm wiki, karpathy wiki, wiki-llm, or a persistent knowledge-base alternative to RAG.
---

<wiki-llm>
Implements Andrej Karpathy's LLM Wiki: the LLM pre-compiles raw documents into structured, interlinked markdown that compounds over time. Do not re-read raw files on every query. Sources are evidence. Pages are current synthesis. The index is the navigation and maintenance surface.

Optimize for evidence-grounded claims, reusable concept pages, explicit relationships, visible uncertainty, and fast future retrieval — not collected summaries.

**Use this wiki** for a focused domain that accumulates documents and needs synthesized insight. **Use RAG** for a broad or frequently-changing corpus, or when exact source citations must be regenerated per query.

### Topics Covered
- **[Wiki-Structure]** — `raw/` + `wiki/{index.md,sources/,pages/}`; initialize; conventions
- **[Reasoning-Rules]** — epistemic rules, page boundaries, typed relationships, orient-before-write
- **[Ingest]** — five-pass pipeline from a raw source to updated synthesis
- **[Query]** — answer from the wiki; persist only reusable results; research to fill a named gap
- **[Audit-Lint]** — structural fixes, semantic investigation, ~20-page cadence
- **[Anti-Patterns-and-Common-Mistakes]** — overload, skipped lint, RAG-shaped pages
- **[Examples]** — end-to-end ingest → query → lint
- References: [templates](references/templates.md), [quality-gate](references/quality-gate.md)

</wiki-llm>

<Wiki-Structure>
```text
<wiki-root>/
├── raw/                 # immutable originals (PDFs, notes, dumps) — never edit
└── wiki/
    ├── index.md         # scope, topic map, tensions, gaps, recent updates
    ├── sources/         # one evidence page per ingested source
    └── pages/           # one synthesis page per reusable object of understanding
```

This skill is the schema. Do not create `INDEX.md`, `SCHEMA.md`, `log.md`, `concepts/`, `entities/`, or `queries/` unless the wiki already uses them.

If `wiki/` already exists with a different internal layout, keep working in that layout. Do not migrate or create a second tree.

**Layers**
- `raw/` — originals only. Read them; never modify. A source page can exist without a `raw/` file (web, conversation, experiment).
- `wiki/sources/` — faithful extraction: provenance, claims, scope, limitations, integration candidates. Valuable even when no synthesis page is justified.
- `wiki/pages/` — ideas, not documents. Types: `concept`, `entity`, `method`, `comparison`, `synthesis`, `question`. A page must integrate and connect; it must not echo one source.
- `wiki/index.md` — scope, discriminative topic map, open tensions, knowledge gaps, compact recent-update history. Read first; update after every material change. That history is the operation log.

**Initialize** (only when the task needs a wiki and it is absent): create `wiki/index.md`, `wiki/pages/`, `wiki/sources/`. Create `raw/` when storing a local original. Use the index template in [templates](references/templates.md).

**Conventions**
- Lowercase kebab-case filenames. Page name = concept, not source title.
- Links: `[[page-slug]]`, `[[source-slug]]`. Open `wiki/` (not the wiki-root) as an Obsidian vault if a graph view is needed.
- ISO dates `YYYY-MM-DD`. Label unsupported conclusions `Inference:` or `Hypothesis:`.
- Work from the wiki-root so both `raw/` and `wiki/` are reachable.
- Update only this structure unless explicitly told otherwise.

</Wiki-Structure>

<Reasoning-Rules>
1. Separate evidence from synthesis. Source pages state what sources support; pages state the integrated model.
2. Make load-bearing claims traceable to source pages.
3. Preserve claim status where it matters: `established`, `supported`, `provisional`, `disputed`, `inferred`, `unknown`.
4. Preserve disagreement. Name exactly what conflicts and what evidence might resolve it.
5. Repeated assertion is not independent evidence.
6. Preserve applicability boundaries: assumptions, conditions, metrics, dates, population, failure modes.
7. Links encode meaning, not term co-occurrence. Following a link must help answer a realistic future question.
8. Prefer surgical edits. Do not overwrite still-valid synthesis.
9. Missing evidence is a recorded gap, not a license to guess.

**Create a page** when the idea is independently queryable, foundational to other explanations, supported by multiple claims/relations/sources, is an important comparison or mechanism, or needs a durable home for unresolved evidence.

**Merge** when new information sharpens the same definition, mechanism, question, entity, trade-off, or conclusion.

**Do not create a page** for every source, incidental mention, isolated example, temporary answer, or conclusion that belongs on an existing page.

**Split** when a page answers independent questions, is no longer retrievable as one unit, or repeated updates touch only a separable section. Preserve links and update the index.

Material links name the relation and why it matters. Prefer: `is-a`, `part-of`, `requires`, `enables`, `causes`, `mediates`, `measures`, `operationalizes`, `generalizes`, `contrasts-with`, `competes-with`, `contradicts`, `explains`, `applies-to`.

```md
- **Requires →** [[related-page]]: depends on ... Evidence: [[source-slug]].
- **Contrasts with →** [[alternative-page]]: both address ..., but differ in ... Evidence: [[source-a]], [[source-b]].
```

**Orient before every ingest, query, integration, or audit:**
1. Confirm the structure exists; initialize only if the task needs a wiki and it is absent.
2. Read `wiki/index.md`.
3. Search pages and sources for central terms, aliases, and adjacent concepts.
4. Read relevant pages before creating, merging, relating, splitting, or recording a tension.

Never create a page before checking whether the idea already exists under another name or as part of a broader page.

</Reasoning-Rules>

<Ingest>
Ingestion is a reasoning pipeline, not a summary command. Never edit files in `raw/`. Do not paste long copyrighted text — capture metadata, faithful paraphrase, necessary short excerpts, and a pointer to the original (`raw/<file>` or URL).

If asked to ingest the backlog: process `raw/` files that have no source page and are not already recorded in the index recent-updates.

### Pass 1 — Capture source evidence
Create or update `wiki/sources/<source-slug>.md` from the source template in [templates](references/templates.md). Record claims, support, scope, limitations, and integration candidates. Do not blend later inference into source-reported content.

### Pass 2 — Extract what can change understanding
Identify the source's central question, definitions, atomic claims and support, mechanisms, assumptions, applicability boundaries, results, contradictions, gaps, and affected existing concepts. Keep what may alter future reasoning; omit storage-only detail.

### Pass 3 — Map each knowledge unit
Classify before editing synthesis pages: `ignore` | `source-only` | `merge` | `new-page` | `relationship` | `tension` | `gap`.

### Pass 4 — Integrate into pages
For every materially affected page: preserve stable explanation, revise only affected sections, link claims to sources, add semantic relationships, state conflict or narrowed scope, refresh metadata. Create a new page only after the boundary rules. Use the page template in [templates](references/templates.md).

### Pass 5 — Update the index
Update topic-map entries, tensions, gaps, and one compact recent-update item that describes the change in understanding, not only the edited files. Be selective: a typical ingest updates 10–15 pages, not one page per sentence.

After a substantial ingest, run the page quality gate in [quality-gate](references/quality-gate.md).

</Ingest>

<Query>
1. Read the index; identify relevant pages, tensions, and gaps.
2. Read the smallest relevant set of synthesis pages. Use only `wiki/` as the answer source.
3. Verify load-bearing claims through their linked source pages.
4. Answer from the wiki's model with page/source citations.
5. State clearly when evidence is absent, narrow, or conflicting.
6. Note durable new relationships, clarifications, or gaps the query exposed.

Update the wiki from a query only when the result is reusable synthesis: a recurring explanation, comparison, sharpened or resolved tension, or important new relationship. When the task is only Q&A, answer first and propose the durable update rather than silently expanding the wiki.

**Research to fill a gap**
1. Start from a named gap, disputed claim, or question.
2. Seek sources capable of changing the answer: primary records, official docs, papers, datasets, or strong analyses.
3. For contested topics, deliberately seek credible counter-evidence.
4. Ingest each useful source through the full pipeline. Use `gemini-deep-research` for long-running web investigations; use `pdf-to-markdown-mcp` when a PDF must be read before capture.
5. Revise synthesis only after comparing new evidence against the existing model.

Search snippets are leads, not evidence. Read and capture a source before it supports durable wiki claims.

</Query>

<Audit-Lint>
Run after roughly every 20 new pages, or when asked to lint / health-check / audit.

**Fix structural faults directly:** missing required structure, broken `[[links]]`, important pages absent from the index, clear duplicates, metadata that the file itself can correct, orphan pages with no useful relation, and any edit that touched `raw/`.

**Investigate semantic faults before fixing:** source-shaped summaries pretending to be concepts, unsupported or overgeneralized claims, stale conclusions, hidden contradictions, over-broad or over-fragmented pages, meaningless links, missing central pages, stale index descriptions.

Use [quality-gate](references/quality-gate.md) for the full checklist and the seven page-pass tests. Reflect important unresolved findings in the index.

</Audit-Lint>

<Connecting-Skills>
- **Companions**: `gemini-deep-research` when a named gap needs a long-running web investigation; `pdf-to-markdown-mcp` when a PDF in `raw/` must be converted before capture; `experiment-lab-loop` when an experiment produces wiki-worthy findings — ingest the write-up as a source.
- **Successors**: `manage-skills` if this skill itself needs to change.

</Connecting-Skills>

<Anti-Patterns-and-Common-Mistakes>
- **Overloading pages** — one concept per file; split when a page stops being one retrievable unit.
- **Skipping lint** — contradictions accumulate silently; run every ~20 pages.
- **Mixing unrelated topics** — focused wikis produce richer link graphs.
- **Ignoring the index** — every material operation updates `wiki/index.md`.
- **Wrong vault / working directory** — launch from the wiki-root; open only `wiki/` in Obsidian, or the graph mixes PDFs with pages.
- **RAG-shaped pages** — a page that only summarizes one source is a source page, not synthesis.
- **Editing `raw/`** — originals are immutable; only `wiki/` is writable.
- **Silent wiki growth from Q&A** — answer first; persist only reusable synthesis.
- **Decorative links** — no link unless the relation and its evidence are stated.

</Anti-Patterns-and-Common-Mistakes>

<Examples>
Building a transformer-architecture wiki from five papers:

1. Initialize `<wiki-root>/raw/` and `<wiki-root>/wiki/` with empty `index.md`, `sources/`, `pages/`.
2. Drop papers into `raw/`: `attention-all-you-need.pdf`, `bert.pdf`, `gpt3.pdf`, `rlhf.pdf`, `foundation-models.pdf`. Convert PDFs with `pdf-to-markdown-mcp` when the raw file cannot be read directly.
3. Ingest. Each paper becomes `wiki/sources/<slug>.md`. Synthesis pages such as `attention-mechanism.md`, `positional-encoding.md`, `masked-language-modeling.md`, `rlhf.md` are created or updated with typed `[[wiki-links]]` and claim-level source citations.
4. Query: "What's the difference between encoder-only and decoder-only transformers?" Answer from existing pages. If the contrast is reusable, save `wiki/pages/encoder-vs-decoder.md` (`type: comparison`) and update the index.
5. After ~20 pages, lint. A conflict such as `bert` vs `roberta` on pretraining-data size is recorded as a tension on both pages and in the index, not silently averaged.

**Mistake caught:** Obsidian opened on the wiki-root instead of `wiki/` — graph view mixed raw PDFs with pages. Open only `wiki/`.

</Examples>

<wiki-llm-reference>
- [templates](references/templates.md) — index, source page, and synthesis page templates. Read when initializing or creating a new source/page.
- [quality-gate](references/quality-gate.md) — seven page-pass tests, structural vs semantic audit, audit output. Read during lint or before completing a substantial ingest.

After ingest, synthesis update, or audit, report:

```md
## Wiki Update
- Sources captured: <files>
- Pages created: <files or none>
- Pages materially revised: <files or none>
- New or changed relationships: <brief list>
- Tensions or uncertainty preserved: <brief list or none>
- Highest-value next investigation: <one item or none>
```

</wiki-llm-reference>
