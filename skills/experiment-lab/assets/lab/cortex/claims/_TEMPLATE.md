---
type: claim
status: provisional          # provisional | confirmed | withdrawn | superseded
verified: unchecked          # pass | partial | fail | unchecked
created: YYYY-MM-DD
description: <the words someone planning a different experiment would search for>
---
# <One sentence that can be true or false, written for a reader who has not seen the experiment or the source.>

## Evidence
<!-- Keep the line that applies. -->
- experiment::`<experiment name>` try `<try name>` round <n> @ `<commit>` — <what was measured and on what; the run files are in `notes/<experiment name>/runs/<nn>-<short-name>/` at that commit>
- quote::[[sources/<source-id>]] — <section or page>
  > <verbatim words from the stored text. Use [...] for an omission.>
- stated::<who>, YYYY-MM-DD — <in what context>

## Conditions
<Experiment repo and try branch, model, data and split, metric and evaluation version (`evaluation_version` in the lab step record), what was held fixed. For a quote: the source's own setting. A reader uses this to decide whether the claim applies to their experiment.>

## Relations
- supports::[[claims/<other>]] — <why>
- contradicts::[[claims/<other>]] — <what exactly disagrees; then write the tension>
<!-- `verified` stays `unchecked`: the writer never sets it. How a claim is corrected, and when it no longer may be: `cortex/profile.md` §4. When a checked claim stops holding, change `status` and add one line here:
- withdrawn::after `<experiment name>` try `<try name>` round <n> — <why it did not hold>
- superseded_by::[[claims/<newer>]] — <what the newer claim corrects>
-->
