---
type: llm
focus: { source: file, path: sales-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a wine distributor's VP of Sales, who reads it on a 14-inch laptop each morning. It covers seven key metrics, regions (YTD, and QTD with pipeline), products, market share, and top customers.

PASS only if all of these hold:

1. The seven key metrics come first in reading order, in the top-left area of the layout.
2. Things meant to be compared sit together: each region's YTD and QTD figures are in the same row or in rows that line up, and the key metrics share one scale or one row pattern.
3. The layout is built for one laptop screen without scrolling: a fixed composition such as a CSS grid sized to the viewport, not a long stack of full-width sections.
4. Groups are separated by white space and at most thin rules. There are no boxed panels with borders on every side, no colored title bars, no drop shadows, and no logo or navigation in the top left.

FAIL otherwise, and name the first rule that was broken.
