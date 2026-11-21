---
name: observation-and-analysis-server
description: Shows the data of NLP and agent experiments to people and to agents at once, with the observation-server tool (`uvx ... observation`) - one repo-aware server that reads `observation-and-analysis/<view>/view.yaml` in a repository and serves the same views as HTML pages, REST and MCP (Streamable HTTP), every answer stamped with repository provenance. Covers Observe views (raw records, agent traces, artifacts), Analyze views (metrics against a baseline, confusion and slice matrices, span and token highlighting, side-by-side diffs, training curves, visuals with backing data), local analyzers and components and promoting them to core, the token-based design system, static HTML export, the runtime lockfile, the sub-agent handoff contract and the verification gate. Use when building or changing a dashboard, viewer or view for experiment results, raw data, model outputs, agent trajectories or error analysis; when an agent needs to read experiment data or charts over MCP; when the user mentions observation, analysis views, view.yaml, a results dashboard, a trace viewer, or `observation serve / verify / export`.
---

<observation-and-analysis-server>
An experiment is understood by looking at its data. This skill gives one way to look, for two readers: a person reads pages, an agent reads the same data over REST and MCP. Both are served by `observation-server`, a standalone tool run with `uvx`; nothing is installed in the repository that is looked at.

The repository declares what to show in `observation-and-analysis/<view>/view.yaml`. The server discovers those views and does the rest. You almost never write a server, an endpoint or a page: you write a view file, and sometimes a small analyzer.

Source of the tool: `https://github.com/avreymi-asraf/observation-server` (its `README.md` is the reference for commands; `examples/demo-repo` is a complete synthetic view).

### Topics Covered
- **Use [Mental-Model]** for the terms (source, view, panel, analyzer, component, visual) and what always holds.
- **Use [Running-the-Server]** to start, find and stop a server, locally or behind a proxy.
- **Use [Writing-a-View]** for the steps from a data file to a verified view.
- **Use [Reading-as-an-Agent]** for the MCP and REST tools and how to keep your context small.
- **Use [Local-Extensions-and-Promote-to-Core]** when the catalog does not have what a view needs.
- **Use [Delegating-a-View]** for the handoff contract an orchestrator gives a sub-agent.
- **Use [Verification-Gate]** before saying a view is done.
- **Use [Static-Export]** to hand a view to someone without a server.
- References: [components-catalog](references/components-catalog.md), [mcp-rest-contract](references/mcp-rest-contract.md), [design-system](references/design-system.md), [static-export](references/static-export.md). Starter file: [assets/view.yaml](assets/view.yaml).

Connected skills: companion `notebook-observability` (a notebook for probing live code; this skill is for looking at results that are already on disk) and `code-as-tools` (analyzers are small tools in the same sense); prerequisite `coding-principles` when writing an analyzer; successor `testing` when promoting to core. In a lab made with `experiment-lab`, the "observation and analysis" shared component of an experiment repo is its `observation-and-analysis/` folder, and a try is a git ref of the source.
</observation-and-analysis-server>

<Mental-Model>
| Term | Meaning |
|---|---|
| **Source** | The repository the server shows, at one git ref. Every answer names it. |
| **View** | One folder `observation-and-analysis/<view>/` with a `view.yaml`: one experiment, one question, or one comparison. |
| **Dataset / traces / artifact** | The data a view names: a table of records (JSONL, JSON, CSV, Parquet), a file of agent trajectories, a text or image file. Paths are relative to the repository root. |
| **Panel** | One entry under `panels:`. It names an analyzer; that single entry becomes a panel on the page, a REST endpoint and an MCP result. |
| **Analyzer** | A pure Python function from (context, params) to JSON. All counting, slicing and diffing happens here. |
| **Component** | The web component that paints an analyzer's result. It never computes: it may filter and page the rows it was given, nothing more. |
| **Visual** | An image or chart tied to the numbers behind it. |
| **Provenance** | `{repo_name, repo_uri, git_ref, git_commit, dirty, view_id, panel_id, ...}` on every REST answer, every MCP result and every page banner. |

