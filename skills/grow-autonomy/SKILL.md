---
name: grow-autonomy
description: Grow an autonomous agent system - one that uses many tools, is too large for any single agent or person to keep in view, needs different skills for different tasks, and keeps changing its structure - so that harder and harder tasks can be handed to it. Use when introducing or changing a behavior in such a system, when its work was rejected and something has to change, when deciding what each agent, forked skill or workflow step needs to know, or when the user's intent and the written content may not mean the same thing. Changes go to the root of what agents understand and of how attention is divided, never as patch sentences. Every reject is recorded in a reject journal.
---

<grow-autonomy>

# Grow autonomy

The user is growing an autonomous agent system: for research, for investing, for running a product or a company. "Autonomous" describes the system, in four ways:

- It uses a wide range of tools.
- It is large. Nobody, human or agent, can keep all of its tasks in view at once.
- Its tasks need different skills.
- It is dynamic. Its structure (agents, skills, workflows) will keep changing.

What grows is how hard a task the user can hand over. Requests of every size arrive at every point in the system's life: today "fix this label", tomorrow "develop the new product up to publication". There are no stages to climb and no level the system "is at". The aim is that, over time, harder and more open requests come back done well.

Two things decide whether they do:

- **The picture**: what each agent understands about the work it is doing.
- **Attention**: which information reaches which agent. In a system this size, attention is the scarce resource, the user's and every agent's.

Both are made of the content agents read (instructions, skills, docs, prompts, the briefs agents hand each other) and of the structure that carries it (skills, forked skills, subagents, workflows, handoff protocols).

You come to this work through one of two entrances: the user wants the system to work in a certain way ([Instilling-a-behavior]), or the system did something and the user rejected it ([Rejects-and-root-causes]). It is the same work in both. Change the picture at its root, and never by adding a sentence that repeats the request.

- **[Autonomy-comes-with-the-request]**: how much is left to the system is set by each request, not by a stage.
- **[Picture-and-attention]**: each agent gets what its piece of the work needs, and that much has to really be there.
- **[Shared-meaning]**: the user's words, the written content and the agent's reading must mean the same thing.
- **[Instilling-a-behavior]**: bringing a way of working into the system through what agents understand.
- **[Rejects-and-root-causes]**: what to do when the system got something wrong. No plasters.
- **[Neighbors]**: a change should also cover the cases nobody has seen yet.
- **[Reject-journal]**: every reject is written down. Not optional.
- **[With-audit-agent-context]**: how this skill and the audit work together.
- **[References]** and **[Examples]**: the detail, and three worked cases from different domains.

These are ways of thinking, with some suggested ways of working. Use judgment; it is not a procedure to run step by step. The one fixed step is the reject journal.

</grow-autonomy>

<Autonomy-comes-with-the-request>

Every request carries its own measure of how much is left to the system. "Rename this column" leaves almost nothing. "Review the portfolio and prepare next quarter's changes" leaves nearly everything. The user sets this, request by request, and it jumps around: a wide request can be followed by a tiny one in the same hour.

- **Read it from the request.** Don't carry it over from the last request, and don't infer it from how the system usually works. When the request doesn't say how far to go and the readings lead to different work, ask, with a concrete case ([Shared-meaning]).
- **Err in neither direction.** On a small request, don't redesign what wasn't asked about; if you notice a problem outside the request, mention it and leave it. On a wide one, don't come back for approval at every step.
- **Keep levels out of the content.** Lines like "the agent only implements" or "always ask before designing" describe one request and contradict the next. A limit the user wants always (never trade without approval) is a different thing: a rule of the system, stated once with its reason, or enforced by permissions and hooks.
- **Know the far goal.** The user has in mind the hardest things they want to hand over one day. Ask once, and write the answer where an agent holding a wide task will see it. Each change is judged against them too: does it serve only today's request, or does it also build something the hard requests will need?
- **A wide request that came back badly is material.** It is the richest source of rejects, and the hardest to read: many decisions were made, by several agents. Find the decision that went wrong and work from there.

