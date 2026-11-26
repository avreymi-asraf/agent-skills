---
name: manage-skills
description: Update, create, fix or improve Agent Skills (SKILL.md files). MUST be read before editing any SKILL.md file. Use when the user asks to update, modify, fix, create, improve, or review any skill — even if they point directly to the skill file path.
---
## manage-skills

Skills are markdown files that teach agents how to perform specific tasks. This skill guides you through creating and updating them, ensuring consistency, high actionability, and readability.

### Topics Covered
- **Use [Skill-File-Structure]** to learn how directories and SKILL.md are structured.
- **Use [Examples]** to see concrete implementations.
- **Use [Writing-Descriptions]** to write effective trigger conditions (WHAT and WHEN).
- **Use [Core-Authoring-Principles]** for the primary rules of skill-writing (progressive disclosure, brevity).
- **Use [Connecting-Skills]** to wire a skill into the ecosystem — its prerequisites, successors, and companions. Connecting skills is one of the most important parts of authoring one.
- **Use [Scripting]** to understand when and how to build versatile internal scripts.
- **Use [Anti-Patterns-and-Common-Mistakes]** to avoid typical pitfalls.
- **Use [Creating-a-New-Skill]** and **[Updating-an-Existing-Skill]** for end-to-end workflows.
- **Use [Verifying-Workflows-and-Processes]** to ensure your instructions execute flawlessly.
- **Use [Checklist]** to consistently verify your work before finalizing.
- **Use [Common-sections]** for standard patterns like checklists and examples.

For broader architectural patterns, consult [Common Patterns](Common Patterns.md).

## Skill-File-Structure

### Directory Layout

```
skill-name/
├── SKILL.md              # Required - main instructions
├── references/           # Optional - one or more reference files (each covering one topic)
│   ├── topic-a.md
│   └── topic-b.md
├── examples.md           # Optional - usage examples
└── scripts/              # Optional - utility scripts
```

> **References is a folder, not a single file.** Each file inside covers exactly one topic. Do not create a single `reference.md` at the skill root — use `references/<topic>.md` instead.

### Storage Locations

| Type | Path | Scope |
|------|------|-------|
| Personal | ~/dotfiles/skills/skill-name/ | Available across all your projects |
| Project | .cl/skills/skill-name/ | Shared with anyone using the repository |

### SKILL.md Structure
Each skill requires a `SKILL.md` with a YAML frontend and a markdown body made of topics. Each topic is a level-2 markdown header (`## Topic-Name`) followed by its content.
the YAML iclude 2 things:
- name: the name of the skill, it should be unique and not too long.
- description: a brief description of the skill, what it does and when to use it. this is very important for the agent to decide when to use the skill, so it should be specific and include trigger terms.

A skill is a list of paragraphs about a specific domain, their function is to teach an agent about a new domain that they don't know. The paragraphs can be very broad and give an explanation about the domain and also contain more specific topics or workflows or error patterns \ examples of using the skill \ common mistakes. One of the most important things is to choose the right paragraphs and the right level of freedom for each paragraph. You can also use references to keep the skill the required length, and keep the paragraph relevant.
Each paragraph is a level-2 header (`## Topic-Name`) and runs until the next `## ` header. Do not use HTML/XML-style tags (`<tag>`) to delimit topics. Use `###` and deeper headers for sub-sections inside a topic.
Within the paragraph, write what you need in an efficient way.

The first topic is like the name of the skill and is very important - it contains an explanation about the skill itself, an expansion of what is in which paragraph and a broader explanation about the domain that needs to be explained.
If the opening section is weak, the rest of the skill may never be used. Write it last, once you know the whole skill.
There is no need to explain obvious things - syntax, famous things in programming. Think carefully about what needs to be explained and what not.

```markdown
---
name: your-skill-name
description: Brief description of what this skill does and when to use it
---

## your-skill-name
explain about the skill, its purpose, and the broader domain it covers. what is in the skill and how the topics are organized. link to reference files if needed.

## Topic-1
Detailed instructions on a specific topic. Link to reference files for more info.
write it as markdown, use code blocks, lists, and formatting as needed to make it clear and actionable for the agent.

## Topic-2
...

## your-skill-name-scripts
Even though scripts are included in the topics, collect them and explain again what they do.

## your-skill-name-reference
If you have reference files, explain what they are and how to use them. link to them in the relevant topics. Even though they are included in the topics.

## Examples
Write an integrated example of using the skill, that includes the different topics and reference files. make it as concrete as possible, and not abstract. you can also include common mistakes in the example and how to fix them. look at the section about examples
```

