---
type: llm
focus: { source: file, path: tickets.svg }
weight: 1
---
You are reading the source of an SVG chart. It goes on a one-page request asking a VP to approve hiring two people for an IT support team that lost two people in May 2014. The data was tickets received and tickets processed for each month of 2014. The team kept up through July, and from August on it processed fewer tickets than it received every month (46, 34, 35, 25, and 37 fewer).

PASS if each of the two lines is labelled by name ("Received", "Processed") with text placed at or beside the line, and there is no separate legend: no row or box of color swatches with the series names, apart from the lines.

FAIL if the series are identified by a legend, or by a legend as well as labels beside the lines.
