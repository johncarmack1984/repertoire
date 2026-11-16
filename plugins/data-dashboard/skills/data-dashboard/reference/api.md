# The library

This file holds the detail for step 6: every call, option, and data field. The library is `assets/dashboard.js`, the styles are `assets/dashboard.css`, and the tooling is `scripts/dashboard.py` with `assets/check.js`, which only the check loads. Every page reaches the library through the global `DataDashboard`, aliased in page code as `const dd = DataDashboard`.

## The page

`dashboard.py new` writes the page. Its parts, in order:

- `<meta name="dd-viewport" content="1440x800">`, the design viewport in CSS px.
- `<!-- data-dashboard:css 0.1.0 sha256:… -->` `<style>` … `</style>` `<!-- /data-dashboard:css -->`, the inlined `dashboard.css`. Never edit it by hand: `check` fails a region whose content no longer matches its sha256, and `sync` rewrites it.
- `<!-- data-dashboard:page-style -->` … `<!-- /data-dashboard:page-style -->`, the page's own CSS. Its first rule is `:root { --dd-cols: 72; --dd-rows: 40; }`, the design viewport divided by 20 px, which `new` writes and `check` compares against the meta. The grid's `grid-template-columns` and `grid-template-areas` go here.
- `<!-- data-dashboard:page -->` … `<!-- /data-dashboard:page -->`, holding `header.dd-head`, `main.dd-grid`, `footer.dd-foot`, the data block `<script type="application/json" id="dd-data">`, and the page script `<script type="module">`. The page script is a module so that it runs after the library, which is inlined after it.
- The header holds `h1.dd-title`, `p.dd-asof` and `p.dd-flags`, the count of flagged rows beside the as-of line. The page script fills the as-of and calls `dd.flags('#dd-flags')`, so a new page says "Nothing flagged" until its sections flag a row.
- `<!-- data-dashboard:lib 0.1.0 sha256:… -->` `<script>` … `</script>` `<!-- /data-dashboard:lib -->`, the inlined `dashboard.js`.

## Data

The data block is one JSON object:

```json
{
  "asOf": "2026-10-13T08:00:00-07:00",
  "tz": "America/Los_Angeles",
  "locale": "en-US",
  "currency": "USD",
  "policy": {"warn": 0.95, "alert": 0.85},
  "measures": {"revenue": {"label": "Revenue", "units": "U.S. $, QTD", "value": 5900000, "target": 7500000, "projection": 7350000, "format": "usd0k", "history": [6120, 5980]}},
  "anything else": "arrays for bars, stacked, line, box, scatter and text"
}
```

`tz` is optional; without it the as-of time prints with its UTC offset. `policy` sets the ratios at which a measure turns `warn` and `alert`; `"warn": null` gives one alert level.

### The measure record

| Field | Meaning |
|---|---|
| `label` | The name. Defaults to the key in `measures`. |
| `units` | The gray line under the label, such as "U.S. $, QTD". |
| `value` | The current value, in raw units (dollars, not thousands; 0.912 for 91.2%). |
| `target`, `forecast`, `prior` | Comparisons. The first one present, in that order, is the basis for the ratio. |
| `norm` | `[lo, hi]`, a normal range. With `better: "in"` it is the comparison; elsewhere it draws the sparkline's band when the line leaves it. |
| `ranges` | Qualitative breakpoints listed bad to good (ascending for `up`, descending for `down`). Up to four breakpoints, five bands. |
| `better` | `"up"` (default), `"down"` or `"in"`. |
| `projection` | The end-of-period projection. When present it is judged instead of `value`, and bullets draw it as a lighter segment. |
| `history` | Numbers for the sparkline, oldest first. Missing or one point is allowed. |
| `format` | A format spec (below). Defaults to `int`. |
| `domain` | `[lo, hi]` for a bullet on its own scale. A domain that excludes zero draws a circle marker and a thin target line instead of a bar. |
| `state` | `good`, `ok`, `warn` or `alert`, when the source system already decided. It wins over everything. |
| `note` | Text added to the accessible name, such as why a state was forced. |
| `policy` | Per-measure `{warn, alert}`, over the call's and the page's. It sets the measure's bands as well as its state. |

