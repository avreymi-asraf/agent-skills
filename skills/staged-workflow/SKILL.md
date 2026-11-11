---
name: staged-workflow
description: Grow an agent workflow toward real autonomy (running experiments, investing, operating a business) in stages - from small, reviewed steps to independent work - by shaping the agent's context and fixing the root cause behind every rejection instead of patching it. Load when designing or evolving such a workflow, when reviewing and rejecting an agent's output, when editing the docs/instructions an agent works from, or when deciding whether to give an agent more autonomy.
---

# Staged workflow building

A workflow that does valuable work on its own is not written in one go. It is grown.
At first the agent takes baby steps: narrow asks, every output reviewed, many rejections.
As it earns trust, the steps get bigger and the reviews get rarer. The aim is always
the far end, even while we are far from it.

## Three things to hold at once

**1. The destination.** Write down what the system should do when it is fully grown,
in concrete terms: "proposes, runs and analyzes its own experiments, and decides what
to try next". Every piece of content is judged against this, not against today's task.

**2. The current stage.** How much we let the agent do *right now*: what we ask, what
tools it has, how often we review. This is a dial, not a design. It should live in
a thin, separate place (a stage note, the task prompt, permissions) so it can be turned
up without rewriting anything else.

**3. The content system.** Everything the agent reads: instructions, skills, docs,
memory, examples, comments. This is where its understanding lives, so this is what we
actually build. It describes the domain, the goal and how to think about it - written
for the destination, even if today the agent only uses a slice of it.

A common mistake is to mix 2 into 3: core docs full of "only do X, never touch Y,
always ask first". Those docs then fight every later stage and teach the agent that the
job is obeying limits, not understanding the work.

## The stages (an illustration, not a ladder to follow)

| Stage | What the agent does | What we do |
| :--- | :--- | :--- |
| Assist | Proposes; a human acts | Read everything, reject a lot |
| Single steps | Does one bounded step | Review every output |
| Sequences | Runs several steps to a checkpoint | Review at checkpoints |
| Loop | Runs the full cycle | Review outcomes and samples |
| Own direction | Chooses what to work on next | Review direction and results |

Move up when the evidence says so: rejections become rarer, smaller, and about taste
rather than understanding. A good way to collect that evidence is *shadow mode* - at
each stage, have the agent also say what it would do at the next stage (which experiment
it would run next, which position it would open), and compare with what the human chose.

## Build capability ahead of permission

The agent should be ready for the next stage before it gets there. Even when it is
not allowed to write code alone, it can explain its plan, predict the result, name what
would prove it wrong, and record what it learned. That is the thinking an autonomous
experimenter needs, practiced while the stakes are low. When the permission comes, the
skill is already there.

So when writing content, ask: *does this teach the agent to understand the work, or only
to complete today's step?*

## Rejections are the main signal

Every rejection says something about the agent's model of the work. The question is
never "how do I stop it from doing this?" but **"what did it believe that made this
look right?"**

### Don't patch

The tempting fix is a patch: the agent did X, so we add "Don't do X". Agents love
doing this when asked to fix something. It is bad because:
- **It doesn't solve the problem.** The belief that produced X is still there, and will
  produce X's neighbors tomorrow.
- **It rots the content.** Patches pile up, contradict each other, bury the real ideas,
  and turn a document that explains the world into a list of scars.
- **It's ugly.** We want content we are proud to read, same as code.

### Trace the context path

Before deciding what to fix, reconstruct what the agent actually saw and how it got
there. Text that exists in the repo is not text the agent read. For the rejected output:
- **What was in context at that moment?** Always-loaded instructions, the task prompt,
  a skill it triggered, files it opened, tool output, memory, what a parent agent
  passed down to a subagent.
- **Where did the belief come from?** Find the text that taught it, or notice there is
  none and the agent filled the gap with a generic default.
- **Did the right knowledge exist but not arrive?** No trigger, no link pointing to it,
  loaded too late, buried in noise, lost in a handoff summary.

This needs a picture of the project's information flow: what is always loaded, what
loads on a trigger, what is reached only by a link or a search, and what each subagent
starts with. Keep that picture explicit, as a short map in the docs, because it is part
of the design. The same text in a different place is a different fix: a concept every
task needs belongs where it is always seen; a narrow procedure belongs behind the
trigger that needs it.

The flow changes with the stages. Early on, a human hands over most of the context in
the prompt. As autonomy grows, the agent has to find what it needs on its own, so the
paths to knowledge must be built before they are needed. Otherwise a fix that worked
because it sat in the prompt quietly disappears at the next stage. To build that map for a set of tasks and test
that it works, read [references/context-flow-review.md](references/context-flow-review.md).

### Find the root

Look for what was missing or wrong in what the agent saw. Typical roots:
- A concept was never explained (the agent didn't know what makes evidence strong).
- The goal wasn't stated, so it optimized for the wrong thing (finishing vs. learning).
- Two texts disagree, or an example teaches the opposite of the rule.
- The right knowledge exists but didn't reach the agent when it needed it.
- The ask itself was ambiguous, or bigger than the stage allows.

Fix it where it lives: rewrite the explanation, state the goal, fix the example, remove
the contradiction. Often the right fix *removes* text.

### The neighbors test

A mistake is one sample from a family. The wrong belief behind it will produce other
mistakes in other tasks, and more of them as the agent gets more freedom. A patch
blocks the one sample; a root fix removes the family. So before accepting a fix:

1. **Name the belief** in one sentence. If you can't, you're still looking at the symptom.
2. **List its neighbors:** what else would an agent holding this belief get wrong?
   Look sideways (other tasks, other inputs) and forward (what would it do with the
   next stage's freedom?). Three or four are enough.
3. **Read the fix against them.** Would an agent reading the new content avoid each one
   without being told about it? If the fix only names the original mistake, it's a patch.
4. **Try a neighbor.** When it's cheap, give the agent a fresh task that invites one of
   them and see what it does. The rejection was the training example; a fix that only
   passes it has overfit.

The test cuts the other way too: a good fix doesn't forbid the neighbors that are fine.
If the new content stops the agent from doing something reasonable, it went too broad.
The fix should explain *why*, so the agent can tell the cases apart itself, not build
a bigger fence.

### Example

An investing agent writes a thesis on a company and leans on the company's own press
release. Rejected.
- Patch: "Do not use press releases as sources." Next week it leans on an analyst note
  paid for by the company.
- Belief: "a published claim about the company is evidence for the thesis".
- Neighbors: a paid analyst note; a viral thread repeating the company line; good news
  everyone already knows; and, at the next stage, buying because a story is popular.
- Root fix: the content never explained that a thesis is a claim *against* the market,
  so evidence counts only if it is independent and not already priced in. Add that idea
  to the core doc on how theses are built. Every neighbor is covered, a press release is
  still fine for checking a launch date, and the agent is a step closer to judging
  sources on its own.

## Keeping the content aligned

As the workflow grows, the content drifts: old stage limits stay behind, docs stop
matching reality, new ideas get bolted on instead of woven in. Every so often, and
always before raising the stage:
- Read the content as the agent would, cold. Does it point toward the destination?
- Run `/audit-consistency` with the destination as the focus, to find contradictions,
  stale facts, patches, and knowledge nothing points to.
- Look back at recent rejections. Recurring kinds point to a root not yet fixed.

A short rejection log helps: what was rejected, the root cause, and where it was fixed.
Over time it shows whether the agent is learning, or whether we're just patching.
