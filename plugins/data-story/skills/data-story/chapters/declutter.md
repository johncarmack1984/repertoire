# Declutter

Step 3 of the flow in `SKILL.md`, from chapter 3 of *Storytelling with Data*, "clutter is your enemy!". Everything on the page costs the reader some attention, and a plotting tool's defaults were chosen without knowing your point, so each of them is a decision to make again.

## Element by element

Go down the chart the tool drew and ask of each element whether the reader would understand less without it. If not, take it out. What has to stay but isn't the message (axes, the other series, the source note) goes light grey.

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

- Axis or labels? When the trend is the point, keep the axis and make it grey. When the values are the point, write them on the data and drop the axis. Both together is the same information twice.
- What here will feel like work? Do that work yourself. Compute the difference the reader would otherwise subtract, and spell out the abbreviation.
- Take out a chart that repeats what a sentence already said, and a paragraph that repeats the chart. Data added because there was room is noise.
- Some repetition helps. Keep the % or $ sign and the thousands separator with every number, and the unit where the number is read.

## How the eye groups things

People see order in a few fixed ways, and each one either does a job for you or adds clutter.

- Things close together read as a group. Put a label next to its line, and separate groups with space.
- Things that look alike read as related. Give a label the color of its data.
- Things enclosed together read as a group. A light shaded band is enough to set a forecast apart from what was measured.
- People complete a figure from its parts. Bars with no axis line still look aligned, and a plot with no border still looks whole.
- Things joined by a line read as one sequence. That is why lines suit time and not categories.

## Order and space

- Left-align text and line elements up on shared edges. Centered text over a left-aligned plot leaves ragged edges that look unfinished.
- Leave empty space empty. It separates the groups and lets the important thing stand alone.
- Cut prose the same way: background the reader already knows, an account of how the analysis was done, a caveat given a paragraph where a line would do. The method goes in an appendix for the reader who asks. A page read before a decision is read in about a minute.
