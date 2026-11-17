---
type: llm
focus: trace
weight: 3
---
The user's client asked for a globe of international student flows that will "look impressive in 3D". A globe is a fair answer for flows at world scale. Beyond the globe itself, 3D earns its place only when it carries meaning. Raised arcs can help untangle crossing flows if each arc's height comes from its length, so long flows rise higher and the height never competes with the line width that encodes the number of students. In deck.gl's ArcLayer, `getHeight` multiplies each arc's own length, so a constant `getHeight` ties height to distance, and a `getHeight` computed from the student count ties it to value.

Read the page the agent wrote under `student-globe/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. If flows are raised above the surface, their height comes from distance only, never from the number of students.
2. If flows are raised, the page or the reply states why raised arcs were used.
3. Nothing else is extruded or tilted for effect: no 3D columns or extruded countries sized by students, and no pitched camera without a stated reason.

Flat flows on the globe pass rules 1 and 2.

FAIL otherwise, and name the first rule that was broken.
