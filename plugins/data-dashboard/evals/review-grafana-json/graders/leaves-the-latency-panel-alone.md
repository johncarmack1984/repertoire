---
type: llm
focus: trace
weight: 2
---
The user asked for a review of a Grafana dashboard before sharing it. One panel is already done well and needs no change: "p95 latency (ms), dashed line is the 300 ms SLO", a time series with a single gray line, a gray dashed threshold line at the 300 ms SLO, no fill, no points, no gridlines, the y-axis starting at zero, and the legend hidden. The other panels (a pie, four gauges, a red or green status stat, and a table with red or green cells) have real faults.

Read the final reply to the user.

PASS if the reply proposes no change to the p95 latency panel. Leaving it unmentioned passes, and so does naming it as a model for the other panels or a panel to keep as it is. Using it as a reference point while fixing other panels also passes.

FAIL if the reply lists any change to the p95 latency panel (adding a legend, a fill, gridlines, colors, a second series, a different threshold style, or anything else), or counts it among the faults. Quote the change it proposed.
