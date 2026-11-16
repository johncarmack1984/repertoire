---
type: llm
focus: trace
weight: 3
---
The user asked for a map of four sales regions' quarter-over-quarter growth for a board deck. From `sales/regional_revenue.csv`, Q2 to Q3 2026 growth is West +12.4%, Midwest +7.9%, Northeast +3.1%, and South −2.6%. Four numbers whose message is how the regions compare, not where they are, read best as sorted bars or a short table. On a map, each region's color would be judged against its land area, and the West's size would dominate.

Read every file the agent wrote and its final reply.

PASS only if all of these hold:

1. The agent made no map in any form: no regions or states drawn on a basemap or outline, no choropleth, no symbols at region centers, no cartogram.
2. It made a bar chart of the four growth rates sorted from highest to lowest, with the South's decline drawn below a zero baseline, or a table sorted the same way.
3. The values agree with the four above, within rounding.
4. The reply tells the user, in a sentence or two, why a map would add nothing here.

FAIL otherwise, and name the first rule that was broken.
