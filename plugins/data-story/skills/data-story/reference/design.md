# Clutter, focus, and words

Steps 4, 5, and 6 in detail: what to cut, what to emphasize, what to say. A plotting tool's defaults were chosen without knowing the point, so each of them is a decision to make again.

## What to cut

Go down the chart the tool drew and ask of each element whether the reader would understand less without it.

| The default | Do this |
| :-- | :-- |
| a border around the chart | remove it; the plot reads as one object without a box |
| gridlines | remove them, or keep them thin and light grey when readers will trace a value across |
| a marker on every point | remove them; keep a marker only on a point that has a label |
| a legend | label each series next to its data, in the same color as the data |
| a value label on every point | label only the points the argument uses |
| axis labels with trailing zeros, or one for every day | drop the zeros and label every fifth or seventh |
| long or rotated labels | abbreviate until they fit horizontally; text rotated 45 degrees reads 52% slower |
| centered titles and notes | left-align them with the edge of the plot |
| more decimals than the difference needs | round to what the reader can use |
| a color for each series | grey for all of them, one accent for the point |
| a category that only sums the others | remove it unless the total is the point |

In a table, cut heavy borders, shading, and labels repeated on every row; `tables.md` has the rules for rows, cells, and width. In prose, cut the account of how the analysis was done, and put it in an appendix for the reader who asks.

Some repetition helps. Keep the % or $ sign and the thousands separator with every number, and keep the unit where the number is read: beside it in prose and on a chart, once in the column header of a table.

## How the eye groups things

People see order in a few fixed ways, and each one either does a job for you or adds clutter.

- Things close together read as a group. Put a label next to its line, and separate groups of rows with space.
- Things that look alike read as related. Give a label the color of its data.
- Things enclosed together read as a group. A light shaded band is enough to set a forecast apart from what was measured.
- People complete a figure from its parts. Bars with no axis line still look aligned, and a plot with no border still looks whole.
- Things joined by a line read as one sequence. That is why lines suit time and not categories.

## What to emphasize

A few visual properties are seen before any reading happens: color, size, weight, position, an added mark, an enclosure. Used on one thing they send the eye there. Used on everything they send it nowhere.

- Start with everything grey and decide what to bring forward. Highlighting one thing makes the rest harder to see, which is what an explanation wants and what exploring the data doesn't.
- Size means importance. Things equally important are the same size, and the most important thing is the largest.
- Length and position are read as quantity. Hue isn't: nobody thinks orange is more than blue. Use a single color from light to dark when the color has to say "more".
- One accent color, used for the thing the title talks about and for the words that refer to it. A second accent only when two ends of a scale both matter, blue for the good end and orange for the bad one.
- A color keeps its meaning through the piece. A change of color tells the reader something changed.
- About one man in twelve can't tell red from green. Don't make that pair the difference between good and bad without a sign, a label, or a difference in brightness as well.
- Color sets tone. Muted greys with one blue read as calm; black and bold type read as formal. Match the tone decided in step 1.
- The eye starts at the top left and works across and down. The conclusion goes there, and scales run the way people expect: negative on the left, positive on the right.

Then test it. Look away, look back, and notice what you see first, second, and third. That order should be the order of the argument.

## Defaults for a chart

Use the destination's own style where it has one. Where nothing else decides:

- White background, painted as a rectangle, and no border.
- Text in dark grey, not black: #333 for the title, #555 for labels, #888 for axis text and notes.
- Context data in #b0b0b0 at 2px; the emphasized series in one accent (#1f6fb5 blue, with #d9731a orange as the second accent) at 3.5px.
- Title 18px bold, a sentence, top left. Subtitle 13px under it, saying plainly what is plotted and in what unit.
- Series labels 12 to 13px at the end of each line, in the line's color, with the last value when it helps.
- Annotations 12px next to the data they explain, the key phrase bold.
- Axis lines 1px in #c8c8c8, no tick marks, at most five or six axis labels.
- A note at the bottom left in 10 to 11px grey: source, period, sample size, how it was measured.
- All text horizontal, except a y-axis title when there is no room for it above the axis.

`assets/storage-cost.svg` is a line graph and `assets/flaky-tests.svg` a bar chart built to these defaults. Each has its scale written in a comment, so the data can be replaced.

## What to say

- The title is the point or the ask, as a sentence. A title that only says what is plotted wastes the first thing the reader sees.
- Say the conclusion in words. Two people looking at the same chart will not reach the same one on their own.
- Name things in the reader's words, and use one name for one thing all the way through.
- Annotate where it happened. A note beside the data explains an outside event, a caveat, or why this point is highlighted.
- The note at the bottom is for what a careful reader will ask: where the numbers came from, what they cover, and what more exists.

## In markdown and plain text

There is no color and little control of size, so the same ideas use different tools.

- Position is the main one. The first line is the conclusion, and the ask is first or last.
- A heading is the large text. Make it a sentence that says something.
- Bold is the accent color. One phrase in a block, the one that states the point.
- A blank line is white space. Short paragraphs, and a number that matters on a line of its own.
- A table is still a table: few columns, the comparison adjacent and computed, no decoration in the cells.
- A `<details>` block is the appendix.