A measure with none of `target`, `forecast`, `prior`, `norm` or `ranges` fails `check` (mistake 2).

### One rule for state

`dd.state(m, policy)` returns `{level, ratio, text}`. `level` is `good`, `ok`, `warn`, `alert`, or `none` when there is nothing to compare.

1. An explicit `state` wins.
2. The judged value is `projection` when present, else `value`.
3. With `better: "in"` and a `norm`, the distance outside the range is laddered.
4. With `ranges`, the band holding the judged value decides. The first (darkest) band is `alert`, the second is `warn` when there are three or more bands and the policy has a `warn`, the last is `good`, and any other is `ok`.
5. Otherwise the ratio to the basis decides. For `up` the goodness is the ratio; for `down` it is `2 − ratio`, so 110% of a budget reads like 90% of a target. Goodness of 1 or more is `good`, under `alert` is `alert`, under `warn` is `warn`, and the rest is `ok`.

Bands and state read one merged policy, the measure's own `policy` over the call's `policy` option over the page's. Without `ranges`, a bullet's bands are drawn at that policy's breakpoints, `alert × basis` and `warn × basis` (mirrored for `down`), so a value's band and its dot always agree. Only `warn` and `alert` draw a dot, bold the value, and put an end dot on the sparkline. `text` reads, for example, "Revenue 5,900 thousand dollars, projected 98% of target, satisfactory".

An alert dot is one line of text across, 1.3 times the type size: 16 px at 12.5 px type, 1.1% of a 72-column page, toward the 1.3% to 1.9% of Few's exemplars. Every medium draws the same dot at its own type size (table rows, bullets, bars, stacked bars, text tables, `dd.alert` and legends), in a column of its own that leaves 0.4 of the type size before the label. A text-table row keeps its height with a dot in it. The sparkline's end dot stays 5 px, since it marks a point on the line rather than the row.

### Flagged rows

`dd.flags('#dd-flags')` writes "2 critical · 4 warnings", with a small dot of each level before its count, or "Nothing flagged". It counts the rows the page flags, so sparkline end dots and legend swatches never count. A row counts once however many dots it has, and rows that share a measure key count as one, so a measure drawn in a table and again as a bullet counts once. Rows from `bars`, `stacked` and `text` have no key unless you give them one. Give each measure its own key, even when two measures belong to one region, such as its revenue for the year and its quarter with pipeline, so the count matches the dots the viewer sees. A row flagged at two levels counts at the worse one. The line's `title` lists the labels at each level. Call it anywhere in the page script: it counts again whenever another mount draws.

## Helpers

| Call | Returns |
|---|---|
| `dd.data(selector = '#dd-data')` | The parsed data block. Sets the page's locale, currency and policy; normalizes every measure (`key`, `label`, `better`, `format`) and adds `m.status = dd.state(m)`. |
| `dd.fmt(value, spec, locale?)` | A string from `Intl.NumberFormat`, with a true minus. A missing value prints an en dash. |
| `dd.asOf(iso, tz?, locale?)` | "Tue, Oct 13, 2026, 8:00 AM PDT" with `tz`, or "… 8:00 AM UTC−07:00" from the offset in `iso`. |
| `dd.state(m, policy?)` | `{level, ratio, text}`, as above. |
| `dd.flags(target)` | Writes the count of flagged rows into `target`, as above, and keeps it current. `dd.svg.flags({alert, warn})` returns the line as HTML from two lists of labels. |
| `dd.flagged(root = document)` | `{total, alert: [labels], warn: [labels]}`, the rows under `root` with each row counted once, as above. `dd.flags` and the check's alert count both read it. |
| `dd.version` | `"0.1.0"`. |

Format specs:

