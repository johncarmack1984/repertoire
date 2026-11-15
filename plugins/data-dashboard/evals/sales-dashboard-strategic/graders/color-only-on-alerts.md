---
type: llm
focus: { source: file, path: sales-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a wine distributor's VP of Sales. Five things need her attention (profit, the Middle East YTD, Asia and the Middle East for the quarter, and Merlot), and nothing else does.

PASS only if all of these hold:

1. Saturated color (a strong red, orange, or similar) is used only to mark alerts.
2. Everything else is drawn in grays, with at most one muted accent for the title and section headings.
3. There is no green for good status, no red-and-green pair, no traffic lights, and no distinct color per series, region, or product. Our company may be set apart from competitors by a darker gray.
4. The title is quiet: muted or light, not the loudest thing on the page.

Colors written in a stylesheet, in inline styles, or as design tokens all count. Colors used only inside an inlined drawing library's code for alert states also count as alert color.

FAIL otherwise, and name the color and where it is used.
