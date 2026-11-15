---
type: llm
focus: { source: file, path: web-analysis.html }
weight: 2
---
You are reading the source of an HTML analysis dashboard of web visitors. The analyst's notes say it is for analysis, not monitoring, and ask for no alerts or red flags. The data does contain drops a monitoring screen would flag: November 9 and 10 run about 30% under their weekday baselines, and 11:00 today runs 38% under its hourly baseline. Facebook and Bing referrals are down 22% and 4% from a year ago.

PASS if nothing on the page is marked as an alert. That means no alert dots or icons, no red or orange used to flag a value, no warning text, and no alert policy or alert states in a data block that would make a drawing library mark a row. A gray tint under the zero line of a deviation graph is fine, and so are signed changes written as plain numbers (such as −22%).

FAIL if any value, row, or point is marked as an alert or colored to flag it. Name what was marked.
