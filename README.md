# Agent Skills

A curated collection of production-grade AI agent skills compatible with the [Skills CLI](https://skills.sh) (`npx skills`).

These skills provide structured workflows, MCP tool wrappers, best practices, and runtime extensions for AI coding agents such as **Claude Code**, **Cursor**, **Codex**, **OpenCode**, and **Antigravity**.

---

## Installation & Usage

### 1. Install via Skills CLI (`npx skills`)

Install skills directly into your local project:

```bash
# Add skills interactively
npx skills add avrymi-asraf/agent-skills

# List all available skills in this repo
npx skills add avrymi-asraf/agent-skills --list

# Install a specific skill (e.g. cortex)
npx skills add avrymi-asraf/agent-skills --skill cortex

# Install multiple specific skills
npx skills add avrymi-asraf/agent-skills --skill cortex code-as-tools coding-principles

# Install all skills non-interactively
npx skills add avrymi-asraf/agent-skills --all
```

### 2. Global Installation

Install globally to make skills available across all projects on your machine:

```bash
npx skills add avrymi-asraf/agent-skills -g
```

### 3. Target Specific Agents

Specify which agent environment to install to (e.g. Claude Code, Cursor, OpenCode, Codex):

```bash
npx skills add avrymi-asraf/agent-skills --agent claude-code cursor
```

---

## Skills Catalog

| Skill | Description |
| :--- | :--- |
| [`agent-and-skill-improvement`](skills/agent-and-skill-improvement) | Maintains and improves agent files (identity, memory, tools) and skill files (`SKILL.md`). Load when completing tasks that produce learnings, updating agent behavior, or refining domain knowledge. |
| [`architecture-map`](skills/architecture-map) | Generates production-quality interactive self-contained HTML architecture diagrams and agent-ready JSON from codebases. |
| [`audit-agent-context`](skills/audit-agent-context) | Audits how well a repo's instructions, docs, and comments support an agent: Sonnet subagents collect all semantic data and can digest past agent sessions (tool calls, thinking, actions); Opus reports problems, fixes, workflow gaps, and missing data. |
| [`chatreplay`](skills/chatreplay) | Parses and interprets `.chatreplay.json` session logs capturing interactions between users, AI agents (VS Code / Copilot), and tools. |
| [`code-as-tools`](skills/code-as-tools) | Guides writing research and exploratory code as small, composable, notebook-friendly tools rather than rigid pipelines. |
| [`coding-principles`](skills/coding-principles) | Fundamental principles for code clarity, naming uniformity, live execution, and clean architecture without unnecessary refactoring. |
| [`colab-cli`](skills/colab-cli) | Manages Google Colab cloud runtimes, secrets, remote execution, and SSH access directly via the Colab CLI in agentic workflows. |
| [`cortex`](skills/cortex) | Builds and maintains a cortex: an LLM-maintained knowledge base in three layers (immutable sources, atomic claims anchored to a quote or an experiment, synthesis pages that cite claims), after Karpathy's LLM wiki. One skill for every operation (add, investigate, ask, review), a per-cortex profile, and a script that checks anchors and links. |
| [`create-qa-spectrum`](skills/create-qa-spectrum) | Streams, filters, and selects diverse reasoning QA datasets across multiple reasoning families, pushing them to Hugging Face. |
| [`experiment-lab`](skills/experiment-lab) | Builds and maintains a research lab repository: an autonomous system that runs experiments on external target repos in rounds (cortex, journal, worktrees, CLI). Ships a scaffold with `AGENTS.md`, the lab's own loop skill, a cortex profile, templates and `lab.py`. |
| [`gemini-deep-research`](skills/gemini-deep-research) | Local MCP server that hands a research question to Google Gemini Deep Research (start + poll) for an independent, background research pass. |
| [`grow-autonomy`](skills/grow-autonomy) | Grows an autonomous agent system (many tools, too large to keep in view, changing structure) so harder tasks can be handed to it: shapes what each agent understands and how attention is divided, fixes rejects at the root instead of with patch sentences, and keeps a reject journal. |
| [`huji-slurm`](skills/huji-slurm) | Runs training and evaluation jobs on the Hebrew University CS Slurm clusters (phoenix, cinder) over SSH: login through the jump host, sbatch/srun/arrays, HUJI-only flags, quota-safe setup, checkpoint-and-requeue, agent-driven submit-and-poll. |
| [`jira-workflow`](skills/jira-workflow) | Jira issue tracking workflow — search, read, create, update issues, plan implementations, and reference commit tickets. |
| [`manage-mcp`](skills/manage-mcp) | Guides designing and implementing focused Model Context Protocol (MCP) tools and integrating them into agent skills. |
| [`manage-skills`](skills/manage-skills) | Rules and quality patterns for creating, auditing, modifying, and improving Agent Skills (`SKILL.md`). |
| [`notebook-observability`](skills/notebook-observability) | Uses Jupyter notebooks as live observability playgrounds for production systems and AI pipelines while keeping them in sync with real APIs. |
| [`opencode-runtime-hooks`](skills/opencode-runtime-hooks) | Runtime architecture analysis and hook authoring guide for OpenCode sessions, agents, and tool execution lifecycle. |
| [`pdf-to-markdown-mcp`](skills/pdf-to-markdown-mcp) | Local MCP server converting PDFs to Markdown using Gemini or Ollama vision models with high-fidelity equation and table extraction. |
| [`project-agent-systems`](skills/project-agent-systems) | Builds project-local agent, skill, MCP, and memory setups across OpenCode, Copilot, and Codex without polluting global settings. |
| [`scripts`](skills/scripts) | Guides creation of operational Python (uv / PEP 723) and JS scripts for AWS/CDN environments with security and session handling. |
| [`tasks`](skills/tasks) | Task runner automation using Python-native `invoke` and `uv` inline PEP 723 dependencies to replace legacy Makefiles. |
| [`testing`](skills/testing) | Decides what to test and how: a small set of meaningful tests at boundaries, connections and external interactions, running code directly instead of trivial unit tests. |

---

## Repository Structure

```text
.
├── README.md
├── LICENSE
├── skills.sh.json
└── skills/
    ├── agent-and-skill-improvement/
    ├── architecture-map/
    ├── audit-agent-context/
    ├── chatreplay/
    ├── code-as-tools/
    ├── coding-principles/
    ├── colab-cli/
    ├── cortex/
    ├── create-qa-spectrum/
    ├── experiment-lab/
    ├── gemini-deep-research/
    ├── grow-autonomy/
    ├── huji-slurm/
    ├── jira-workflow/
    ├── manage-mcp/
    ├── manage-skills/
    ├── notebook-observability/
    ├── opencode-runtime-hooks/
    ├── pdf-to-markdown-mcp/
    ├── project-agent-systems/
    ├── scripts/
    ├── tasks/
    └── testing/
```

---

## License

[MIT](LICENSE)
