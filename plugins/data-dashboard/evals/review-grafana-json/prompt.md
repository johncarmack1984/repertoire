---
description: A review of a Grafana service-health dashboard, asked for in plain words, with the file left untouched. The reply should mark the pie, the four gauges, and the red and green status coloring, each with a concrete fix, and should put no mark on the p95 latency panel, which is already done well.
tags: [behavior, review, invocation]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill]
---

I'm about to share our service health dashboard with the on-call rotation. The export is `grafana/service-health.json`. Can you look it over and tell me what to change first? Don't edit the file; I'll make the changes in Grafana myself.
