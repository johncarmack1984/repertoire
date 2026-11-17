# Review and refine

This file holds the detail for the review and refine modes, and shows how to apply Few's rules inside the stack a dashboard already lives in. A review cites `mistakes.md` by number; a refine fixes what the review found.

## The review format

Open with a one-line verdict that names the dashboard's role and says whether a glance shows what needs action. Then list the faults, worst for the viewer first. For each one, quote it or locate it (a selector, a component, a panel title, a region of a screenshot), name the mistake by number, and give the fix in that stack. List by name every measure that has nothing to compare against, since that is mistake 2 wherever it appears.

Put no mark on anything that keeps the rules, however differently you would have built it. Name it once as one to keep, and suggest nothing for it, not even an addition such as annotations, markers, or another series, since a suggestion on a correct panel reads as one more fault. When a fix to the arrangement moves it, say that it moves unchanged. Don't rewrite in a review; each fix is one line, not a new dashboard.

```
A strategic sales dashboard whose one real alert is lost among a dozen colors.

- `<PieChart>` "Revenue by region": mistake 5. Use `<BarChart layout="vertical">` sorted largest first, titled "Revenue by region, share of total".
- `<CartesianGrid strokeDasharray="3 3" />` in all six charts: mistake 7. Delete it.
- Status column with red, yellow, and green fills: mistakes 10 and 12. Gray text, and an alert dot only on rows past the threshold, in two intensities of red.
- Card "Active users 48,212": mistake 2. Add last month's value or the target, and a 12-month sparkline.
- Logo and date picker in the top left: mistake 9. Move them to the bottom right and put "Revenue by region" there.
```

## The refine rules

- Run the review first, then fix each fault it found.
- Keep every measure and every value. Drop or replace one only when it is a deficient measure (mistake 4), such as actual and budget shown where the variance is the point, and name each one dropped or replaced, with the reason, in the reply.
- Never invent a comparison. When a measure has none in the data, show the prior period if the data holds it, or ask for the target.
- Fix in place when the user maintains the code. Keep their data plumbing and change the presentation with the tables below.
- Rebuild as a page with the library when the input is a screenshot or a PDF, or when the user asks for a new file. Run steps 2 to 7 on it, and say in the report which values were read off the image.

## Recharts

| Fault | Change |
| :-- | :-- |
| grid lines | delete `<CartesianGrid>` |
| legend | delete `<Legend>`; label lines at their ends with a `label` function that draws only the last point, and bars with `<LabelList>` |
| pie or donut | `<PieChart>` becomes `<BarChart layout="vertical">` with `<XAxis type="number">` and `<YAxis type="category" dataKey="name">`, data sorted largest first |
| radial gauge | `<RadialBarChart>` becomes a bullet graph (below) |
| gradients, shadows | remove the `<defs>` gradients and SVG filters added by hand; Recharts draws neither by default |
| animation | `isAnimationActive={false}` on each series |
| sparkline with a normal band | `<LineChart>` with no axes, `<ReferenceArea y1={lo} y2={hi} fill="#e0e0e0" />`, and `<Line dot={false} strokeWidth={1.5} />` |
| bullet graph | port `dd.svg.bullet` into a component that renders its markup |

Recharts draws SVG, so the output stays crisp. It has no bullet graph, and end labels need the custom `label` function.

## Chart.js

| Fault | Change |
| :-- | :-- |
| grid lines | `scales.x.grid.display: false` and `scales.y.grid.display: false` |
| legend | `plugins.legend.display: false`; direct labels need a plugin such as chartjs-plugin-datalabels |
| pie, doughnut, half-doughnut gauge | `type: "bar"` with `indexAxis: "y"`, data sorted largest first |
| bars from zero | `beginAtZero: true` on the value axis |
| animation | `animation: false` |
| sparkline with a normal band | `type: "line"`, both scales `display: false`, `elements.point.radius: 0`; draw the band as two constant datasets at `lo` and `hi`, the second with `fill: "-1"` in light gray and no border |
| bullet graph | port `dd.svg.bullet` and place it beside the canvas |