| Spec | 7213456 or 0.0213 prints |
|---|---|
| `int` | 7,213,456 |
| `dec1` | 7,213,456.0 |
| `usd0` | $7,213,456 |
| `usd0k` | $7,213K (spoken "7,213 thousand dollars") |
| `usd1m` | $7.2M (spoken "7.2 million dollars") |
| `pct0`, `pct1` | 2%, 2.1% |
| `+pct0`, `+pct1` | +2%, +2.1%, and −2.1% for negatives |

Tick labels drop the currency sign and the K or M and use as many decimals as the tick step needs.

## Media

Every medium is a pure function and a mount:

- `dd.svg.<medium>(input, opts)` returns markup as a string. Besides the medium's options it takes `width` (px, default 400), `u` (px per unit, default 20; type is `0.625u`) and `measure(text, sizePx, weight)` (defaults to an estimate).
- `dd.<medium>(target, input, opts)` draws into `target` (a selector or an element) at the container's real width and font size, measuring text as it renders (SVG text with tabular figures, so digits measure at their rendered width), and redraws through a `ResizeObserver` and on window resize. It returns the element.

Every graphic is an `<svg role="img">` named from the state text, and each row or point carries an SVG `<title>` with the exact values. Axes, ticks and bands use `shape-rendering: crispEdges`; marks that carry meaning have the class `dd-mark` and at least 3:1 contrast.

### `table(measures, opts)`: the graphical table

`measures` is the `measures` object (with `rows`) or an array. Each row reads sparkline, alert dot, label with a gray units line, graph, value.

| Option | Meaning |
|---|---|
| `rows` | Keys in display order. |
| `cols` | Which columns to draw, in fixed order: `['spark', 'alert', 'label', 'graph', 'value']` by default. |
| `scale` | `'pctTarget'`, the default, puts every row as a ratio to its basis on one shared scale, with one continuous 100% line through all rows and one axis at the foot. `'shared'` puts rows that share a unit, such as eight blood types in days of supply, on one scale in that unit, with one axis at the foot in the first row's format. Each row draws its bands from its own breaks. The target is one continuous line through every row when all rows have the same target, and a tick per row when they don't. `'own'` draws a bullet graph per row on its own scale, with ticks under each band. |
| `domain` | `[lo, hi]` for the `pctTarget` scale, such as `[0, 1.5]`, or the `shared` one, such as `[0, 9]` days. A value past the maximum is clipped with a break mark. |
| `axis` | `false` drops the axis at the foot. |
| `head` | `{spark, label, graph, value}` column headers, drawn over one hairline. Each column is as wide as the wider of its header and its cells, except the graph, whose header is ellipsized a column gap short of the value header. |
| `labelWidth`, `valueWidth` | Fixed widths for the label and value columns, a number in u or a string in px such as `'140px'`. A longer label is ellipsized; a wider value widens its column. Use them to line tables up (below). |
| `norm` | `false` hides the sparkline's normal band. |
| `endDot` | `'alert'` (default), `'always'` or `'none'`. |
| `title` | Prefix for the accessible name. |
| `policy` | Overrides the page policy. A measure's own `policy` overrides both. |

At 12.5 px type the band is 13 px, the bar a third of it, sparkline one text line (16 px) tall and 7 to 10 times as wide, alert column 21 px with a 16 px dot, label column as wide as its widest label, units line or header, at most 24% of the width, with ellipsis.

Stacked tables line up column for column when their containers are the same width, they draw the same `cols`, and they pass the same `labelWidth` and `valueWidth`: the sparkline, label, graph and value columns then start at the same x in every table.

```js
const lined = {labelWidth: 7, valueWidth: 3.5}
dd.table('#key', d.measures, {rows: ['revenue', 'profit', 'orderSize'], head: {label: 'Metric', graph: '% of target', value: 'Actual'}, ...lined})
dd.table('#ops', d.measures, {rows: ['availability', 'backlog'], scale: 'own', ...lined})
```

