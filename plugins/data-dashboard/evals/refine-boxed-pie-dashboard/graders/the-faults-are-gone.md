---
type: llm
focus: { source: file, path: dashboard/index.html }
weight: 2
---
You are reading the source of a sales dashboard after a redesign. The original had a large company logo in the top left; boxed panels with gradient blue title bars and drop shadows; four semicircular red, yellow, and green gauges for the KPIs; a pie of revenue by region with a legend; a region table with heavy black borders on every cell and red or green fills on the % of target column; product-line bars in five colors, in no order, with a legend and dashed gridlines; every amount to the cent; a refresh time to the second; and a page about 1,960 pixels tall.

PASS only if all of these hold in the new version:

1. No pie, no gauges, and no dials. Region revenue is compared on one shared scale, such as sorted bars or a graphical table against target, and the KPIs are shown against their targets as bullet graphs or similar.
2. Product-line bars are sorted by value, in one gray (or one gray with a single emphasized bar), labeled directly with no legend and no gridlines.
3. No boxed panels, colored title bars, shadows, or heavy table borders. White space and at most thin rules separate groups.
4. No red-and-green status fills. Saturated color, if any, marks only real exceptions, such as Middle East & Africa at 81% of target.
5. The logo is gone from the top left, or shrunk and moved out of the way.
6. Amounts are rounded to thousands or millions.
7. The layout is built to fit one laptop screen without scrolling.

FAIL otherwise, and name the first rule that was broken.
