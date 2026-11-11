# Isolating agent context

How to make a repository the only intended source of what a Claude Code agent knows and does, and how to check that it really is, both locally and in cloud sessions (claude.ai/code).

Isolated means: every skill, setting, MCP server, agent and instruction file the agent gets comes from files committed to the repo. Everything else is either turned off, or known and listed. Memory and context that can't be turned off aren't failures. They only have to be known.

Each fact is marked:
- **[docs]** stated in the official documentation (code.claude.com/docs, checked 2026-11-11).
- **[seen]** observed in Claude Code 2.1.322 in a cloud container and in `claude -p` runs, but not documented. Can change between versions.

There are three layers, and you need all three:
1. **The repo:** a committed `.claude/settings.json` that turns off what a repo can turn off.
2. **One-time setup outside the repo:** what only the person, the cloud environment or the organization can turn off.
3. **A check:** what actually loaded, on every machine and environment the repo runs in.

## Every source of context

| Source | Where it comes from | Local | Cloud | Who can turn it off |
|---|---|---|---|---|
| Base system prompt | Claude Code itself | yes | yes | nobody (only replaced with `--system-prompt`) [docs] |
| Cloud additions to the prompt | Anthropic's control plane: git branch rules, GitHub rules, proxy credentials, the user's email, attribution text | no | yes | nobody [seen] |
| Managed policy | `managed-settings.json`, MDM, server-managed settings; can add CLAUDE.md, skills, agents, MCP, hooks | yes | server-managed only | the organization [docs] |
| Project CLAUDE.md, `.claude/CLAUDE.md`, `.claude/rules/` | the repo | yes | yes | — (this is the intended context) |
| Subdirectory CLAUDE.md | the repo, loaded when the agent touches files there | yes | yes | — |
| CLAUDE.md in parent directories | folders above the repo | yes | rarely | `claudeMdExcludes` [docs] |
| `~/.claude/CLAUDE.md`, `~/.claude/rules/` | the user | yes | only if a setup script writes it | `claudeMdExcludes` [docs, seen] |
| `CLAUDE.local.md` | uncommitted file in the repo | yes | no (not in the clone) | the person (delete it) |
| `AGENTS.md` | the repo; read only when no CLAUDE.md exists in or above the folder | yes | yes | add a CLAUDE.md [docs] |
| `@path` imports | any file a CLAUDE.md imports, inside or outside the repo | yes | yes | the repo (don't import outside files) |
| CLAUDE.md in `--add-dir` folders | only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` | opt-in | the cloud sets this for `/mnt/user-data` [seen] | — |
| Auto memory (`MEMORY.md`) | `~/.claude/projects/<project>/memory/`, first 200 lines at every start | on by default | starts empty | `autoMemoryEnabled: false` [docs] |
| claude.ai project memory and instructions | claude.ai project | no | project threads only | don't use project threads [docs] |
| Repo skills, commands, agents | `.claude/skills/`, `.claude/commands/`, `.claude/agents/` | yes | yes | — |
| User skills, agents | `~/.claude/skills/`, `~/.claude/agents/` | yes | the platform puts its own skill there [seen] | `skillOverrides`, `Agent(...)` deny |
| claude.ai account skills (`anthropic-skills:*`) | skills enabled on the account, the org's skills, and Anthropic's `pdf`, `xlsx`, `docx`, `pptx`, which always sync | when signed in with claude.ai | yes | `syncClaudeAiSkills: false` (not from the repo) [docs] |
| Bundled skills | Claude Code itself (`code-review`, `loop`, `dataviz`, ...) | yes | yes | `disableBundledSkills` [docs] |
| claude.ai account plugins (`@synced`) | plugins enabled on the account | when signed in | yes [seen] | `enabledPlugins: {"<name>@synced": false}` [docs, seen] |
| User-installed plugins | `~/.claude/plugins/` | yes | no | `enabledPlugins: false` [docs] |
| Built-in plugins (`@builtin`) | Claude Code itself | yes | yes | part of the tool; their skills via `skillOverrides` |
| Repo MCP servers | `.mcp.json` | yes | yes (auto-approved) | — |
| User/local MCP servers | `~/.claude.json` | yes | no | `allowedMcpServers` [docs, seen] |
| Plugin MCP servers | a plugin | yes | yes | `allowedMcpServers` [seen] |
| claude.ai connectors | the account; fetched by Claude Code locally, passed in by the host in the cloud | when signed in | yes | locally `disableClaudeAiConnectors`; in the cloud `allowedMcpServers`/`deniedMcpServers` [docs] |
| Platform tools | cloud: GitHub tools, Claude Code Remote MCP, Artifact, plugin suggestions | no | yes | `permissions.deny`, and only if you don't need them [docs] |
| Hooks | repo, user, plugin, managed settings, and the cloud platform's own | yes | repo + platform | `disableAllHooks` is all-or-nothing, including platform hooks |
| Output style | `outputStyle` in any settings file | yes | yes | pin it in the repo |
| Environment | shell env; in the cloud the environment's variables, setup script, network secrets | yes | yes | the person / the environment's owner |
| Session content | the date, a git snapshot, GitHub PR comments in auto-fix, Slack thread text | yes | yes | nobody; it is data, not configuration |

Same-name rules, when two sources define the same thing [docs]:
- **Skills:** enterprise beats personal, and personal beats project. A user skill named like a repo skill wins.
- **Agents:** managed beats project, and project beats user.
- **MCP servers:** local beats project, then user, then plugin, then connectors. Fields are not merged.
- **CLAUDE.md:** nothing overrides anything. All the files are joined together.
- **Account skills:** they keep the `anthropic-skills:` prefix when a local skill has the same short name. Both stay in context, so the agent sees two versions of the same skill.

## Layer 1: the repo

Keep all agent context in `CLAUDE.md`, `.claude/` and `.mcp.json`, and commit it. Put `CLAUDE.local.md` and `.claude/settings.local.json` in `.gitignore`. They are personal and invisible to everyone else.

A committed `.claude/settings.json` that turns off everything a repo can turn off:

```json
{
  "disableBundledSkills": true,
  "skillOverrides": {
    "design": "off",
    "doctor": "off",
    "plugin-authoring": "off",
    "session-start-hook": "off",
    "anthropic-skills:pdf": "off",
    "anthropic-skills:docx": "off",
    "anthropic-skills:xlsx": "off",
    "anthropic-skills:pptx": "off"
  },
  "allowedMcpServers": [
    { "serverName": "<each server in .mcp.json>" }
  ],
  "autoMemoryEnabled": false,
  "claudeMdExcludes": [
    "/{root,home/*,Users/*}/.claude/CLAUDE.md",
    "/{root,home/*,Users/*}/.claude/rules/**"
  ]
}
```

What each key does:
- **`disableBundledSkills`** removes the skills that ship with Claude Code [docs]. Three stay listed in 2.1.322, `design`, `doctor` and `plugin-authoring`, so they are also in `skillOverrides` [seen].
- **`skillOverrides`** turns off one skill by name. It accepts `"off"`, `"user-invocable-only"` and `"name-only"` [docs]. There is no wildcard, so it can't turn off all account skills [seen]. Two entries need care:
  - **The `anthropic-skills:` prefix.** A short name hits the local skill: `"code-as-tools": "off"` turned off the repo's skill and left `anthropic-skills:code-as-tools` on [seen].
  - **`session-start-hook`.** It is a user skill the cloud platform installs [seen].
- **`allowedMcpServers`** lists every server in `.mcp.json` by name, and every other server is dropped: user servers, plugin servers, and connectors [docs]. A plugin's MCP server was dropped this way [seen]. Use `[]` if the repo has no servers.
  - In the cloud, the docs say allowlist entries that reach the session filter the connectors the host passes in. This audit hasn't checked that in a cloud session, so confirm it with the check below.
  - Built-in servers skip the allowlist [docs].
  - `serverName` is not a security control, but it is enough for isolation, where nobody is trying to get around it.
- **`autoMemoryEnabled: false`** stops reading and writing `MEMORY.md` [docs]. Leave it on if you want memory, but then it is a source the check will list.
- **`claudeMdExcludes`** skips CLAUDE.md files by absolute-path glob. The brace pattern covers Linux, macOS and the cloud's `/root` [seen]. A parent folder's CLAUDE.md has no portable path, so the check reports it instead.
- **`enabledPlugins: {"<name>@synced": false}`** keeps one account plugin out of the repo [docs, seen]. Layer 2 turns them all off at once, which is simpler. Use this key only for a plugin you can't turn off there.

Leave these out:
- **`disableAllHooks`.** It also removes the cloud platform's hooks and the repo's own.
- **`disableClaudeAiConnectors`.** It only acts on connectors Claude Code fetches itself, not on those a cloud host passes in [docs]. `allowedMcpServers` covers both.

Where this file is not read [docs]:
- **Project threads.** No `settings.json`, `.mcp.json`, skills or agents load. Only CLAUDE.md and rules do.
- **Sessions with several repositories.** Only `enabledPlugins` and `extraKnownMarketplaces` are read.

So run isolated work in single-repo sessions.

Optional: a short "Agent context" section in the README that lists the sources (CLAUDE.md, `.claude/`, `.mcp.json`, the cloud environment's name). It makes the sources clear to people. The check reads the files themselves, so the list can't make the check wrong.

## Layer 2: one-time setup outside the repo

A repo can't stop account skills from syncing: `syncClaudeAiSkills` is read only from user, local and managed settings [docs]. Account skills are the largest outside source. In one cloud session, 19 account skills loaded, 4 of them copies of skills in the repo [seen].

**Locally, per person.** Create `.claude/settings.local.json` in the repo, not committed:

```json
{ "syncClaudeAiSkills": false, "syncClaudeAiPlugins": false }
```

This stops account skills and account plugins in this repo only. Other projects keep them, and nothing is deleted [docs, seen]. The same keys in `~/.claude/settings.json` turn them off in every project, and move the synced skills to `~/.claude/skills/.trash/` [docs].

**In the cloud, per environment.** User and local settings files are not read from your machine [docs]. Pick one:
- **A cloud environment for this repo** whose setup script writes the same file:
  ```bash
  if [ -d <repo> ]; then printf '{"syncClaudeAiSkills": false, "syncClaudeAiPlugins": false}\n' > <repo>/.claude/settings.local.json; fi
  ```
  The script runs after the clone [docs]. A `claude -p` in a cloud container honored the file [seen]. Whether the main cloud session honors it isn't documented, so confirm it with the check below. This keeps local and cloud on one mechanism.
- **claude.ai → Customize → Skills:** turn off the skills you don't want. This applies to every surface on the account, including chat. Anthropic's `pdf`, `xlsx`, `docx` and `pptx` always sync [docs], which is why Layer 1 turns them off by name.
- **Organization owner:** server-managed settings with `syncClaudeAiSkills: false` (and, if wanted, `allowedMcpServers` with `allowManagedMcpServersOnly`). This reaches cloud sessions for the whole organization [docs].

**Connectors.** `allowedMcpServers` in Layer 1 handles them. To also keep them away from the account, disconnect them at claude.ai/customize/connectors, or turn them off per session [docs].

**The environment itself is context.** Its variables, setup script and network secrets reach every session in it [docs]. Name the environment after the repo, keep its script short, and mention it in the README.

**GitHub Actions (`claude-code-action`).**
- **Authenticate with an API key or a `claude setup-token` token.** Account skills, account plugins and connectors then never load [docs].
- **Pass `--setting-sources project` in `claude_args`.** This drops user settings. The action's `settings` input is written to user settings, so with this flag pass settings with `--settings` instead [reported, from the action's source].
- **PR runs restore `.claude/`, `.mcp.json` and `CLAUDE.md` from the base branch** [docs].

## What can't be turned off

Know these and list them in the report. Don't treat them as failures:
- the base system prompt, and in the cloud the control plane's additions, including the user's email and the git and PR rules [seen]
- managed and server-managed policy [docs]
- cloud platform hooks and tools. One cloud session had a SessionStart hook that reports a failed setup script, a Stop hook that checks for unpushed git work, the GitHub tools and the Claude Code Remote MCP server [seen]
- built-in agents (`general-purpose`, `Explore`, `Plan`, ...) and built-in plugins. Explore and Plan can be removed only with an environment variable [docs]
- auto-mode rules an organization admin adds [seen]
- data that enters the session: PR review comments in auto-fix, Slack thread text, files the agent reads

## Layer 3: check what actually loaded

**The script.** Run it in the repo, locally and inside a cloud session:

```
python3 scripts/check_isolation.py [--repo DIR] [--allow NAME ...] [--json]
```

What it does:
- It starts `claude -p` with stream-json output and reads the `system/init` event: skills, plugins with their source, MCP servers with their source, and agents [docs].
- It reads every `InstructionsLoaded` hook payload: the path, `memory_type` (`User`, `Project`, `Local`, `Managed`) and `load_reason` of each CLAUDE.md and rule [docs]. The hook is passed with `--settings` and needs nothing in the repo.
- It stops before any model call, so it costs nothing. Both arrive before the first request [seen].

What the report shows:
- what came from the repo, and repo files git doesn't track (such as `CLAUDE.local.md`)
- everything else, grouped as instructions, skills (labelled account, plugin, or bundled/user), plugins, MCP servers and agents
- built-in plugins on their own line, without counting them as external

Exit code: 0 when nothing external loaded, 1 when something did, 2 when the check couldn't run. `--allow` accepts a name on purpose. That makes the script usable in CI.

**In the session itself.** Two things are out of the script's reach:
- **Connectors.** A cloud host passes them to the main session, not to a `claude -p` started inside it [seen].
- **Hooks.** The init event doesn't list them.

To check those:
- **Commands:** `/context` (memory files, skills, MCP tools, agents, each with its source), `/mcp`, `/skills` (account skills appear under `claude.ai sync`), `/hooks`, `/status` (settings files loaded) [docs].
- **Ask the agent.** It sees its own skill list and MCP servers. Ask it to list them and compare with `.claude/` and `.mcp.json`.
- **Read the session transcript.** In a cloud container it is at `~/.claude/projects/<project>/<session>.jsonl`. Its `attachment` entries (`skill_listing`, `mcp_instructions_delta`, `session_context`) show what the main session received [seen]. See [reading-agent-traces.md](reading-agent-traces.md).

Run the check again after changing account skills, creating a new cloud environment, or upgrading Claude Code. Account skills sync in the background, so new ones appear without any change to the repo [docs].

## Where the docs and what we saw disagree (2.1.322)

- **Account plugins in ordinary cloud sessions.** The plugin docs list only Cowork and terminal sessions, but they loaded in a cloud session, and the changelog agrees [seen].
- **The cloud user folder.** "`~/.claude/skills` and `~/.claude/settings.json` aren't read in the cloud" is true of your machine's files. The cloud platform puts its own skill, settings (`launcher-settings.json`) and hooks there [seen].
- **AGENTS.md.** It should load when no CLAUDE.md exists. It did not load in `claude -p` runs [seen].
- **Auto memory in the cloud.** It was off by default in cloud `claude -p` runs, where the docs only say it is on locally [seen].

## Sources

code.claude.com/docs/en/:
- `memory`, `settings`, `settings-reference` (`syncClaudeAiSkills`, `skillOverrides`, `claudeMdExcludes`)
- `skills` (synced skills, bundled skills), `plugins/loading`
- `mcp` (how connectors reach Claude Code), `managed-mcp` (allowlists and denylists)
- `hooks` (`InstructionsLoaded`, `SessionStart`), `headless` (init event)
- `cloud-environments` (what carries over), `claude-projects`, `github-actions`, `agent-sdk/claude-code-features`