| Field | Requirements | Purpose |
|-------|--------------|---------|
| `name` | Max 64 chars, lowercase letters/numbers/hyphens | Unique identifier |
| `description` | Max 1024 chars, non-empty | Helps agent decide when to apply the skill |

Use [Common Patterns](Common Patterns.md) for writing patterns.

## Examples
Concrete examples of using this skill's tools and workflows.

**Example: A Good Opening Section**
Instead of a single sentence, provide context and explicitly link to all subsequent topics so the agent knows exactly where to look:

```markdown
## csv-parser
Parses complex CSV files with nested structures.

### Topics Covered
- **Use [Basic-Parsing]** for standard schema extraction.
- **Use [Error-Handling]** for dealing with malformed rows.
- **Use [Scripting]** for the `parse_csv.py` automated tool.
- Reference [Formatting Rules](reference.md) for output standards.
```

## Writing-Descriptions

The description is **critical** — the agent uses it to decide when to apply the skill.

1. **Write in third person** (injected into system prompt):
   - Good: "Processes Excel files and generates reports"
   - Bad: "I can help you process Excel files"

2. **Be specific and include trigger terms**:
   - Good: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
   - Bad: "Helps with documents"

3. **Include both WHAT and WHEN**:
   - WHAT: What the skill does (specific capabilities)
   - WHEN: When the agent should use it (trigger scenarios)

## Core-Authoring-Principles
### Understanding the Skill

Before making changes, make sure you understand:

1. **Purpose and scope**: What tasks does this skill help with?
2. **Key domain knowledge**: What domain knowledge is required?
3. **Trigger scenarios**: When should the agent automatically apply this skill?

If unsure, verify with the user. Use AskQuestion when available.
### 1. Concise is Key

The context window is shared. Every token competes for space. The agent is already smart — only add context it doesn't have.

### 2. Progressive Disclosure

**SKILL.md must be under 300 lines.** Put essentials in SKILL.md; detailed reference in separate files read on demand. Keep references one level deep.

**SKILL.md ↔ references folder relationship**: The SKILL.md must explain each topic it covers well enough for the agent to act on it — references supplement, they don't replace. References live in a `references/` folder; each file covers exactly one topic. Never put everything in a single `reference.md` at the skill root. If a reference file is growing long or covering multiple concerns, split it into separate files in the folder, or fold the essential parts back into SKILL.md.

### 3. Set Appropriate Degrees of Freedom

| Freedom Level | When to Use | Example |
|---------------|-------------|---------|
| **High** (text) | Multiple valid approaches | Code review guidelines |
| **Medium** (templates) | Preferred pattern with variation | Report generation |
| **Low** (specific scripts) | Fragile, consistency critical | Database migrations |

## Connecting-Skills

### Connecting Skills — The Most Important Authoring Move

A skill is never an island. The single biggest factor in whether a skill actually gets used is how well it is **wired into the rest of the ecosystem**. An agent rarely finishes a task with one skill — it moves through a chain of them. If a skill does not tell the agent where to go next, the agent stalls mid-workflow even when the right skill already exists.

Every skill should make its place in the ecosystem explicit by naming three kinds of neighbours:

- **Prerequisites** — skills that must run first (e.g. `cdn-backup` before `deploy`).
- **Successors** — skills the agent hands off to next (e.g. `deploy` → `testing`).
- **Companions** — skills routinely used alongside this one, sharing data or context (e.g. `cdn-etl` ↔ `grafana-alerts`).

Rules for connecting:
1. **Name the actual skill in backticks** so its trigger terms are present and the agent can load it.
2. **Say when to hand off**, not just that a link exists — "after editing the config, use `deploy` to push it."
3. **Make links bidirectional** — if A points to B as its next step, B should name A as its prerequisite.
4. **Update the ecosystem map** — add the skill and its edges to the project's dependency map / routing table (e.g. `AGENTS.md`) so the connection is discoverable from outside the skill.

A skill with no inbound or outbound links is a red flag: it usually means the skill is mis-scoped, or the surrounding skills were never updated to point at it.

