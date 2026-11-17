# Display media

This file holds the detail for step 4. It says which medium shows each measure and what a correct drawing of it looks like. The library draws every medium here except the combined bar-and-line graph, the Pareto chart, and maps, so the geometry is for judging a drawing, not for making one. The rules follow chapter 6 of Few's book, "Effective Dashboard Display Media", unless another chapter is named.

## Choosing

Choose by the nature of the information, the nature of the message, and the needs and preferences of the viewer (chapter 6, "Select the Best Display Medium"). A dashboard holds many kinds of data, so it holds several media, each matched to its data.

Text is read one word at a time and gives precision; tables of text are the medium for looking a value up. Graphs give numbers a shape, which shows patterns, the whole, and comparisons at a glance. "Displaying individual values does not require graphics," Few writes, so a value that only needs to be read stays text.

Build up a single measure one step at a time, and stop at the first step that says enough:

1. The value alone, with its label.
2. The value in bold when it is bad. Bold reaches color-blind viewers, as long as only bad values are bold.
3. The target beside the value.
4. The variance beside them, as an amount or a percentage, or the variance alone when that is the message.

A graph earns its place once the viewer needs comparisons across measures or the bigger picture, which text can't give. Few's library admits a medium only if it is the best way to show a common kind of dashboard data and still works when small.

| The viewer needs to see | Medium | dd call |
| :-- | :-- | :-- |
| one measure against its target and its good and bad ranges | bullet graph | `dd.bullet` |
| a column of key measures, each against its target, with history | graphical table | `dd.table` |
| a measure's recent history beside its value | sparkline | `dd.spark` |
| one value that is read, not judged | text | `dd.text` |
| items of a category compared (regions, products, people) | bars, sorted | `dd.bars` |
| shares of a whole | bars sorted largest first, with the whole named in the title | `dd.bars` |
| several wholes and their parts, when the whole matters most | stacked bars | `dd.stacked` |
| a firm amount plus what is expected, against a target | a bullet graph with a projection segment, or stacked bars when each part matters | `dd.table`, `dd.stacked` |
| individual values and an overall shape together | combined bars and line | not in the library; see below |
| how much each ranked item contributes to the total | Pareto chart | not in the library; see below |
| the shape of a series over time | line | `dd.line` |
| deviation from a target or a baseline over time | deviation line | `dd.line` |
| how values spread across their range | box plot or range bars | `dd.box` |
| whether two paired measures move together | scatter plot | `dd.scatter` |
| an exception that needs attention now | alert icon | `dd.alert` |
| direction of change, when the period is stated | up/down icon | `dd.trend` |
| a flag on some items in a list | on/off icon | `dd.mark` |
| exact values to look up, ranked lists, schedules | text table | `dd.text` |
| the same graph for each channel, region, or system | small multiples on one shared domain | each call with the same `domain` |

## Graphs

### Bullet graph

Few invented the bullet graph to replace gauges and meters. It shows one key measure, a comparative measure such as the target, and qualitative ranges such as bad, satisfactory, and good, in a strip that packs tightly beside others. It is the one graph in the library for a single instance of a measure. Use it for every key measure that has a target and a state; avoid it for a value with nothing to compare against, which stays text.

- The bar is about a third of the band's thickness, in near-black, and starts at zero. The target is a short line about 0.7 of the band across it, so a bar that passes its target forms a cross the eye finds at once. Use at most five ranges, told apart by the intensity of one hue, never by different hues. List `ranges` from bad to good. The darkest band is the bad one, and with `better: "down"` the bands mirror so the dark band sits at the high end. On a scale that doesn't start at zero the value is a dot, not a bar, because "The length of the bar represents the value, not just the location of its endpoint." A `projection` continues the bar in a lighter gray to the expected end-of-period value.
- `dd.bullet("#revenue", d.measures.revenue)`

### Sparkline

Tufte's word-sized line gives a measure its history without a scale. Use it beside a current value whenever the trend or the volatility matters, and in place of an up or down arrow, which never says what period it covers. Avoid it when the viewer needs values off the line. "Sparklines are not meant to provide the quantitative precision of a normal line graph."

- It is one line of text tall and 8 to 11 times as wide, with a 1.5 px stroke and no axis or grid. A light gray `norm` band marks the acceptable range when the line leaves it, so the points outside stand out; a line that stays inside its range gets no band, since the band would only fill the plot. An end dot appears only when the measure alerts, in the alert color. The value sits as text to the right, and the column header states the window ("Past 12 months").
- `dd.spark("#defects", d.measures.defects)`

