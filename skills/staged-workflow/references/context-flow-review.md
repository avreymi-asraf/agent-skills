# Context flow review

Read this when you need to map how information reaches an agent in a project, or check
that the map actually works. A content system can be well written and still fail: what
matters is what the agent *sees*, at the moment it decides, and how little else competes
for its attention.

Two facts make this worth doing:
- **Text in the repo is not text the agent read.** Most knowledge arrives only through a
  trigger, a pointer, a search, or a handoff, and each of those can fail silently.
- **More context isn't better.** Attention is a finite budget. Performance drops as input
  grows and as distractors pile up, especially text that is similar but wrong
  (Chroma's "context rot" study). Anthropic's framing of the goal: the smallest set of
  high-signal tokens that makes the right outcome likely.

## How information reaches an agent

Every project has these routes, under different names. The Claude Code version is given
as a concrete example; check the current docs, because the details change.

| Route | In Claude Code | How it fails |
| :--- | :--- | :--- |
| **Always present** | System prompt, root `CLAUDE.md` / `AGENTS.md` and its `@` imports, rules without `paths:`, the start of auto memory (`MEMORY.md`), every skill's description | Bloat: narrow text costs attention on every task. Contradictions get resolved at random |
| **Triggered** | Subdirectory `CLAUDE.md` and path-scoped rules when a matching file is touched; a skill's body when it is invoked (it stays for the session) | Trigger never fires: wrong path pattern, vague skill description. Fires too late, after the decision was made |
| **Pulled by the agent** | Docs, READMEs, reference files, memory topic files, code comments, search results, tool output | Nothing points there, or the pointer doesn't say when it matters, so the agent never looks |
| **Handed over** | The task prompt; a subagent's start: its own definition, the `CLAUDE.md` hierarchy, preloaded skills, the delegation message. *Not* the parent's conversation, skills, or files read | The handoff message drops the key idea. The parent gets back only a summary |
| **Carried over time** | Compaction summaries; skills re-attached after compaction within a token budget; notes the agent writes for itself | The key point is lost in a summary. Long on-demand files are cut off |

## Build the map from tasks

Map per task, not per file. `/audit-consistency` already records, for every file, how an
agent would reach it; use that as raw material, then turn it around:

1. **Pick the tasks.** 5-8 realistic ones for the current stage, plus 2-3 from the next
   stage and one from the destination. The next-stage tasks are where gaps hide.
2. **Write the needed set** for each task: the few ideas the agent must hold to do it
   well. Concepts, the goal, constraints, where things are. Keep it short.
3. **Trace the reached set:** walk the task as a cold agent and note what arrives, by
   which route, and when.
4. **Compare.** The useful categories:
   - *Missing*: needed, never reached.
   - *Late*: reached after the choice it should have shaped.
   - *Noise*: reached, not needed, especially narrow text that is always loaded.
   - *Conflicting*: two sources that disagree.
   - *Distorted*: reached through a summary or handoff that lost the point.
   - *Human-only*: reaches the agent only because a person typed it into the prompt.

Write the result down as a short map in the project docs: what is always loaded and why,
what each trigger brings, what each kind of subagent starts with. This is part of the
design, so keep it next to the content it describes.

## Test it, don't just read it

A map you only reasoned about is a hypothesis. Some ways to check it:
- **Look at what loaded.** In Claude Code, `/context all` lists memory files that loaded
  at launch. An `InstructionsLoaded` hook can log each instruction file with its load
  reason (session start, nested directory, path match, import, compaction). This shows
  lazy loads that `/context` misses.
- **Read the transcript.** Which skills fired, which files were opened, what was
  searched, what the delegation prompt to each subagent actually said.
- **Ask a cold agent.** Start fresh on the task and, before it acts, ask what it plans
  and which principles it relies on, and where it learned them. Compare with the needed
  set. Ask again after a long run or a compaction to see what survived.
- **Flip a fact.** Change or remove one piece of knowledge and see if behavior changes.
  If it doesn't, that piece wasn't reaching the agent, or wasn't being used.
- **Run a neighbor.** A fresh task that needs the same idea in a different form, as in
  the neighbors test.

## Fixing reach, not just text

Often the text is fine and the route is wrong. Some moves:
- **Place by how often it's needed.** Every task: always loaded, and short. Some tasks:
  behind a trigger (path rule, skill). Rarely: a reference file with a pointer.
- **A pointer is content too.** "See X" gets followed only if it says when and why. Skill
  descriptions are triggers: write them as "use when ...".
- **Don't rely on the handoff.** What a subagent always needs belongs in its definition
  or preloaded skills, not in a delegation message the parent may or may not write well.
- **Make long-run knowledge durable.** Anything that must survive compaction or a new
  session goes into standing instructions or notes files, not a remark mid-conversation.
- **Enforce with mechanisms, explain with text.** Hard limits (including the current
  stage's limits) fit better in permissions and hooks than in prose. That keeps the core
  docs about understanding, and the dial easy to turn.
- **Cut noise.** Removing an always-loaded paragraph that only matters for one task is a
  real improvement, not just cleanup.

## As the stages advance

The map moves. Early on, most of the needed set is *human-only*: a person supplies it in
the prompt. Each item on that list is a route to build before the next stage, or it
disappears the moment the human steps back. Later, the agent becomes an author of
context: its notes, memory and handoff messages feed the next agent. Review those like
any other content, since they now carry the flow.

## Sources

- Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): attention budget, just-in-time retrieval, compaction, note-taking, subagents
- Chroma, [Context Rot](https://research.trychroma.com/context-rot): performance vs. input length and distractors
- Claude Code docs: [memory and instruction loading](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/sub-agents)
