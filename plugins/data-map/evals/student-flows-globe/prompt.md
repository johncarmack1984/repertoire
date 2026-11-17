---
description: An interactive globe of international student flows between 40 countries (300 pairs), invoked with the slash command, for a client who wants it to look impressive in 3D. The largest flow (China to the United States) and every Pacific pair between Australia or New Zealand and the United States or Canada cross the 180th meridian. The globe needs great circles with none going the long way round, a stated top-N cut, a ranked companion, and raised arcs only with height tied to distance and a stated reason.
tags: [behavior, build, flows, globe]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

/data-map Our client, an education consultancy, wants an interactive globe of where international students go to study, for their website. The data and notes are in `students/`. They've asked for it to "look impressive in 3D". Save it in `student-globe/`, with the page at `student-globe/index.html`.
