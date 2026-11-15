---
description: Few's chapter 8 sales dashboard rebuilt from CSVs, invoked with the slash command. The page should be one self-contained screen built from the library, with the seven key metrics top left as a graphical table against target. It should alert exactly profit, the Middle East YTD, Asia and the Middle East for the quarter (all pipeline still short of target), and Merlot, and leave Asia's 95% YTD alone.
tags: [behavior, build, book-example]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

/data-dashboard Our VP of Sales wants one screen she can check every morning to see how sales are going and where she needs to step in. The data is in `sales/`, and `sales/NOTES.md` explains the files and how we judge good and bad. Save it as `sales-dashboard.html` in this folder.
