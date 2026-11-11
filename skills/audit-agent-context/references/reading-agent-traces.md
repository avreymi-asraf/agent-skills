# Reading agent traces

How to read what an agent actually did in a past or running session: the tool calls it made, what it thought, what it read and changed, and the same for its subagents. Used by Step 2 (Observe) of the audit to understand how context really flowed to the agent.

Each fact is marked:
- **[docs]** stated in the official documentation (checked 2026-11-11).
- **[seen]** observed directly in a real session, but not documented. Formats marked this way can change between versions.

## What to look for in a trace

Whatever the platform, the audit wants the same five things from a session:

1. **Context at start.** What was injected before the agent acted: instruction files, skill listings, reminders.
2. **Loads along the way.** Every instruction file or skill the agent read or invoked, and what triggered it.
3. **Search path.** What the agent looked for, how many attempts it took, what it found.
4. **Stalls.** Failed or repeated tool calls, guesses, user corrections and interruptions.
5. **Handoffs.** What each subagent was told, what it did, and what came back to the parent.

## Claude Code, local

### Session transcripts (the main source)

- Path: `~/.claude/projects/<project>/<session-id>.jsonl`. `<project>` is the working directory with every non-alphanumeric character replaced by `-`. Paths over 200 characters are truncated with a hash suffix. `CLAUDE_CONFIG_DIR` moves the whole `~/.claude` folder. **[docs]**
- Retention: deleted after `cleanupPeriodDays` (settings.json), 30 days by default. Sessions run with `-p --no-session-persistence` leave no transcript. **[docs]**
- Format: one JSON object per line. The docs call the entry format internal and warn that it changes between versions, so parse defensively. **[docs]**
- Entries observed in version 2.1: **[seen]**
  - `type: "user"`: `message.content` is a string (a prompt) or a list with `text` and `tool_result` blocks (`tool_use_id`, `content`, `is_error`).
  - `type: "assistant"`: `message.content` is a list with `text`, `thinking` and `tool_use` blocks (`name`, `input`, `id`). `message.model` names the model.
  - `type: "attachment"`: what the harness injected into context (environment, skill listing, reminders). This is the best evidence for "context at start".
  - `type: "system"`: hook summaries and notices.
  - Every entry carries `uuid`, `parentUuid`, `timestamp`, `cwd`, `gitBranch`, `sessionId` and `isSidechain`.
- Thinking: the block is always there, but its text can be empty, with only a signature left. By default the API redacts thinking; the `showThinkingSummaries` setting controls whether summaries are returned. So a transcript may show *that* the agent thought, not *what*. In that case, infer intent from the text it wrote and the order of its tool calls. **[docs for the setting, seen for the empty block]**

### Subagent transcripts

- Path: `~/.claude/projects/<project>/<session-id>/subagents/agent-<agentId>.jsonl`, with an `agent-<agentId>.meta.json` beside it. **[docs]**
- The meta file holds `agentType`, `description` and `toolUseId`, which links it to the parent's `Agent` tool call. The first entry of the transcript is the brief the subagent received. Entries have `isSidechain: true`. **[seen]**
- The parent's own transcript contains only the brief (in the `tool_use` input) and the subagent's final result (in the `tool_result`). The subagent's tool calls are only in its own file. Read both to see what was lost in the handoff. **[docs for forks, seen for other subagents]**

### The digest script

`scripts/trace_digest.py` reads the files above so you don't have to load raw transcripts, which run to megabytes:

```
python3 scripts/trace_digest.py list [--repo DIR] [--limit N]
python3 scripts/trace_digest.py digest <transcript.jsonl> [--out FILE] [--max-chars N] [--no-subagents]
```

`list` shows the repo's sessions, newest first, with size, subagent count and first prompt. `digest` keeps prompts, thinking, injected context, every tool call and a truncated result, then appends each subagent. A 590 KB session becomes about 30 KB. It skips entries it doesn't recognise, so a format change gives a thinner digest, not a crash. If a digest looks empty, open the raw file and check the entry shapes against the list above.

### Other ways

| Way | What you get | When to use |
|---|---|---|
| `/export [file]` | The conversation as plain text. **[docs]** | A person wants to hand over one session. |
| `claude --resume <id or .jsonl path>`, `claude --continue` | Reopens a session with its full history. There is no command that lists sessions non-interactively. **[docs]** | To ask the original agent why it did something. |
| `claude -p "..." --output-format stream-json --verbose` | A live JSON event stream: `system` (init, hooks, retries), `assistant`, `user`, and a final `result`. Subagent messages carry `parent_tool_use_id`. Subagent text and thinking are forwarded only with `--forward-subagent-text`. **[docs]** | To capture a fresh run of a test task. |
| Agent SDK message stream | The same events as objects (`AssistantMessage`, `SystemMessage`, `ResultMessage`, `StreamEvent`). **[docs]** | Scripted experiments. |
| Hooks | Every hook gets `transcript_path`. `PreToolUse` gets `tool_name`, `tool_input`. `PostToolUse` adds `tool_response`, `duration_ms`. `SubagentStop` gets `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`. The transcript file is written asynchronously and can lag behind the hook. **[docs]** | To log tool calls live, or collect traces from many sessions into one place. |
| OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1` plus `OTEL_*` exporters) | Events `claude_code.tool_result` and `claude_code.tool_decision` with tool name and decision. Prompts, tool inputs and responses are left out unless `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_ASSISTANT_RESPONSES` are set. **[docs]** | Counting tool use across a team. Too thin for a context-flow audit on its own. |

## Claude Code, cloud sessions

- **Inside the running container** the transcript is at the same path as locally (`~/.claude/projects/...`, subagents included), and the digest script works on it. The container is temporary, so this only covers the session you are in. **[seen]**
- **Anthropic keeps the transcript** server-side so the session can be reopened; deleting the session deletes it. **[docs]**
- **Reading from outside:**
  - The web UI at claude.ai/code shows the session, and it can be shared. **[docs]**
  - `claude --teleport <session-id>` (or `/teleport`) pulls a cloud session into a local CLI session, after which it has a local transcript like any other. It needs the same repository, a clean git state and the branch pushed. Messages that were compacted away are not copied. **[docs]**
  - From another cloud session that has the `claude-code-remote` tools: `list_sessions` finds sessions, `list_events` pages through one session's events (filter `kinds` to `user`, `assistant`, `result` to drop the noise), `get_event` reads one. This is the only route that needs no local machine. **[seen]**
- `claude --resume` does not list cloud sessions. **[docs]**

## Antigravity (agy)

Not researched yet; this section is filled in separately.

## Privacy

Transcripts contain the user's own messages, file contents, and sometimes secrets printed by tools. Keep digests under `.audit/`, make sure `.audit/` is in `.gitignore`, and never quote a credential in a digest or report.