Chart.js draws on a canvas, so a screen reader can't read its text and no one can select it. Give each `<canvas>` an accessible name and fallback text with the values.

## ECharts

| Fault | Change |
| :-- | :-- |
| grid lines | `splitLine: {show: false}` on each value axis |
| legend | remove `legend`; label lines with `endLabel: {show: true, formatter: "{a}"}` |
| pie or donut | `type: "pie"` becomes `type: "bar"` on a category `yAxis`, sorted with a dataset transform `{type: "sort", config: {dimension: "value", order: "desc"}}` |
| gauge | `type: "gauge"` becomes a bullet graph (below) |
| 3D | remove the echarts-gl series such as `bar3D` |
| shadows, gradients | remove `shadowBlur` and `LinearGradient` colors from `itemStyle` |
| controls | remove `toolbox`; keep `dataZoom` only on an analytical screen |
| animation, renderer, screen readers | `animation: false`; `echarts.init(el, null, {renderer: "svg"})`; `aria: {enabled: true}` |
| sparkline with a normal band | a line series with `showSymbol: false`, both axes `show: false`, and a light gray `markArea` from `{yAxis: lo}` to `{yAxis: hi}` |
| bullet graph | bars on a category `yAxis`, a `markArea` for bands every row shares, and a `markLine` for a shared target; otherwise port `dd.svg.bullet` |

The native bullet graph works only when every row shares one set of bands and one target, as on a % of target scale. Bands that differ per row need a `custom` series or the ported function.

## Vega-Lite

| Fault | Change |
| :-- | :-- |
| grid lines, frame | `"config": {"axis": {"grid": false}, "view": {"stroke": null}}` |
| legend | `"legend": null` on the color channel; label each series with a layered `text` mark on its last point |
| pie or donut | `"mark": "arc"` becomes `"mark": "bar"` with `"y": {"field": "category", "sort": "-x"}` |
| scales | keep `"zero": true` on bars, the default; set `"zero": false` on a line so it fills the plot |
| renderer, menu | vega-embed with `{"renderer": "svg", "actions": false}` |
| bullet graph | layer `bar` marks with `x` and `x2` for the ranges, a narrower `bar` for the value, and a `tick` for the target |
| sparkline with a normal band | a light gray `rect` from `"y": {"datum": lo}` to `"y2": {"datum": hi}` under a `line` mark, both axes `null` |

Vega-Lite can layer every graph the skill uses, but each direct label and each bullet graph is a layer of its own, so a dashboard's spec grows long. Build the bullet layer once and reuse it.

## Grafana

The `custom` settings below sit under `fieldConfig.defaults` in the panel JSON.

| Fault | Change |
| :-- | :-- |
| pie | `"type": "piechart"` becomes `"type": "barchart"` with `"orientation": "horizontal"`, rows sorted by a Sort by transformation |
| gauge | `"type": "gauge"` becomes `"type": "bargauge"` with `"displayMode": "basic"`, `"showUnfilled": true`, and gray threshold steps, darkest for the bad range, so a bad value draws the heaviest bar |
| colored stat | `"colorMode": "none"` and `"graphMode": "area"`, which adds a sparkline; add the comparison as a % of target field with an Add field from calculation transformation |
| red and green thresholds | a gray base step, and red only on the alert steps, in two intensities |
| grid lines, fills, gradients | `custom.axisGridShow: false`, `custom.fillOpacity: 0`, `custom.gradientMode: "none"` |
| legend | `options.legend.showLegend: false`, with the series named in the panel title |
| panel boxes | `"transparent": true` on each panel |
| normal band | `custom.thresholdsStyle.mode: "area"`, with a gray step at the low end and a transparent step at the high end |
| layout | key panels at `gridPos` x 0, y 0; check the fit in kiosk mode at the screen it will hang on |

Grafana has no bullet graph. A bar gauge shows the value against fixed limits with no target marker, and the bar takes the gray of the range its value falls in, which only stands in for the bands. A stat panel shows one value and its sparkline, with no normal band, and no Grafana panel labels a line at its end. Panel titles and padding also take rows from the budget. When these limits cost the viewer, offer a companion page built with the library from the same queries.
