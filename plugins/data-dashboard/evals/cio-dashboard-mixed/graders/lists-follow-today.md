---
type: llm
focus: { source: file, path: cio-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a CIO. Today is Friday, November 13, 2026. The data has six milestones, a queue of eight projects with priorities, and eight change-calendar events, of which the CIO wants the five top projects and the events in the next 14 days.

The right answers:

- Milestones, days until (+) or past (−) due: Budgeting system −13, data warehouse upgrade −3, ERP patch 4.2 +4, HR self-service portal +9, network refresh +25. The email migration milestone (due November 2) was completed October 30, so it is done, not past due; it may be shown as done or left off.
- Top five queued projects by priority: 1 Data warehouse capacity expansion, 2 Single sign-on for vendor portals, 3 Backup site failover test, 4 Laptop fleet refresh, 5 Help desk chatbot.
- Events in the next 14 days: November 14 generator test, November 17 ERP go-live, November 19 security audit, November 21 email cutover, November 24 holiday change freeze. Not the November 11 payroll patch (past), the December 2 board review, or the December 15 year-end support.

PASS if the page shows the milestones with days until or past due that match the list (computed in code or written into the data, either is fine), the five projects in priority order, and exactly the five events.

FAIL if a day count is wrong, the completed milestone is shown as past due, the projects are out of order or a different five, or an event outside the window appears or one inside it is missing. Name the first error.