The user decides what to ask for. Your part is to say honestly where you expect a wide request to break, and to learn from where it does.

</Autonomy-comes-with-the-request>

<Picture-and-attention>

An agent acts on its picture of the job: what the work is for, what good looks like, why things are the way they are. A rule without a reason gets followed where its sentence fits and nowhere else.

A small agent doing a small piece does not need to understand the whole system, and should not be loaded with it. It needs what its piece needs, and that has to really be there:

- what the piece is for: one level up, what will be done with the result
- what good looks like for this piece
- the things it would not know to ask about
- what to hand back, and what to flag when the piece doesn't fit

The test: can it do the piece well, and would it notice when something is off and say so? With too little it can't notice. With too much the important part is diluted and its attention is spent on the rest.

So the picture is layered. What the system is for, the far goal and the shared vocabulary sit where an agent holding a wide task will see them. Knowledge of an area sits in a skill and loads when the area is touched. What one piece needs travels in its brief.

The structure tools are attention tools:

- A **skill** is knowledge on demand.
- A **forked skill** does a piece in a clean context, and only the result comes back.
- A **workflow** keeps the plan in a script, not in an agent's context.
- A **protocol** fixes the shape of a brief and of a report, so "what does this agent need" is decided once and not improvised at every handoff.

Meaning is lost at handoffs. A summary keeps the result and drops the reason. When an agent decided badly, first check whether the reason ever reached it.

The structure will change, so say each thing once, in a place named for its subject and not for today's layout of agents. When the structure changes, who receives what changes with it.

[Attention](references/attention.md) covers how to divide work and what each tool gives an agent. [Information flow](references/information-flow.md) shows how to map what reaches an agent for a given task, and how to test the map.

</Picture-and-attention>

<Shared-meaning>

Three readers have to agree: the user, who has the system in their head; you, who turn what they say into content; and the agent that will read that content cold. Meaning can slip at each handoff. The user may not be writing in their first language, or may think in one language while the content is written in another. A phrase can be unclear. Worse, it can be clear to both sides in two different ways.

The risk is highest in exactly this kind of system. A narrow task has a right answer, and a wrong reading shows up as a failure. A far goal and an open-ended way of working have much less right and wrong; they rest on judgment. An agent that read "close the ticket" or "worth trying" differently from the user doesn't fail. It does something plausible, and the difference surfaces weeks later, if at all.

Some ways to keep the meaning in one piece:

- **Agree on cases, not on sentences.** An abstract restatement gets a "yes" from two people who mean different things. Offer a concrete situation: "The customer asks for a refund on day 40 and the policy says 30. You want the system to refund?" Borderline cases show a difference fastest.
- **Say it back in the user's language.** Before writing content, and again after, tell the user, in the language they are most at home in (ask if you don't know it), what the agent will take from the text and what it will do because of it. They judge the consequence; they shouldn't have to judge the nuance of English.
- **Don't polish meaning in.** Turning rough phrasing into fluent text adds precision the user never stated. Each addition is your guess. When it matters, show it as a guess and ask. When both readings lead to the same content, just pick one.
- **Watch the words that carry judgment.** Every system has a few: "experiment", "closed", "promising", "done", "review". Translation picks one word out of several (ניסוי can come out as experiment, trial or test), and each brings its own associations to the agent. Give every key term one meaning, written once, with an example of what it is and of what it isn't, and use the same word everywhere. An agent reads a new word as a new thing.
- **Ask the agent what it read.** A fresh agent reads the content and explains the goal and the key terms in its own words, then says what it would do in two or three borderline cases. Bring the answers to the user: is this what you meant?

All of this holds between agents too. A brief is also read cold.

</Shared-meaning>

<Instilling-a-behavior>

The user wants the system to gain something: "from now on, every buy proposal says what would prove it wrong." The shallow way is to add that sentence to the instructions. That is a plaster applied before the wound. The agent will comply where the sentence fits and miss everywhere else, because it has a rule and no reason.

A behavior holds when it follows from how the agent understands the work. So start from the understanding:

