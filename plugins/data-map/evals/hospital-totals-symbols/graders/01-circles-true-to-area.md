---
type: llm
focus: trace
weight: 3
---
The user asked for a map of staffed beds at each of 40 Minnesota hospitals, 8,060 beds in all. Riverside University Hospital in Minneapolis has 1,918 beds; the next largest, St. Paul Regional Medical Center, has 612; the smallest, Austin Cedar Hospital, has 16. Beds are totals at points, so they call for proportional symbols. Under area scaling, the radius grows with the square root of the value, and Riverside's circle has 10.9 times the smallest one's radius. Scaling the radius in proportion to the value would make it about 120 times, so Riverside's circle would have about 14,370 times the smallest one's area instead of about 120 times.

Read the page the agent wrote under `bed-map/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Each hospital is a point symbol, a circle or similar, sized by its staffed beds.
2. Symbol area, not radius, is proportional to beds: the radius follows the square root of the value (or Flannery's 0.57 exponent, or a few range-graded sizes with a legend that says so). In MapLibre, a `circle-radius` that interpolates linearly on the raw bed count is radius scaling and fails; one built on `["sqrt", ...]` passes.
3. No area is shaded by bed totals: no choropleth of counties or regions by the number of beds.

FAIL otherwise, and name the first rule that was broken.
