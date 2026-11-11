---
name: graduated-workflow
description: Grow an agent system toward a broad, genuinely autonomous workflow (running experiments, investing, operating a company) in stages - narrow tasks with full review first, more independence as it is earned. Use when designing or advancing such a workflow, deciding what the agent may do alone at the current stage, turning a reject of the agent's work into a change in the instructions, or checking that the repo's content (CLAUDE.md/AGENTS.md, skills, docs, prompts) is aligned with the far goal. Teaches fixing the root cause in the content instead of adding patch sentences.
---

<graduated-workflow>

# Graduated workflow

The user wants agents to do something of real value mostly on their own: run experiments, manage investments, operate a company. That can't be switched on. It is grown: at first the agent gets a narrow task and a human reads everything it did and rejects what is wrong; as the rejects dry up, the agent gets wider steps and lighter review, and so on up.

What moves the system up is the content the agent reads: instructions, docs, skills, prompts, the wording of the task. The work is a loop of three things: shape the content, let the agent try a step, review what it did. Your job with this skill is to help the user run that loop while keeping the far goal in view. We are not at full automation yet and should not pretend to be, but everything we write is aimed there.

- **[Far-goal-and-current-stage]**: know where the user is heading and where the system stands today.
- **[Understanding-and-leash]**: how to write content that serves the far goal while the agent is still on a short leash.
- **[Rejects-and-root-causes]**: what to do when the agent got something wrong. No plasters.
- **[Aligning-the-content]**: checking the whole content system, with `audit-consistency`.
- **[Example]**: one reject, handled badly and then well.

These are ways of thinking, with a few suggested ways of working. Use judgment; none of it is a procedure to run step by step.

</graduated-workflow>

<Far-goal-and-current-stage>

Before changing anything, know two things. Ask the user if either is unclear.

- **The far goal**: what the agent does when the workflow is finished. "The agent chooses, runs and concludes experiments by itself."
- **The current stage**: what the agent does alone today, what a human checks, and what kind of step comes next.

A ladder for the experiments goal might look like this (the user's ladder will differ, and different parts of a system can stand on different rungs):

1. The agent writes one function to a spec. A human reads every line.
2. The agent implements a whole experiment a human designed. A human reviews the diff and the results.
3. The agent proposes the experiment. A human approves the plan; the agent runs it and reports.
4. The agent chooses, runs and concludes. A human reads the conclusions.

Both facts should be written in the repo, once, where the agent always sees them. An agent that doesn't know the far goal optimizes for the small task in front of it; an agent that doesn't know the stage takes steps nobody is ready to review.

Don't build ahead of the stage. On rung 1 there is no reason to write orchestration, schedulers or self-directed loops for rung 4; they will be wrong by the time they are needed. Moving up is the user's call. The signal is that rejects on the current kind of step have become rare, and the ones left are matters of taste, not misunderstanding. After a move, review closely again for the first few runs.

</Far-goal-and-current-stage>

<Understanding-and-leash>

Content carries two different things. Keep them apart.

- **Understanding**: what the project is for, how the domain works, what good work looks like and why. Write this for the agent of the far goal, from day one. It does not change between stages.
- **Leash**: how big a step the agent takes alone and what needs approval. This is short, lives in one place, and is the only thing that changes when the system moves up a rung.

When the two are mixed, with "you only implement, don't think about design" scattered through every file, the agent never forms the full picture, and every move up means rewriting everything. When they are separate, a move up is an edit of a few lines, and the agent arriving at the new rung already understands the work.

So restrict what the agent *does*, not what it *understands*. An agent that today may only write one function should still know what experiment the function belongs to, what hypothesis is being tested and what result would be surprising. It writes a better function now, and it is being prepared for the day it designs the experiment.

Let each stage rehearse the next one. On rung 2 the human designs the experiment, but writes the hypothesis and the expected outcome in the same file and format the agent will use on rung 3, and the agent reports its results against them. By the time it is allowed to propose an experiment, it has read thirty good proposals and seen how each one turned out.

</Understanding-and-leash>

<Rejects-and-root-causes>

A reject is the most valuable thing the loop produces. It shows a gap between what the agent understood and what was needed.

The easy response is a plaster: add a sentence that says the thing the user just said. "IMPORTANT: always normalize the data before evaluating." Agents love doing this. It is wrong twice. It is ugly: the content turns into a pile of scars, each one remembering an incident. And it doesn't fix anything: the gap that produced this mistake is still there and will produce its siblings tomorrow.

Instead, treat the agent's action as reasonable given what it read, and ask what it read. What was in its context, and what picture did that give it? Where did the picture differ from the real one? Usual answers:

- A concept it needed is explained nowhere, or only somewhere it never loads.
- Two places say different things and it followed the wrong one.
- An example or a piece of existing code shows the wrong pattern, and examples beat prose.
- The purpose is unstated, so it couldn't tell which of two readings of the task was meant.
- The task itself was worded loosely, or was too big a step for this stage.
- The important thing is there, buried under ten unimportant ones.

Then fix that, at the place where it lives. Often the fix is rewriting an explanation, deleting a contradiction or replacing an example, and the text gets shorter. Sometimes the right fix is not in the content at all: a smaller task, or a rung down.

Two checks for a fix: Would it also have prevented the mistakes *next to* this one, which nobody has seen yet? And does it read as if it was always part of the document, with no trace of the incident? If the user asks to "make it stop doing X" and the cause is not yet clear, say so and look for it before editing anything.

</Rejects-and-root-causes>

<Aligning-the-content>

From time to time, and always around a move to a new rung, look at the content as a whole and not one file at a time. What matters is what the agent actually receives: what is always loaded, what it reaches only by following a link, what it never sees.

The `audit-consistency` skill does the heavy part: it collects every instruction, doc, comment and prompt in the repo, records how an agent gets to each one, and reports contradictions, stale facts and gaps. It is user-invoked, so suggest it with a focus: `/audit-consistency readiness for the agent proposing experiments by itself`. Read the report with these questions:

- Are the far goal and the current stage stated, once, where the agent always sees them?
- Is the leash in one place, or smeared across files where it will be forgotten at the next move?
- Do docs describe automation that doesn't exist yet as if it does? Or the reverse: do they describe the agent as a typist, with no view of the purpose?
- Does the agent have what the *next* rung needs: the concepts, the formats, examples of good work?
- Which plasters have piled up, and what root causes are they covering?

Treat every finding as in [Rejects-and-root-causes]: one cause, fixed in one place.

</Aligning-the-content>

<Example>

Far goal: the agent runs experiments alone. Current stage: it implements experiments a human designed (rung 2).

The agent implements an evaluation and reports 94% accuracy. The user rejects it: the test set overlaps with the training data.

**Plaster.** Add to CLAUDE.md: "IMPORTANT: never evaluate on training data." Next week the agent tunes a threshold on the test set. Another line is added. The file grows and the agent understands no more than before.

**Root cause.** What did the agent read? The task said "evaluate the model on the dataset." The repo has one loader, `load_data()`, which returns everything. Nothing explains what the experiments are for. The agent's picture was: produce a number. The real picture: we are measuring whether the model generalizes, and any leak from evaluation data into decisions makes the number meaningless.

**Fix.** The project's description of its experiments gets a short paragraph on what a result means here and what makes one trustworthy. The loader returns named splits, so the easy path is the correct one. The human's experiment design now states which split each number comes from. No rule against evaluating on training data is written anywhere, and the threshold mistake doesn't happen either, because it had the same cause.

This is also what rung 3 needs: an agent that will one day design experiments has to know what makes a result trustworthy. The reject on rung 2 paid for a capability of rung 3.

</Example>
