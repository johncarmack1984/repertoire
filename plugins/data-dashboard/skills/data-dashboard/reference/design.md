# Perception, simplicity, layout, and color

This file holds the detail for steps 5 and 6. It covers how the eye reads a screen, what to strip from it, where each group goes, and the color and type every page uses. The chapter for each rule is named in its section; `sources.md` maps them.

## Perception

These rules come from chapter 4, "Tapping into the Power of Visual Perception".

Short-term memory holds three to nine chunks of visual information at once, and what leaves the screen is lost from it. Each number on a dashboard is its own chunk, while the shape of a line can hold a great many values as one chunk, which is why graphs let a viewer take in a dashboard "in big visual gulps." Current research puts the capacity nearer four, so design to the low end. Keep the groups on a screen between three and nine, and let graphs carry history.

Preattentive attributes are the ones seen before any reading happens, and only some of them can say how much (chapter 4, "Encoding Quantitative Versus Categorical Data").

| Attribute | Quantity? | Use it for |
| :-- | :-- | :-- |
| 2-D position, line length | yes | every value, as a position on a scale or a bar's length |
| color intensity, line width, size | only more or less, not how much | alert levels, ranges in a bullet graph, a heavier line for the key series |
| hue, shape, orientation, added mark, enclosure | no, categories only | telling series apart, an alert dot, a group set off by a light rule |
| flicker | limited | nothing; see the 2026 updates below |

Keep any attribute other than position and length to five distinct values. In Few's words, "you should be careful not to exceed five distinct expressions." Five grays are the most a viewer separates at a glance, and short-term memory holds the meanings of about nine hues at most. Use simple shapes only, such as circles, squares, triangles, dashes, and crosses, because complex shapes and most icons are not seen preattentively. Never encode a value as an area. Viewers underestimate area differences; Few's test circle is sixteen times the area of its neighbor, and most guesses come in lower.

The Gestalt principles, read as layout rules:

- **Proximity.** Put items of a group close together and separate groups with white space. Tighter spacing across a row makes the eye read in rows; tighter spacing down a column makes it read in columns.
- **Similarity.** Give one measure the same color wherever it appears, and give unrelated things different looks, since viewers link anything that looks alike.
- **Enclosure.** A border or a fill groups more strongly than anything else, so a light one is enough. Use it only where white space can't separate groups.
- **Closure.** Two axes define a graph's area. Draw no box around a plot.
- **Continuity.** Align items to group them, and show hierarchy by indentation, never by vertical rules.
- **Connection.** A line joining items groups them more strongly than proximity or similarity. Use connecting lines for relations that aren't quantities, such as process steps and reporting lines.

## Simplicity

Chapter 5, "Eloquence Through Simplicity", adapts Tufte's data-ink ratio to the screen. A non-data pixel is any pixel that doesn't show data, apart from the blank background. Work in Few's order, and look for unneeded non-data pixels again in every round.

1. **Eliminate the unneeded non-data pixels.** Remove decoration, color that means nothing, borders between sections, fills behind titles, plots, and tables, gradients, grid lines in graphs and in tables, alternating row shading, the box around a plot, 3D, and anything that imitates a physical object.
2. **De-emphasize and regularize the rest.** Keep what supports structure or legibility, such as axes and the rule under a column header, and make it light gray and thin, "just visible enough to do their job, but no more." Make every non-data element with the same job identical, with one axis gray and one hairline weight. Put controls out of the way, bottom right and muted, and move instructions to a pop-up or a separate screen.
3. **Eliminate the unneeded data pixels.** Choose data strictly by the task, summarize to the level the viewer acts on, and show exceptions rather than every row. Keep a basic picture on screen when all is well; a single all-clear light takes management by exception too far.
4. **Highlight the most important data pixels.** Data that is always important gets the best position. Data that matters only now gets a visual change, switched on by a rule on the data.

Highlight by making a thing more (a darker or more saturated color, a larger size, a thicker line) or by making it different (a distinct hue, an added mark, an enclosure). For values that need attention, add a small circle in one hue and vary its intensity for urgency, as in `dd.alert`, and set the value in bold as the second cue. Highlight sparingly. "If you highlight too much information, nothing will stand out." The check reports the share of rows that alert.

## Layout

Chapter 7, "Designing Dashboards for Usability", gives the arrangement; chapter 5 gives the emphasis zones.

**Grouping.** Group by business function (order entry, shipping), by entity (departments, systems, projects), or by use (revenue beside expenses). For a viewer whose role spans many units, such as a CEO, group and order by importance to the bottom line or by the order the overview should be read. Learn how the data is used before arranging it.

**Separating.** Separate groups with white space. Where the screen is too dense for that, use hairlines, and keep them faint. "You might be surprised at how light lines can be and still do the job." Hairlines go under section titles and column headers, never around a section.

**Emphasis.** The top left and the center get the most emphasis, and the center only when white space sets it apart. The top right and bottom left are neutral, and the bottom right gets the least. Put the always-important group top left, never a logo or controls. Keep every position fixed, so the viewer learns where things are.

**Comparisons.** Support the comparisons that mean something. Put compared items in one table or graph, or next to each other on shared scales, stack graphs to be compared one above the other, and show comparative values such as % of target, % of total, and variance. Discourage the meaningless ones by separating unrelated items and never letting one color mean two things.

**Consistency.** Anything that means the same thing looks the same everywhere. The same kind of data used the same way gets the same medium, even if every graph on the screen is a bullet graph.

**Multi-foci time.** Where history matters, show recent time in fine detail and older time coarsely, such as this month by day, the last 12 months by month, and the years before by year.

