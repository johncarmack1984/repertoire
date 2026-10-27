# Tables

A table is for looking up values and comparing them one at a time. Its values are read, as text is, so its design is about where the eye lands and what it finds there.

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

## Width

- A table that wraps in a PR or an issue is unreadable; about six columns of short headers is the limit. Shorten headers (`-j`, not `parallelism`), drop a column the sentence already covers, or split by measure before abbreviating values.
- Markdown draws the separators and the alignment row itself, so the only ink left to control is the characters in the cells: fewer is better.

## Around the table

- Above: the takeaway sentence, ending in a colon when the table follows directly.
- Below: the method line (`reference/measurements.md`).
- The table never carries the point alone; a reader who skips it still gets the result from the sentence.
