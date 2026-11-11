# Cortex templates

Read this when starting a cortex or writing a node of a kind for the first time. The forms are defaults: a cortex's `profile.md` may rename folders and page types, and then its names are the ones to use.

Files are lowercase kebab-case. A claim's filename is its sentence, shortened. Dates are `YYYY-MM-DD`. Files whose name starts with `_` are templates and are skipped by `cortex.py`.

## `profile.md`

The default, for a reading knowledge base. Fill the first section in the owner's words; a guess there steers every later write.

```md
# Cortex profile

> What this cortex is. Read before any operation. Where this file and the `cortex` skill differ on a name or a place, this file wins.

## 1. What the synthesis is for
[The question a reader brings here, in the owner's words. It is the test for what is worth writing: a claim or a page earns its place when it changes what that reader understands or decides. What is in scope, and what is not.]

## 2. Layout
| Layer | Where | Notes |
|---|---|---|
| Sources | `../sources/`: `raw/` originals, `text/` extracted text, `<source-id>.md` notes | Never edited |
| Claims | `claims/` | One per file |
| Synthesis | `pages/` (concept, method, comparison), `tensions/`, `questions/` | Cite claims |
| Map | `index.md` | One line per page, tension and question |

## 3. Anchors
| Anchor | Accepted | What it earns here |
|---|---|---|
| `quote` | Yes | The source says it. A page resting only on quotes says so. |
| `experiment` | [Yes / No] | |
| `stated` | [Yes / No] | |

A claim moves from `provisional` to `confirmed` when: [a second independent source supports it | it was used and held | ...].

## 4. Checking
`cortex.py check` passes before every commit. Blind verification of new claims: [always | for claims a page will cite | never].

## 5. Moments
Fusion happens at the end of every `add`. A review runs [every ~20 claims | before a decision that leans on the cortex].
```

## Claim: `claims/<the-claim-shortened>.md`

```md
---
type: claim
status: provisional          # provisional | confirmed | withdrawn | superseded
verified: unchecked          # pass | partial | fail | unchecked
created: YYYY-MM-DD
description: <search words: the terms someone looking for this would type>
---
# <The claim, as one sentence that can be true or false, with the conditions that belong in it.>

## Evidence
- quote::[[sources/<source-id>]] — <section, page or timestamp>
  > <verbatim words from the stored text. Use [...] for an omission.>
- experiment::`<experiment name>` round <n> @ `<commit>` — <what was measured, and with what>
- stated::<who>, YYYY-MM-DD — <in what context>

## Conditions
<What this was true under: model, data, metric and its version, population, date. "None stated in the source" is an answer.>

## Relations
- supports::[[claims/<other>]] — <why, and whether the evidence is independent>
- contradicts::[[claims/<other>]] — <what exactly disagrees>
- refines::[[claims/<other>]] — <narrower conditions, or a more exact statement>
```

One anchor kind per claim is the normal case; keep only the lines that apply. When the claim stops holding, change `status` and add one line to Relations. `check` requires it:

```md
- superseded_by::[[claims/<newer>]] — <what the newer one corrects>
- withdrawn::<why, and after what: an experiment and round, a source, a review>
```

## Source note: `sources/<source-id>.md`

The note is what `quote::[[sources/<source-id>]]` points at. `check` looks for the quoted words in this file and in `sources/text/<source-id>.*`, so the text that was read must be in one of them.

```md
---
type: source
kind: paper | article | docs | transcript | dataset | code | conversation | other
origin: "<authors or organization>"
published: YYYY-MM-DD | unknown
captured: YYYY-MM-DD
location: "<URL, or sources/raw/<file>>"
read: full | partial (<which parts>) | abstract only
reliability: primary | secondary | informal | unknown
---
# <Title>

**What it is and what it can establish:** <two or three sentences. What it measures or argues, and what it cannot tell us.>

**Limits:** <single preprint, one dataset, no code, vendor-written, ...>

## Text
<The extracted text, or: "Full text in `sources/text/<source-id>.md`". Long copyrighted text stays out of a public repo: keep the passages that claims quote, with their section names.>
```

## Page: `pages/<idea>.md`

```md
---
type: concept               # or the type names the profile uses: method, comparison, finding, ...
status: developing          # stub | developing | stable | contested
updated: YYYY-MM-DD
aliases: [<other names for the same idea>]
---
# <The idea>

## In short
<What a reader should take away, in a few sentences. Every load-bearing sentence ends with its claim: ([[claims/<claim>]]).>

## How it works / what distinguishes it
<The explanation: mechanisms, distinctions, conditions. Cite claims. Mark reasoning beyond them as `Inference:` or `Hypothesis:`.>

## Where it stops holding
<Conditions under which the claims were made, known failures, what must not be concluded.>

## Open
- tension::[[tensions/<tension>]] — <one line>
- question::[[questions/<question>]] — <one line>

## Related
- contrasts_with::[[pages/<other>]] — <both address ..., and differ in ...>
```

Adapt the middle headings to the type. A comparison uses the dimensions compared; a method uses preconditions, procedure and failure modes.

Relation names in common use: `is_a`, `part_of`, `requires`, `enables`, `causes`, `measures`, `generalizes`, `contrasts_with`, `competes_with`, `explains`, `applies_to`.

## Tension: `tensions/<the-question-in-dispute>.md`

```md
---
type: tension
status: open                # open | narrowed | resolved
created: YYYY-MM-DD
description: <search words>
---
# <The disagreement, as a question.>

<Two or three sentences: what each side reports.>

## Sides
- supports::[[claims/<claim-a>]] — <side A, with its conditions>
- contradicts::[[claims/<claim-b>]] — <side B, with its conditions>

## What might explain it
<The differences in conditions between the sides: model, scale, metric, data, date.>

## What would settle it
<The measurement or the source that would decide. This is a lead for `investigate`, or for an experiment.>
```

When it is settled, set `status: resolved`, say by which claims, and keep the file.

## Question: `questions/<the-question>.md`

```md
---
type: question
status: open                # open | narrowed | answered
created: YYYY-MM-DD
asked_by: <the user | a page | an add | a review>
---
# <The question.>

## What we have
- bears_on::[[claims/<claim>]] — <how>

## What is missing
<What kind of source or measurement could answer it.>

## Searched
<What was looked for and where, with dates, so the next search starts further on.>
```

## `index.md`

```md
# Cortex index

> One line per page, tension and question: what it helps answer. Updated in the same commit as the change. Claims are not listed here; find them with `cortex.py claims`.

## Pages
- [[pages/<idea>]]: <the question it helps answer>

## Open tensions
- [[tensions/<tension>]]: <one line>

## Open questions
- [[questions/<question>]]: <one line>
```
