---
type: llm
focus: { source: file, path: fleet.svg }
weight: 2
---
You are reading the source of an SVG scatterplot for a one-page proposal to rebalance delivery routes. Each point is one of 34 vans: miles driven a month across, cost per mile up. Thirteen vans cost more per mile than the rest: eight driven under about 1,700 miles a month ($1.90 to $2.80) and five driven over about 3,300 ($1.65 to $2.20). The other 21, in between, cost $0.80 to $1.40. The average cost per mile is about $1.50.

PASS if a labelled reference makes the comparison, either a line at the average cost per mile labelled as the average or the 1,700 to 3,300 mile range the proposal asks for, marked and labelled, and the 13 high-cost vans stand out from the other 21: in an accent color or a heavier mark with the rest grey, or in a contrasting color from the rest. Both high-cost groups, the low-mileage vans and the high-mileage vans, must be among the emphasized points.

FAIL if every point is drawn the same way, if color encodes something else (such as a gradient by value), if only one of the two high-cost groups is emphasized, or if there is no labelled reference.