### `bullet(measure or [measures], opts)`

Few's standalone bullet has its label right-aligned in semibold with the units line under it, a band 1.4u (28 px) thick, a bar a third of the band, a target line 0.7 of the band, ticks hanging from the band, and the value to the right. The band stops at 13 times its thickness rather than stretching. Several measures stack 2.35 band thicknesses apart. Options: `domain`, `value` (`false` hides the value), `policy`. A `projection` draws a lighter segment from the bar's end. A domain that excludes zero draws a circle marker and a 1 px target line.

### `spark(measure, opts)`

A sparkline one text line tall and 10 times as wide, then the value in bold and the label in gray. The line spans its own data's range, top to bottom. The `norm` band is drawn only when at least one point lies outside it, since a line that never leaves its band would sit on a gray box that says nothing. When it is drawn it is clipped to the plot, so it runs from the plot's edge to the acceptable limit, as in Few's figure 6-31. Options: `text` (`false` draws the line alone), `norm` (`false` hides the normal band), `endDot` (`'alert'`, `'always'`, `'none'`). A single point draws as a dot at the right end; no history draws nothing.

### `bars(rows, opts)`

`rows` are `{label, value, target?, highlight?, others?, state?, better?, key?}`. Bars fill 56% of their slot and always start at zero. Labels are left-aligned beside the alert-dot column; values sit in a right-aligned column.

| Option | Meaning |
|---|---|
| `orient` | `'h'` (default) or `'v'`. |
| `sort` | `'desc'` (default for horizontal), `'asc'`, or `'none'` (default for vertical). "All others" (or `others: true`) always goes last. |
| `highlight` | A label, or a function of the row, for the one category drawn darker; a row's own `highlight: true` also works. |
| `format` | Format spec for values and ticks. |
| `values` | `false` hides the value column. |
| `pctTotal` | Adds a gray "% of total" column. |
| `domain` | Must include zero, or the call throws (mistake 8). |
| `axis` | `false` drops the axis. |
| `height` | Vertical bars only, in u (default 8). |

A row with a `target` gets a target tick and a state, and a dot when it is `warn` or `alert`.

### `stacked(rows, opts)`

`rows` are `{label, <part>: number, …, target, key?}`. Parts are drawn darkest first; a key with swatches sits above the plot.

| Option | Meaning |
|---|---|
| `parts` | Part keys, at most three (default `['actual', 'pipeline']`). |
| `names` | Display names for the parts. The default is the keys, capitalized. |
| `target` | The target key (default `'target'`). |
| `alertWhen` | `'sumBelowTarget'`: the row is `alert` when even the sum of all parts falls short of target, else `good`. |
| `value` | `'first'` (default) shows the first part; `'sum'` shows the total. |
| `format`, `axis` | As for bars. |

### `line({x, series}, opts)`

`series` are `{name, values, emphasis?}`, at most three, told apart by gray and stroke weight (2 px for the first). `null` values leave gaps. Names sit at the line ends, spread apart so they don't collide.

| Option | Meaning |
|---|---|
| `height` | In u (default 7). |
| `deviation` | The values are deviations. Draws a 0 reference line, tints the region below zero, and defaults the format to `+pct0`. |
| `refLabel` | The 0 line's end label (default "Target"). |
| `format`, `domain`, `endLabels` (`false`), `title` | |

### `box(groups, opts)`

`groups` are `{label, values}` (quartiles computed) or `{label, min, q1, median, q3, max}`, each with an optional `band: [lo, hi]`. Few's simplified box plot has a whisker from min to max with no caps, a light box from q1 to q3 with a dark outline, and the median as a 2 px line, all over an optional acceptable band. Options: `band` (for every group), `range` (draws range bars from min to max with a median line instead), `format`, `domain`, `axis`.

### `scatter(points or {sets}, opts)`

