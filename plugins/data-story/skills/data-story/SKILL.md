---
name: data-story
description: Present measured numbers to a reader. Use before putting benchmark results, timings, a before/after comparison, a performance or size claim, or any metrics into a PR description, issue, README, report, commit message or chat reply, and when asked to summarize runs, write up a benchmark or make a table of results. Picks the form (a sentence for one or two numbers, a table for values to look up or compare, a chart handed to a charting skill for a trend or a distribution), writes the takeaway sentence, builds a markdown table that reads well, and reports the measurement as a distribution (medians over means, run count, spread, time kept apart from throughput and cost).
---

# Data story

Numbers in front of a person are an argument. The reader should get the point from one sentence, check it in one look, and know how far to trust it. The report goes in that order: the takeaway, then the evidence in the form that fits it, then how it was measured.

## Steps

1. **Context.** Name the reader and what they will do with the result (merge, choose, stop worrying). Write the takeaway as one complete sentence that gives the direction, the size and what limits it ("cuts CPU time about in half; wall time drops less at higher -j, least in release, where one file takes 10 s on its own"). Done when the sentence could stand alone as the report.
2. **Form.** One or two numbers: a sentence, the takeaway with the numbers in it. Values the reader will look up or compare exactly, several configurations, or more than one measure of the same thing: a table, built from `reference/tables.md`. A message that lives in the shape of the data (a trend across many points, a distribution, a tail): a chart, so hand the data, the takeaway sentence and the method line to a charting skill (`dataviz` where it is installed) and keep the sentence above the chart and the method below it. Done when the form fits the reader's question rather than the amount of data.
3. **Evidence.** Build the sentence or the table. A table answers one question: the things compared are the rows, in an order that means something; the measures are the columns, with the compared values side by side and their difference computed; units sit in the headers; numbers are right-aligned with one precision per column. Done when the reader can find any value in one look and never does arithmetic.
4. **Method.** Below the table, or after the sentence, one or two lines: the statistic (medians, not means), how many runs and how they were ordered, the spread or an overlap statement, the machine and toolchain, and the condition that was varied. Follow `reference/measurements.md`, which also covers skewed runs, tails, and keeping time apart from throughput and cost. Done when someone could repeat the measurement and expect the same table.
5. **Declutter.** Read it as the reader. Anything that is not the takeaway, a value, a label, a unit or the method goes: arrows and units inside cells, bold, a second table for the same question, a paragraph that repeats the table. Done when removing one more thing would lose information.

## Worked example

A build-script change, measured against main for two profiles at three `-j` values, with the change switched on by an opt-in variable. The first draft:

| | -j16 | -j4 | -j1 |
| --- | --- | --- | --- |
| debug | 5.34 → 4.05 s | 6.75 → 4.73 s | 22.04 → 11.36 s |
| release | 13.64 → 12.10 s | 14.77 → 13.19 s | 38.35 → 22.60 s |

Every cell carries two values, an arrow and a unit, so the reader computes each change; `-j` runs backwards; CPU time, the half of the story the change is about, is missing; and nothing says how many runs there were or how much they varied. Rebuilt:

> It cuts the build script's CPU time about in half. Wall time drops less at higher -j, most of all in release, where `bcm.c` alone takes about 10 s at -O3:
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

The sentence carries the point and its limit. One row per configuration, grouped by profile with the label written once, `-j` ascending. The two variants sit side by side with their change computed, and the wall-time change sits next to the CPU-time change, so the reader sees that parallelism, not the change, is what shrinks the wall-time win. Units live in the headers, numbers are right-aligned with two decimals throughout, and the method line says what the numbers are and how much they moved.

## Sources

The context and form steps follow Cole Nussbaumer Knaflic's *Storytelling with Data*, the table rules follow Stephen Few's *Show Me the Numbers*, and the measurement rules follow Martin Kleppmann's *Designing Data-Intensive Applications*. `reference/sources.md` maps each rule to its chapter.
