---
name: gemini-deep-research
description: Local MCP server that hands a research question to Google Gemini Deep Research and polls for the report. Use when the user wants a Gemini Deep Research run, a second and independent research pass next to your own, or a long background search that costs none of your own context.
---

# Gemini Deep Research MCP

A local MCP server with two tools: start a Gemini Deep Research run, and poll it until the report is ready. The research is done by Google's agent, with its own search index, so it is independent of anything you find yourself.

## When to use it

- The user asks for Gemini Deep Research by name.
- A broad first survey of a topic, to run in the background while you do other work.
- A second opinion on a question you researched yourself: the two runs share no sources and no reasoning.

It returns a finished report, not sources you can open and check. For work that must rest on documents you read yourself, do the reading yourself and use this only for leads.

## Setup

- `GOOGLE_API_KEY` must be set in the environment.
- Optional: `GEMINI_API_BASE_URL` overrides the API base (default `https://generativelanguage.googleapis.com/v1alpha`).

```bash
uv run skills/gemini-deep-research/mcp-server.py
```

The agent ids are preview models (`deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`) on a `v1alpha` API. If a start call fails with an unknown agent, the ids in `mcp-server.py` (`AGENT_IDS`) need updating.

## Tools

- `deep_research_start(prompt, mode="regular", additional_instructions=None, file_uris=None, file_search_stores=None)`: starts a run in the background and returns `interaction_id`. `mode="max"` is deeper and slower. `file_uris` attaches documents; `file_search_stores` adds file-search stores.
- `deep_research_poll(interaction_id)`: returns `status`, `done` and the raw response.

## Usage

1. Call `deep_research_start` and keep the `interaction_id`.
2. A run takes about 10 minutes. Do other work meanwhile and poll every minute or so until `done` is `true`.
3. If `status` is `failed` or `cancelled`, report that and stop. Otherwise read the report from `raw.outputs`.

## Reading the result

`raw.outputs` is a list of items in order:

- `type: "thought"`: progress notes ("Mapping the Landscape", ...). They show the run is alive; leave them out of what you present.
- `type: "text"`: the report, in Markdown, in the `text` field. If there are several, join them in order.

A `text` item may carry `annotations`: `{start_index, end_index, url, type: "url_citation"}`, where the indexes are character positions in `text`.

**The cited URLs are Google redirect links** (`vertexaisearch.cloud.google.com/grounding-api-redirect/...`), not the sources themselves, and they can expire. Before a claim from the report goes into your own work with a link, open the redirect, take the real URL, and check that the page says what the report says. A claim you did not check is a lead from Gemini, and is presented as one.
