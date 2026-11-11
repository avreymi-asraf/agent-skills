---
name: review-wiki
description: Periodic review of a research lab's compiled knowledge (wiki-llm, JOURNAL.md) - checks that it is well built, well linked and still true, fixes what the evidence settles, and reports what needs the user. Use when the user asks to review, check, clean, lint or verify the wiki or the lab journal, when it is run on a schedule, after several experiments have closed, or before a wide request that will choose a research direction from the wiki.
---

<review-wiki>

# Review the wiki

Every experiment starts by reading the lab's compiled knowledge: `wiki-llm/` and `JOURNAL.md`. A wrong or buried claim there quietly steers every later experiment, and nobody sees it happen. This skill is one pass over that knowledge, run from time to time, that asks three questions: is it **well built**, is it **well linked**, and is it **still true**?

The pass reads a lot and returns little, so run it in a fresh context (a subagent, or a session of its own). It follows the lab's `AGENTS.md` for vocabulary and rules.

- **[What-good-looks-like]**: the standard the pass measures against.
- **[The-pass]**: what to read and what to check.
- **[Fix-or-report]**: which problems to fix and which to bring to the user.
- **[Report]**: what to hand back.

Companion skills: `experiment-lab-loop` (how claims get into the wiki, and the provisional mark this pass follows up), `audit-consistency` (the same kind of check for instructions and docs; this skill is for knowledge), `grow-autonomy` (when the pass keeps finding the same kind of problem, the cause is in how agents write to the wiki, not in the wiki).

</review-wiki>

<What-good-looks-like>

A reader who has never seen the experiments opens the wiki to choose what to do next. It serves them when:

- **Every claim can be traced.** It names its source: an experiment (and round), or a literature note. A claim from literature says so and is not presented as something the lab verified.
- **Every claim says how sure it is.** Provisional, confirmed, withdrawn, superseded. A number says what it was measured with.
- **One thing is said once.** The same lesson is not written in three pages in three wordings, and two pages do not disagree.
- **It holds what others need and no more.** A page is about what a different experiment should know, not one experiment's settings and debugging; those belong in that experiment's log, next to its code.
- **The routing pages match the content.** `index.md` lists the pages that exist. `gap_map.md` lists questions that are really open. `JOURNAL.md` Sparks point at gaps and experiments that exist, the Frontier matches the experiments' `results.json`, and the Banlist entries carry their "unless" condition.
- **System pages describe the code as it is.**

</What-good-looks-like>

<The-pass>

1. **Mechanical state first**, from the lab root:
   ```bash
   uv run scripts/lab.py sync-repos     # so system pages can be compared with the code
   uv run scripts/lab.py check-drift    # system pages whose monitored code changed
   ```
2. **Read all of it**: `wiki-llm/index.md`, `purpose.md`, `gap_map.md`, every page in `systems/` and `findings/`, the titles and theses of `literature/`, `JOURNAL.md`, and every `experiments/*/postmortem.md` and `results.json`.
3. **Built.** For each findings and system page: does each claim have a source and a status? Is anything stated as lab-verified that only comes from a paper? Is there one experiment's detail that no other experiment needs? Is a page so long that its main points are buried?
4. **Linked.** Do all `[[links]]` resolve to a page or an experiment? Does `index.md` match the files on disk in both directions? Does every closed experiment in the journal's matrix appear in the pages its postmortem says it updated? Are there pages nothing points to?
5. **True.** This is the part that needs judgment.
   - *Provisional claims whose experiment has closed*: the postmortem should have confirmed or withdrawn each one. Find the ones left hanging.
   - *Contradictions*: two pages, or a page and a postmortem, that say different things. Later evidence usually wins, but check what each was measured on.
   - *Claims a later experiment overturned* without the page being marked `Superseded`.
   - *Numbers*: do Frontier numbers match `results.json`, and were compared numbers measured with the same `eval_script_sha`?
   - *Gaps*: is a gap listed as open that an experiment has answered? Did an experiment reveal a question that is on no list?
   - *Drifted system pages*: read the diff that `check-drift` points at and see what on the page is no longer so.
   - *Stale Sparks and Banlist entries*: a Spark already done or made pointless; a Banlist entry whose "unless" condition has since changed.

To check a claim against its source, read the experiment's postmortem in the lab. For more, the plan and log are in `notes/<exp-name>/` on the experiment's branch in the target repo (`uv run scripts/lab.py mount-exp --exp <id>`).

</The-pass>

<Fix-or-report>

**Fix it yourself** when the evidence in the lab settles it:

- broken links, index entries, dates, the `Updated` fields;
- a missing source on a claim whose source is clear from the experiments;
- a provisional claim that its experiment's postmortem clearly confirms or withdraws;
- a Frontier number that disagrees with `results.json`;
- duplicates: keep the better-sourced wording in one place and link to it from the others.

Never delete a claim silently. An overturned claim stays, marked `Status: Superseded by [[<exp-name>]]` or `Status: Withdrawn after [[<exp-name>]]`, with the reason. Experiment folders are evidence; do not edit them.

**Report it and leave it** when it needs a decision the lab's evidence does not make:

- two results that contradict each other and neither is clearly wrong;
- a claim with no traceable source that might still be true;
- a gap or a Spark whose priority no longer looks right;
- anything about what the lab is for (`purpose.md`).

Append one line to `wiki-llm/log.md`: `## [YYYY-MM-DD HH:MM] review | wiki — <what was fixed, how many items reported>`. Commit the fixes as one commit so the review can be read, or undone, as a whole.

</Fix-or-report>

<Report>

Short, for the user, in their language:

- **Fixed**: what changed, grouped by kind, with page names.
- **Needs you**: each open item as a question with the two readings and the evidence for each.
- **Patterns**: the same kind of problem appearing in several places (for example, lessons that keep landing in the wiki with one experiment's settings attached). A pattern is a sign that something in how experiments write to the wiki should change; say so, and do not patch each case as if it were alone.
- **Not checked**: what the pass could not reach (for example, a target repo that could not be cloned, so system pages were not compared with the code).

</Report>