Two modes, equal in standing:
- **Observe**: the data as it is, with no assumption about what it means. Records, traces, files.
- **Analyze**: numbers and comparisons, each one click or one call away from the records behind it.

What always holds, and why:
1. **Computation is in Python, never in the page.** A number computed in the browser is a number an agent cannot get, and the two readers would stop seeing the same thing.
2. **Every answer carries provenance.** An agent working across several repositories or tries must never mix up where a result came from. Report provenance with any number you quote.
3. **A view writes no CSS and no colour.** Colours and type come from the tool's tokens, so every view in every repository looks like one system and works in light and dark.
4. **Catalog first.** Compose a view from existing analyzers before writing code; local code only for a question the catalog cannot ask.
</Mental-Model>

<Running-the-Server>
```bash
OBS="uvx --from git+https://github.com/avreymi-asraf/observation-server observation"

$OBS status --repo .        # is one running? prints runtime info, exit 1 if not
$OBS serve --repo .         # starts it; if one is running, prints its info and exits (never a duplicate)
$OBS stop --repo .
```

- Run `serve` in the background (it stays up). It prints JSON with `url` and `mcp_endpoint`, and writes the same to `.observation/runtime.json` in the repository (`pid`, `port`, `url`, `mcp_endpoint`, `health`, repo). Read that file, or `status`, before starting anything.
- `--repo` takes a folder or a git url with an optional ref: `--repo https://github.com/org/repo@branch`. A remote source is cloned into the cache and its `analyzers.py` is not run unless `--allow-code` is given.
- `--ref <ref>` shows another ref of a local repository (a try branch) without touching the working copy. To compare two refs inside one view, pin a dataset: `ref: <ref>` in `view.yaml`.
- One server shows one source. Two repositories means two servers on two ports; each has its own `runtime.json`.
- Connect an MCP client: `claude mcp add --transport http observation <url>/mcp`.
- Other machines, a proxy or https: `--host`, `--port`, `--root-path`, `--public-url`, `--allowed-host`. See [mcp-rest-contract](references/mcp-rest-contract.md).
- A view's local analyzer runs in the tool's environment. If it imports the repository's own packages, start from that environment: `uv run --with git+https://github.com/avreymi-asraf/observation-server observation serve --repo .`
</Running-the-Server>

<Writing-a-View>
1. **Look at the data first.** Open two or three records of each file. Note the id field, the gold and predicted fields, the long text fields, any nested spans or tokens.
2. **Read the catalog**: `$OBS catalog` (or MCP `get_catalog`). It lists every analyzer with its params. [components-catalog](references/components-catalog.md) says which to use for which question.
3. **Write `observation-and-analysis/<view>/view.yaml`**, starting from [assets/view.yaml](assets/view.yaml). Observe panels first, then Analyze panels that each answer one stated question. Give each panel a `title` that says what it shows and, where useful, a `note` that says what to look for.
4. **Declare `labels:`** in the order they should be read (for example `[CR, PR, SD, PD]`). Label order fixes colour and matrix order for the whole view.
5. **Serve and look**: `$OBS serve --repo .`, open `/views/<view>`. The server re-reads `view.yaml` and the data files on every request, so edit and reload.
6. **Run the gate**: `$OBS verify --repo . --view <view>` (see [Verification-Gate]).

A minimal view:

```yaml
title: Stage extraction · run 3
labels: [I, II, III, IV]
datasets:
  preds: {path: runs/run3/predictions.jsonl, id_field: patient_id}
panels:
  - {id: records, analyzer: dataset_overview, dataset: preds, params: {highlight: [patient_id, gold, pred, text]}}
  - {id: headline, analyzer: kpi, dataset: preds, params: {gold: gold, pred: pred, baseline: {accuracy: 0.71}}}
  - {id: confusion, analyzer: confusion, dataset: preds, params: {gold: gold, pred: pred}}
```

