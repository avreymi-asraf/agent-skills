# Quality gate and review checklist

Read this before finishing a substantial `add`, and during `review`.

## The claim gate

A new claim passes when a reader who sees only the claim file would agree with each line:

| Test | Passes when |
|---|---|
| One thing | The sentence can be true or false as a whole. No "and" that joins two separable statements. |
| Anchored | There is an evidence item, of a kind the profile accepts. |
| No wider than the anchor | The sentence says what the evidence carries and stops there: same scope, same strength, same conditions. |
| Conditions present | What it was true under is written, or said to be unstated. |
| Findable | The `description` holds the words someone would search for. |
| Not a duplicate | `cortex.py claims --grep` shows no claim that already says this under the same conditions. |

A claim that fails "no wider than the anchor" is the common one. Narrow the sentence; do not look for stronger words in the source. This is the test a blind verifier applies from the output of `cortex.py pairs`: `partial` means it failed here.

## The page gate

A new or heavily revised page passes all of these. Revise a page that fails; do not only record that it failed.

| Test | Passes when |
|---|---|
| Purpose | It answers a question the profile's reader really brings, more than once. |
| Boundary | It is about one idea. It is not one source's summary, and not a fragment of a wider page. |
| Synthesis | It explains, distinguishes or concludes. It does not list what each source said in turn. |
| Grounding | Every load-bearing sentence cites a claim, and the claim says that. Reasoning beyond the claims is labeled. |
| Anchor honesty | A page resting only on `quote` claims says that this is what sources report. |
| Conflict | Disagreement and unknowns are visible, and point to a tension or a question. |
| Findable | Title, aliases and its line in `index.md` let a future reader reach it. |

## Review checklist

Mechanical state first: `cortex.py check`, `cortex.py claims --status provisional`.

**Fix directly** (the cortex's own record settles it):

- broken `[[links]]`; pages, tensions or questions missing from `index.md`, or index lines for files that are gone;
- a page citing a superseded claim, where the newer claim says the same thing more exactly: cite the newer one;
- a `provisional` claim that the record clearly settles (the second source is there; the experiment closed and its postmortem confirms or withdraws it);
- two claims that say the same thing under the same conditions: keep the better-anchored one, mark the other `superseded`;
- two pages for one idea under different names: merge, keep an alias;
- a tension whose sides are no longer both standing: mark it resolved and say by what.

**Investigate before changing:**

- a page that is one source's summary;
- a sentence in a page with no claim under it that the page's conclusion depends on;
- a claim generalized in a page beyond its conditions (another model, another metric, another population);
- a page that leans on a withdrawn claim, where removing it changes the conclusion;
- two pages that disagree and no tension between them;
- a claim nobody cites that bears directly on an existing page or tension;
- a `stated` claim that a source or a measurement could now replace.

**Report and leave** (needs a decision the record does not make):

- a contradiction with no clear loser;
- a claim whose anchor cannot be found or opened;
- a question or a tension whose priority no longer looks right;
- anything about what the cortex is for.

A profile may add checks of its own (a lab's profile adds its journal, its system pages and its experiments). Run them in the same pass.

**Patterns matter more than cases.** The same fault in several places (claims without conditions, pages built from one source, one experiment's settings in the synthesis) means something in how agents write to this cortex should change: usually a line in the profile or a field in a template. Say so in the report, and do not patch each case as if it stood alone.

## Reports

After `add` or `investigate`:

```md
## Cortex update
- Source: <id>, read: <full | partial | abstract only>
- Claims added: <n> (<m> verified pass, <k> partial and rewritten)
- Pages changed: <files, or none>
- Tensions opened or changed: <files, or none>
- Left as claims only: <n>, because <nothing asks for them yet | ...>
- Best next step: <one question to investigate, or none>
```

After `review`, in the user's language:

- **Fixed:** what changed, grouped by kind, with file names.
- **Needs you:** each open item as a question, with the two readings and the evidence for each.
- **Patterns:** a fault that repeats, and what it suggests changing.
- **Not checked:** what the pass could not reach.
