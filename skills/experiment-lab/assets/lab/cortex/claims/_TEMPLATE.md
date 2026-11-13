---
type: claim
status: provisional          # provisional | confirmed | withdrawn | superseded
verified: unchecked          # pass | partial | fail | unchecked. Never set by the writer.
created: YYYY-MM-DD
description: <the words someone looking for this knowledge would search for>
---
# <One sentence that can be true or false, written for a reader who has seen neither the source nor the experiment.>

## Evidence
<!-- Keep the line that applies. A claim can have several evidence items. -->
- quote::[[sources/<source-id>]] — <section or page>
  > <verbatim words from the stored text. Use [...] for an omission.>
- experiment::`<experiment name>` try `<try name>` round <n> @ `<commit>` — <what was measured and on what; the run files are in `notes/<experiment name>/runs/<nn>-<short-name>/` at that commit>
- stated::<who>, YYYY-MM-DD — <in what context>

## Conditions
<The setting the claim holds under. For a quote: the source's own setting (model, data, scale, domain, year). For an experiment: experiment repo and try branch, model, data and split, metric and evaluation version (`evaluation_version` in the lab step record), what was held fixed. A reader uses this to decide whether the claim applies to their case.>

## Relations
- supports::[[claims/<other>]] — <why>
- contradicts::[[claims/<other>]] — <what exactly disagrees; then write the tension>
<!-- How a claim is corrected, and when it no longer may be: `cortex/profile.md` §4. When a checked claim stops holding, change `status` and add one line here:
- withdrawn::<the source, or `<experiment name>` try `<try name>` round <n>> — <why it did not hold>
- superseded_by::[[claims/<newer>]] — <what the newer claim corrects>
-->
