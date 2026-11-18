# Dossier templates

Use these forms when scaffolding or refactoring a dossier. Keep `brief.md` dense and cohesive; keep full evidence in `raw-sources.md`.

## `research-vault/INDEX.md`

```md
# Research Vault Index

## Active Affairs

| Affair | Status | Governing Thesis | Cross-Affair Links | Last Updated |
|---|---|---|---|---|
| `affair-slug` | active / monitoring / dormant / resolved | 1-2 line summary | `other-affair` | YYYY-MM-DD |

## Global Research Queue

- [ ] <specific document, protocol, dataset, or question>

## Cross-Affair Linkages

- `affair-a` <-> `affair-b`: <binding mechanism or evidence relationship>
```

## `affairs/<affair-slug>/brief.md`

```md
# <Affair Title>

**Slug:** `<affair-slug>`
**Status:** active / monitoring / dormant / resolved
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Primary Jurisdiction:** <Country/Legislature/Court/Agency/Municipality/...>

## Research Meta

### Governing Thesis

**Confidence:** low / medium / high / contested

<Two or three paragraphs synthesizing the strongest supported explanation. State what it does not claim.>

**Falsification Criteria**

- <A record, result, or event that would weaken or falsify the thesis.>

**Thesis Evolution Log**

| Date | Evidence or Interpretation Change | Thesis Effect |
|---|---|---|
| YYYY-MM-DD | <what changed> | <confirmed / narrowed / weakened / rejected> |

### Source Credibility and Vested-Interest Audit

| Actor or Source | Tier | Reliability | Proximity | Structural or Financial Bias | Known Corrections |
|---|---|---|---|---|---|
| <name> | 1/2/3 | high/medium/low | primary/secondary/remote | <incentive> | <prior errors or omissions> |

### Stakeholder Matrix

| Actor | Declared Position | Structural Incentive | Binding Record | Rhetoric vs. Record Gap |
|---|---|---|---|---|
| <actor> | <what they say> | <what survival/law/finance requires> | <vote/law/budget/ruling/action> | <none or precise gap> |

### Active To-Do and Falsification Queue

1. [ ] <highest-priority primary record or counter-hypothesis>
2. [ ] <lead and exact portal or X account>
3. [ ] <visual artifact or map comparison>

## Roots

<Foundational law, history, institutions, budgets, territorial or demographic structures, and earlier decisions that created the affair.>

### Subsurface Insights

- **<Insight title>:** <non-obvious finding, source-grade confidence, and citation>.

## Trajectory

<How the roots interacted over time, which reforms or interventions mattered, and how actors changed position or control.>

## Current State

<Present institutional status, operative law or court posture, coalition or public stakes, and the best-supported near-term scenarios.>

## Evidence Ledger

| ID | Claim | Tier | Status | Primary Anchor | Confidence | Last Checked |
|---|---|---|---|---|---|---|
| E001 | <one falsifiable claim> | 1/2/3 | confirmed/corroborated/disputed/inferred/unverified | `raw-sources.md#...` | high/medium/low | YYYY-MM-DD |

## Cross-Affair Linkages

- **`other-affair`:** <mechanism, shared actor, precedent, budget, or legal pathway>
```

## `affairs/<affair-slug>/raw-sources.md`

```md
# Raw Sources: <Affair Title>

## Source Protocol

Use one entry per primary source or important artifact. Full verbatim text belongs here. Search summaries and tweets are leads unless independently corroborated.

## Sources

### S001 - <Document or ruling title>

- **Type:** primary official / investigative / partisan / social lead
- **Tier:** 1 / 2 / 3
- **Issuer or Account:** <name>
- **Published:** YYYY-MM-DD
- **Captured:** YYYY-MM-DD
- **Version:** draft / final / amended / post
- **URL:** <stable URL>
- **Local Copy:** `assets/<filename>` if applicable
- **Document/Docket Number:** <value or not shown>
- **Read:** full / partial
- **Provenance Notes:** <authentication, missing pages, translation, OCR, or leak caveats>
- **Can Establish:** <what this source proves>
- **Cannot Establish:** <limits>

#### Verbatim Extract

> <Full operative clause or complete relevant passage>

#### Analytical Note

<Tie the passage to a claim and explain its limits.>

#### Follow-Up Leads

- [ ] <specific record or query>

## Visual Artifacts

### V001 - <Filename>

- **Source:** S001 / external URL
- **Artifact Type:** document scan / chart / map / social screenshot
- **Issue Date:** YYYY-MM-DD
- **Captured:** YYYY-MM-DD
- **Local Path:** `assets/YYYY-MM-DD_<source>_<slug>.<ext>`
- **Issuing Authority:** <name>
- **Legend/Axes:** <exact legend or axes>
- **Extraction:** <verbatim text or exact data>
- **Distortion/Integrity Audit:** <methodology, omissions, baseline, resolution or geospatial caveats>
- **Primary Corroboration:** <S-number or missing>
- **Interpretation:** <what the artifact supports and does not support>
```