Points are `{x, y, label?}`; `sets` are `{name, points}`, at most two. Hollow circles, a least-squares line per set labeled with the set's name at its right end, axes that need not start at zero, axis titles written horizontally. Options: `height` (u, default 8), `formatX`, `formatY`, `labels` (labels points that have one, on the side away from the fit line, dropped when no free spot exists), `fit` (`false`), `xLabel`, `yLabel`, `name`.

### `text(rows, opts)`

An HTML `<table class="dd-text">`: right-aligned numbers, bottom-aligned headers, one hairline under them, and one stretching column that takes the width left over, ellipsized with its full text in `title`. Every other column keeps its content width on one line.

| Option | Meaning |
|---|---|
| `cols` | Strings `'key:format:Label'` (format and label optional, `'name::Customer'`) or `{key, format, label, wrap}`. A label with `\n` makes a two-line header. `wrap: true` on the stretching column wraps its text instead of ellipsizing it. |
| `stretch` | The key of the column that stretches, such as `'where'` in `cols: ['expires::Expires', 'where::Held at', 'units:int:Units']`. The default is the first text column. A key that names no column throws. |
| `rank` | Adds a leading rank column. |
| `title`, `policy` | |

Rows with a `state` or a `target` get a dot column and bold cells when `warn` or `alert`. A row's `key`, if it has one, is its identity for `dd.flags`.

### `legend(items, opts)`

For the `.dd-legend` slot on a section title. Items are `{mark, label, tone?, level?}` with `mark` one of `bar`, `projection` (the lighter segment beyond the bar), `target`, `band` (tone 0 to 4, darkest 0), `fill`, `highlight`, `part` (tone 0 to 2), `line` (tone 0 to 2), `dot` (level `warn` or `alert`, the same size as the page's alert dots at the legend's type size).

### Icons

`dd.alert(target, level)`: a dot for `warn` or `alert`, nothing otherwise. `dd.trend(target, 'up' | 'down', {bad})`: a gray triangle, red when `bad`. `dd.mark(target, 'check' | 'x' | 'asterisk')`: a gray stroke icon. All are one text line in size.

### Refused media

`dd.pie`, `dd.donut`, `dd.gauge`, `dd.radar` and `dd.area` (and their `dd.svg.*` twins) throw, for example "dd.pie: a Few dashboard draws no pie charts (mistake 5); use dd.bars with pctTotal". Nothing draws 3D.

## CSS

Tokens on `:root`: `--u` (the unit, `min(100vw / --dd-cols, 100vh / --dd-rows)`), `--dd-font`, `--dd-bg` #FBFBF9, `--dd-ink` #222, `--dd-ink-2` #5C5C5C, `--dd-ink-3` #6B6B6B, `--dd-accent` #4E6275 (section titles, 6.1:1), `--dd-title` #7D8FA0 (page title, 3.2:1 as large text), `--dd-rule`, `--dd-axis`, `--dd-alert` #A8261E (6.9:1), `--dd-warn` #DB6A5A (3.3:1), and the gray ramps for bars, bands and parts.

Classes: `dd-page` (on body), `dd-head`, `dd-title`, `dd-asof`, `dd-flags`, `dd-grid`, `dd-stack` (a column of sections inside a grid cell), `dd-sec`, `dd-sec-title`, `dd-qual`, `dd-legend`, `dd-foot`, `dd-sr` (screen-reader-only).

The title can sit in the footer, as on Few's telesales dashboard. Move `h1.dd-title`, `p.dd-asof` and `p.dd-flags` from `header.dd-head` into `footer.dd-foot`, after which a header with no elements left in it takes no space. The footer sets the title on one line, then the as-of, the count, and any `span.dd-legend` and notes, all on one baseline, and wraps them at phone width. The count keeps body size there, a step above the as-of, and its dots key the two reds, so the page needs no dot legend. Leaving `p.dd-flags` alone in the header keeps the count at the top left, at the cost of one line of height. The page needs no CSS of its own for either.

