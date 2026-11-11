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

### Find the root

Look for what was missing or wrong in what the agent saw. Typical roots:
- A concept was never explained (the agent didn't know what makes evidence strong).
- The goal wasn't stated, so it optimized for the wrong thing (finishing vs. learning).
- Two texts disagree, or an example teaches the opposite of the rule.
- Important knowledge exists but nothing leads the agent to it.
- The ask itself was ambiguous, or bigger than the stage allows.

Fix it where it lives: rewrite the explanation, state the goal, fix the example, remove
the contradiction. Often the right fix *removes* text. Then check: would this fix also
prevent the related mistakes the agent hasn't made yet? If not, you haven't found the
root.

### Example

An investing agent writes a thesis on a company and leans on the company's own press
release. Rejected.
- Patch: "Do not use press releases as sources." Next week it leans on an analyst note
  paid for by the company.
- Root: the content never explained that a thesis is a claim *against* the market, so
  evidence counts only if it is independent and not already priced in. Add that idea
  to the core doc on how theses are built. Press releases, paid notes and hype threads
  are all covered, and the agent is a step closer to judging sources on its own.

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
