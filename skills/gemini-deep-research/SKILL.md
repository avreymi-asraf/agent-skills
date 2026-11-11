---
name: gemini-deep-research
description: Local MCP server for Google Gemini Deep Research interactions using explicit regular/max start tools, explicit file-capable variants, and status polling. Use when the user wants long-running Deep Research jobs with explicit start + poll control.
---

# Gemini Deep Research MCP

This skill provides a local MCP server for Google Gemini Deep Research interactions.

## Files

- `skills/gemini-deep-research/mcp-server.py`

## Requirements

- `GOOGLE_API_KEY` must be set in the environment.
- Optional: `GEMINI_API_BASE_URL` to override the default API base (`https://generativelanguage.googleapis.com/v1alpha`).

## Run Manually

```bash
uv run skills/gemini-deep-research/mcp-server.py
```

## Tools Exposed

- `deep_research_start_regular(prompt, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_max(prompt, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_regular_with_files(prompt, file_uris, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_max_with_files(prompt, file_uris, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_file_aware(prompt, file_uris, mode="regular", additional_instructions=None, file_search_stores=None)`
- `deep_research_poll(interaction_id)`

## Usage Pattern

1. Call one start tool and capture `interaction_id`.
2. Poll with `deep_research_poll` until `done` is `true`.
3. Read the `raw` field for final model output.

> **Note:** Deep Research interactions typically take **~10 minutes** to complete. The agent can perform other tasks or answer unrelated questions while the research runs in the background. Poll periodically (e.g., every 30–60 seconds) to check status.

## How to Read Results

`deep_research_poll` returns a JSON object with this structure:

```json
{
  "interaction_id": "v1_...",
  "status": "completed",
  "done": true,
  "raw": {
    "id": "v1_...",
    "status": "completed",
    "outputs": [
      {
        "type": "thought",
        "summary": [{"text": "**Mapping the Landscape**...", "type": "text"}],
        "signature": ""
      },
      {
        "type": "text",
        "text": "# Final Report Title\n\nReport body in Markdown...",
        "annotations": [
          {"start_index": 2879, "end_index": 2891, "url": "https://...", "type": "url_citation"}
        ]
      }
    ]
  }
}
```

### Output Array (`raw.outputs`)

The `outputs` array contains **mixed content types** in order:

| `type` | Purpose | How to Handle |
|--------|---------|---------------|
| `thought` | Research process updates (e.g., "Mapping the Landscape", "Preparing to Write") | These are *internal reasoning steps*. You may skip them when presenting the final answer, but they confirm progress during polling. |
| `text` | The final Markdown report | This is the **primary deliverable**. Present this to the user. |

**Important:** There may be multiple `thought` entries and one or more `text` entries. Always look for `type: "text"` to find the actual report.

### Extracting the Report

1. Filter `raw.outputs` for items where `type == "text"`.
2. The `text` field contains the full Markdown report.
3. If there are multiple `text` entries, concatenate them in order.

### URL Citations (`annotations`)

Text outputs may include an `annotations` array with URL citations:

```json
{
  "start_index": 2879,
  "end_index": 2891,
  "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/...",
  "type": "url_citation"
}
```

- `start_index` / `end_index`: Character positions in the `text` string where the citation applies.
- These are **grounded sources** from the web search. When presenting the report, you may:
  - Present the report as-is (citations are inline by position).
  - Optionally extract the cited URLs and append them as a "Sources" section.

### Recommended Presentation Flow

When `done == true` and `status == "completed"`:

1. **Extract report text** from all `type: "text"` outputs.
2. **Present the Markdown report** to the user directly.
3. **Optionally extract URLs** from `annotations` and list them as sources.
4. **Skip `thought` entries** in the final presentation (they are for debugging/progress only).

If `status == "failed"` or `"cancelled"`, report the failure and do not attempt to parse outputs.

## Notes

- Deep Research interactions typically take **~10 minutes** to complete. The agent can perform other tasks or answer unrelated questions while the research runs in the background.
- Input validation returns explicit `Error: ...` messages.
- Regular mode defaults to `deep-research-preview-04-2026`; max mode defaults to `deep-research-max-preview-04-2026`.
- Start requests use Deep Research `agent`, set `background=true`, and send `agent_config.type="deep-research"`.
- Tools are sent using typed entries and include `file_search.file_search_store_names` when `file_search_stores` is provided.
- File-aware requests require `file_uris` as URI-like strings.
- This server intentionally keeps scope minimal: start interaction + poll status.
