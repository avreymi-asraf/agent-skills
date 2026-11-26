---
name: opencode-runtime-hooks
description: Explains how OpenCode runs sessions and tools, and how to create plugin hooks safely. Use when analyzing opencode debug/event logs, troubleshooting agent/subagent behavior, or implementing hooks like tool.execute.before, tool.execute.after, shell.env, and experimental.session.compacting.
---

## opencode-runtime-hooks
This skill covers two connected jobs: understanding OpenCode runtime behavior and extending OpenCode with hooks.

### Topics Covered
- **Use [runtime-architecture]** for how OpenCode runs (TUI client, server, sessions, agents, tools).
- **Use [runtime-lifecycle-analysis]** to read logs and reconstruct what happened in a run.
- **Use [hook-creation-workflow]** to build hooks in `.opencode/plugins/`.
- **Use [hook-types-and-selection]** to understand hook families and pick the right hook quickly.
- **Use [hook-catalog]** for high-value hook signatures and when to use each.
- **Use [safety-permissions]** to avoid unsafe or fragile hook behavior.
- **Use [validation-debugging]** to verify hooks and debug failures quickly.
- **Use [examples]** for end-to-end implementation patterns.

**References:**
- `references/runtime-sequence.md` - concrete event sequencing, hooks vs events distinction, and jq parsing workflow.
- `references/hooks-reference.md` - hook signatures and a practical decision table.
- `references/hooks-and-events-payloads.md` - complete payload shapes, mutability, and lifecycle stages.

**Scope:**
- Runtime analysis for `opencode`, `opencode run`, `opencode serve`, and subagent task execution.
- Plugin hooks and behavior modification (not full custom tool architecture design).

## runtime-architecture
When OpenCode starts (`opencode`), it runs a TUI client and an HTTP server together. The TUI sends prompts and receives streamed events from the server.

Runtime building blocks:
1. **Sessions**: parent and child (subagent) sessions.
2. **Agents**: primary agents (for example `build`, `plan`) and subagents (`general`, `explore` or custom).
3. **Tool loop**: the model emits tool calls, OpenCode executes them, then resumes reasoning.
4. **Event bus**: state changes are emitted as events (`session.*`, `message.*`, `tool.execute.*`, etc.).
5. **Plugins**: hook into events and trigger points to inspect or modify behavior.

Run surfaces:
- `opencode` for interactive TUI.
- `opencode run "..."` for non-interactive automation.
- `opencode serve` for headless API server.
- `opencode attach <url>` to connect TUI to an existing server.

Config layering matters because hooks, agents, and permissions can be defined in multiple places and merged:
- remote org defaults
- global config (`~/.config/opencode/opencode.json`)
- project config (`opencode.json`)
- `.opencode` directories (agents, commands, plugins, skills, tools)
- inline or env overrides
- managed or admin config

## runtime-lifecycle-analysis
Use this sequence to analyze any debug or event stream. Hooks (🔧) can be intercepted and mutated by plugins. Events (📡) are read-only state change notifications.

1. **Session start**:
   - 📡 `session.created`
   - 📡 `session.updated`

2. **Prompt entry**:
   - 🔧 `chat.message` — intercepts user message; can mutate `output.parts`
   - 📡 `message.updated` / `message.part.updated` — user message stored
   - 📡 `session.status` becomes `busy`

3. **Model framing** (fires for title generation AND main agent):
   - 🔧 `experimental.chat.system.transform` — mutates `output.system: string[]`
   - 🔧 `chat.params` — mutates temperature, maxOutputTokens, options
   - 🔧 `chat.headers` — mutates request headers
   - 🔧 `tool.definition` — fires once per tool; mutates description/parameters

4. **Message history shaping**:
   - 🔧 `experimental.chat.messages.transform` — mutates `output.messages` array

5. **Assistant parts stream**:
   - 📡 `message.part.updated` with `step-start`
   - 📡 `message.part.updated` with `tool` state `pending`

6. **Tool lifecycle**:
   - 🔧 `tool.execute.before` — validate/modify `output.args`; throw to block
   - 📡 `message.part.updated` tool state `pending -> running`
   - 🔧 `tool.execute.after` — redact/transform `output.output` or `output.metadata`
   - 📡 `message.part.updated` tool state `completed` or `error`
   - 📡 `message.part.updated` with `step-finish`

7. **Text streaming**:
   - 📡 `message.part.updated` with `type: "text"`
   - 📡 `message.part.delta` — incremental text deltas

