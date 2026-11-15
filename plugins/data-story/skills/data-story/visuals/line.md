# A line graph

The chooser's row in `SKILL.md` for how something changed over time. From chapter 2 of *Storytelling with Data*, with chapter 9's case on the tangle of lines she calls a spaghetti graph.

Lines are for continuous data, nearly always time. The line joining the points says they belong to one sequence, which is false for categories: those go in bars.

- Keep the intervals even. An axis that goes by decade and then by year puts ten years and one year the same distance apart, and the trend it draws is false.
- A line may start above zero when the axis is labelled and the zoom doesn't turn a small change into a large one.
- Label each line at its right end, in the line's color, with its last value when that helps, in place of a legend.
- For a trend, write values only at the two ends of the line the point is about.
- An average can be drawn with its range around it (a minimum and a maximum, or a confidence band) when the spread is part of the point.
- A forecast is drawn differently from what was measured: a thinner dotted line, labelled, with the forecast region lightly shaded.
- Two measures in different units never share a chart through a second y-axis: the reader has to work out which series reads against which side. Label the second series with its values directly, or stack two graphs on one x-axis. Drawing two measures together also implies they are related, so check that they are.

## Lines that tangle

Several lines that cross each other are unreadable as a set. Pick one of these:

- Emphasize one line and grey the rest. In a talk, step through the others one at a time when each one matters.
- Pull the lines apart into small panels that share an axis, stacked vertically to compare each trend, side by side to compare levels.
- Show fewer series, or fewer years.

When none of these keeps the point, go back to the chooser: two points in time across many categories is a slopegraph.

## The model

`assets/storage-cost.svg` is a line graph built to `reference/chart-defaults.md`. Read it before drawing one: keep the structure, replace the data. Its scale is written in a comment.

## Worked example

Monthly cloud spend by service, for the platform lead who sets log retention and has seen the bill rise without knowing why. The first draft was the plotting library's default: clustered columns in three colors, a legend, gridlines, and the title "Monthly cloud spend".

```
Reader:    the platform lead, who decides retention; knows the total went up, not which service
Ask:       approve a 14-day retention on debug logs
Medium:    one chart in the monthly cost review, read alone
Big Idea:  Storage cost has doubled since debug logging went on in June while compute and network stayed flat, so a retention limit is the fix.
Evidence:  for: storage $4.2k in May, $8.4k in October. Against: compute is still the largest line, at $12.7k.
Visual:    a line graph, not a slopegraph: the change happens in June, so every month matters, not only the two ends
```

Rebuilt as `assets/storage-cost.svg`: a line graph, because it is change over time. Compute and network are grey, storage is the one accent color, and each line is labelled at its end with its October value in place of a legend. A note at June says what happened. The title is the ask, with the plain label under it, and the source and period are in small type at the bottom.
