---
type: llm
focus: { source: file, path: sales-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a wine distributor's VP of Sales, built from these files: seven key metrics YTD with targets and 12 months of history (revenue, profit, average order size, on-time delivery, new customers, customer satisfaction, market share); five regions' revenue YTD against target and QTD with open pipeline against the Q4 target; five wines' revenue and cases YTD against targets; market share for us (Larkspur), six competitors, and all others; and the largest customers with open pipeline, QTD, and YTD revenue. Revenue YTD is $23,770,103.

PASS only if all of these hold:

1. Each of the seven key metrics is shown against its target, with its recent history (a sparkline or similar) beside it.
2. Each region shows YTD revenue against its target, and QTD revenue together with its pipeline against the Q4 target.
3. Each wine shows revenue against target and cases against target.
4. Market share shows us among the competitors on one scale, sorted, with us set apart from the rest.
5. The customers appear ranked by open pipeline, with their QTD and YTD revenue.
6. Money is rounded to what a VP acts on, such as $23.8M or $23,770K, not $23,770,103 or cents. If the page formats numbers at run time, judge by the format it asks for.

FAIL if any group is missing, if a measure appears without the comparison named above, or if money is shown to the dollar or the cent. Name the first rule that was broken.
