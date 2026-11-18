---
name: israeli-politics-public-affairs-investigator
description: Investigate, verify, and maintain living primary-source dossiers on Israeli politics and public affairs in a persistent local Markdown vault. Use when the user invokes this skill, says open/update/refactor a dossier, or asks to research an Israeli public, political, legal, economic, security, or institutional affair using official records, Twitter/X leads, and downloaded documents, charts, or maps.
argument-hint: "[open <affair-slug> | update <affair-slug> [focus, claim, or artifact] | refactor <affair-slug>] [vault path]"
---

<israeli-politics-public-affairs-investigator>

This skill builds a durable, truth-seeking investigative dossier from structural roots to present developments. It treats public claims, press summaries, leaked documents, and social posts as leads that must be reconciled with primary evidence.

The persistent vault is `research-vault/` by default, or a user-specified path. Copy the starter vault from [`assets/research-vault/`](assets/research-vault/) when scaffolding a new project. Use [Templates](references/templates.md) for exact dossier forms and [Artifact Audit](references/artifact-audit.md) for visual and geospatial evidence.

Companion skills: use `cortex` for atomic claim pages or cross-dossier knowledge graphs, `pdf-to-markdown-mcp` for high-fidelity PDF extraction, and `gemini-deep-research` only for independently discovered leads that must still be checked against primary text. Use `manage-skills` after changing this skill.

</israeli-politics-public-affairs-investigator>

<action-modes>

Choose one mode from the user's words or `/israeli-politics-public-affairs-investigator` arguments.

### `open <affair-slug>`

1. Choose `<affair-slug>` as a lowercase kebab-case stable identifier.
2. Scaffold `research-vault/affairs/<affair-slug>/brief.md`, `raw-sources.md`, and `assets/`, plus `research-vault/INDEX.md` if absent. The reusable starter files are in [`assets/research-vault/affairs/_TEMPLATE/`](assets/research-vault/affairs/_TEMPLATE/).
3. Base the first pass on the template in [Templates](references/templates.md).
4. Establish the affair's legal, historical, institutional, and economic roots.
5. Write an initial Governing Thesis with confidence, what would falsify it, and a thesis evolution log.
6. Build the stakeholder matrix, source-audit register, and prioritized next-step queue.
7. Record missing facts as questions or leads, never as verified findings.

### `update <affair-slug> [direction]`

With a direction, investigate that claim, quote, leaked image, chart, map, or question.

Without a direction, work the highest-priority items in `brief.md`'s `Active To-Do and Falsification Queue`, then sweep configured Twitter/X MCP sources and official institutional portals.

Update the dossier; do not merely append a dated news summary.

### `refactor <affair-slug>`

Consolidate the living dossier without losing citations, raw quotations, artifact findings, or credibility judgments.

Preserve the `Roots -> Trajectory -> Current State` structure. Split only orthogonal axes into clearly linked subsections, merge duplicates, and move all raw evidence to `raw-sources.md` or `assets/`.

</action-modes>

<vault-and-continuity>

Read `INDEX.md`, then `affairs/<slug>/brief.md`, before every update. Read `raw-sources.md` only when a citation or exact quotation needs checking.

- `brief.md` is the living synthesis and meta-research record.
- `raw-sources.md` is the unabridged evidence archive.
- `assets/` holds downloaded visual evidence.
- `INDEX.md` maps active affairs, status, thesis summaries, cross-affair links, and global research priorities.

Preserve external URLs and capture dates in source records. A local file does not replace a citation; every finding needs a source and retrieval date.

</vault-and-continuity>

<investigation-loop>

Use a deliberate `Gather -> Ingest Full Source -> Mine Leads -> Re-Query` loop.

1. **Frame the lead.** Copy the exact claim, named actors, date, place, docket or document number, and how the source was encountered.
2. **Capture the source.** Download the full bill, ruling, committee protocol, government resolution, letter, dataset, chart, or map. Do not rely on a search snippet or press summary.
3. **Read the full text.** Follow footnotes, citations, schedules, statutory cross-references, and minor actors until the operative text is visible.
4. **Verify provenance.** Confirm the issuing authority, version, date, signatories, docket number, authentication, and whether a draft or final is in hand.
5. **Mine its dependencies.** Extract follow-up queries, protocols, datasets, original tables, attachments, and competing official versions.
6. **Triangulate.** Require independent or structurally distinct evidence for important conclusions. Repeating the same press line does not add a source.
7. **Audit incentives.** Separate what an actor declares, what survival or legal authority requires, and what binding votes, budgets, resolutions or actions show.
8. **Fuse and re-thesis.** Reconcile the evidence with the Governing Thesis. Preserve uncertainties and explicitly state evidence that weakens or falsifies it.

Stop only when the remaining queue contains genuinely unavailable records or newly bounded follow-up questions. Never convert absence of evidence into proof of a claim.

</investigation-loop>

<source-grading>

Use these tiers consistently.

