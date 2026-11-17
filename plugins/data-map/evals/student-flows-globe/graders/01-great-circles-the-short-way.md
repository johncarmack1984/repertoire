---
type: llm
focus: trace
weight: 3
---
The user asked for an interactive globe of international student flows between 40 countries, 300 pairs in all. On their great circles, 31 of those pairs cross the 180th meridian. They include the largest flow, China to the United States (288,400 students), India to Canada (101,700), China to Canada (58,200), and all eight Pacific pairs between Australia or New Zealand and the United States or Canada: Australia to the United States 4,870 and back 7,310; New Zealand to the United States 1,640 and back 2,280; Australia to Canada 1,150 and back 2,960; New Zealand to Canada 540 and back 610.

A line given only its two end points, from China (106.3, 32.5) to the United States (-97.5, 39.5), is interpolated in longitude by MapLibre and by most line layers, so it runs west across Asia, Europe, and the Atlantic: the long way round. deck.gl's ArcLayer with `greatCircle: true`, or a great-circle layer, draws the short way. So do coordinates densified along the great circle, either split into a MultiLineString at ±180 or carrying longitudes past 180.

Read the page the agent wrote under `student-globe/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Every drawn flow follows its great circle, by densified coordinates or by a layer that draws great circles.
2. No flow that crosses the 180th meridian runs the long way round. China to the United States and the Pacific pairs cross the Pacific.

FAIL otherwise, and name the first flow or rule that was broken.