- **What is it for?** A proposal that nothing could prove wrong can't be checked later, and a position nobody can check is never closed for a reason. That is what the agent has to grasp. Confirm with the user that this is in fact their reason ([Shared-meaning]).
- **Who needs it?** Not every agent. The one that writes proposals does, and the one that reviews open positions. The worker that fetches prices does not ([Picture-and-attention]).
- **What picture do those agents have now?** Read what reaches them, whole, as they do. Where in that picture does the behavior belong? Usually inside the description of the work itself, where a proposal is explained, and in the template it is written into. Rarely in a list of rules at the end of a file.
- **What pulls the other way?** Past proposals the agent reads as examples have no such section, and the report schema has no field for it. Examples and formats outweigh a sentence, so they change too. When *updating* a behavior, find every place the old one is written or shown; otherwise the agent gets both.
- **What should come with it?** The [Neighbors] question in the positive. An agent that understood the reason will also go back to those conditions when it reviews the position, say so when it can't name any, and not rewrite them after the price moves. If the content would produce the named behavior without these, it taught a rule.
- **What does it build?** Check it against the far goal. This behavior is half of what a system needs in order to manage positions with nobody watching.

Then let the system work, and look closely at the first results. The rejects show which part of the picture didn't land, and they are handled the same way.

</Instilling-a-behavior>

<Rejects-and-root-causes>

A reject is the most valuable thing this work produces. It shows a gap between what an agent understood and what was needed. Write it in the journal first ([Reject-journal]), then look for the cause.

The easy response is a plaster: add a sentence that says what the user just said. "IMPORTANT: always normalize the data before evaluating." Agents love doing this. It is wrong twice. It is ugly: the content turns into a pile of scars, each one remembering an incident. And it fixes nothing: the gap that produced this mistake is still there and will produce its neighbors tomorrow.

Instead, treat the agent's action as reasonable given what it had, and find out what it had. Which agent made the decision? What had reached it by that moment? ([Information flow](references/information-flow.md) shows how to establish this as fact.) Then name, in one sentence, what it believed that made the action look right. If you can't, you are still looking at the symptom.

Where the belief usually comes from:

- A concept it needed is explained nowhere, or only somewhere that never reaches this agent.
- The purpose was unstated, so it optimized for the nearest thing: finishing, producing a number, closing the ticket.
- Two places say different things, or an example shows the opposite of the prose. Examples win.
- A word means one thing to the user and another to the agent ([Shared-meaning]).
- The brief it was handed left out the reason, or a summary on the way dropped it.
- The important thing was there, buried under ten unimportant ones.
- The request itself could be read two ways.

Then fix that, where it lives. Often the fix is rewriting an explanation, deleting a contradiction or replacing an example, and the text gets shorter. Often it is not text at all: a tool whose easy path is the correct one, a template with a place for the thing that was forgotten, a field in a report schema, a different cut of the work between agents. Make the right path the easy path, and no sentence is needed.

A good fix leaves no trace of the incident; it reads as if it was always there. And it covers more than the incident ([Neighbors]). If the user asks to "make it stop doing X", or asks for a rule outright ("add a rule that it always cites"), and the cause is not yet clear, say so and look for it before editing anything. Then tell them what you found and what you would change instead. It is their system: if they still want the rule, write it once, with its reason, in the place it belongs.

A rule and a plaster can be the same words. A rule states something the user wants always and gives a reason the agent can apply to cases the rule didn't name. A plaster records an incident and gives no reason.

</Rejects-and-root-causes>

<Neighbors>

The mistake the user rejected is one sample from a family. A wrong belief produces many mistakes; this one only happened to surface first. So the question for any change is: does it also cover the neighbors, the cases nobody has seen yet?

Ask it before fixing, as a way to find the cause. Once you can name the belief, name two or three other mistakes it would produce. An agent that believes an experiment's job is to produce a number will evaluate on training data, and will also tune a threshold on the test set, drop the runs that failed, and report the best seed of five.

- If you can't name any neighbors, you have described the symptom, not the cause. Keep looking.
- If the neighbors look unrelated to each other, there is probably more than one cause.
- The neighbors show where the fix belongs: at the point they all pass through.