| Tier | Source class | Examples |
|---|---|---|
| 1 | Primary official records | Enacted laws, Knesset plenary and committee transcripts, Supreme Court/HCJ and lower-court rulings, Government Resolutions, Attorney General opinions, State Comptroller reports, CBS and Bank of Israel datasets, authenticated official maps |
| 2 | Corroborated investigative | Multi-source investigations, verified leaks cross-checked to official records, peer-reviewed studies |
| 3 | Partisan, spin, or unverified | Spokesperson briefings, anonymous leaks without documentary proof, partisan framing, uncorroborated social claims |

Apply a `T1/T2/T3` tag and a confidence note to every significant claim. An official source can still be incomplete or strategically framed, and an investigative source can become stronger through primary corroboration.

**Anti-Echo Rule:** ten outlets repeating one anonymous brief are one weak Tier 3 lead, not ten confirmations.

</source-grading>

<twitter-and-x>

Treat all tweets as leads, never proof.

When Twitter/X MCP is available:

- search Hebrew, English, and relevant local-language terms;
- hunt for drafts, official letters, budget tables, court filings, and authenticated maps;
- inspect quote-tweets and replies for omitted clauses or specialist critiques;
- use post timestamps and account context to identify the original document and actor.

When X MCP is unavailable or a result cannot be retrieved, state that limitation. Record promising leads with account, post URL, timestamp, exact wording, and the Tier 1 source needed to verify it. Do not present an inferred screenshot or quote as primary evidence.

Twitter leads often disappear; download and transcribe their artifacts according to [Artifact Audit](references/artifact-audit.md).

</twitter-and-x>

<visual-evidence>

Any relevant downloaded image, document scan, chart, PDF page, or map belongs in `assets/` and must be logged in `raw-sources.md`.

Name files `YYYY-MM-DD_<source>_<short-slug>.<ext>`. Use the original capture date when publication date and capture date differ.

For each artifact:

- record issuing authority, version, public URL, capture date, and local path;
- extract exact text or data, including axes, units, baselines, dates, sample sizes, docket numbers and signatories;
- compare with the full primary source and competing official versions;
- report chart distortion, missing layers, coordinate or boundary discrepancies, redactions, OCR uncertainty, and what the image cannot establish.

Follow [Artifact Audit](references/artifact-audit.md). Do not rely on hotlinks or leave media available only in a conversation.

</visual-evidence>

<zero-append-fusion>

Rewrite the existing analytical prose. Never tack dated news bullets onto the bottom of `brief.md`.

Each update should:

1. revise the relevant paragraph under Roots, Trajectory, or Current State;
2. add or retire a subsurface insight with its evidence;
3. update stakeholder incentives and rhetoric-versus-record gaps;
4. update confidence and falsification conditions for the Governing Thesis;
5. append a concise evolution entry describing what evidence changed the interpretation;
6. replace completed queue items with specific next leads;
7. update cross-affair links and `INDEX.md`.

Use grounded labels: `Confirmed`, `Corroborated`, `Disputed`, `Inferred`, `Unverified`, or `Not established`.

</zero-append-fusion>

<quantitative-checks>

Where the affair concerns elections, budget passage, coalition survival, or policy deadlines and real-money prediction markets are available, record market-implied probability, timestamp, venue, contract wording, and order-book depth. Treat it as one data point, not an oracle. Check whether its settlement rules match the factual question.

For charts and datasets, distinguish nominal from real values, raw counts from rates, one-off from annualized figures, and the publication revision from the underlying vintage.

</quantitative-checks>

<git-checkpoint>

Commit the vault with a clean, factual checkpoint:

```bash
git add research-vault
git commit -m "vault(<affair-slug>): <concise finding and thesis change>"
```

Include co-authored commit trailers only if repository policy requires and the user has not forbidden it.

After committing, report: records verified, principal change to the thesis, unresolved leads, local artifacts added, and cross-affair links updated.

</git-checkpoint>

<examples>

**Open:**

`open judicial-reform-2023`

Create the vault, establish the constitutional, statutory, and coalition roots, identify the final and draft texts that matter, and make the first Governing Thesis falsifiable.

**Directed update:**

`update coalition-budget-2024 "A chart claims defense spending rose 40%; verify the series"`

Download the chart, extract its exact series and baseline, retrieve the CBS or budget source, correct the interpretation, and revise the governing narrative.

**Routine update:**

`update netanyahu-trial`

Read the queued ledgers and current case protocols, sweep official court records and Twitter/X leads, download new filings or maps, update the thesis, and commit.

</examples>

<israeli-politics-public-affairs-investigator-scripts>

No scripts are required. Downloads and visual extraction should use established CLI or Python tools and preserve local provenance.

</israeli-politics-public-affairs-investigator-scripts>

<israeli-politics-public-affairs-investigator-reference>

- [Templates](references/templates.md): exact `brief.md`, `raw-sources.md`, `INDEX.md`, and asset metadata forms.
- [Starter Vault](assets/research-vault/): copyable project structure with dossier templates and an `assets/` placeholder.
- [Artifact Audit](references/artifact-audit.md): document, chart, and map verification procedure.

</israeli-politics-public-affairs-investigator-reference>
