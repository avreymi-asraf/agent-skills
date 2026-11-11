# Reject journal

A record of every time the user rejected the system's work, and what was learned from it. Keeping it is not optional: every reject handled with this skill gets an entry.

## Why it exists

- **Memory.** The same root comes back months later in different clothes. Without a record it looks new, and gets a new plaster.
- **Honesty about fixes.** An entry says what was changed and how it was checked. A root that returns after being "fixed" shows that the fix missed.
- **Evidence of growth.** "The system can take harder requests now" is otherwise a feeling. The journal shows which kinds of requests used to come back wrong and now come back clean. The user decides what to hand over next with this in front of them.
- **Protection.** Before changing content in some area, the entries for that area show which paragraphs are there because of a root that was once found. They don't get simplified away by accident.

## Where it lives

In the repo of the system being grown, outside what working agents receive: `.grow-autonomy/rejects.md` is a reasonable default. Nothing in the instruction files links to it. Its first line says what it is:

```
# Reject journal. A record for the user and for whoever maintains the system's content. Not instructions.
```

Working agents don't read it, and entries never become rules. The journal remembers incidents so that the content doesn't have to.

When it gets long, split by year or by area. Don't delete entries.

## An entry

```
## 2026-11-12 · Proposed selling the hedge

- Request: the user's words, verbatim, in the language they used.
  How much it left to the system: one line.
- What the system did: the part that was rejected, and which agent decided it.
- Reject: the user's words, verbatim.
- What the agent had: what had reached the deciding agent by then, and what had not.
- Belief: one sentence. What it believed that made this look right.
- Root: why it believed that.
- Neighbors: two or three other mistakes the same root would produce.
- Change: what was changed and where (content, tool, template, protocol, the cut of the work).
- Check: how the change was tested and what happened.
```

How to keep it:

- **Write the first three lines when the reject arrives**, before looking for a cause and before fixing anything. Fill in the rest as it is found.
- **Keep the user's words as they were said**, in their language. A translation or a tidy paraphrase is already an interpretation, and the gap between what was said and what was understood is often the root.
- **Unknown is a valid value.** "Root: unknown", "Change: none yet", "Check: not tested" are honest entries. An invented root is worse than an open one, because it closes the question.
- **Small rejects count.** A reject on a one-line request often has the same root as a later failure in a wide one, and it is much easier to read.
- **A reject that repeats gets a new entry** that points to the old one. Don't edit the old one to look right.

## Reading it

From time to time, and always before a change in an area that has entries, read the journal for patterns:

- **A root that returns.** The earlier fix didn't reach it, or it reached one agent and the root lives in another.
- **Many rejects around one word.** The term means different things to different readers ([Shared-meaning] in the skill).
- **Many rejects at one handoff.** The brief or the report at that point drops something. The fix is a protocol ([Attention](attention.md)).
- **Rejects with "what the agent had: everything".** The knowledge arrived and still wasn't used. It was probably buried, or contradicted by an example.
- **By size of request.** Which kinds of wide requests produce rejects, and which have stopped producing them. Tell the user what you see; it is their evidence for what to ask next.
- **Open entries.** Roots still unknown, changes never checked. These are debts.

A report to the user from the journal should be short and in their language: what keeps coming back, what stopped, what is still open.
