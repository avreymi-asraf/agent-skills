# Reviewing the information flow for a task

The question this file helps answer: **given this task, what does the agent doing it actually have in front of it?**

"It is written in the repo" does not answer it. An agent works from what reaches its context, and most of a repo never does. The flow can be drawn for a concrete task and then tested, like any other part of the system.

## How information arrives

Sort every piece of information by how it gets to the agent:

- **Given.** In context before the first step: the system prompt, the always-loaded instruction files, the names and descriptions of skills and tools, and the wording of the task itself. For a worker agent, the brief it was handed is nearly all of this.
- **Triggered.** Loads when something happens: the agent opens a file in a certain directory, a task matches a skill's description, a rule is scoped to a path. It arrives only if the trigger fires, and only from that moment on.
- **Found.** Docs, READMEs, comments, other code. The agent sees it if something points there or if it goes looking.
- **Never.** Nothing leads to it, or it exists only in someone's head.

One distinction decides where a piece of information should sit. An agent searches only for what it knows it is missing. "How do I run the tests?" is a question it will ask by itself, so the answer can wait to be found. "The test split must not influence any decision" is not a question anyone asks; an agent that lacks it notices nothing and carries on. Information whose absence is silent has to be given, or sit on a path the agent is certain to walk. Leaving it to be found means leaving it out.

The opposite mistake costs too. Context is a limited budget, and each always-loaded line takes attention from the others. Anthropic's guidance is to aim for the smallest set of high-signal tokens that makes the right outcome likely. So the aim is not "give everything", it is each piece arriving by the cheapest route that is still reliable.

## Drawing the map

Take one real task, worded as it is really given. List what someone needs in order to do it well:

- what the task is for
- the concepts of the domain it touches
- the conventions here, and where things live
- what "done" looks like
- an example of good work
- how much the request leaves to the agent

For each item, write where it lives, how it arrives, and whether it arrives before the decision it should shape.

| Needed for "implement the evaluation for experiment 12" | Lives in | Arrives |
|---|---|---|
| What the experiment tests | `experiments/12/index.md` | Found: the task wording names the file |
| What makes a result trustworthy | nowhere | Never |
| Which split each number comes from | nowhere; the design names the model and the hypothesis only | Never |
| How to load data | `data/README.md` | Found, if it looks; `load_data()` is what a search hits first |
| How results are reported | `CLAUDE.md` | Given |
| Deployment rules | `CLAUDE.md`, 60 lines | Given, irrelevant here |

Then read the map for these:

- **Missing**: needed, and nothing carries it.
- **Silent and only findable**: the agent won't know to look.
- **Late**: it arrives after the decision. A convention the agent meets in the fifth file it opens, after writing code in the first.
- **Clash**: two routes deliver different answers. The doc says one thing; the code the agent copies from says another, and the code usually wins.
- **Buried**: it is given, among much that this task doesn't need.

Draw a map for a small request and another for a wide one, of the kind the user hopes to hand over. The second shows what is still missing while there is time to build it.

A wide request passes through several agents, and each one has its own map. Draw one per agent on the path: the main agent, then each worker, with the brief as the worker's "given". Compare neighbors on the path: what did the caller know that the worker's map lacks? That difference is where reasons get lost ([Attention](attention.md)).

`audit-agent-context` gives the raw material for the whole repo: for every file it records the ways an agent could end up reading it, and with traces, what past sessions really opened. The map here is the same data seen from the other side, starting from one task.

## Testing it

A map is a prediction about what the agent will read. Check it. For a worker, test with exactly its brief and nothing from the conversation that produced it.

**Cold read.** Start a fresh agent with exactly what the real one gets: the same directory, the same task wording, nothing explained on the side. Before it works, ask: What is this task for? What will "done" look like? What will you read first? What are you unsure about? Compare the answers with the real picture. Keep the questions open. "What do you know about data splits?" hands over the very thing being tested.

**Watch a run.** Let it do the task, then read the transcript for the flow, not the result: which files it opened and in what order, what it searched for and didn't find, where it guessed without checking, which skill it used or passed over. What happened outranks what the map predicted.

**After a reject.** Run the map backward. At the moment of the wrong decision, what had the agent read? This is the factual half of finding the root cause.

**Removing.** When always-loaded text is suspected of being dead weight, take it out and repeat the cold read. If nothing changes, it wasn't doing anything.

When the flow changes, test it again. A fix that moves a paragraph from one file to another changes who receives it and when.

## Loading rules in Claude Code

Every agent tool has its own rules for what loads when; learn the ones of the tool in use. For Claude Code, at the time of writing (these change, so check the docs linked below):

- `CLAUDE.md` in the working directory and above, and rules without `paths`, load at launch. `@path` imports are expanded with them. A sentence that says "read `docs/x.md`" is not an import: the agent sees that file only if it decides to open it.
- A subdirectory's `CLAUDE.md`, and rules with `paths`, load when the agent first reads a matching file. Before that they don't exist for it.
- For a skill, only the description is in context until the skill is invoked, and long descriptions are cut. A skill with `disable-model-invocation` is never picked up by the agent itself. Files in `references/` load only if `SKILL.md` points to them and the agent follows.
- A subagent starts with a fresh context and does not see the conversation, the files already read, or the skills already invoked. It gets its own system prompt, the brief the caller wrote, `CLAUDE.md` (the built-in Explore and Plan agents skip it), and the full text of any skills its definition preloads. Only its final report comes back.
- A forked skill (`context: fork`) runs the same way, with the skill's text as the task. An agent started by a workflow script gets the prompt the script passes it. For all delegated work, the brief is nearly the entire flow.
- After compaction in a long session, earlier content is a summary and invoked skills are re-attached only in part. What was given at the start may be thinner by step 200.

To see what actually loaded: `/context all` lists what is in the window, including which memory files; `/memory` and `/skills` show what is available; an `InstructionsLoaded` hook can log each instruction file as it loads and why; `claude --debug` shows the rest.

## Sources

- Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Claude Code docs: [How Claude remembers your project](https://code.claude.com/docs/en/memory), [Skills](https://code.claude.com/docs/en/skills), [Create custom subagents](https://code.claude.com/docs/en/sub-agents), [Dynamic workflows](https://code.claude.com/docs/en/workflows), [Debug your configuration](https://code.claude.com/docs/en/debug-your-config), [Hooks](https://code.claude.com/docs/en/hooks)
- Drew Breunig, "How Long Contexts Fail" (context poisoning, distraction, confusion, clash)
