---
type: llm
focus: trace
weight: 3
---
The user asked for a review of a Grafana dashboard (`grafana/service-health.json`) before sharing it with the on-call rotation, and asked that the file not be edited. The dashboard has a full-width "Service status" stat panel whose whole background turns red (DOWN) or green (UP); four gauges (CPU usage, Memory usage, Error rate, Apdex) with green, yellow, and red threshold arcs and two to four decimals; a "Requests by region" pie chart with a legend table; a p95 latency time series; and an "Endpoints" table whose Error % cells fill green or red, with four decimals and centered numbers.

Read the final reply to the user.

PASS only if all of these hold:

1. The reply marks the pie and gives a fix, such as a bar chart or bar gauge of requests by region, sorted, labeled directly.
2. The reply marks the gauges and gives a fix, such as bullet graphs, a bar gauge, or stat panels with a sparkline and a target or threshold beside the value, in far less space.
3. The reply marks the red and green status coloring (the stat background, the table cells, or both) and gives a fix, such as gray by default with color only when something is wrong, or a reason such as red-green color blindness.
4. Each finding names the panel by its title or type and says what to change in Grafana terms (a panel type, an option, or a setting), not only a principle.
5. The reply does not edit or rewrite the file, and does not claim to have.

FAIL otherwise, and name the first rule that was broken.
