---
type: llm
focus: trace
weight: 3
---
The user asked for their freight flow map, `freight-map/index.html`, to be fixed, and said it looks like spaghetti and nobody can tell which way anything moves. The original drew each of 12 flows as a straight line between two points, so the three reciprocal pairs (Chicago and Indianapolis, Chicago and Detroit, Chicago and St. Louis) lay exactly on top of each other. It had no direction cue at all. It sized each center's circle with `circle-radius` equal to pallets divided by 250, so the radius, not the area, was proportional to the value: Chicago's 9,400 drew 37.6 px against Des Moines's 1,150 at 4.6 px, about 67 times the area for about 8 times the value.

Read the new page and the final reply.

PASS only if all of these hold:

1. Flows are drawn as curves, not straight two-point lines.
2. Each reciprocal pair is drawn as two separate lines that do not lie on top of each other.
3. Every flow shows its direction on the map itself, with an arrowhead or another explicit cue that stays visible on the thinnest flow.
4. Center circles are sized by area: the radius follows the square root of the value (or Flannery's 0.57 exponent), not the value itself.

FAIL otherwise, and name the first rule that was broken.
