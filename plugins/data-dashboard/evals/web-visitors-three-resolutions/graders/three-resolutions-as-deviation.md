---
type: llm
focus: { source: file, path: web-analysis.html }
weight: 3
---
You are reading the source of an HTML analysis dashboard of web visitors, as of 2:00 PM on Friday, November 13, 2026. The analyst compares each month's average daily visitors with the same month a year earlier, each day this month with the average for the same weekday over the prior 13 weeks, and each hour today with the average for the same hour on Fridays over the prior 13 weeks. Computed from the data, the deviations are:

- Months, November 2025 to October 2026: +6, +9, +12, +10, +15, +18, +16, +21, +24, +22, +27, +31 percent. November 2026 to date is +19% over November 2025.
- Days, November 1 to 12: +3, −2, +4, +2, −3, +5, +1, −1, −30, −29, +2, −4 percent.
- Hours today, 00:00 to 13:00: +2, −3, +5, −1, +3, −4, +4, +8, +6, +3, −6, −38, −12, +1 percent.

PASS only if all of these hold:

1. Visitors appear at all three resolutions: by month for about the last 12 months, by day for this month so far, and by hour for today so far.
2. Each of the three is drawn as the percent deviation from its baseline around a 0% reference line, or as actual against baseline on one graph where the gap reads directly. Raw visitor counts alone, with no baseline, fail.
3. The values match the list above within a point or two, whether computed in code or written into the data. Using November 2026 to date as the twelfth month is fine.
4. The drops on November 9 and 10 and at 11:00 today can be seen on the graphs.

FAIL otherwise, and name the first rule that was broken.
