---
type: llm
focus: trace
weight: 2
---
The user asked for an interactive web map of October trips between 20 bike-share stations. Flow sizes run from 1,486 trips (Union Station to South Waterfront) down to single trips.

Read the page the agent wrote under `trip-flows/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Line width encodes the number of trips.
2. The legend shows 3 or 4 sample line widths, each labeled with its trip count.
3. The sample widths come from the same scale the map uses, so a legend line labeled with a value is as wide as a flow of that value on the map.
4. The legend names the unit (trips in October 2026, or similar).

FAIL otherwise, and name the first rule that was broken.
