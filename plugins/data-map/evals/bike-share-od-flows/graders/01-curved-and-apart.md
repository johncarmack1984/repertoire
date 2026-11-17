---
type: llm
focus: trace
weight: 3
---
The user asked for an interactive web map of October trips between 20 bike-share stations in Portland. Every ordered pair of stations has trips in both directions, so each drawn pair has a reciprocal. The largest flow is Union Station to South Waterfront (OHSU Commons), 1,486 trips, with 297 back. Sellwood (S20) to Lloyd Center (S10) has 655 trips and 588 back, and the Brooklyn station (S12, SE Milwaukie & Holgate) sits exactly on the straight segment between them, 42% of the way from Sellwood. No other station is within 600 m of that segment.

Read the page the agent wrote under `trip-flows/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. Flows are drawn as curves, not as straight two-point lines.
2. A flow and its reciprocal are drawn as two separate lines that do not lie on top of each other, for example by bending each to the right of its direction of travel, or by offsetting them. Merging each pair into one net flow also passes if the page says so and gives both directions' counts in its tooltip or companion.
3. The flows between Sellwood and Lloyd Center do not run straight through the Brooklyn station: they are curved or routed so that they visibly clear its symbol.

FAIL otherwise, and name the first rule that was broken.