8. **Subagent task path** (when `task` tool is used):
   - Parent 🔧 `tool.execute.before:task`
   - Child 📡 `session.created` with `parentID`
   - Child runs its own full lifecycle (steps 1-7)
   - Parent 🔧 `tool.execute.after:task`

9. **Completion**:
   - 📡 `session.status` becomes `idle` (or `busy` if more turns)
   - 📡 `session.diff` and summary or title updates can follow

> **Critical distinction**: Some names are BOTH hooks and events (e.g., `tool.execute.before`). In debug logs, a top-level `type: "tool.execute.before"` is the 🔧 hook (mutable). A nested `event.type: "tool.execute.before"` inside `type: "event"` is the 📡 notification (read-only).

For quick parsing commands and a worked sequence, use `references/runtime-sequence.md`.
For complete payload shapes and mutation examples, use `references/hooks-and-events-payloads.md`.

## hook-creation-workflow
Use this implementation flow for stable hooks:

1. **Create plugin file** in project scope:
   - `.opencode/plugins/<name>.ts` or `.js`
2. **Use typed plugin signature** when possible:
```ts
import type { Plugin } from "@opencode-ai/plugin"

export const GuardPlugin: Plugin = async ({ client, project, directory, worktree, $ }) => {
  return {
    // hooks
  }
}
```
3. **Add npm dependencies only when needed**:
   - create `.opencode/package.json`
   - OpenCode runs `bun install` at startup for local plugin deps
4. **Enable npm plugins via config** (local file plugins auto-load):
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@my-org/opencode-plugin"]
}
```
5. **Restart OpenCode** after plugin or config changes.
6. **Validate with logs and events** before relying on behavior.

Plugin load order is deterministic across configured sources. Keep hooks idempotent and avoid assuming a hook runs only once.

## hook-types-and-selection
OpenCode hooks are easier to use when grouped by function. Use this taxonomy first, then choose a specific hook.

Hook families:
1. **Execution guard hooks** (around commands/tools)
  - `tool.execute.before`, `tool.execute.after`, `shell.env`, `command.execute.before`, `permission.ask`
  - Use for validation, argument normalization, output redaction, and policy enforcement.
2. **Prompt shaping hooks** (what the model receives)
  - `chat.message`, `chat.params`, `chat.headers`, `tool.definition`, `experimental.chat.system.transform`, `experimental.chat.messages.transform`
  - Use for instructions, model parameters, request headers, and tool schema shaping.
3. **Continuation hooks** (long-context behavior)
  - `experimental.session.compacting`, `experimental.compaction.autocontinue`, `experimental.text.complete`
  - Use for compaction prompt control and continuation behavior.
4. **Observation hooks** (event stream)
  - `event`
  - Use for analytics, notifications, auditing, and non-invasive monitoring.

Fast selection map:

| Goal | Hook to Start With | Why |
|------|--------------------|-----|
| Block dangerous tool usage | `tool.execute.before` | Stops risky calls before execution |
| Rewrite noisy or sensitive output | `tool.execute.after` | Central post-processing point |
| Inject runtime env vars | `shell.env` | Applies to shell execution context |
| Force model behavior (temperature, top-p, etc.) | `chat.params` | Mutates model request parameters |
| Add provider-specific headers | `chat.headers` | Central header injection point |
| Alter default system instructions | `experimental.chat.system.transform` | Directly rewrites system prompt fragments |
| Modify available tool schema text | `tool.definition` | Controls what the model sees about tools |
| Track session lifecycle without mutation | `event` | Read-only subscription to emitted events |

### Hooks vs Events: How to Tell Them Apart

OpenCode has two mechanisms with similar names:

| Mechanism | Symbol | In Debug Logs | Can Mutate? | Example |
|-----------|--------|---------------|-------------|---------|
| **Hooks** | 🔧 | Top-level `type` field | **Yes** — via `output` object | `tool.execute.before`, `chat.params` |
| **Events** | 📡 | Inside `type: "event"` records | **No** — read-only notifications | `session.created`, `message.part.updated` |

Some names exist as **both** (e.g., `tool.execute.before`). The hook fires first (allowing mutation), then the event emits (notifying observers of what happened).

When implementing plugins, you only interact with **hooks**. The `event` hook is the single exception — it lets you observe events without mutating them.

How to use hooks safely:
1. Start with one hook only.
2. Scope logic to explicit conditions (`input.tool === "read"`, specific paths, specific commands).
3. Mutate only fields you own in `output`.
4. Throw errors only when you want to hard-stop execution.
5. Keep expensive network work out of high-frequency hooks.

## hook-catalog
Common hooks and practical use:

| Hook | Input | Output | Use |
|------|-------|--------|-----|
| `tool.execute.before` | `{ tool, sessionID, callID }` | `{ args }` | Validate or modify tool arguments before execution |
| `tool.execute.after` | `{ tool, sessionID, callID, args }` | `{ title, output, metadata }` | Post-process tool results, redact output, add metadata |
| `shell.env` | `{ cwd, sessionID?, callID? }` | `{ env }` | Inject environment vars for shell execution |
| `experimental.chat.system.transform` | `{ sessionID?, model }` | `{ system: string[] }` | Add or remove system-prompt instructions |
| `experimental.chat.messages.transform` | `{}` | `{ messages }` | Rewrite message history before model call |
| `tool.definition` | `{ toolID }` | `{ description, parameters }` | Modify tool schema and description sent to model |
| `experimental.session.compacting` | `{ sessionID }` | `{ context, prompt? }` | Customize compaction prompt or context |
| `experimental.compaction.autocontinue` | compaction context | `{ enabled }` | Disable or allow synthetic auto-continue after compaction |
| `event` | `{ event }` | n/a | Subscribe to lifecycle events across sessions/messages/tools |

High-value patterns:
- Block sensitive reads (for example `.env`) in `tool.execute.before`.
- Add org-required env vars in `shell.env`.
- Enforce output redaction in `tool.execute.after`.
- Add persistent policy hints in `experimental.chat.system.transform`.
- Use `event` for telemetry and alerts without mutating execution.

> For complete payload documentation including input/output shapes, mutability, and lifecycle position, see `references/hooks-and-events-payloads.md`.

## safety-permissions
Hooks run inside OpenCode's execution flow, so safety and permissions must be explicit.

Rules:
1. Keep permissions restrictive by default for destructive tools.
2. Use pattern-based `permission.bash` rules (`"*": "ask"` then allowlist safe commands).
3. Never inject secrets into logs or tool outputs.
4. Prefer fail-closed behavior for sensitive checks (`throw` in pre-hook).
5. Keep hook logic fast and deterministic; long hooks stall interaction.
6. Treat `experimental.*` hooks as unstable API surfaces.

Useful permission defaults:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "read": "allow",
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow"
    }
  }
}
```