Ask it again after fixing, as a test. Reread the changed content as the agent would and go through the neighbors one by one: is each now clearly wrong to someone who read only this? A plaster fails here, however well it is phrased. A rule covers the case its sentence names; an explanation of *why* covers cases nobody listed. When it is cheap, test for real: give the agent a task where a neighbor is the tempting move and watch what it does.

The test cuts the other way too. A fix that stops the agent from doing something reasonable went too wide. A reason lets the agent tell the cases apart; a bigger fence doesn't.

Don't write the neighbors into the content as rules. That is the same pile of plasters, laid in advance. They measure the fix and stay out of the text.

This is what makes wide requests possible. On a small request the user sees every mistake. On a wide one nobody reads every step, so the mistakes that matter are exactly the ones nobody saw.

</Neighbors>

<Reject-journal>

Every reject handled with this skill gets an entry in the system's reject journal, opened when the reject arrives and before anything is fixed, then filled in as the cause is found. The entry holds the request and the reject in the user's own words, what the agent had, the belief, the root, the neighbors, the change, and how the change was checked. "Root: unknown" is an honest entry.

The journal is for the user and for you. Working agents don't read it, and its entries never turn into rules: that would be the pile of scars again.

What it gives: a root that returns shows an earlier fix that missed. Rejects that gather around one word or one handoff point at a term or a protocol. And over time it shows which kinds of wide requests now come back clean, which is the evidence that the system has grown.

Format, location and how to read it: [Reject journal](references/reject-journal.md).

</Reject-journal>

<With-audit-agent-context>

`audit-agent-context` is a general tool. It audits the content of any repo for any agent setup: it collects every instruction, doc, comment and prompt, records how an agent gets to each one, and reports contradictions, stale facts and gaps. Asked for traces, it also reads past agent sessions and shows what actually reached the agent. It knows nothing about this system's far goal. This skill does.

So the audit measures, and this skill supplies the intent and decides what to do with the findings.

- It is user-invoked. Suggest it with a focus taken from the far goal or from a recent group of rejects: `/audit-agent-context how the reason a position is held reaches the agents that judge it`.
- Good moments: after the structure changed, when rejects pile up with no clear source, before the user tries a kind of wide request for the first time.
- Its report lists a fix per problem. Don't apply them one by one. Group the problems by shared root and fix the roots, as with any reject.
- Its collected data records, per file, how an agent could reach it. That is raw material for [Information flow](references/information-flow.md).

</With-audit-agent-context>

<References>

- [Attention](references/attention.md): dividing work between agents; what a skill, a forked skill, a subagent and a workflow each give the agent inside them; protocols for briefs and reports; keeping knowledge in place while the structure changes. Read it before designing or changing who does what.
- [Information flow](references/information-flow.md): for a given task, map what reaches the agent and how, and test the map with a real agent. Read it when tracing a reject or checking a change.
- [Reject journal](references/reject-journal.md): the entry format, where the journal lives, how to read it. Read it at the first reject.
- [Examples](references/examples.md): three worked cases.

For a research lab built with `experiment-lab`, that skill carries this method in a lab's own terms (its `references/growing-a-lab.md`): which part of a lab carries what, the beliefs behind the failures labs usually show, and the journal entry with a lab's fields. Use it there, and come back here for what it leaves out.

</References>

<Examples>

Three cases, from three kinds of systems, are worked through in [Examples](references/examples.md). Read the one closest to the work at hand when seeing the whole line of work in a real case would help.

- **Research, a small request, a reject.** An evaluation reports a number that means nothing. The fix is a paragraph of explanation and a data loader with named splits; no rule is written.
- **Running a shop, instilling a behavior.** "The system closes customer tickets by itself." The word "closes" meant two different things, and three agents each needed a different part of the picture.
- **Investing, a wide request, a reject.** A portfolio review proposes selling a hedge. Every agent did its piece correctly; the reason the position exists was lost in the handoff. The fix is in the brief and the report schema.

</Examples>
