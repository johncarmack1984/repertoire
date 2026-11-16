---
type: llm
focus: trace
weight: 3
---
The user asked for an interactive web map of October trips between 20 bike-share stations. All 380 ordered pairs have at least one trip, 20,599 trips in all. The tail is long: the median pair has 13 trips, and 155 pairs have fewer than 10. Drawing all 380 makes a hairball.

The share of all trips that the largest N flows carry, with the smallest flow kept at that N:

- top 5: 18.5% of trips (smallest kept flow 535)
- top 10: 30.1% of trips (smallest kept flow 417)
- top 15: 38.2% of trips (smallest kept flow 302)
- top 20: 45.2% of trips (smallest kept flow 267)
- top 25: 50.8% of trips (smallest kept flow 220)
- top 30: 55.4% of trips (smallest kept flow 185)
- top 40: 63.0% of trips (smallest kept flow 144)
- top 50: 69.1% of trips (smallest kept flow 105)
- top 60: 73.7% of trips (smallest kept flow 86)
- top 75: 78.8% of trips (smallest kept flow 58)
- top 100: 84.7% of trips (smallest kept flow 38)
- top 150: 91.5% of trips (smallest kept flow 21)
- top 200: 95.5% of trips (smallest kept flow 12)

Read the page the agent wrote under `trip-flows/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. The map, as it first opens, draws only the largest flows, not all 380. A control that lets the reader show more is fine.
2. The page itself, not only the reply, states how many flows are drawn and what share of all trips they carry (or how many are left out and their share).
3. The stated share is within one percentage point of the true share for the cut the page makes. When the cut is a threshold, use the smallest kept flow above to find N.

FAIL otherwise, and name the first rule that was broken.
