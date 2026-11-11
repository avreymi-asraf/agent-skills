# Attention

A system that is wide enough to be worth growing is too big to fit in one context. No agent can hold all of it, and neither can the user. So the system needs a design for attention: which agent holds what, and how the rest gets to an agent at the moment it is needed.

The principle is in the skill: an agent does not need to understand the whole system. It needs what its piece of the work needs, and that much has to really be there. This file is about deciding what that is and building the structure that delivers it.

## What a piece needs

For any agent about to do a piece of work, four things:

1. **What the piece is for.** One level up is enough: what will be done with the result, and by whom. An agent that summarizes a filing writes a different summary when it knows the reader is deciding whether to sell.
2. **What good looks like** for this piece.
3. **What it would not know to ask about.** The reasons behind the current state, the constraint that isn't visible in the material. See "silent" information in [Information flow](information-flow.md).
4. **What to hand back**, and what to flag when the piece doesn't fit what it found.

The fourth is easy to forget and matters most in wide requests. A worker that was told only what to produce will produce it even when the situation makes it meaningless. A worker that knows what the result is for can say "this doesn't fit" and stop.

Everything else stays out. Each extra line takes attention from these four.

## Layers

The picture of the system is spread over layers, and each layer has its own home:

- **The whole system**: what it is for, the far goal, the shared vocabulary, the rules that always hold. Short. Lives where an agent holding a wide task always sees it.
- **An area**: how proposals are written, how experiments are run, how customers are answered. Lives in a skill or a doc for that area, and loads when the area is touched.
- **A piece**: this holding, this ticket, this file. Travels in the brief.

When something is found missing, the question is which layer it belongs to. A concept every decision in the area depends on belongs to the area. A fact about one holding belongs with that holding and reaches the worker through the brief. Putting a piece-level fact into the system layer is how always-loaded files fill up.

## Where to cut the work

Cutting work into pieces saves attention and costs meaning, because each cut is a handoff. Some guides:

- Cut where the result is small compared to the reading it takes. Research, search, review of many files: much goes in, little comes back.
- Don't cut through the middle of one judgment. Two agents that each need the same subtle understanding will each understand it a little differently. Keep the judgment with one agent, or give both the same source.
- Keep the reason with the decision. If the agent that decides gets only summaries, every reason that matters has to survive the summary. Check that it does.
- A cut is only as good as its brief.

## The tools

What each tool does to attention. These are Claude Code's, described as of the time of writing; they change, so check the docs listed at the end. Other agent tools have equivalents with their own rules.

| Tool | What the agent inside starts with | What comes back | Use it for |
|---|---|---|---|
| **Skill** | The current conversation, plus the skill's text once it is invoked. Until then only its description is in context. | Nothing comes back; the same agent goes on. | Knowledge of an area, loaded when the area is touched. |
| **Forked skill** (`context: fork`) | A fresh context. The skill's text is the task. No conversation history. | A summary of the result. | A piece done the same way every time, with heavy reading and a small result. The skill's text is the entire brief, so it has to stand alone. |
| **Subagent** | A fresh context: its own system prompt, the brief the calling agent wrote, the project's instruction files (some built-in agent types skip them), and any skills its definition preloads. | Its final report only. | A piece that needs a specialist's setup: its own tools, its own standing instructions. |
| **Fork of the conversation** | Everything the parent has so far. | A report. | Side work that needs all that is already known. It saves nothing on the way in. |
| **Workflow** | Each agent gets the prompt the script passes it, as a subagent does. | What the script returns. Intermediate results stay in script variables and never enter the main context. | A wide task whose shape is known: many items, fixed phases, cross-checks. The plan lives in code, where it is not forgotten, and can be read and rerun. |

Two points that follow:

- In every row except the skill and the conversation fork, **the agent does not see the conversation**. What the user said an hour ago, what the main agent read at the start, the decision reached three turns back: none of it arrives unless the brief carries it. This is the most common root of rejects in wide requests.
- A workflow moves the question "what runs next" out of an agent's attention. It does not answer "what does each agent need to know". That is still in the prompts the script builds, and those deserve the same care as any brief.

## Protocols

A protocol is an agreed shape for a handoff. It decides once what a brief carries and what a report carries, so it is not improvised at every delegation by an agent that is busy with something else.

A brief worth agreeing on carries:

- the purpose: what the result will be used for
- the piece itself
- what good looks like
- the reasons behind the current state that this piece could run into
- what to return
- when to stop and flag instead of finishing

A report carries:

- the result
- what was assumed
- what was not checked
- what was surprising
- what needs the caller, or a person

Where the protocol lives depends on the tool: in the text of a forked skill, in a subagent's definition, in the prompt template and the output schema of a workflow step. A schema is the strongest form. A field named `evidence_against_role` cannot be forgotten by the worker and cannot be dropped by a summary.

Keep a protocol about shape. The content of each field comes from where that knowledge lives (the holding's file, the experiment's design), so there is still one source.

## A structure that keeps changing

The system will be reorganized many times: an agent split in two, a skill turned into a workflow, a new tool added. Content that is tied to the layout breaks at each change.

- Write knowledge by subject. "What makes a result trustworthy" outlives "instructions for the evaluation agent".
- One source, many readers. Briefs and skills pull from the place where a thing is written; they don't each carry a copy.
- Protocols outlive the agents on either side of them. If the brief for "research one holding" is fixed, the worker behind it can be replaced.
- After a change in structure, redo the information-flow map for the tasks it touches. Moving a paragraph, or moving a piece of work from the main agent into a worker, changes who receives what. Things that used to arrive because they happened to be in the conversation stop arriving.

## Signs that attention is the root

When tracing a reject, these point to attention and not to missing knowledge:

- The knowledge exists, and the agent that decided never had it.
- The main agent knew, and the worker didn't.
- Each agent's piece is correct taken alone, and the whole is wrong.
- The system did it right early in a long run and wrong late in it.
- Two workers given the same kind of piece decided in opposite ways.

The fix is then in the brief, the protocol or the cut. Writing the knowledge down a second time, louder, does not help an agent that never receives it.

## Sources

Claude Code docs: [Skills](https://code.claude.com/docs/en/skills), [Create custom subagents](https://code.claude.com/docs/en/sub-agents), [Dynamic workflows](https://code.claude.com/docs/en/workflows), [Run agents in parallel](https://code.claude.com/docs/en/agents). Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
