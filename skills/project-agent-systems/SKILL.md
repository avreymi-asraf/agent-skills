---
name: project-agent-systems
description: Build and document project-local agent, skill, MCP, and memory setups across OpenCode, VS Code/Copilot, and Codex without using user/global settings.
---
## project-agent-systems

This skill covers best practices for designing and documenting project-local agent systems, including repository-local agents, skills, MCP servers, prompts, custom instructions, and agent memory. The focus is on ensuring that projects are set up in a way that is compatible with popular agent platforms while avoiding assumptions about platform behavior or committing sensitive information.

## project-agent-systems-components

readme: the main file for use this project.
AGENT.md: a common file for OpenCode agents.

## Project-local agent systems

Use this skill when designing or documenting repository-local agents, skills, MCP servers, prompts, custom instructions, or agent memory. The default is always project/workspace-local setup only.

### Core rules

- Do not use user/global settings for project behavior.
- Do not commit secrets; use placeholders such as `<set-outside-git>`.
- Do not assume platform behavior that has not been verified in official docs.
- Do not create active platform directories/files unless the user explicitly approves them.
- Keep reusable source skills in this repo's `skills/<skill>/SKILL.md` convention unless activation in a platform-native path is intended.

### Repository conventions

- Source skills live at `.agents/skills/<skill>/SKILL.md`.
- Source MCP scripts can live beside a skill, commonly `.agents/skills/<skill>/mcp-server.py`.

Remember to update the relevant files. Skills, memory, and shared docs are very important to continue working on the project. You have all this as live files, and currently updating them is very important. Remember to do it!
