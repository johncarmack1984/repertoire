---
description: An interactive web map of October trips between 20 bike-share stations, asked for in plain words, so the skill must fire on its own. All 380 ordered pairs are nonzero. The map needs curved flows with reciprocals apart, a direction cue, Sellwood to Lloyd Center clear of Brooklyn (which sits on their straight line), a stated top-N cut, a 3 to 4 width legend, small flows on top, a ranked or matrix companion, and exact-value tooltips.
tags: [behavior, build, flows, invocation]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

Our planning team wants to see where people ride between our stations. Can you make them an interactive web map of October's trips? The data and notes are in `bike-data/`. Save it in `trip-flows/`, with the page at `trip-flows/index.html`; they'll open it in a browser.
