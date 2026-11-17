---
type: llm
focus: trace
weight: 3
---
The user asked for a static world map of measles for a newsletter. `data/measles_2025.csv` gives each country's cases and population, and 172 countries reported. Counts mostly follow population. India has the most cases, 62,855, but a rate of only 4.6 per 100,000, 56th of 172. Nigeria is second with 35,057 cases. By rate, Kyrgyzstan leads the populous countries at 96.4 per 100,000 (6,224 cases), ahead of Kazakhstan at 61.0 and Tajikistan at 54.0.

Read the page the agent wrote under `measles-map/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. The color of each country encodes a rate: cases divided by population, per 100,000, per million, or another per-person unit.
2. Raw case counts are not what the color encodes. Counts may appear in a tooltip, a label, or a table beside the map.
3. The legend or the title names the rate's unit, such as "cases per 100,000 people".

FAIL otherwise, and name the first rule that was broken.
