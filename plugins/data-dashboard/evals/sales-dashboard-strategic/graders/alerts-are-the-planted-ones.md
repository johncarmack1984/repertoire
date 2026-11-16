---
type: llm
focus: { source: file, path: sales-dashboard.html }
weight: 3
---
You are reading the source of an HTML dashboard for a wine distributor's VP of Sales. The data's notes set the company's rule. Against target, under 85% is poor, 85% up to 100% is satisfactory, and 100% or more is good. A region is in trouble for the quarter when its quarter-to-date revenue plus all of its open pipeline still falls short of its whole-quarter Q4 target. Anything poor or in trouble needs an alert, and satisfactory isn't news.

By that rule exactly these need an alert:

1. Profit YTD: $2,807,640 against $3,600,000, 78% of target.
2. Middle East revenue YTD: $1,281,644 against $1,600,000, 80% of target.
3. Asia for the quarter: $612,464 QTD plus $910,969 of pipeline reaches 93% of its $1,636,000 Q4 target.
4. Middle East for the quarter: $182,136 QTD plus $362,683 of pipeline reaches 87% of its $623,000 Q4 target.
5. Merlot revenue YTD: $2,159,874 against $3,000,000, 72% of target.

Nothing else crosses the rule. The other six key metrics run 96% to 103% of target, and total revenue is 99%. Asia's YTD revenue is 95% of target, which is satisfactory. North America, Europe, and South America reach 108%, 105%, and 111% of their Q4 targets with pipeline. The other four wines are 101% to 105% of their revenue targets, and every wine's cases are at 92% of target or better, Merlot's included. QTD revenue alone is 29% to 43% of the Q4 target in every region only because the quarter is six weeks old, and that is not an exception.

The page may set alerts in several ways: a library may draw alert dots from the values and an alert policy in a JSON data block, a row may carry an explicit state, or alert styling may be written by hand. Work out from the source which rows the page marks as alerts.

PASS if the page marks all five and nothing else. The Middle East marked once for YTD and once for the quarter is correct.

FAIL if any of the five is unmarked, if Asia's YTD revenue is marked, if a region is marked only because its QTD revenue is under the Q4 target, or if anything else is marked. Name what was missed or marked wrongly.