## validation-debugging
Use a tight validation loop after each hook change:

1. **Check resolved config**:
```bash
opencode debug config
```

2. **Run with verbose logs**:
```bash
opencode --print-logs --log-level DEBUG
```

3. **Exercise target flow quickly**:
```bash
opencode run --format json "test hook behavior"
```

4. **Verify event stream** (headless server):
   - `GET /event` for SSE events
   - `GET /session/:id/message` for message parts

5. **Inspect session logs**:
   - confirm `tool.execute.before` and `tool.execute.after` fire
   - confirm args or output mutations are present
   - confirm permission prompts are expected

If behavior is inconsistent, first disable all but one plugin to isolate load-order and interaction effects.

## opencode-runtime-hooks-reference
Use these reference files when implementing or debugging:
- `references/runtime-sequence.md` — event sequencing, hooks vs events distinction, jq parsing commands
- `references/hooks-reference.md` — hook signatures and practical decision table
- `references/hooks-and-events-payloads.md` — complete payload shapes, mutability, and lifecycle stages

## examples
End-to-end example: block `.env` reads and inject project env to shell.

1. Create `.opencode/plugins/security-guard.ts`:
```ts
import type { Plugin } from "@opencode-ai/plugin"

export const SecurityGuard: Plugin = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && typeof output.args?.filePath === "string") {
        if (output.args.filePath.includes(".env")) {
          throw new Error("Blocked: reading .env files is not allowed")
        }
      }
    },
    "shell.env": async (input, output) => {
      output.env.PROJECT_ROOT = input.cwd
      output.env.OPENCODE_GUARD = "enabled"
    },
  }
}
```

2. Start OpenCode and test:
```bash
opencode run "List secrets in .env"
```

3. Expected result:
- the read attempt fails with the plugin error
- shell executions include `PROJECT_ROOT` and `OPENCODE_GUARD`

4. If not working:
- run `opencode debug config`
- run with `--print-logs --log-level DEBUG`
- confirm plugin file path and export name
