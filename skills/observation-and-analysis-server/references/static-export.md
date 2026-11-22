# Static export

`observation export` writes a view, or every view of a repository, as one HTML file that opens from disk with no server and no network. Use it to send a result to someone, to attach it to a record of an experiment, or to keep what a view showed at one commit.

```bash
OBS="uvx --from git+https://github.com/avreymi-asraf/observation-server observation"

$OBS export --repo . --view recist-thinking --out reports/recist-thinking.html
$OBS export --repo . --out reports/all-views.html                        # every view, with a home page
$OBS export --repo https://github.com/org/repo@some-branch --out r.html  # a ref that is not checked out here
```

It prints a JSON report: the file, its size, the views, what was cut, and the provenance. Keep that report with the file.

| Option | Default | Meaning |
|---|---|---|
| `--view <id>` | all views | Export one view |
| `--out <file>` | required | Where to write |
| `--max-records <n>` | 2000 | Records embedded per dataset |
| `--max-traces <n>` | 200 | Traces embedded per trace set |
| `--ref`, `--allow-code` | | As for `serve` |

## What is in the file

- The styles (`tokens.css`, `components.css`) and the scripts (Vega, Vega-Lite, Vega-Embed, the components, the view's local components), inlined.
- The answer of every panel, computed at export time by the same analyzers the server uses.
- The records of every dataset and the steps of every trace, up to the limits; strings longer than 20,000 characters are cut.
- Every visual as an image, and image artifacts.
- The provenance of the moment of export, in the banner and in every embedded answer, and the note "Static export · <time>".

The file is about 1 MB before data (the chart library), plus the data.

## What works offline, and what does not

| Works | How |
|---|---|
| Both tabs, every panel, charts with tooltips, light and dark | Answers are embedded |
| Search, value filters and paging in the record table; clicking a matrix cell or a slice | Filtered in the page over the embedded records |
| The record drawer; the trace viewer with all steps | Embedded |
| The diff's `changed / fixed / broken / all` choices | Each answered at export time |

| Does not work | Why |
|---|---|
| Paging past the first page of a `spans` or `diff` panel | Only the first page is computed. The panel says so; raise the panel's `limit` in `view.yaml` before exporting if more is needed |
| Records beyond `--max-records` | Not embedded; the banner states "N of M records", and counts in the record table are counts of the embedded records |
| MCP and REST | A file is not a server. The "for agents" chips say so |

The rule that makes this possible is the same one the live page follows: a component may **filter and page rows it was given**, and never aggregates. Every number on the page was computed in Python, so the export and the server cannot disagree.

Metric panels (`kpi`, `confusion`, `slices`, `curves`) are always computed over the **whole** dataset, whatever `--max-records` is. Only the browsable records are limited.

## Before sending the file

The file contains the data itself: record text, traces, prompts. Opening it needs no access to the repository.

- Check that the data may leave the place it lives. For protected data (for example patient records), do not export; show the live server to someone who has access instead.
- Check the banner: `uncommitted changes` means the file does not correspond to a commit. Commit first if the export is a record of a result.
- Open the file once and click through both tabs. `observation verify` checks the live server, not the file.

## For an agent that receives an export

The page model is a JSON block in the file: `<script type="application/json" id="oa-page">`. Its `store.answers` maps `"<operation>|<params as JSON>"` to the same envelopes the server gives (for example `get_panel|{"panel":"confusion","view":"recist-thinking"}`), and `store.views.<view>.records.<dataset>` holds the embedded records. Parse that block rather than the rendered page.
