---
name: agent-and-skill-improvement
description: Maintains and improves agent files (identity, memory, tools) and skill files (SKILL.md). Load when completing a task that produced learnings, when the user corrects a mistake, when updating agent behavior, when logging work, when improving or updating domain knowledge in a skill, or when the user explicitly asks to update agent files, memory, tools, or skills.
---
## agent-and-skill-improvement

Agent & Skill Improvement System

This skill governs how an agent maintains and evolves two categories of files:
1. **Agent files** (agent, memory, tools) — project-scoped files that define how the agent operates within a specific project. They record what happened, what's needed, and how tools behave here.
2. **Skill files** (SKILL.md) — concept-scoped files that teach agents domain knowledge independent of any project. They capture the essential things about a topic.

### Topics Covered
- **Use [What-Goes-Where]** to decide whether information belongs in agent files or skills.
- **Use [Agent-File]** to update the agent's core identity and behavioral rules.
- **Use [Memory-File]** to manage project-specific activity logs and knowledge.
- **Use [Tools-File]** to record project-specific tool usage patterns and pitfalls.
- **Use [Skill-Improvement]** to update skills with domain knowledge and conceptual insights.
- **Use [Integration-Principles]** for the rules on how new information must be woven into existing content.
- **Use [File-Constraints]** for size limits and the reorganization mandate.
- **Use [Update-Workflow]** for the end-to-end process.
- **Use [Examples]** for concrete scenarios.
- **Use [Update-Checklist]** before finalizing any change.

## What-Goes-Where

### Classifying Information — Agent Files vs. Skills

The most important decision is: **where does this information belong?**

### Agent Files (Project-Scoped)
Agent files live in `.opencode/agents/` and are specific to the current project:
- **Agent file** (`<name>.md`): How the agent behaves — personality, decision-making rules, communication style. General behavioral patterns, not domain knowledge.
- **Memory file** (`<name>.memory.md`): What happened in this project — completed tasks, project-specific facts, architectural decisions, deployment rules.
- **Tools file** (`<name>.tools.md`): How tools work in this project — environment quirks, project-specific flags, workflows discovered here.

### Skill Files (Concept-Scoped)
Skills live in `~/dotfiles/skills/` or `.cl/skills/` and are about a **topic or domain**, not a project:
- The essential knowledge about a concept — what matters, how it works, core patterns.
- Domain-specific workflows, anti-patterns, and examples.
- Knowledge that is true regardless of which project you're in.

### The Decision Rule
Ask: **Is this about what happened or is needed in this project, or is this about understanding a concept?**

| Information | Target | Why |
|-------------|--------|-----|
| "Our API uses cursor pagination" | **Memory** | Project fact |
| "Cursor pagination vs. offset: tradeoffs and when to use each" | **Skill** | Concept knowledge |
| "Always use `--no-cache` for our Docker builds" | **Tools** | Project-specific tool usage |
| "Multi-stage Docker builds separate build and runtime deps" | **Skill** | Concept knowledge |
| "Stop being verbose in code reviews" | **Agent** | Behavioral rule |

## Agent-File

### Agent File — Core Identity & Behavior

Defines who the agent is: personality, behavioral rules, and principles. Loaded every session.

- **Location**: `.opencode/agents/<agent-name>.md`
- **Scope**: Identity, communication style, decision-making principles, hard rules.
- **When to update**: User corrections on behavior, recurring mistakes revealing a missing rule, workflow changes altering how the agent should operate.
- **When NOT to update**: One-off facts → Memory. Tool tips → Tools. Domain knowledge → Skill.

**Be proactive.** If you notice a pattern causing repeated friction — fix it here without waiting to be told.

### Writing Rules
Content must read as a coherent identity document. When adding a behavioral rule:
1. Find where it logically belongs among existing content.
2. Integrate naturally — rewrite surrounding sentences if needed.
3. Remove what it replaces — delete superseded rules entirely.
4. Never append a "Notes" or "Warnings" section.

## Tools-File

### Tools File — Project-Specific Tool Knowledge

Captures how tools behave in this specific project — quirks, flags, workflows, and fixes discovered while working here.

- **Location**: `.opencode/agents/<agent-name>.tools.md`
- **Scope**: CLI commands, API calls, tool flags, workflow sequences, environment quirks, error fixes — all specific to this project's context.
- **When to update**: Better way to use a tool here, unexpected tool behavior, user corrects tool usage.
- **General tool knowledge** (not project-specific) belongs in a skill instead.

**Actively maintain this file.** Don't let useful project-specific knowledge evaporate.

### Writing Rules
Organize by tool or command. Each section is a clean, unified guide:
1. Find the tool's existing section (or create one).
2. Integrate new findings so it reads as a complete guide.
3. Merge related tips into one clear statement.
4. Remove outdated entries — replace contradicted content.

## Memory-File

### Memory File — Project Activity & Knowledge

Two purposes: **short-term activity log** and **long-term project knowledge base**.

- **Location**: `.opencode/agents/<agent-name>.memory.md`

### Short-Term Log
Chronological record of recent project activity.
- Brief descriptions of completed tasks, decisions, outcomes. Date-stamped, newest first, 1-3 lines each.
- Trim older entries that no longer provide value.

### Long-Term Knowledge Base
Curated project-specific facts that persist across sessions.
- Project rules, API versions, architectural decisions, user preferences, environment facts.
- NOT general domain knowledge (that belongs in a skill).

**Be aggressive about capturing project knowledge.** If forgetting a fact would cause a mistake — write it now.

### Writing Rules
1. Find the right category — place facts where related knowledge lives.
2. Reorganize if needed — restructure when new facts reveal better groupings.
3. Write as settled knowledge — "Payments API uses v2", not "I learned that..."
4. Merge with related facts — update existing entries rather than adding new lines.
5. Never just append to the bottom.

