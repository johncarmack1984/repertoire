---
type: llm
focus: { source: file, path: fleet.svg }
weight: 2
---
You are reading the source of an SVG scatterplot for a one-page proposal to an operations director: rebalance delivery routes so no van runs under about 1,700 or over about 3,300 miles a month. Each point is one of 34 vans, miles a month against cost per mile. The vans driven least and most cost more per mile than the average of about $1.50; the ones in between cost less.

PASS if the most prominent text in the chart, the first or the largest, states the pattern or the ask in words: that vans driven under about 1,700 or over about 3,300 miles a month cost more per mile than average, or a request to rebalance routes into that range. A plain label for what is plotted may appear as well, smaller.

FAIL if the only title names what is plotted, such as "Scatter plot" or "Cost per mile by miles driven".