Below the width at which body text would drop under 11 px (1,267 px for 72 columns), the library sets `data-dd-layout="column"` on `<html>`: the grid becomes one scrolling column at a fixed `--u` of 19.2 px (12 px type). A short window keeps the grid and scales down, because one screen comes first.

## `scripts/dashboard.py`

- `new OUT [--viewport WxH] [--title T] [--data D.json] [--force]` writes the template. It refuses to overwrite without `--force`.
- `sync OUT [--data D.json] [--check]` rewrites the css and lib regions from `assets/` and, with `--data`, the data block. `--check` writes nothing and exits 1 when anything differs; with `--data` its PASS line says the data block matched too.
- `check OUT [--viewport WxH] [--phone WxH] [--json] [--no-browser]` runs the static pass, then the browser pass, prints one `PASS`, `WARN` or `FAIL` line per finding with the mistake number and the fix, saves `<stem>.<W>x<H>.png` at the design viewport and `<stem>.phone.png`, the full length of the one-column phone layout, beside the page, and exits 1 on any FAIL.

The page carries no check code. `check` writes a copy of the page beside it, named `.<stem>.<random>.dd-check.html`, with `assets/check.js` inlined after the lib region, renders the copy, and deletes it, so the page keeps its relative paths and is never changed. `check.js` reads the page through the DOM and the library's public `DataDashboard.flagged()` and `DataDashboard.version`, records the errors the page script throws, and writes the report once the page has loaded and its fonts are ready. The screenshots are of the page itself.

The static pass checks the regions' hashes, the data block, comparisons (mistake 2), refused media calls (5), hand-drawn `<rect>`, `<circle>`, `<path>`, `<line>`, `<polyline>`, `<polygon>` or `<ellipse>` (7), network loads, gradients and shadows (11), canvas and rotated text (7), rounded or fully bordered boxes (11), saturated or red-and-green colors in the page's CSS (12), and that `--dd-cols` and `--dd-rows` match the viewport meta.

The browser pass judges the page's report for fit against the viewport and the footer (1), overlapping sections (9), clipped or colliding text and type under 9 px (7), text contrast under 4.5:1 (3:1 for large text) and marks under 3:1 (12), saturated colors other than the two alert reds (12), alert share over 20% (10), groups outside 3 to 9 (9), mounts that drew nothing (2), and script errors, which carry their own mistake number.

### The report

`check.js` writes `<script type="application/json" id="dd-report">`, which holds `{version, viewport: {w, h}, layout, page: {w, h}, fontPx, sections: [{name, x, y, w, h, bottom, right}], footTop, overlaps: [{a, b, w, h}], clipped: [{text, px}], collide: [{a, b}], small: [{text, px}], contrast: [{text, ratio, need, color, bg}], marks: [{el, color, ratio}], colors: [{color, count, where}], rows: {total, alert: [labels], warn: [labels]}, groups, empty: [elements], noComparison: [labels], asOf, errors: [messages]}`. `rows` is `dd.flagged()`, so the check's alert count and the page's count line always agree.

### Browser

Discovery order: `$DD_BROWSER`; the Google Chrome, Chromium, Microsoft Edge and Brave Browser app bundles in `/Applications` and `~/Applications`; `google-chrome`, `google-chrome-stable`, `chromium`, `chromium-browser`, `microsoft-edge` and `brave-browser` on `PATH`; then the Playwright caches, headless shell first. Flags: `--headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --no-first-run --no-default-browser-check --disable-extensions --virtual-time-budget=5000` and a throwaway `--user-data-dir`, plus `--no-sandbox` when running as root. With no browser, or one that does not finish within 60 s, the check runs the static pass and WARNs that fit was not measured.

The report pass reads `innerWidth` and `innerHeight` back and relaunches with the difference added, because `--dump-dom` on Chrome 157 for macOS lays out 87 px shorter than `--window-size`. Chrome on macOS also lays out no narrower than 500 px, so there the phone pass and its PNG run at 500 px and say so; Playwright's headless shell lays out at a true 390 px.
