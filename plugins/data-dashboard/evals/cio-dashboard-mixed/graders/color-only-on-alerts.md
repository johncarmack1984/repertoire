---
type: llm
focus: { source: file, path: cio-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a CIO, kept open all day. Six items need attention: the Data Warehouse (critical), Network and ERP (warnings), CPU (warning), and two late milestones (one critical, one warning).

PASS only if all of these hold:

1. Saturated color is used only to mark those alerts, in at most two intensities of one hue (one for critical, one for warning).
2. Everything else is drawn in grays, with at most one muted accent for the title and section headings.
3. There is no green for good status, no red-and-green pair, no traffic lights, and no distinct color per system or per series.
4. The page is not split into boxed panels with colored title bars or drop shadows. One bordered strip for the live "now" status is fine.

Colors written in a stylesheet, in inline styles, or as design tokens all count. Colors used only inside an inlined drawing library's code for alert states also count as alert color.

FAIL otherwise, and name the color or element and where it is used.