## Skill-Improvement

### Skill Files — Domain Knowledge & Concepts

Skills teach agents about topics and domains. Unlike agent files, skills are **not project-specific** — they capture essential knowledge about a concept that is true everywhere.

### What Goes Into a Skill
Every piece of content in a skill should answer: **what is essential about this concept?**
- Core principles and key patterns of the domain.
- How things work — the mechanisms, not just the commands.
- Common mistakes and anti-patterns in this domain.
- Concrete examples that teach the concept.

Do not put project-specific details in skills. A skill about Docker should teach Docker concepts — not that "our project uses Docker 24.0" (that's Memory).

### When to Update a Skill
- You discover essential domain knowledge the skill should capture.
- You find a pattern or anti-pattern important to the concept.
- The user corrects your understanding of a domain concept.
- Existing skill content is outdated, wrong, or missing important nuance.

### How to Update a Skill
**Always load `manage-skills` first** — it has the full rules for writing and updating skills.

Key principles:
1. **Read the full skill** — understand its structure, style, and voice.
2. **Integrate naturally** — new content must match existing style and flow.
3. **Focus on what matters about the concept** — not project details, not obvious things.
4. **Keep it connected** — preserve and add cross-links to related skills (prerequisites, successors, companions); a skill that points nowhere leaves the agent stranded mid-workflow.
5. **Stay under 300 lines** — trim elsewhere if adding content.

### Creating a New Skill
When a concept deserves its own skill:
1. Load `manage-skills` for the full creation workflow.
2. Ask: what are the essential things about this concept? What would cause mistakes if not known?
3. Write for any project, not just the current one.
4. Connect it — name the skills it depends on, feeds into, and pairs with, and add it to the project's dependency map / routing table so the agent can discover it.

## Integration-Principles

### Integration Principles — Adding New Information

New information must be **integrated integrally**, not added as patchwork. This applies to all files — agent, memory, tools, and skills.

### The Core Rule
1. **Read the entire target file first** — understand its structure, voice, and organization.
2. **Decide where the new information belongs** — in the specific section where it fits, not "at the bottom."
3. **Rewrite surrounding context if needed** — new info should read as if it was always there.
4. **Consider restructuring** — sometimes new information reveals suboptimal organization.
5. **Remove redundancy** — no overlapping or contradictory statements.

### What NOT to Do
- Do not append "Lessons Learned" sections — integrate into relevant sections.
- Do not add "WARNING:" blocks at the end — rewrite instructions to include the warning naturally.
- Do not duplicate information across files.
- Do not preserve outdated content "just in case."

## File-Constraints

### File Constraints — Size Limits & Reorganization

**HARD LIMIT**: No file may exceed **300 lines** (agent, memory, tools, or skill files).

These files are loaded into the context window. Every line competes for space.

### The Reorganization Mandate
Every edit is an opportunity to:
- Remove outdated entries.
- Merge related entries saying similar things.
- Tighten wording — same meaning, fewer words.
- Demote less important content — remove what hasn't been useful.
- Promote important content — move frequently relevant facts to prominent positions.

After every edit, the file must be **better organized than before**, not just longer.

## Update-Workflow

### Update Workflow — End-to-End Process

1. **Classify**: Is this about identity/behavior (Agent), tool usage (Tools), a project fact/event (Memory), or domain knowledge (Skill)?  Use [What-Goes-Where] if unsure.
2. **Check if the file exists** — if not, create it with a clean initial structure.
3. **For skills**: Load `manage-skills` first. Follow its updating workflow.
4. **Read the target file in full** — never edit blind.
5. **Plan the integration** — where does this belong? What existing content does it relate to?
6. **Edit with reorganization** — add new content and simultaneously improve organization.
7. **Verify line count** — ensure the file stays under 300 lines. Trim if needed.
8. **Run the checklist** below.

## Examples

### Concrete Scenarios

**Scenario 1: User corrects behavior**
User: "Stop summarizing changes — I can see the diff."
→ **Agent file**. Find communication section. Integrate: "Do not summarize code changes." Remove conflicting rules.

**Scenario 2: Tool pitfall in this project**
`grep` fails due to mixed encodings in project files.
→ **Tools file**. Find/create grep section. Add: "Use `LC_ALL=C grep` for mixed encodings." Merge with existing tips.

**Scenario 3: Project-specific fact**
User: "We deploy to staging first, never directly to prod."
→ **Memory file**, long-term. Find/create deployment section. Write: "Deployment: staging → prod. Never deploy directly to prod."

**Scenario 4: Domain knowledge discovery**
You learn that Kubernetes liveness probes should not check external dependencies.
→ **Skill file** (e.g., cloud-infrastructure skill). This is concept knowledge — true for any project. Load `manage-skills`, update the skill's relevant section.

**Scenario 5: Logging completed work**
Finished migrating a database schema.
→ **Memory file**, short-term log. Add: "2026-04-16: Completed users table migration to v3."

## Update-Checklist

### Before Finalizing Any Edit

- [ ] Classified correctly: Agent / Memory / Tools / Skill (used [What-Goes-Where]).
- [ ] For skills: loaded `manage-skills` and followed its workflow.
- [ ] Read the entire target file before editing.
- [ ] New content integrated into the right location — not appended.
- [ ] Surrounding content adjusted for flow and coherence.
- [ ] No duplicate or contradictory entries remain.
- [ ] Outdated or low-value content trimmed if space is tight.
- [ ] File remains under 300 lines.
- [ ] The file is better organized after the edit than before.
- [ ] Project-specific info is in agent files; concept knowledge is in skills.

