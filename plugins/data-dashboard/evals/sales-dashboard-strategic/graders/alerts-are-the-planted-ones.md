---
type: llm
focus: last_message
weight: 3
---
What follows is the agent's final reply after building a sales dashboard for a wine distributor's VP of Sales. The company's rule: under 85% of target is poor and needs an alert, and a region needs an alert for the quarter when its quarter-to-date revenue plus all of its open pipeline still falls short of its Q4 target. By that rule exactly five things are flagged: profit (78% of target), Middle East revenue for the year (80%), Asia for the quarter (93% of its Q4 target even with all pipeline), Middle East for the quarter (87% even with all pipeline), and Merlot revenue (72%).

PASS if the reply says the page flags those five and nothing else. The Middle East counts once for the year and once for the quarter. Mentioning Asia's year-to-date revenue (95%) as satisfactory or not flagged is fine.

FAIL if the reply leaves one of the five out of what it says is flagged, says anything else is flagged (such as Asia's year-to-date revenue, a wine's cases, or a region only because its quarter-to-date revenue is under the Q4 target), or doesn't say what is flagged.
