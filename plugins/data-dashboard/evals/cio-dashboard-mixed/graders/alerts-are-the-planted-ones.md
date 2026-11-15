---
type: llm
focus: { source: file, path: cio-dashboard.html }
weight: 3
---
You are reading the source of an HTML dashboard for a CIO. The data's notes set IT's rules: a system not `up` right now is critical; 30-day availability below a system's acceptable level is a warning, and more than 2 points below is critical; hardware 70% to 85% used is a warning; an open milestone past due is a warning, and more than 7 days past due is critical. Today is November 13, 2026.

By those rules exactly these need an alert:

1. Data Warehouse, critical: 93.2% available over 30 days against an acceptable 97.0% (3.8 points under), and down right now since 2:50 PM. It may be marked in a "now" strip, in the availability row, or both.
2. Network, warning: 98.6% against 99.0%.
3. ERP, warning: 97.9% against 98.5%.
4. CPU, warning: 79% used.
5. Budgeting system milestone (vendor contract signed), critical: due October 31, open, 13 days past due.
6. Data warehouse upgrade milestone (cutover rehearsal), warning: due November 10, open, 3 days past due.

Nothing else crosses a rule. Web Site (99.4% against 99.0%), Email (99.7% against 99.5%), HR (96.7% against 95.0%), and Problem Tracking (94.7% against 94.0%) meet their levels. Storage is 63% used. Every system has 90% or more of today's response-time samples within its limit (Data Warehouse 28 of 30, ERP 29 of 30). Expenses are 96% of the YTD budget, satisfaction is 3.52 against a 3.50 target, and level 1 problems are 87 against a limit of 110. The email migration milestone was due November 2 but was completed October 30, and the ERP milestone is due in 4 days, so neither is past due.

The page may set alerts in several ways: a library may draw alert dots from the values and an alert policy in a JSON data block, a row may carry an explicit state, or alert styling may be written by hand. Work out from the source which items the page marks.

PASS if the page marks all six and nothing else, and critical items are visibly stronger than warnings (a more intense color, or a different marker).

FAIL if any of the six is unmarked, if anything else is marked, or if critical and warning look the same. Name what was missed or marked wrongly.
