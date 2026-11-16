---
type: llm
focus: trace
weight: 2
---
The user asked for an interactive web map of October trips between 20 bike-share stations, for a planning team deciding where to add docks and where to rebalance bikes. The largest flow is Union Station to South Waterfront (OHSU Commons), 1,486 trips, with 297 back.

Read the page the agent wrote under `trip-flows/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Beside the map, the page shows a companion view of the flows: a ranked list or bar chart of the largest flows, or an origin-destination matrix.
2. Hovering or clicking a flow shows its origin, its destination, and its exact trip count.

FAIL otherwise, and name the first rule that was broken.
