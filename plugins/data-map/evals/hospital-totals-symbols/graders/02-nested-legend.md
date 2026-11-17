---
type: llm
focus: trace
weight: 2
---
The user asked for a map of staffed beds at each of 40 Minnesota hospitals. Beds run from 16 to 1,918, with most hospitals under 500.

Read the page the agent wrote under `bed-map/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. The legend shows at least 3 sample circles, each labeled with a bed count.
2. The sample circles are nested (drawn inside one another, sharing a base or a center) rather than set in a row.
3. Each sample circle is sized by the same scale the map uses, so a legend circle labeled 1,000 beds is as large as a 1,000-bed hospital's circle on the map.
4. The legend values are round numbers that span the data, such as 1,500, 500, and 100.

FAIL otherwise, and name the first rule that was broken.
