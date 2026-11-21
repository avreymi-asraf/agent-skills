# Components catalog

What a view can be built from. The live list, with every param, is `observation catalog` (or `GET /api/catalog`, MCP `get_catalog`); this page says which entry answers which question and what its result holds.

A panel entry in `view.yaml`:

```yaml
- id: confusion              # kebab-case; the panel's address for people and agents
  analyzer: confusion        # from the catalog, or from the view's analyzers.py
  dataset: thinking          # the dataset the analyzer reads, when it needs one
  title: Where the labels are confused
  note: Click a cell to read the cases in it.     # one line: what to look for
  span: half                 # full (default) or half of the page width
  component: confusion-matrix   # only to override the analyzer's default component
  params: {gold: label, pred: prediction}
```

## Observe: the data as it is

| Analyzer → component | Use it to | Params |
|---|---|---|
| `dataset_overview` → `raw-data-explorer` | Browse any table: schema with types, missing values and common values; search; click a value to filter; a row opens the whole record (long text readable, nested values as a tree) | `highlight: [fields]` shown first; `samples` |
| `trace_index` → `agent-trace-viewer` | Read agent runs in order: system, user, thought, tool call, tool output (under its call), final answer; latency and tokens per step; failed steps marked | `traces: <name>` |
| `artifact` → `artifact-viewer` | Show a prompt, a Markdown note, a log or an image, with path and size | `artifact: <name>` |

Datasets: `.jsonl`, `.ndjson`, `.json`, `.csv`, `.tsv`, `.parquet`; a glob (`runs/*.jsonl`) reads several files as one. Every record gets `_row`, its position.

Trace files, one trace per line (`.jsonl`) or a list (`.json`). `format: auto` recognises:

| Shape | Example of one trace |
|---|---|
| Chat messages (OpenAI or Anthropic) | `{"id": "t1", "messages": [{"role": "user", ...}, {"role": "assistant", "tool_calls": [...]}, {"role": "tool", ...}]}` |
| Steps | `{"id": "t1", "steps": [{"kind": "thought", "content": "..."}, {"kind": "tool_call", "name": "search", "content": {...}}]}` |
| One step per line | `{"trace_id": "t1", "kind": "user", "content": "..."}` |
| Inspect log (`.eval`) | read with `inspect-ai` when installed: `uvx --with inspect-ai ...` |

Step kinds: `system`, `user`, `thought`, `tool_call`, `tool_output`, `final`. Optional per step: `name`, `error`, `latency_ms`, `tokens_in`, `tokens_out`. Other keys of a trace (`label`, `score`, ...) are shown as its metadata.

## Analyze: what it means

| Analyzer → component | Question it answers | Main params |
|---|---|---|
| `kpi` → `kpi-header` | How good is this run, and against what? | `gold`, `pred`, `metrics: [accuracy, macro_f1, error_rate, n]`, `aggregates: [{field, agg, label, format, higher_is_better}]`, `baseline: {metric: value}` or `baseline_dataset: <name>` |
| `confusion` → `confusion-matrix` | Which labels are taken for which? | `gold`, `pred`, `labels` (order) |
| `slices` → `slice-matrix` | Where is it weak? | `by: <field>`, `gold`, `pred`, `min_records` |
| `spans` → `span-highlighter` | What did it point at in the text? | `text` + one of: `spans`; `gold_spans` + `pred_spans` (+ `match: exact \| overlap`); or `tokens` alone. `title_field` |
| `diff` → `side-by-side-diff` | What changed between two runs or two prompts? | `left`, `right` (datasets), `key`, `fields`, `gold` + `pred` (marks pairs fixed or broken), `context: [fields]`; or `left_artifact`, `right_artifact` |
| `curves` → `vega-panel` | How did training go? | `x: step`, `y: [metrics]`, `series: <run field>` |
| `vega` → `vega-panel` | A chart of your own | `spec: <path to Vega-Lite JSON>`; with a panel `dataset`, its records become the chart's data |
| `visuals` → `visual-gallery` | The figures the experiment saved | `only: [ids]` |

Shapes the analyzers expect:

- **Span**: `{"start": 12, "end": 40, "label": "target_lesion", "score": 0.92}`; offsets are characters of the `text` field; `score` is optional.
- **Token**: `{"token": " the", "logprob": -0.12}` or `{"token": " the", "prob": 0.89}`.
- **Curves table**: one row per step and run: `step, run, train_loss, eval_loss, ...`. Each metric is its own chart; two metrics never share a y-axis.
- **Aggregate formats**: `number`, `percent`, `integer`, `duration_ms`.

Runtime args (set per request, by the page or by `get_panel(..., args={...})`): `spans`: `offset`, `limit`, `filter`; `diff`: `only` (`changed`, `fixed`, `broken`, `all`), `offset`, `limit`; `trace_index`: `offset`, `limit`.

## Visuals: a picture and its numbers

```yaml
visuals:
  label_distribution:
    title: Gold label distribution
    image: runs/label_distribution.svg       # PNG, JPEG or SVG the experiment saved
    data: runs/label_distribution.json       # the numbers the plot was drawn from (JSON, JSONL or CSV)
  calibration:
    title: Calibration
    spec: runs/calibration.vl.json           # a Vega-Lite spec; `data` may supply its values
    data: runs/calibration.json
```

Every panel shown by `vega-panel` is also a visual, with id `panel.<panel id>`. When your experiment code saves a plot, save the table it was drawn from next to it and register both: a picture without numbers can be looked at but not read.

## Vega-Lite patterns

Return a spec from an analyzer; never set colours or fonts in it (the theme supplies them).

```python
chart = {
    "width": "container", "height": 200,
    "data": {"values": rows},                                  # rows computed in Python
    "mark": {"type": "bar", "width": 24},                      # bars stay thin
    "encoding": {
        "x": {"field": "bin", "type": "ordinal", "sort": order, "axis": {"labelAngle": 0}},
        "y": {"field": "error_rate", "type": "quantitative", "axis": {"format": ".0%"}},
        "tooltip": [{"field": "bin"}, {"field": "records"}, {"field": "error_rate", "format": ".1%"}],
    },
}
return {"charts": [{"id": "margin", "title": "", "vega": chart}], "summary": rows}
```

- Several series: `"color": {"field": "run", "type": "nominal"}`; the theme assigns hues in fixed order. More than eight series: fold the rest into "other" or split into several charts.
- Two measures with different scales: two charts in `charts`, never two y-axes.
- Always return `summary` (the rows behind the chart): the page shows it as a table and an agent reads it instead of the picture.
- Use Vega-Lite 5 syntax.

## The analyzer context

```python
context.dataset(name=None)   # the panel's dataset, or a named one → .rows(fields, filter, offset=, limit=), .count(filter), .columns, .name
context.traces(name)         # list of traces, each {"id", "title", "metadata", "steps": [...]}
context.artifact(name)       # {"title", "path", "kind", "text", ...}
context.labels               # the view's label order
context.source.resolve(path) # a file inside the repository
context.panel                # the panel entry (id, dataset, params)
```

Attach `"filter": {...}` to each row or cell a reader might want to open; the page and agents pass it to `query_records`.

## Promote to Core

The protocol is in the skill's `Local-Extensions-and-Promote-to-Core` topic. When it is done, add the new analyzer or component to the tables on this page.
