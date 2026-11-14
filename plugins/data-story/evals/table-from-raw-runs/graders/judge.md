---
type: llm
focus: { source: file, path: pr-numbers.md }
weight: 3
---
The file is the performance section of a PR description, read by the maintainer who decides whether to merge. The raw data was five interleaved runs per configuration on main and on the branch, two profiles (debug, release) by three -j values (1, 4, 16), with wall and CPU seconds. Medians, main then branch: wall, debug 21.6/11.2, 6.9/4.8, 5.4/4.1; release 38.0/22.9, 14.9/13.3, 13.7/12.2; CPU, debug 21.3/11.0, 24.6/12.6, 30.1/13.8; release 37.5/22.4, 44.2/25.3, 55.0/28.1. The means are within 1 percent of these. So CPU time drops 40 to 54 percent in every configuration, while wall time drops 48, 30, and 24 percent in debug and 40, 11, and 11 percent in release.

PASS only if all of these hold:

1. Before the table, a sentence or two in words gives the conclusion: the direction and rough size of the change, and that the wall-time gain shrinks at higher -j or in release. A section that opens with the table, or with how the measurement was done, fails.
2. There is one table with six data rows, one per configuration, in an order that means something (by profile, then by -j), where the main and branch wall times are adjacent columns, and the change is computed for wall time and for CPU time.
3. The values match the figures above within rounding, and no cell holds two values or an arrow.
4. After the table, a short note says where the numbers came from: the statistic, the five alternating runs per configuration, and the machine or toolchain.

A heading above the text and a line naming the raw data file are fine. Otherwise FAIL, and name the first rule that was broken.
