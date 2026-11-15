---
type: llm
focus: { source: file, path: concerns.svg }
weight: 2
---
You are reading the source of an SVG chart. The data was ten design concerns for a car, in concerns per 1,000: engine power less than expected 12.9, tires make excessive noise 12.3, engine makes abnormal or excessive noise 11.6, seat material 11.6, excessive wind noise 11.0, hesitation when shifting 10.3, Bluetooth sound quality 10.0, steering play 8.8, Bluetooth difficult to use 8.6, front seat audio and navigation controls 8.2. Three of the ten are noise: tires, engine noise, and wind. The reader is a chief engineer deciding where engineering time goes, and the author wants noise first.

PASS if the concerns are horizontal bars (rect elements whose width varies) that start from one shared x, with widths in proportion to their values, so a bar for 8.2 is roughly two thirds the width of a bar for 12.9, and the bars run from the largest at the top to the smallest at the bottom. Related concerns may be combined into one bar with labelled segments, such as one bar for the three noise concerns; a combined bar counts as one bar, placed by its total.

FAIL if the bars are vertical, if they are not in order of size, if they are cut off to exaggerate differences, or if a concern from the list is missing altogether.
