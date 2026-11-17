---
type: llm
focus: trace
weight: 2
---
The user asked for their freight flow map to be fixed and to be told what changed. The original drew 12 flows as straight two-point lines, so the three reciprocal pairs through Chicago lay on top of each other; it gave no direction; and it scaled the center circles by radius instead of area.

Read the final reply to the user.

PASS only if all of these hold:

1. The reply names, in terms tied to this map, what changed for the straight and overlapping lines, for the missing direction, and for the radius-scaled circles.
2. Each of the three says what replaced it (for example "each flow now bends to its right, so Chicago to Detroit and Detroit to Chicago no longer overlap").
3. The reply says whether any flow or value was dropped, or says plainly that none was.

FAIL if the reply is generic ("cleaned up the map", "improved the styling"), misses one of the three, or drops a flow or value without saying so.