Mistakes that cost time:
- A path relative to the view folder. Paths are relative to the **repository root**.
- An unknown key. `view.yaml` is strict: a misspelt key fails the view, and the error is shown on the home page and by `verify`.
- Analyze panels with no Observe panel. Always give the raw records a panel: a number nobody can trace to a record is not trusted.
- A view per run. Put two runs in one view as two datasets and compare them with `kpi` (`baseline_dataset`) and `diff`.
</Writing-a-View>

<Reading-as-an-Agent>
The same data, over MCP tools or `GET <url>/api/...` (the names match; `GET <url>/api` lists them). Every result is `{"provenance": ..., "data": ...}`.

Read in two tiers, so that a dataset of long clinical notes does not fill your context:

| Tier | Tools | Gives |
|---|---|---|
| Overview | `list_views`, `get_view`, `get_catalog`, `get_dataset_overview`, `list_traces`, `get_trace_outline`, `get_metrics_summary`, `list_visuals` | Shapes, counts, one line per thing |
| Drill-down | `query_records`, `get_record`, `query_errors`, `get_trace_step`, `get_panel`, `compare_runs`, `get_visual`, `get_artifact` | Content, in pages, long fields cut |

- Start with `list_views`, then `get_view`, then `get_metrics_summary(view)`: all numbers of a view in one call.
- `query_records` takes a structured `filter`, not SQL: `{"label": "PD", "prediction": "SD"}`, or `{"confidence": {"lt": 0.5}}`, or `{"label": {"ne_field": "prediction"}}`. Every matrix cell and slice in a panel result carries the `filter` that selects its records.
- A cut field is listed under `_truncated` with its full length. Fetch it with `get_record(view, dataset, row)` or one window of one field with `field`, `offset`, `max_chars`.
- `get_visual` returns the picture (PNG, look at it) and the numbers and spec behind it (read values from these, never from the picture).

Full contract: [mcp-rest-contract](references/mcp-rest-contract.md).
</Reading-as-an-Agent>

<Local-Extensions-and-Promote-to-Core>
The tool is a locked shell with open plugins. Work on a view writes **only** inside that repository's `observation-and-analysis/`; the tool's own code changes only in a Promote to Core task. The reason: every repository runs the same tool, so a private change to it would make one repository's views differ from what agents and people see elsewhere.

When the catalog cannot ask the view's question:

- **Local analyzer**: `observation-and-analysis/<view>/analyzers.py`.

  ```python
  from pydantic import BaseModel, Field
  from observation_server.catalog import analyzer

  class Params(BaseModel):
      field: str = Field(description="...")

  @analyzer("my_question", mode="analyze", component="vega-panel", params=Params)
  def my_question(context, params: Params) -> dict:
      """One sentence: it becomes the description agents read."""
      rows = context.dataset().rows([params.field])
      return {"charts": [{"id": "c", "title": "", "vega": {...}}], "summary": [...]}
  ```

  Prefer an existing component: return `charts` + `summary` for `vega-panel`, or `items` for `kpi-header`. Then no page code is needed.
- **Local component**: `observation-and-analysis/<view>/components/<name>.js`, only when no built-in component can paint the result. Built from the shared classes and helpers; see [design-system](references/design-system.md).

**Promote to Core** when a second view, in any repository, needs the same analyzer or component. It is its own task, done in the `observation-server` repository:
1. Move the analyzer to `src/observation_server/analyzers/` (and the component to `static/components/`, with a line in `COMPONENTS` in `catalog.py`). Make its params general: field names as params, no view-specific constant.
2. Add a panel that uses it to the fixture view (`src/observation_server/fixture/.../view.yaml`), so it appears in `/_gallery` and is run by the tests.
3. Run `uv run pytest -q`, look at `/_gallery` in light and dark.
4. Add its row to the tables in the tool's `README.md` and in [components-catalog](references/components-catalog.md).
5. Delete the local copies and point the views at the core name.
</Local-Extensions-and-Promote-to-Core>