**The design viewport.** The page is designed for one screen at 1440 by 800 CSS px, a laptop screen less the browser chrome. Everything is sized in the unit `--u`, which is 20 px there, so the canvas is 72 u wide and 40 u tall and scales whole to any desktop screen. The page's padding takes 1.2 u of the height and the title, in the header or the footer, about 2 u, which leaves about 37 u for the grid. Keep 2 u of that spare, because system fonts differ between machines, and plan every column to 35 u. Write the budget before building, from the heights the library draws:

| Element | Height in u |
| :-- | --: |
| section title, with its rule | 1.55 |
| column header | 0.95 |
| graphical table row with a units line | 1.45 |
| graphical table row without one, bar row | 1.15 |
| text table row | 0.95 |
| axis | 1.15 |
| standalone bullet graph, with its ticks | 3.3 |
| line graph | 7, or its `height` |
| gap between sections | 0.8 |

The worked example's budget, written into its brief:

```
Two bands, columns 55fr / 45fr; title in the footer; plan 35 u
  Top band
    Red cells on hand   1.55 title + 0.95 header + 8 rows x 1.45 + 1.15 axis   15.25
    Hospital stock      1.55 title + 0.95 header + 9 rows x 1.15 + 1.15 axis   14.0
  gap                                                                         0.8
  Bottom band
    Tomorrow's donors   1.55 title + 0.95 header + 7 rows x 1.45 + 1.15 axis   13.8
    Expiring, 72 hours  1.55 title + 0.9 header + 8 rows x 0.95                10.05
    gap                                                                        0.8
    Last week           1.55 title + 0.95 header + 3 rows x 1.45 + 1.15 axis    8.0
  total 15.25 + 0.8 + 18.85 = 34.9, inside 35
```

When a column doesn't fit, cut a measure or move a group, and say which in the report; never shrink the unit or let the page scroll. The check measures the real heights and says by how many pixels a page overflows.

**The phone reflow.** Below a floor width the page becomes one column that scrolls. Groups keep their order of importance, the top-left group first, and each group stays whole with its axis. The check saves a phone-width screenshot as well as the desktop one.

## Color and type

Chapter 7, "Make the Viewing Experience Aesthetically Pleasing", and chapter 4, "Using Vivid and Subtle Colors Appropriately", set the palette. Use soft colors from nature for most things, bright color only for data that needs attention, and a barely visible pale background instead of white. The tokens in `assets/dashboard.css` fill these roles:

| Role | What it is | Contrast on the background |
| :-- | :-- | :-- |
| background | barely off-white, never pure white, never dark | |
| text | dark gray for labels and values; lighter gray for units lines, column headers, axis labels, and the as-of line | 4.5:1 or more |
| data | near-black bars, lines, and target marks; the bullet graph's three range grays; one medium gray for bars | 3:1 for marks that carry meaning |
| accent | one muted hue on section titles only | 4.5:1 |
| title | the largest text, in the accent but lighter than the section titles, so it doesn't compete with the data | 3:1, as large text |
| alert | two intensities of one red, for `warn` and `alert` only | each 3:1 or more, with a second cue |
| rules | hairlines under section titles and column headers | as light as still shows |

Few's own colors fall short of these targets. Sampled from his chapter 8 dashboards, his title accents reach 1.8 to 3.0:1 on his cream background, his light alert red 2.0:1, and his dark one 3.9:1, so the tokens keep his hues and darken them. Every alert also sets its value in bold and writes its percent of target as text, a second cue that doesn't depend on color. The light range bands of a bullet graph stay as Few drew them; each row's state is written in its screen-reader text instead.

Use one sans-serif family, the system stack, throughout. Set numbers in tabular figures (`font-variant-numeric: tabular-nums`) and right-align them, so digits line up down a column. The size steps, as multiples of the 12.5 px body text at the design viewport:

| Text | Size |
| :-- | --: |
| page title | 2 |
| section title | 1.2 |
| labels and values | 1 |
| units lines, column headers, axis labels | 0.8 |

No text goes below 9 px; the check flags anything smaller.

## The 2026 updates

| The 2006 book | This skill |
| :-- | :-- |
| one fixed monitor, with no size given | a named design viewport the page scales to, and a phone reflow |
| low-resolution images made in Excel and Illustrator | SVG, crisp at any pixel density |
| hover and click with a mouse | every hover also opens on focus and tap; drill-down is a link to a detail view; nothing essential lives only in a tooltip |
| blinking alerts and a sound that grows louder | no blinking or sound; an alert is an added mark, and the page honors reduced-motion settings |
| an as-of date with no time zone | the as-of time with its zone, at the precision the update cadence needs, never to the second |
| red, yellow, and green fail 10% of men and 1% of women | today's usual figures are about 8% and 0.5%; color is never the only cue (WCAG 1.4.1) |
| pale accents and alert colors on cream | darkened to 4.5:1 for text and 3:1 for marks that carry meaning (WCAG 1.4.3 and 1.4.11) |
| thousands separators and rounding, in U.S. style | locale-aware formats, with one scale per column (thousands or millions) named in the header |
| three to nine chunks in short-term memory | about four in current research, so the low end of Few's range |
| a Help button | information on demand from the headers, reachable by keyboard |
| a freeze button for live data | a pause control and a visible stale indicator; the layout never moves when data updates |
| executives who print their dashboards | a PNG of the page at the design viewport |
| 2006 measures for IT and the web | service-level objectives, error budgets, and p95 latency; sessions, conversion, and Core Web Vitals |

`mistakes.md` gives the 2026 form of each old vendor style, such as donuts, glassy cards, count-up numbers, and neon on dark.
