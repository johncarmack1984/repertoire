---
type: llm
focus: trace
weight: 2
---
The user asked for a static world map of measles. In `data/measles_2025.csv`, North Korea, Eritrea, and Turkmenistan have a blank case count, which the notes define as "did not report", not zero. Belize and Greenland reported 0 cases, which is a real value. Antarctica and the French Southern and Antarctic Lands have no row because nobody lives there.

Read the page the agent wrote under `measles-map/`, any data or legend files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. North Korea, Eritrea, and Turkmenistan are drawn in a fill, pattern, or hatch that no data class uses.
2. The legend has an entry for that fill, such as "No data" or "Not reported".
3. Belize and Greenland fall in the lowest data class, not in the no-data style.

Antarctica and the French Southern lands may be drawn in the no-data style, in a neutral fill, or left off the map.

FAIL otherwise, and name the first rule that was broken.
