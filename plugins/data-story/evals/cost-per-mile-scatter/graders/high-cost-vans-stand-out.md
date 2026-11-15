---
type: llm
focus: { source: file, path: fleet.svg }
weight: 2
---
You are reading the source of an SVG scatterplot for a one-page proposal to rebalance delivery routes. Each point is one of 34 vans: miles driven a month across, cost per mile up. The average cost per mile is about $1.50. Thirteen vans cost more than that: eight driven under about 1,700 miles a month ($1.90 to $2.80) and five driven over about 3,300 ($1.65 to $2.20). The other 21, in between, cost $0.80 to $1.40.

PASS if a reference line marks the average cost per mile and is labelled as the average, and the vans above it are drawn in an accent color or a heavier mark while the vans below it are grey or muted, with both high-cost groups (the low-mileage vans and the high-mileage vans) among the emphasized points.

FAIL if every point is drawn the same way, if color encodes something other than above or below the average (such as a gradient by value), if only one of the two high-cost groups is emphasized, or if there is no labelled average line.
