---
description: An existing MapLibre page of weekly pallets between 8 distribution centers, invoked with the slash command, to be fixed in place. Its 12 flows are straight two-point lines, so the three reciprocal pairs lie on top of each other, with no direction, and its centers are sized by radius. The refine must keep every flow and value, curve the flows with reciprocals apart, show direction, size the centers by area, and say what changed.
tags: [behavior, refine, flows]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

/data-map Our freight flow map at `freight-map/index.html` looks like spaghetti, and nobody can tell which way anything moves. Can you fix it? Keep it one HTML file at the same path, and tell me what you changed.
