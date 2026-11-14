---
description: Raw interleaved runs of a build-script change, two profiles by three -j values, wall and CPU seconds. The numbers section should lead with the takeaway and its limit, put one configuration per row with the two variants side by side and a change column for each measure, keep units in the headers, and say below the table what was measured and how many runs.
tags: [behavior, table]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

I'm opening a PR for the build-script change on this branch: it runs the compiler feature probes once per build instead of once per source file. The raw timings are in `bench/` (`runs.csv`, with `NOTES.md` describing the setup). Write the performance section of the PR description to `pr-numbers.md`.
