---
type: llm
focus: trace
weight: 2
---
The user asked for a map of staffed beds at each of 40 Minnesota hospitals. Riverside University Hospital (1,918 beds) sits inside a dense Twin Cities cluster of 16 hospitals within 30 km of each other. Its nearest neighbors are Hennepin Avenue Medical Center (486 beds) at 2.4 km and Lake Street Hospital (118 beds) at 3.5 km. Drawn last, Riverside's circle would cover them.

Read the page the agent wrote under `bed-map/`, any data files it prepared for the page, and its final reply.

PASS if the page draws the largest circles first and the smallest last, so that small circles sit on top, by any means: features sorted from largest to smallest before drawing, a sort key that puts small values on top (in MapLibre, a `circle-sort-key` that rises as the bed count falls), or separate layers ordered by size. Transparency or outlines may be added, but they don't replace the order.

FAIL if large circles are drawn over small ones, or if the drawing order is left to the order of the source file. Quote the code that sets the order, or say that none does.
