---
type: llm
focus: trace
weight: 2
---
The user asked for an interactive globe of international student flows for a consultancy's website, where prospective students and their parents will land. A globe shows only one side of the Earth at a time, so a reader can't compare flows on opposite sides at a glance. The largest flows are China to the United States (288,400), India to the United States (271,900), China to the United Kingdom (154,300), India to the United Kingdom (112,600), and India to Canada (101,700).

Read the page the agent wrote under `student-globe/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Beside the globe, the page shows a ranked view of the flows: a sorted list, a table, or bars of the largest flows, or ranked lists of the top destinations and origins.
2. The ranked view's numbers agree with the data above.
3. Hovering or clicking a flow on the globe shows its origin, its destination, and its exact number of students.

FAIL otherwise, and name the first rule that was broken.
