# Choosing the form

Pick the form this reader will read most easily. The common ones are the better choice, because nobody has to learn how to read them.

## A sentence

One or two numbers go in a sentence that has the numbers in it: "Median build time fell from 14 minutes to 9." One before and after is still two numbers, even when each comes with a range or a run count: those go in the same sentence or the next one. A chart or a table around two numbers costs space and makes them look smaller, so the sentence stands alone. Shown alone on a slide or a dashboard tile, the number is set large, with a few words under it saying what it is.

Be careful when collapsing several numbers into one. "Halved" hides whether it went from 40 to 20 or from 4 to 2, so keep both values when their size matters to the reader.

## A table

A table is read cell by cell, the way text is. Use one when each reader will look up their own row, when exact values matter, or when the measures have different units. Fade the structure so the values stand out: light borders or none, white space between groups, no shading.

Put the values being compared in adjacent columns and compute the difference, so nobody subtracts. Order the rows by what the reader is looking for. A table should still have a sentence above it that says what to conclude.

In a live presentation a table loses the room, because people read it and stop listening. Pull out the one comparison the point needs and put the full table in an appendix. In markdown the appendix is a `<details>` block or a linked file.

A heatmap is a table whose cells are shaded by value, one color from light to dark, so the high and low cells show without reading every number. Say which end is high.

## A line graph

Lines are for continuous data, nearly always time. The line joining the points says they belong to one sequence, which is false for categories.

- Keep the intervals even. An axis that goes by decade and then by year puts ten years and one year the same distance apart, and the trend it draws is false.
- An average can be drawn with its range around it (a minimum and a maximum, or a confidence band) when the spread is part of the point.
- A forecast is drawn differently from what was measured: a thinner dotted line, labelled, with the forecast region lightly shaded.
- Several lines that cross each other are unreadable as a set. Emphasize one line and grey the rest, or pull the lines apart into small panels that share an axis (stacked vertically to compare each trend, side by side to compare levels), or show fewer series and fewer years.

## A slopegraph

A slopegraph compares two points in time, or two conditions, across several categories, with a line per category from its first value to its second. It shows the values, the direction, and the size of each change together, and one line can be emphasized against the rest. It stops working when the lines pile up on each other, and the order of the categories is set by their values, so use bars when the order has to be controlled.

## Bars

Bars are for categories. The eye compares where the bars end, so the comparison is only true when they all start at zero.

- Horizontal bars are the default for categories. The names read left to right before the bar does, and long names fit.
- Vertical bars suit a few categories with short names, or periods of time. With two series, what is adjacent gets compared, so group by the comparison that matters.
- Stacked bars show a total and its parts, but only the bottom part has a baseline. Use them when the total and one part are the point.
- 100% stacked horizontal bars show parts of a whole across a few groups, and answers on a scale from negative to positive: the two ends each have a baseline, so both are easy to compare. Give the group sizes in a note, since the bars hide them.
- A waterfall shows where a value started, each change to it, and where it ended.

Make bars wider than the gaps between them. Order them by value with the important end on top, unless the categories have an order of their own.

## A scatterplot

A scatterplot plots two measures for each item, to show whether and how they relate. Add a reference line (the average, a target) and color the group the title talks about.

## Square areas

People judge areas badly, so avoid area graphs. The exception is numbers of very different sizes, where bars would make the small one invisible: squares drawn to scale fit both.

## Leave out

- Pies and donuts. Angles, areas, and arcs are hard to compare: two similar slices can't be ranked without their labels, and with the labels the picture adds nothing. Bars sorted by size say the same thing readably. If "these are parts of one whole" has to show, state the total.
- 3D. It distorts every value it touches and adds marks that mean nothing.
- A second y-axis. The reader has to work out which series reads against which side. Label the second series with its values directly, or stack two graphs on one x-axis. Drawing two measures together also implies they are related, so check that they are.

## Axis or labels

When the trend is the point, keep the axis and make it grey. When the values are the point, write them on the data and drop the axis. Both together is the same information twice.

## What each medium can do

- Plain text (a commit message, a terminal, a chat reply): the sentence, and the order things are said in.
- Markdown (a PR, an issue, a README, docs): the sentence, a table, a `<details>` block as the appendix, one bold phrase, and an image for an actual graph, committed to the repo or attached.
- A rendered chart (SVG, HTML, an image from a plotting library): every form here. Draw on white and paint the background yourself, so a dark-themed page can't turn grey text invisible.
- Slides: one point per slide, said in the title, with the detail in what is spoken.

If a charting skill or a plotting library is already in use, let it draw, and apply these choices to it: the form, what is cut, what is emphasized, and the words.
