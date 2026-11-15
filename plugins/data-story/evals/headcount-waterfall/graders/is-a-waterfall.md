---
type: llm
focus: { source: file, path: headcount.svg }
weight: 2
---
You are reading the source of an SVG chart for an email to a VP of Engineering. The data was the group's headcount over a year: 100 on 1 January, then 30 hires, 8 transfers in, 12 transfers out and 10 exits, and 116 on 31 December.

PASS if the two headcounts (100 and 116) are bars standing on the baseline, and each of the four changes is a floating bar that starts where the running total stood: hires from 100 up to 130, transfers in from 130 up to 138, transfers out from 138 down to 126, exits from 126 down to 116. Read the bars' y and height attributes to check.

FAIL if all six values are bars rising from the baseline, if the data is a line or a table, or if the floating bars don't follow the running total.
