# MCP and REST contract

One list of operations, served twice by the same server: as MCP tools at `<url>/mcp` (Streamable HTTP) and as `GET <url>/api/...`. The names, parameters and results are the same. `GET <url>/api` returns the list with paths.

## The envelope

Every REST answer and every MCP tool result (in `structuredContent`, and as JSON text):

```json
{
  "provenance": {
    "repo_name": "OncoLens-experiments",
    "repo_uri": "https://github.com/org/OncoLens-experiments",
    "git_ref": "01-recist/thinking",
    "git_commit": "3f9a2c1e…",
    "dirty": false,
    "view_id": "recist-thinking",
    "panel_id": "confusion",
    "data_refs": {"direct": "main"},
    "generated_at": "2026-11-21T16:04:13+00:00",
    "server_version": "0.1.0"
  },
  "data": { }
}
```

- `dirty: true` means the working copy has uncommitted changes: the commit alone does not identify the data.
- `data_refs` appears when a dataset is pinned to another ref in `view.yaml`.
- `view_id`, `panel_id` are `null` for answers that are not about one view or panel.
- An error keeps the envelope: `{"provenance": ..., "error": {"type": "NotFound", "message": "..."}}`, with HTTP 404 or 400, or `isError` in MCP. Messages name what does exist (the fields of a dataset, the panels of a view).
- A raw image (`/api/views/<view>/visuals/<id>/image`) carries the same provenance in the `X-Observation-Provenance` header.

When you quote a number, quote `repo_name`, `git_ref`, `git_commit` and `dirty` with it.

## Overview tier: what is here

| Tool | REST path under `/api` | Returns |
|---|---|---|
| `list_views` | `/views` | Views with title, mode, panel count; views that do not parse, with their error |
| `get_view(view)` | `/views/{view}` | Panels (id, analyzer, component, mode, runtime args), dataset, trace, artifact and visual names |
| `get_catalog(view?)` | `/catalog` | Every analyzer with params, every component |
| `get_dataset_overview(view, dataset)` | `/views/{view}/datasets/{dataset}` | Record count; per field: type, missing, distinct, range or common values; three cut samples |
| `list_traces(view, traces, offset, limit)` | `/views/{view}/traces/{traces}` | One line per trace: steps, tool calls, errors, latency, tokens |
| `get_trace_outline(view, traces, trace_id)` | `/views/{view}/traces/{traces}/{trace_id}` | One line per step: kind, tool name, preview, error, cost |
| `get_metrics_summary(view)` | `/views/{view}/metrics` | Every metric tile, each matrix's accuracy and largest confusions, weakest slices, last and best of each curve |
| `list_visuals(view)` | `/views/{view}/visuals` | The visuals of the view |

## Drill-down tier: the content

| Tool | REST path under `/api` | Returns |
|---|---|---|
| `query_records(view, dataset, filter, search, fields, offset, limit, max_chars)` | `/views/{view}/datasets/{dataset}/records` | A page of records; long fields cut |
| `get_record(view, dataset, row, field?, offset, max_chars)` | `…/records/{row}` | One whole record, or a window of one field |
| `query_errors(view, panel, filter, offset, limit, max_chars)` | `/views/{view}/panels/{panel}/errors` | Records where gold differs from predicted, for a `kpi`, `confusion` or `slices` panel |
| `get_trace_step(view, traces, trace_id, index, offset, max_chars)` | `…/{trace_id}/steps/{index}` | One step in full |
| `get_panel(view, panel, args?)` | `/views/{view}/panels/{panel}` | Exactly what the panel shows |
| `compare_runs(view, left, right, key, fields, gold, pred, only, offset, limit)` | `/views/{view}/compare` | Counts of changed, fixed, broken pairs and the changed pairs with differences marked |
| `get_visual(view, visual)` | `/views/{view}/visuals/{visual}` | The picture and the numbers behind it |
| `get_artifact(view, artifact, offset, max_chars)` | `/views/{view}/artifacts/{artifact}` | A text file in a window |

All tools are read-only.

## Filters, paging and cut fields

`filter` is a JSON object; all conditions must hold. Over REST pass it as a JSON string: `?filter={"label":"PD"}`.

| Form | Meaning |
|---|---|
| `{"label": "PD"}` | equals (`null` matches a missing value) |
| `{"label": {"in": ["PD", "SD"]}}` | one of |
| `{"confidence": {"lt": 0.5}}` | `gt`, `gte`, `lt`, `lte` |
| `{"report": {"contains": "nodule"}}` | text contains, any case |
| `{"prediction": {"is_null": true}}` | missing |
| `{"label": {"ne_field": "prediction"}}` | differs from another field (`eq_field` for equal) |

- `search` matches text in any text field.
- Results are pages: `total`, `offset`, `limit`, `has_more`. Default `limit` is 10; ask for the next page rather than a huge one.
- `max_chars` (default 240 in `query_records`) cuts long fields. A cut record has `"_truncated": {"report": 1873}`: the field and its full length. Read the rest with `get_record(..., field="report", offset=0, max_chars=4000)`.
- Filters name top-level fields. To filter on a nested value, add a flat field when the data is written.

## The dual visual contract

`get_visual` answers with two things about one visual:

- **MCP**: an `image` content block (PNG; an SVG or a Vega-Lite chart is drawn to PNG on the server) and a text block with the envelope. `data.specs` holds the Vega-Lite specs, `data.data` the backing numbers.
- **REST**: the envelope with `data.image = {"mime_type", "base64"}`, `data.specs`, `data.data`.

Look at the picture for shape (a trend, an outlier, a mislabelled axis). Read values from `data`, never by eye.

## Lifecycle: `.observation/runtime.json`

Written in the repository when the server is up, removed when it stops (the folder ignores itself in git):

```json
{"pid": 4031, "host": "127.0.0.1", "port": 8787, "url": "http://127.0.0.1:8787",
 "mcp_endpoint": "http://127.0.0.1:8787/mcp", "health": "http://127.0.0.1:8787/health",
 "started_at": "…", "server_version": "0.1.0", "repo": {"repo_name": "…", "repo_uri": "…", "git_ref": "…", "git_commit": "…"}}
```

`observation status --repo .` reads it and checks that the process is alive and answers for this repository; a stale file is removed. `serve` does the same check first and prints `"status": "already_running"` instead of starting a second server. `GET /health` returns `{"status": "ok" | "degraded", "views": [...], "view_errors": {...}}` in the envelope.

## Other machines, proxies, cloud

| Need | Option |
|---|---|
| Reach the server from another machine | `--host 0.0.0.0 --port 8787` |
| Served under a path prefix | `--root-path /observation` (the proxy strips the prefix) |
| https or a public name | `--public-url https://lab.example.org/observation`: recorded in `runtime.json`, so agents get the right `mcp_endpoint` |
| The proxy sends another Host header to `/mcp` | `--allowed-host lab.example.org` (repeatable) |
| Trust `X-Forwarded-*` from a proxy | `--forwarded-allow-ips <proxy ip>` |
| A repository that is not on this machine | `--repo https://github.com/org/repo@ref` (cloned into `$OBSERVATION_CACHE_DIR`, default `~/.cache/observation-server`) |
| Data in object storage | Mount it (for example with the provider's FUSE tool) and give paths under the repository; or add a loader to `LOADERS` in the tool's `source.py` |

The server has no login. Bind it to a public address only on a network where everyone may read the data, or put it behind a proxy that authenticates.
