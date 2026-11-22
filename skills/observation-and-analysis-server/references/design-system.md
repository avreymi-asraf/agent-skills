# Design system

Every view in every repository is drawn by the same tool with the same tokens, so the pages read as one system: quiet surfaces, one accent, colour used only where it means something, long text set to be read. This page is the contract for anyone who writes a local component or changes the tool's styles.

The living reference is `/_gallery` on a running server: every token and every component, drawn from a synthetic fixture through the real analyzers. Look at it in light and dark before and after any change to `tokens.css` or a component.

## Where things are defined

| File (in the tool, `src/observation_server/static/`) | Holds | Who edits it |
|---|---|---|
| `tokens.css` | Every colour, typeface, size, space, radius. The only file with a literal colour. | A design change to the tool |
| `components.css` | The shell, the shared classes, the built-in components. Refers to tokens by name. | A Promote to Core task |
| `theme.py` | The Vega chart theme, read from `tokens.css`, for the browser and for the PNG an agent gets | Follows the tokens |
| A view's `components/*.js` | Markup built from shared classes | The view's author |

A view never adds a stylesheet, a `style` attribute or a literal colour. `observation verify` rejects all three. The reason is not taste: a hex value does not change in dark mode, and a private layout is one more thing every later reader has to learn.

## Tokens

Colours are written once as `light-dark(<light>, <dark>)`; the mode follows the system setting, or the button in the banner.

| Layer | Tokens | Use |
|---|---|---|
| Surfaces | `--surface-page`, `--surface-1` (panels), `--surface-2` (insets, table heads, code), `--surface-3` (hover) | Depth comes from surface steps and hairlines, not from shadows |
| Ink | `--text-primary`, `--text-secondary`, `--text-muted`, `--border`, `--border-strong`, `--accent`, `--accent-ink` | Text always wears a text token, never a series colour |
| Chart | `--series-1` … `--series-8` (fixed order: blue, orange, aqua, yellow, magenta, green, violet, red), `--seq-1` … `--seq-5` (one hue, "near nothing" to "most"), `--div-mid`, `--chart-grid`, `--chart-axis` | Identity, magnitude, polarity |
| Status | `--status-good`, `--status-warning`, `--status-serious`, `--status-critical`, and `-ink` forms for text | State. Reserved: never a series colour, always with a word or an icon |

Research roles (layer 2) say what a colour means in an experiment:

| Role | Token | Shown as |
|---|---|---|
| Found and right | `--color-tp` | solid underline, tag `TP` |
| Predicted, not in gold | `--color-fp` | solid underline, tag `FP` |
| In gold, missed | `--color-fn` | dashed underline, tag `FN` |
| Reference answer / model answer | `--color-gold` / `--color-pred` | |
| Better / worse than baseline | `--color-better` / `--color-worse` | with ▲ or ▼ |
| Trace step kinds | `--color-system`, `--color-user`, `--color-thought`, `--color-tool-call`, `--color-tool-output`, `--color-tool-error`, `--color-final` | a rail and a dot beside the kind's name |
| Diff | `--color-diff-add`, `--color-diff-remove` | wash; removed text is also struck through |
| Selection, search hit | `--color-highlight` | |

A role is never carried by colour alone: each has a word, a tag, a line style or an arrow, so it survives colour-blindness and print.

Type and space:

| Token | Value | Use |
|---|---|---|
| `--font-ui`, `--font-read` | system sans, with Hebrew faces in the stack | Interface; long text |
| `--font-mono` | system mono | Identifiers, field names, structured values |
| `--text-xs` … `--text-hero` | 11px … 40px | Labels, interface (14px), reading (15px), titles, the one big figure of a tile |
| `--leading-read`, `--measure` | 1.7, 72ch | Long clinical and model text |
| `--space-1` … `--space-8` | 4px … 64px | All gaps and padding |
| `--radius-sm/md/lg/pill` | 4, 8, 12px | |

## Colour for labels

A class or entity label takes its hue from its position in the view's `labels:` list: first label `--series-1`, second `--series-2`, and so on. The hue follows the label, not its rank in a result, so a filter never repaints the survivors. Labels past the eighth share the neutral "other" hue: declare the eight that matter first, or fold the rest in the analyzer.

In a component: `OA.hue(label)` returns the class (`oa-hue-3`), which sets `--hue` for the shared classes.

## Writing a local component

