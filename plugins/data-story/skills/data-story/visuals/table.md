# A table

The chooser's row in `SKILL.md` for a reader who will look up their own row, needs exact values, or compares measures in different units. Chapter 2 of *Storytelling with Data* covers the table and the heatmap; the rules for rows and cells follow Stephen Few's *Show Me the Numbers*.

A table is read cell by cell, the way text is, so its design is about where the eye lands and what it finds there. For a table these rules are steps 3 to 5: the shape is its focus, the cells and the width are its clutter, and the lines around it are its words.

## Shape

- A table answers one question. The rows are the things compared (configurations, variants, inputs) and the columns are the measures; a second question with a different row set is a second table.
- One row per configuration, with the varied conditions as the leading columns (`profile`, `-j`), ordered to mean something: by the grouping condition, then by the swept condition ascending, or by the size of the effect when that is the point; alphabetical only for looking up items that have no natural order. The order the runs happened in is not an order.
- The compared values sit side by side: the baseline and the change are adjacent columns, baseline first, and their difference is the next column, Δ as a signed percent of the baseline (−48%), or the signed absolute difference when the reader thinks in units. Say once which direction is better when the sign could be read either way.
- One measure's change sits next to the other's: wall time beside CPU time, latency beside cost or throughput, each with its own Δ, so the reader sees when they move apart.
- Headers carry the units and the condition: `wall, main (s)`, `p99 (ms)`, `RSS (MiB)`. A change column keeps its sign and `%` in the cells, because a bare −48 reads as a count.

## Cells

- Numbers right-aligned (`--:`), labels left-aligned (`:--`).
- One precision per column, chosen for the reader: two decimals for seconds, whole numbers for percentages and milliseconds, three significant figures otherwise. Write `11.20` rather than mix `11.2` with `22.04`.
- One value per cell. No `before → after` pairs, no units, no ranges in parentheses, no bold, no footnote markers unless the method line needs one.
- A label that repeats in consecutive rows is written once; the rows below leave it blank, so the group reads as a group with no rule line.
- Summary rows (total, overall median) go last and say what they are.
- Fade the structure so the values stand out: light borders or none, white space between groups, no shading.

## Width

- A table that wraps in a PR or an issue is unreadable; about six columns of short headers is the limit. Shorten headers (`-j`, not `parallelism`), drop a column the sentence already covers, or split by measure before abbreviating values.
- Markdown draws the separators and the alignment row itself, so the only ink left to control is the characters in the cells: fewer is better.

## Around the table

- Above: the takeaway sentence, ending in a colon when the table follows directly.
- Below: the method line (`reference/measurements.md`).
- The table never carries the point alone; a reader who skips it still gets the result from the sentence.
- In a live presentation a table loses the room, because people read it and stop listening. Pull out the one comparison the point needs and put the full table in an appendix. In markdown the appendix is a `<details>` block or a linked file.

## A heatmap

A heatmap is a table whose cells are shaded by value, one color from light to dark, so the high and low cells show without reading every number. Use it when the pattern across the cells matters as much as the values, keep the numbers in the cells, and say which end is high.

## Worked example

A build-script change in a PR, measured against main for two profiles at three `-j` values, with the change behind an opt-in variable. The brief's Big Idea: running the probes once cuts the build script's CPU time about in half at every setting, so it is safe to take; the wall-time gain is smallest in release. The first draft of the numbers:

| | -j16 | -j4 | -j1 |
| --- | --- | --- | --- |
| debug | 5.34 → 4.05 s | 6.75 → 4.73 s | 22.04 → 11.36 s |
| release | 13.64 → 12.10 s | 14.77 → 13.19 s | 38.35 → 22.60 s |

Every cell has two values and an arrow, so the reader does the subtraction; `-j` runs backwards; CPU time, the measure the change is about, is missing; and no words say what to conclude. Rebuilt:

> It cuts the build script's CPU time about in half at every setting measured. Wall time drops less as -j rises, least in release, where `bcm.c` alone takes about 10 s at -O3:
>
> | profile | -j | wall, main (s) | wall, opt-in (s) | Δ wall | Δ CPU |
> | :-- | --: | --: | --: | --: | --: |
> | debug | 1 | 22.04 | 11.36 | −48% | −48% |
> | | 4 | 6.75 | 4.73 | −30% | −49% |
> | | 16 | 5.34 | 4.05 | −24% | −54% |
> | release | 1 | 38.35 | 22.60 | −41% | −41% |
> | | 4 | 14.77 | 13.19 | −11% | −43% |
> | | 16 | 13.64 | 12.10 | −11% | −49% |
>
> Medians of 4 to 8 interleaved runs per row (x86_64 Linux, gcc 15.2, `default-features = false`). In every row, the slowest run with the variable beat the fastest without it.

The first sentence is the Big Idea. The second gives the number that cuts against it before the reader finds it. A table is the visual because the maintainer will look up their own configuration and there are two measures; the change is computed, and wall time is next to CPU time so the reader sees that parallelism, and not the change, is what shrinks the gain. The last line says where the numbers came from.
