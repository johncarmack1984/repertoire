---
description: A map of staffed beds at 40 Minnesota hospitals, invoked with the slash command. One hospital (1,918 beds) dominates inside a dense Twin Cities cluster. The map needs circles sized by area, a nested legend of at least 3 circles, the largest drawn first so the small ones stay visible, a sorted-bars companion, and no choropleth of the totals.
tags: [behavior, build, symbols]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

/data-map We need a map of staffed beds at every hospital in the state for the capacity chapter of our annual report. The survey data and notes are in `hospitals/`. Save it in `bed-map/`, with the page at `bed-map/index.html`.
