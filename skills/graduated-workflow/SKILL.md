---
name: graduated-workflow
description: Grow an agent system toward a broad, genuinely autonomous workflow (running experiments, investing, operating a company) in stages - narrow tasks with full review first, more independence as it is earned. Use when designing or advancing such a workflow, instilling or changing a behavior in it, deciding what the agent may do alone at the current stage, turning a reject of the agent's work into a change in the instructions, or checking that the repo's content (CLAUDE.md/AGENTS.md, skills, docs, prompts) is aligned with the far goal. Teaches changing what the agent understands, at the root, instead of adding patch sentences, and making sure the user's words and the agent's reading of them mean the same thing.
---

<graduated-workflow>

# Graduated workflow

The user wants agents to do something of real value mostly on their own: run experiments, manage investments, operate a company. That can't be switched on. It is grown: at first the agent gets a narrow task and a human reads everything it did and rejects what is wrong; as the rejects dry up, the agent gets wider steps and lighter review, and so on up.

What moves the system up is the content the agent reads: instructions, docs, skills, prompts, the wording of the task. The work is a loop of three things: shape the content, let the agent try a step, review what it did.

Content gets shaped for two reasons: the user wants the agent to start working in a certain way, or the agent did something wrong. They are the same work. In both, the thing being changed is the picture the agent holds of the job, and an added sentence rarely changes a picture.

Your job with this skill is to help the user run that loop while keeping the far goal in view. We are not at full automation yet and should not pretend to be, but everything we write is aimed there.

- **[Far-goal-and-current-stage]**: know where the user is heading and where the system stands today.
- **[Understanding-and-leash]**: how to write content that serves the far goal while the agent is still on a short leash.
- **[Shared-meaning]**: making sure the user's words, the written content and the agent's reading all mean the same thing.
- **[Instilling-a-behavior]**: bringing a new way of working into the workflow, through what the agent understands.
- **[Rejects-and-root-causes]**: what to do when the agent got something wrong. No plasters.
- **[Neighboring-mistakes]**: a fix should also prevent the mistakes the agent hasn't made yet.
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

<Shared-meaning>

Three readers have to agree: the user, who has the workflow in their head; you, who turn what they say into content; and the agent, which will read that content cold. Meaning can slip at each handoff. The user may not be writing in their first language, or may think in one language while the content is written in another. A phrase can be unclear. Worse, it can be clear to both sides in two different ways.

The risk is highest in exactly this kind of workflow. A narrow task has a right answer, and a wrong reading shows up as a failure. A far goal and an open-ended way of working have much less right and wrong; they rest on judgment. An agent that read "conclusion" or "worth trying" differently from the user doesn't fail. It does something plausible, and the difference surfaces weeks later, if at all.

Some ways to keep the meaning in one piece:

- **Agree on cases, not on sentences.** An abstract restatement gets a "yes" from two people who mean different things. Offer a concrete situation: "The run finished and the metric dropped. You want the agent to stop and report, not to try a second variant?" Borderline cases show a difference fastest.
- **Say it back in the user's language.** Before writing content, and again after, tell the user in their own language what the agent will take from the text and what it will do because of it. They judge the consequence; they shouldn't have to judge the nuance of English.
- **Don't polish meaning in.** Turning rough phrasing into fluent text adds precision the user never stated. Each addition is your guess. When it matters, show it as a guess and ask. When both readings lead to the same content, just pick one.
- **Watch the words that carry judgment.** Every workflow has a few: "experiment", "result", "promising", "done", "review". Translation picks one word out of several (ניסוי can come out as experiment, trial or test), and each brings its own associations to the agent. Give every key term one meaning, written once, with an example of what it is and of what it isn't, and use the same word everywhere. An agent reads a new word as a new thing.
- **Ask the agent what it read.** A fresh agent reads the content and explains the goal and the key terms in its own words, then says what it would do in two or three borderline cases. Bring the answers to the user: is this what you meant?

</Shared-meaning>

<Instilling-a-behavior>

The loop doesn't start only from mistakes. Often the user wants the workflow to gain something: "from now on the agent writes down what it expects before every run." The shallow way is to add that sentence to the instructions. It is the same plaster, applied before the wound. The agent will comply where the sentence fits and miss everywhere else, because it has a rule and no reason.

A behavior holds when it follows from how the agent understands the work. So start from the understanding:

