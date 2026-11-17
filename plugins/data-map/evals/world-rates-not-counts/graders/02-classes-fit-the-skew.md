---
type: llm
focus: trace
weight: 3
---
The user asked for a static world map of measles. The rates per 100,000 people are strongly right-skewed: skewness 4.7 across the 172 reporting countries, a median of 2.23, and a maximum of 117.7. Belize and Greenland reported 0 cases. Equal intervals over this range would put almost every country in the lowest class.

Read the page the agent wrote under `measles-map/`, any data or legend files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. The map is classed, with 3 to 7 classes for the data. A separate no-data class does not count toward that number. An unclassed continuous ramp fails.
2. The classing method is not equal intervals. It fits the skew: quantiles, natural breaks (Jenks or Fisher), head/tail breaks, geometric or logarithmic intervals, or hand-picked breaks with a stated reason.
3. The method is named, on the page or in the reply.
4. Each legend entry's limits are the same numbers as the thresholds the page's color code uses, with no gaps and no overlaps between neighboring classes.
5. No class is empty.

FAIL otherwise, and name the first rule that was broken.
