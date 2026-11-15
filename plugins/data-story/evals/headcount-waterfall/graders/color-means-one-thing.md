---
type: llm
focus: { source: file, path: headcount.svg }
weight: 1
---
You are reading the source of an SVG waterfall chart of a year of headcount: a start, two additions (hires, transfers in), two losses (transfers out, exits), and an end.

PASS if color is used sparingly: the bars use at most two colors that carry meaning (for example one for the totals and one accent for the step the title is about, with the rest grey), and additions and losses are told apart by direction and signed labels rather than by red against green alone.

FAIL if red and green are the only way to tell additions from losses, or if every bar has its own color.
