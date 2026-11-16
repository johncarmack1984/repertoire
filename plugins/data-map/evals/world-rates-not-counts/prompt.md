---
description: A static world figure of measles for a newsletter, invoked with the slash command. The data gives cases and population, so the map must show a rate on an equal-area projection, in 3 to 7 classes fit to strongly skewed data, with no data set apart, the Falklands' rate from 4 cases flagged, legend limits equal to the breaks, a title that states the pattern, and a source line.
tags: [behavior, build, choropleth]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

/data-map I need the lead figure for our December newsletter: a world map of measles this year. The data and our notes are in `data/`. It goes out as a static image, so build it as a page I can open and screenshot. Put everything in `measles-map/`, with the page at `measles-map/index.html`.
