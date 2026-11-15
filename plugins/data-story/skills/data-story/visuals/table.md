# A table

The chooser's row in `SKILL.md` for a reader who will look up their own row, needs exact values, or compares measures in different units. Chapter 2 of *Storytelling with Data* covers the table and the heatmap; the rules for rows and cells follow Stephen Few's *Show Me the Numbers*.

A table is read cell by cell, the way text is, so its design is about where the eye lands and what it finds there. For a table these rules are steps 3 to 5: the shape is its focus, the cells and the width are its clutter, and the lines around it are its words.

## Shape

- A table answers one question. The rows are the things compared (configurations, variants, inputs) and the columns are the measures; a second question with a different row set is a second table.
- One row per configuration, with the varied conditions as the leading columns (`format`, `size`), ordered to mean something: by the grouping condition, then by the swept condition ascending, or by the size of the effect when that is the point; alphabetical only for looking up items that have no natural order. The order the runs happened in is not an order.
- The compared values sit side by side: the baseline and the change are adjacent columns, baseline first, and their difference is the next column, Δ as a signed percent of the baseline (−37%), or the signed absolute difference when the reader thinks in units. Say once which direction is better when the sign could be read either way.
- One measure's change sits next to the other's: time beside memory, latency beside cost or throughput, each with its own Δ, so the reader sees when they move apart.
- Headers carry the units and the condition: `time, main (s)`, `p99 (ms)`, `RSS (MiB)`. A change column keeps its sign and `%` in the cells, because a bare −37 reads as a count.

## Cells

- Numbers right-aligned (`--:`), labels left-aligned (`:--`).
- One precision per column, chosen for the reader: two decimals for seconds, whole numbers for percentages and milliseconds, three significant figures otherwise. Write `21.00` rather than mix `21.0` with `14.90`.
- One value per cell. No `before → after` pairs, no units, no ranges in parentheses, no bold, no footnote markers unless the method line needs one.
- A label that repeats in consecutive rows is written once; the rows below leave it blank, so the group reads as a group with no rule line.
- Summary rows (total, overall median) go last and say what they are.
- Fade the structure so the values stand out: light borders or none, white space between groups, no shading.

## Width

- A table that wraps in a PR or an issue is unreadable; about six columns of short headers is the limit. Shorten headers (`size`, not `image dimensions`), drop a column the sentence already covers, or split by measure before abbreviating values.
- Markdown draws the separators and the alignment row itself, so the only ink left to control is the characters in the cells: fewer is better.

## Around the table

- Above: the takeaway sentence, ending in a colon when the table follows directly.
- Below: the method line (`reference/measurements.md`).
- The table never carries the point alone; a reader who skips it still gets the result from the sentence.
- In a live presentation a table loses the room, because people read it and stop listening. Pull out the one comparison the point needs and put the full table in an appendix. In markdown the appendix is a `<details>` block or a linked file.

## A heatmap

A heatmap is a table whose cells are shaded by value, one color from light to dark, so the high and low cells show without reading every number. Use it when the pattern across the cells matters as much as the values, keep the numbers in the cells, and say which end is high.

## Worked example

A change to an image-resizing service in a PR: it reuses decoder buffers between images instead of allocating new ones, measured against main for two formats at three image sizes. The brief's Big Idea: reusing the buffers cuts peak memory by about 60% at every size, so it is safe to take; the time saved is smallest for large images. The first draft of the numbers:

| | medium | large | small |
| --- | --- | --- | --- |
| JPEG | 18.20 → 14.90 s | 96.00 → 88.30 s | 4.10 → 2.60 s |
| PNG | 25.50 → 21.00 s | 140.20 → 131.80 s | 6.00 → 3.90 s |

Every cell has two values and an arrow, so the reader does the subtraction; the sizes are out of order; memory, the measure the change is about, is missing; and no words say what to conclude. Rebuilt:

> Reusing decoder buffers cuts peak memory by about 60% at every size measured. Time drops less as images grow, least for large PNGs, where decoding itself takes most of the time:
>
> | format | size | time, main (s) | time, reuse (s) | Δ time | Δ memory |
> | :-- | :-- | --: | --: | --: | --: |
> | JPEG | small | 4.10 | 2.60 | −37% | −61% |
> | | medium | 18.20 | 14.90 | −18% | −59% |
> | | large | 96.00 | 88.30 | −8% | −58% |
> | PNG | small | 6.00 | 3.90 | −35% | −63% |
> | | medium | 25.50 | 21.00 | −18% | −60% |
> | | large | 140.20 | 131.80 | −6% | −57% |
>
> Seconds per 1,000 images and peak resident memory, medians of 6 interleaved batches per row (arm64 Linux, 8 cores, the same 1,000 images at each size). In every row, the slowest batch with reuse beat the fastest without it.

The first sentence is the Big Idea. The second gives the number that cuts against it before the reader finds it. A table is the visual because the reviewer will look up their own format and size and there are two measures; the change is computed, and the time change sits next to the memory change, so the reader sees that decoding, and not the change, is what shrinks the time saved on large images. The last line says where the numbers came from.
