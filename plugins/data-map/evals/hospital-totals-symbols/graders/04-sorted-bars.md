---
type: llm
focus: trace
weight: 2
---
The user asked for a map of staffed beds at each of 40 Minnesota hospitals for the capacity chapter of an annual report. Circle sizes show the pattern but can't be read precisely: Riverside University Hospital has 1,918 beds, St. Paul Regional Medical Center 612, and Hennepin Avenue Medical Center 486.

Read the page the agent wrote under `bed-map/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Beside the map, the page shows a bar chart of staffed beds by hospital, sorted from most to fewest. It may show every hospital, or the largest ones with a note of how many are left out.
2. The bars' values agree with the data above.

A sorted table with a bar in each row passes. A plain table or an unsorted list fails.

FAIL otherwise, and name the first rule that was broken.
