---
type: llm
focus: trace
weight: 2
---
The user asked for an interactive web map of October trips between 20 bike-share stations. Trips run both ways between every pair, and many pairs are lopsided: Union Station to South Waterfront carries 1,486 trips, with 297 back.

Read the page the agent wrote under `trip-flows/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Every drawn flow shows its direction on the map itself, with an arrowhead or another explicit cue such as a half-arrow or a taper that the legend explains.
2. The cue stays visible on the thinnest drawn flows; for example, arrowheads have a minimum size rather than shrinking in proportion to the line.

A color gradient along the line with no legend, or direction given only in a tooltip, fails.

FAIL otherwise, and name the first rule that was broken.