## Scripting

When a skill needs automation or tooling, use scripts. Scripts are explicit, portable, and easy to audit. Place them in `scripts/` and invoke them from the skill instructions.

**Critical Scripting Principles:**
- **No simple commands**: Scripts should cover actions that have no simple way to do them. If there are simple CLI commands or one-liners to perform the action, there is no reason to create a script. Do not create scripts that just wrap simple commands.
- **Document All Commands**: Even if actions can be done with simple commands and don't require scripts, **all necessary base commands must be explicitly documented in a reference file** (e.g., `reference.md`).
- **Versatile and Modular**: Think of scripts as versatile and modular tools that will allow for extensive work. Build them to handle complex logic, error handling, or multi-step processes that are too brittle for simple command strings.
- See the [scripts skill](../scripts/SKILL.md) for how to write and structure auxiliary scripts correctly.

## Anti-Patterns-and-Common-Mistakes

- **Windows paths**: Use `scripts/helper.py`, not `scripts\helper.py`
- **Too many options**: Provide one default approach, mention alternatives only when clearly needed
- **Time-sensitive info**: Use "Current method" / "Old patterns (deprecated)" sections
- **Inconsistent terminology**: Pick one term and use it throughout
- **Vague names**: Use `processing-pdfs`, not `helper` or `utils`
- **Island skills**: a skill with no links to related skills. Always name its prerequisites, successors, and companions, and add it to the dependency map (see [Connecting-Skills])

## Creating-a-New-Skill

When creating a new skill, follow these steps:
1. **Discovery**: Gather purpose, location, triggers, constraints, existing patterns
2. **Design**: Draft name, write description (with WHAT + WHEN), outline sections, identify supporting files
3. **Implement**: Create directory, write SKILL.md with frontmatter, create supporting files
4. **Connect**: Wire it into the ecosystem — name its prerequisite/successor/companion skills and add it to the dependency map / routing table (see [Connecting-Skills])
5. **Verify**: Run the checklist below

## Updating-an-Existing-Skill

When updating, the most important thing is **keeping consistency and quality**.

1. **Read the full skill first** — understand its structure, style, and voice
2. **Identify the root cause** — don't pile on fixes and warnings. Determine what's fundamentally wrong and fix that
3. **Integrate changes naturally** — new content must match the existing style and flow. Do NOT add a separate "rules" or "warnings" section
4. **Stay under 300 lines** — if adding content, trim elsewhere
5. **Verify**: Run the checklist below

## Verifying-Workflows-and-Processes

When a skill describes a process or workflow, **you must verify it yourself** before finalising. Do not assume a process is correct just because it was written — go through every step and confirm it works end-to-end.

1. **Walk through each step** — simulate or execute the process as the agent would. Don't just read it; follow it.
2. **Check for gaps** — are there steps that assume knowledge not stated in the skill? Fill them in.
3. **Check for errors** — does each step produce the expected output for the next step?
4. **Check for clarity** — would an agent unfamiliar with the domain understand every instruction? Rewrite anything ambiguous.
5. **Fix issues in place** — don't add a warning note. Correct the process directly so it is accurate and clear.

## Checklist

### Core Quality
- [ ] Description is specific and includes trigger terms (both WHAT and WHEN)
- [ ] Written in third person
- [ ] SKILL.md is under 300 lines
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract

### Structure
- [ ] Opening section is a broad intro with links to all topics and reference files
- [ ] References live in a `references/` folder — each file covers exactly one topic, not a second SKILL.md
- [ ] File references are one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Scripts cover complex actions and are versatile (no simple command wrappers)
- [ ] Workflows have clear steps
- [ ] Skill is connected — names its prerequisite, successor, and companion skills and is added to the dependency map / routing table
- [ ] Processes have been walked through and verified end-to-end

### Update-Specific
- [ ] Read the full existing skill before editing
- [ ] Changes match existing style and voice
- [ ] No "pile of fixes" — root cause addressed
- [ ] New content integrated into existing sections

## Common-sections

- **checklist**: For specific workflows, states, or for the system.
- **anti-patterns-and-common-mistakes**: A grouped list of common mistakes. Keep it practical.
- **examples**: An integrated example that will teach the agent how to work.
- **testing**: How to verify that the logic or tool works correctly.

