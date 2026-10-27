---
type: llm
focus: { source: file, path: pr-numbers.md }
weight: 3
---
The raw data was five interleaved runs per configuration on main and on the branch, two profiles (debug, release) by three -j values (1, 4, 16), with wall and CPU seconds. Medians, main then branch: wall, debug 21.6/11.2, 6.9/4.8, 5.4/4.1; release 38.0/22.9, 14.9/13.3, 13.7/12.2; CPU, debug 21.3/11.0, 24.6/12.6, 30.1/13.8; release 37.5/22.4, 44.2/25.3, 55.0/28.1. So CPU time drops 40 to 54 percent in every configuration, while wall time drops 48, 30 and 24 percent in debug and 40, 11 and 11 percent in release. In every configuration the slowest branch run beat the fastest main run.

PASS only if all of these hold:

1. Above the table, a sentence or two in words gives the direction and rough size of the change and says that the wall-time gain shrinks at higher -j or in release.
2. There is one table with six data rows, one per configuration, ordered by profile and then by -j, where the main and branch wall times are adjacent columns, and there is a change column for wall time and a change column for CPU time.
3. The table reports medians (or another named statistic that is not the mean) and its values match the medians above within rounding; numbers are right-aligned; no cell contains a unit, an arrow or two values; and the seconds columns use the same number of decimals in every row.
4. Below the table, a short method note names the statistic, the five alternating runs per row, something about the spread (ranges, or that the runs did not overlap), and the machine or toolchain.

A heading above the text, a line naming the raw data file, and a -j column with no decimals are all fine. Otherwise FAIL, and name the first rule that was broken.
