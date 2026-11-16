---
type: llm
focus: { source: file, path: cio-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a CIO. Its data includes hourly network traffic for yesterday with the 7-day and 6-month means for each hour; 30 response-time samples each for Data Warehouse, ERP, Web Site, and HR, with acceptable limits of 3.0, 2.0, 1.6, and 1.5 seconds; and CPU (79%) and storage (63%) used, where under 70% is good, 70% to 85% excessive, and over 85% critical.

PASS only if all of these hold:

1. Network traffic is one line graph with three lines over the 24 hours, yesterday drawn darkest or boldest and the two means lighter, in grays rather than a color per line.
2. Response times show each system's distribution (a box plot, a strip of the samples, or percentiles drawn as a range), not only an average, against that system's acceptable limit, on one shared scale.
3. CPU and storage are each drawn against the good, excessive, and critical ranges, as a bullet graph or similar, not as a gauge, a dial, or a pie.

FAIL otherwise, and name the first rule that was broken.