```js
/* observation-and-analysis/<view>/components/margin-note.js */
OA.define("margin-note", class extends OA.Panel {
  render(data) {                       // data = the analyzer's result; return one node
    const { h, fmt } = OA;
    return h("div.oa-kpis", data.summary.map((row) => h("div.oa-kpi",
      h("div.oa-label", row.distance_from_threshold),
      h("div.oa-kpi__value", fmt.value(row.error_rate, "percent")),
      h("div.oa-kpi__delta", h("span.oa-muted", row.errors + " errors in " + fmt.count(row.records, "record"))))));
  }
});
```

Use it from the view: `component: margin-note` on a panel. `OA.Panel` fetches the panel's result and handles the loading, empty and error states.

Helpers:

| Helper | Gives |
|---|---|
| `OA.h("tag.class", {attrs}, ...children)` | A DOM node. Text children are text, so data is never parsed as HTML. `vars: {name: value}` sets a CSS variable such as a share |
| `OA.fmt.value(v, "percent" \| "integer" \| "duration_ms" \| "number")`, `OA.fmt.count(n, "record")`, `OA.fmt.delta(d, format)` | Numbers as text |
| `OA.ui.records({view, dataset, filter, first})` | The table of records for a filter; a row opens the whole record |
| `OA.ui.openRecord(view, dataset, row)`, `OA.ui.drawer(title, node)` | The drawer |
| `OA.ui.read(text)`, `OA.ui.json(value)`, `OA.ui.chip(text, kind)`, `OA.ui.state(kind, title, detail)`, `OA.ui.pager(state, onMove)` | Long text, JSON tree, chip, state, pager |
| `OA.call(operation, params)` | Any operation of the contract; works in a static export too |
| `this.load({offset: 20})` | Fetch the panel again with runtime args |

Shared classes (all in `components.css`):

| For | Classes |
|---|---|
| Layout | `oa-stack`, `oa-stack--tight`, `oa-row`, `oa-row--tight`, `oa-row--between`, `oa-grow`, `oa-split`, `oa-inset`, `oa-rule` |
| Text | `oa-label`, `oa-muted`, `oa-secondary`, `oa-small`, `oa-xs`, `oa-num` (aligned figures), `oa-mono`, `oa-read`, `oa-pre`, `oa-prose` |
| Pieces | `oa-chip` (`--good`, `--warning`, `--critical`, `--accent`, `--button`), `oa-button`, `oa-input`, `oa-dot`, `oa-bar`, `oa-table-wrap` + `oa-table` (`oa-table--rows` for clickable rows), `oa-disclosure`, `oa-legend`, `oa-swatch` |
| Figures | `oa-kpis`, `oa-kpi`, `oa-kpi__value`, `oa-kpi__delta` (`--better`, `--worse`) |
| Meaning | `oa-hue-1` … `oa-hue-8`, `oa-role-tp`, `oa-role-fp`, `oa-role-fn`, `oa-mark`, `oa-token` |

If a layout cannot be built from these, that is a gap in the tool: say so in your report and propose the class; do not write it locally.

## Layout and reading rules

- **The banner is always there**: repository, uri, ref @ commit, an "uncommitted changes" chip. It is drawn on the server, before any script.
- **One view, two tabs**: Observe and Analyze. A panel is a card with a title that says what it shows, an optional one-line note, and a "for agents" chip with the equivalent MCP call and REST url.
- **Panels are full width; `span: half` puts two side by side** (a matrix next to its slices). Do not go below half.
- **Long text** is set in `oa-read`: 15px, 1.7 leading, at most 72 characters a line, `dir="auto"` so Hebrew and Arabic run right to left and mixed text stays readable. Never put long text in a table cell: a cell shows one line, the drawer shows the whole.
- **Numbers in columns** use `oa-num`. A big standalone figure does not.
- **Every number leads to its records**: a matrix cell, a slice row, a span's record chip. A panel that shows a count with no way to the records is unfinished.
- **Three states**, drawn by the base class: loading, empty ("No records match"), error (the analyzer's message, which names what exists).
- **Charts**: one measure per chart, thin lines and bars, a legend for two or more series, a hover tooltip, and under the chart a "numbers" disclosure with the same data as a table.

## Changing the design itself

A change to `tokens.css` reaches every view of every repository, the charts in the page and the PNGs agents get. Do it as its own task in the tool's repository: change the token, look at `/_gallery` in light and dark, and for a chart colour check the new palette for colour-blind separation and contrast against both surfaces before keeping it. `tests/test_export_e2e.py` fails if a literal colour enters `components.css`.