- **What is it for?** A written expectation is what makes a result informative: a surprise can only be seen against a prediction. That is what the agent needs to grasp. Check with the user that this is in fact their reason ([Shared-meaning]).
- **What picture does the agent have now?** Read the existing content whole, as the agent does. Where in that picture does the new behavior belong? Usually inside the description of the work itself, where experiments are explained, and in the template the agent fills in. Rarely in a list of rules at the end of a file.
- **What pulls the other way?** The three past experiments the agent will read as examples have no expectation written, and the report format has no place for one. Examples and formats outweigh a sentence, so they change too. When *updating* a behavior, find every place the old one is written or shown; otherwise the agent gets both.
- **What should come with it?** The question from [Neighboring-mistakes] works in the positive. An agent that understood the reason will also leave the prediction unedited after the run, say so when it has no expectation, and point out the result that surprised it. If the content would produce the named behavior without these, it taught a rule.
- **Where does it lead?** A behavior worth instilling on this rung usually rehearses the next one. This one is the first half of designing an experiment.

Then let the agent work, and review the first runs closely. The rejects show which part of the picture didn't land, and they are handled the same way.

</Instilling-a-behavior>

<Rejects-and-root-causes>

A reject is the most valuable thing the loop produces. It shows a gap between what the agent understood and what was needed.

The easy response is a plaster: add a sentence that says the thing the user just said. "IMPORTANT: always normalize the data before evaluating." Agents love doing this. It is wrong twice. It is ugly: the content turns into a pile of scars, each one remembering an incident. And it doesn't fix anything: the gap that produced this mistake is still there and will produce its siblings tomorrow.

Instead, treat the agent's action as reasonable given what it read, and ask what it read. What was in its context, and what picture did that give it? Where did the picture differ from the real one? Usual answers:

- A concept it needed is explained nowhere, or only somewhere it never loads.
- Two places say different things and it followed the wrong one.
- An example or a piece of existing code shows the wrong pattern, and examples beat prose.
- The purpose is unstated, so it couldn't tell which of two readings of the task was meant.
- The task itself was worded loosely, or was too big a step for this stage.
- A word means one thing to the user and another to the agent ([Shared-meaning]).
- The important thing is there, buried under ten unimportant ones.

Then fix that, at the place where it lives. Often the fix is rewriting an explanation, deleting a contradiction or replacing an example, and the text gets shorter. Sometimes the right fix is not in the content at all: a smaller task, or a rung down.

A good fix reads as if it was always part of the document, with no trace of the incident. And it covers more than the incident: see [Neighboring-mistakes]. If the user asks to "make it stop doing X" and the cause is not yet clear, say so and look for it before editing anything.

</Rejects-and-root-causes>

<Neighboring-mistakes>

The mistake the user rejected is one sample from a family. A gap in the agent's picture produces many mistakes; this one only happened to surface first. So the question for any fix is: does it also prevent the neighbors, the mistakes the agent has not made yet?

Ask it before fixing, as a way to find the cause. Once you think you know the cause, name two or three other mistakes it would produce. An agent that thinks an experiment's job is to produce a number will evaluate on training data, and will also tune a threshold on the test set, drop the runs that failed, and report the best seed of five.

- If you can't name any neighbors, you have described the symptom, not the cause. Keep looking.
- If the neighbors look unrelated to each other, there is probably more than one cause.
- The neighbors show where the fix belongs: at the point they all pass through. Here that is the explanation of what a result means, not the evaluation script.

Ask it again after fixing, as a test. Reread the changed content as the agent would and go through the neighbors one by one: is each of them now clearly wrong to someone who read only this? A plaster fails here, however well it is phrased. A rule covers the case its sentence names; an explanation of *why* covers cases nobody listed. When it is cheap, test for real: give the agent a task where a neighbor is the tempting move and watch what it does. That checks what it understood, not whether it remembers a rule.

Don't write the neighbors into the content as rules. That is the same pile of plasters, laid in advance. They are a measure of the fix and stay out of the text.

This is what makes moving up a rung possible. On a low rung a human catches each mistake as it happens. Higher up nobody reads every step, so the mistakes that matter are exactly the ones nobody has seen. A system that fixes only what was caught stays as wide as its reviewer's attention.

</Neighboring-mistakes>

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

**Fix.** The project's description of its experiments gets a short paragraph on what a result means here and what makes one trustworthy. The loader returns named splits, so the easy path is the correct one. The human's experiment design now states which split each number comes from. No rule against evaluating on training data is written anywhere, and the threshold mistake doesn't happen either: it was a neighbor, with the same cause.

This is also what rung 3 needs: an agent that will one day design experiments has to know what makes a result trustworthy. The reject on rung 2 paid for a capability of rung 3.

</Example>