### Bars

Bars show several instances of a measure across a category, such as regions, departments, or products. Use them for every nominal or ordinal scale, where a line never belongs; for a time scale when individual values or neighboring periods are compared, such as day shift against night shift each month; and for shares of a whole, with the title saying the bars are parts of one total. Avoid them when the shape of a time series is the message.

- The scale starts at zero, and the library refuses any other. A horizontal bar fills about 56% of its slot. Sort largest first with "All others" last, draw one series in one medium gray, and make a highlighted category ("Our company") a darker gray. Draw no grid lines. For two measures of each category, such as revenue and units against their targets, put two graphical tables side by side on the same rows, the second without labels, as the worked example does for O− and O+ stock.
- `dd.bars("#share", d.share, {highlight: r => r.us, pctTotal: true})`, which sorts largest first and puts "All others" last by itself.

### Stacked bars

Stacked bars show several instances of a whole and its parts when the whole matters most, such as sales per quarter split by channel, or Few's quarter-to-date revenue drawn as actual plus pipeline against target. Avoid them for a single part-to-whole series, and when shifts among the parts must be read closely, since only the bottom segment sits on a shared baseline.

- Segments run in grays from darkest at the base, named in a small key above the bars, the way Few's sales dashboard names them on its title line.
- When the parts are a firm amount and an expected one, such as booked and walk-in donors or actual and pipeline revenue, prefer a bullet graph with a `projection` on a dense screen. It says the same thing with a third of the ink, since its bar is a third of the band's height, and the stacked bars' near-black mass no longer outweighs the alerts. Keep stacked bars for when each part matters on its own.
- `dd.stacked("#pipeline", d.pipeline, {parts: ["actual", "pipeline"], target: "target"})`

### Combined bars and line, and the Pareto chart

Combine bars and a line only when part of the data needs bars (individual values) and part needs a line (an overall shape), such as monthly revenue and expense bars with profit as a line. The Pareto chart draws ranked items as bars and their running total as a line. It is the one place a line crosses a category scale, because each running total builds on the one before, and the slope shows how much each item adds.

- The line is darker and heavier than the bars and is labeled at its end. Expenses are negative bars below the zero line. A Pareto chart gets a reference line where the point is, such as 75% of revenue.
- The library draws neither yet. Draw the bars with `dd.bars` and its `pctTotal` column, and say the running share in the section's qualifier, such as "(top 3 reps, 75% of revenue)".

### Line

Lines show the shape of data over time, such as trends, cycles, rates of change, and how two series move together. Use them on time scales and other interval scales only. Avoid them on categories, where the line invents a pattern between unrelated items.

- The scale need not start at zero; run it from just below the lowest value to just above the highest. The data lines are the most prominent thing in the graph, in up to five grays or muted hues, labeled at their right ends instead of a legend, over light axes and no grid. The deviation form plots the percentage above or below a target or baseline around a 0% line, which shows the variance itself (mistake 4), and tints the region below zero a neutral gray.
- `dd.line("#visitors", d.visitors, {deviation: true, refLabel: "Same month last year"})`, with each value already a deviation such as 0.12 for 12% above.

### Box plot and range bars

These show how a set of values spreads across its range, which a sum or an average hides, such as salaries in each grade or response times for each system. Range bars from low to high are the simplest form; range bars with a median line are enough for many dashboards; the simplified box plot is Few's choice when the spread inside the range matters. Teach the box plot to viewers who haven't read one (chapter 7, "Test Your Design for Usability").

- The simplified box plot has whiskers to the lowest and highest values with no caps, a light gray box from the 25th to the 75th percentile, and the median as a solid line. Range bars float on a zero-based axis with the median as a dark line. A gray band behind the glyphs can mark the acceptable range.
- `dd.box("#response", d.systems, {band: [0, 3]})`. A group's `state` comes from the alert rule, such as the share of samples within the limit, and draws its alert dot; its `note` says why, such as "27 of 30 within 3.0 s".

### Scatter plot

A scatter plot shows whether two paired sets of values are related, in which direction, and how strongly, such as monthly ad spots against revenue. Use it when that relation is the message; the same months as a time series would hide it. Avoid 3D and any other way of adding a third variable, and avoid curved fit lines unless the viewers are trained to read them.

