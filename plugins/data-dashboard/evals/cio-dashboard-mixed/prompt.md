---
description: Few's chapter 8 CIO dashboard rebuilt from CSVs, asked for in plain words with no slash command, so the description has to bring the skill in. The page should show availability against each system's acceptable level on a scale that makes small gaps visible, response times as distributions, yesterday's network traffic against two means, and milestones with days past due counted from today. It should alert exactly the Data Warehouse (critical), Network and ERP (warnings), CPU (warning), and the two late milestones (13 days critical, 3 days warning).
tags: [behavior, build, invocation, book-example]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

Can you build our CIO's dashboard? She keeps it open all day and wants to see at a glance how IT is doing: the systems, hardware capacity, the network, response times, the budget, and our projects. Everything is in `it/`, and `it/NOTES.md` explains each file and what counts as a problem. Save it as `cio-dashboard.html` here.
