---
type: llm
focus: { source: file, path: concerns.svg }
weight: 2
---
You are reading the source of an SVG chart. The data was ten design concerns for a car, in concerns per 1,000: engine power less than expected 12.9, tires make excessive noise 12.3, engine makes abnormal or excessive noise 11.6, seat material 11.6, excessive wind noise 11.0, hesitation when shifting 10.3, Bluetooth sound quality 10.0, steering play 8.8, Bluetooth difficult to use 8.6, front seat audio and navigation controls 8.2. Three of the ten are noise: tires, engine noise, and wind. The reader is a chief engineer deciding where engineering time goes, and the author wants noise first.

PASS if the most prominent text in the chart, the first or the largest, states the finding or the ask in words: three of the top ten are about noise, noise is the largest group, or fix noise first.

FAIL if the only title is a label such as "Top 10 design concerns".