- Points are hollow circles, each set has one straight line of best fit labeled at its end, and sets differ by a muted color. Neither axis needs to start at zero.
- `dd.scatter("#ads", d.ads, {xLabel: "Radio ads, $K", yLabel: "Revenue, $K"})`, which draws the straight fit line unless `fit: false`.

### Treemap

A treemap fits a large hierarchy into the least space, with rectangle size for one quantity and one hue from neutral to saturated red for another. In a sales treemap, each state's area is its revenue and its color is its percent of quota. Few keeps it for spotting conditions that need attention across many items, never for comparing or ranking values. Use it when there are too many items for a table's rows, and a graphical table, worst first, when there are few.

- Cells are squarified, so they stay near square, and grouped one level deep under header strips. A cell at or above its target stays neutral, a cell under the alert threshold is the full alert red, and the cells between take tints of it, so a cell's color and its alert agree. A label and its value appear only where they fit; every cell's exact values are on hover. Every cell's area is its share of the total to within the rounding of its edges to whole pixels, as `reference/api.md` details.
- `dd.treemap("#states", d.states, {sizeLabel: "Revenue"})`, keyed with `dd.legend` and its `heat` mark.

## Icons

- **Alert.** A plain circle in front of the row, drawn only when attention is needed, so it reads as a newly added mark. "Try to limit alert levels to a maximum of two, and ideally to one." Two levels are two intensities of one red, never red, yellow, and green. `dd.alert(el, "warn")`
- **Up/down.** A triangle pointing the way the measure moved. If colored, the two differ in intensity as well as hue, with saturated red for the wrong direction and pale green for the other. Prefer a sparkline, which shows the period. `dd.trend(el, "down", {bad: true})`
- **On/off.** A checkmark, an asterisk, or an X that flags items in a list, such as deals near closing. Pick one and use it everywhere. `dd.mark(el, "check")`

## Text and organizers

**Text.** A value shown alone, with nothing to compare it to, reads faster as text than as a graph. Write the label, then the value, as in "Reps online 20". Ranked lists the viewer reads entry by entry, schedules, and top-ten tables are text too. Right-align numbers, give each column a header with its units, put one thin rule under the headers, and draw no grid. `dd.text("#customers", d.customers, {rank: true, cols: ["name::Customer", "pipeline:usd0k:Pipeline", "qtd:usd0k:QTD", "ytd:usd0k:YTD"]})`

**Tables.** Rows and columns can hold graphs and icons as well as text. The graphical table reads, left to right, sparkline, alert dot, label with its units line, graph, value; on a % of target scale it draws one 100% line through every row and one axis at the foot of the column, and rows that share a unit, such as days of supply, take `scale: "shared"`, one axis in that unit. Tables stacked in one column line up when they get the same `labelWidth` and `valueWidth`. `dd.table("#key", d.measures, {rows: ["revenue", "profit", "orderSize"], scale: "pctTarget"})`

**Small multiples.** Small multiples repeat one graph, each copy differing in a single variable (channel, region, system), in a row, a column, or a grid. Give every copy the same `domain`, so equal lengths mean equal values, and print the category labels, the units, and any key once.

**Maps.** Use a map only when the meaning depends on where things are and can't be seen otherwise, such as absenteeism across stores nationwide or temperatures on a floor plan. Revenue for four sales regions doesn't qualify; it goes in a table or bars. The library draws no maps.

## Left out

| Medium | Why it is left out | Use instead |
| :-- | :-- | :-- |
| Pie | Eyes compare areas and angles poorly, and its one strength is saying the slices make up a whole | bars sorted largest first, with the whole named in the title |
| Donut | Not in Few's book; it is a pie with its middle cut out, leaving the same angles and arcs to judge | the same sorted bars |
| Area graph | Areas are misjudged, and one series hides another | lines |
| Radar | A line graph bent around a circle, slower to read than bars | sorted bars, or a line for a cycle such as hours of the day |
| 3D | Depth that encodes nothing distorts values; depth that encodes something hides bars behind others | flat bars or small multiples |
| Gauge or meter | Its circle wastes space and can't be packed beside others | bullet graph |
| Thermometer | Space spent on "meaningless realism" | bullet graph |
| Traffic light | A green light says nothing, a color change adds no mark, and red against green fails color-blind viewers | an alert dot shown only on exceptions, in two intensities of one red |

The library has no function for any of these; a call to one throws an error that names the medium to use.