<Delegating-a-View>
A sub-agent sees none of your conversation. Give it this, filled in:

```text
Build an observation-and-analysis view. Load the skill `observation-and-analysis-server` first.

mode:        observe | analyze | hybrid
repository:  <path or git url>          view id: <kebab-case name>
data:        <path>  — <what one record is>, id field <name>
             <path>  — ...
sample records (2–3, real shape, cut long text):
             {...}
focus:       observe → the fields a reader must see first: <fields>
             analyze → the 2–4 questions the view must answer:
                       1. <question>   2. <question>
agents must be able to ask (MCP): <e.g. get_metrics_summary; query_records for errors of class X>
write only in: <repository>/observation-and-analysis/<view id>/
done when:   `observation verify --repo <repository> --view <view id>` passes, and you report
             its output, the panel ids, and anything the catalog could not express.
stop and report instead of finishing if: the data lacks a field a question needs, or a
             question needs a change to the tool itself.
```

Never include real patient or otherwise protected records as samples: describe the shape, or use synthetic records of the same shape.

When the work comes back, read the `verify` output, open the view, and check that each question has a panel that answers it.
</Delegating-a-View>

<Verification-Gate>
A view is not done until this passes:

```bash
$OBS verify --repo . --view <view>
```

It uses the running server, or starts one for the check, and tests what both readers rely on: `/health`; the view parses; every panel answers over REST and over MCP with provenance naming this repository, view and panel; every visual gives a picture and its numbers; the pages load with the provenance banner; local components use no literal colour, no inline style and no stylesheet. Exit code 0 means all passed. Paste its last lines in your report.

`verify` cannot see what a person sees. After it passes, open the page once (or take a screenshot with a browser tool) and read each panel: does the title say what it shows, is long text readable, does a click on a number lead to records.

If a check fails, fix the view, not the gate. A failing panel prints the analyzer's own message, which names the fields or params that exist.
</Verification-Gate>

<Static-Export>
```bash
$OBS export --repo . --view <view> --out report.html      # one view
$OBS export --repo . --out report.html                    # every view, with a home page
```

One file, readable offline: styles, scripts, every panel result, the records and traces behind them (up to `--max-records` and `--max-traces`; a cut is stated in the banner). Filters, search, the record drawer and the trace viewer keep working. The file holds the data itself: before sending it anywhere, check that the data may leave where it lives. Details: [static-export](references/static-export.md).
</Static-Export>

<examples>
**Task:** "Show me where the stage model fails, and let the next agent query it."

1. `$OBS status --repo .` → not running. Start `$OBS serve --repo .` in the background; note `mcp_endpoint`.
2. `head -n 2 runs/stage/predictions.jsonl` → fields `patient_id, text, gold, pred, evidence_gold, evidence_pred, cancer_type`.
3. `$OBS catalog` → `dataset_overview`, `kpi`, `confusion`, `slices` (by `cancer_type`) and `spans` (gold against predicted evidence) cover the question. No local code.
4. Write `observation-and-analysis/stage-errors/view.yaml` with those five panels and `labels: [I, II, III, IV]`.
5. `$OBS verify --repo . --view stage-errors` → `1 failed: REST get_panel stage-errors/evidence — dataset 'preds' has no field 'evidence'; it has: [..., 'evidence_gold', ...]`. Fix the param names, run again → all pass.
6. Report: the url, the MCP endpoint, the panel ids, the `verify` summary, and the headline from `get_metrics_summary` **with its provenance** (`repo`, `git_ref`, `git_commit`, `dirty`).

**Mistake:** writing `components/confusion.js` with a hand-made table and hex colours because "it is faster". The catalog already has `confusion`; `verify` rejects the colours; and the agent reading over MCP would get nothing from a table computed in the page. Use the analyzer.
</examples>
