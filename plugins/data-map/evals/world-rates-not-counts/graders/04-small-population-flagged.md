---
type: llm
focus: trace
weight: 2
---
The user asked for a static world map of measles. The Falkland Islands reported 4 cases in a population of 3,398, a rate of 117.7 per 100,000. That is the highest rate in the data, but it rests on 4 cases, so it is not comparable with Kyrgyzstan's 96.4 from 6,224 cases. Apart from Greenland, which reported 0 cases among 56,225 people, every reporting country has more than 280,000 people.

Read the page the agent wrote under `measles-map/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. The Falklands' rate is flagged as unreliable or based on few cases, by a note or footnote on the page, a hatch or marker, a minimum-population rule shown on the page, or a caveat in the reply.
2. Neither the title nor the reply presents the Falklands as the place where measles is worst.
3. If the Falklands are left out of the classes or the map, the page or the reply says so and why.

FAIL otherwise, and name the first rule that was broken.
