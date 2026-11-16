---
type: llm
focus: trace
weight: 2
---
The user asked for an interactive web map of October trips between 20 bike-share stations. Downtown flows cross and crowd each other, and the largest (1,486 trips) is several times wider than most.

Read the page the agent wrote under `trip-flows/`, any data files it prepared for the page, and its final reply.

PASS if the page draws smaller flows above larger ones, by any means: the features sorted from largest to smallest before drawing, a sort key that puts small values on top (in MapLibre, a `line-sort-key` that rises as the value falls), or separate layers ordered by size.

FAIL if large flows are drawn over small ones, or if the drawing order is left to the order of the source file. Quote the code that sets the order, or say that none does.
