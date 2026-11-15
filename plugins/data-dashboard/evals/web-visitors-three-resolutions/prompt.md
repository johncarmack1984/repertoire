---
description: Few's chapter 8 web marketing analysis dashboard rebuilt from CSVs for an analyst who wants no alerts. Visitors should appear at three resolutions (months against the prior year, days against the 13-week weekday average, hours against the 13-week same-hour average), each as a deviation from a zero line. The page should mark nothing as an alert, even the 30% daily drops and the 38% hourly drop, and should compare products' revenue share with their view share on one scale.
tags: [behavior, build, book-example]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

I'm the web marketing analyst here, and I want a dashboard for digging into our site traffic: how visitors are running by month, by day, and by hour compared with what's normal, which products people look at versus buy, and where our referrals come from. The data is in `web/`, and `web/NOTES.md` explains it. Put it in `web-analysis.html`.
