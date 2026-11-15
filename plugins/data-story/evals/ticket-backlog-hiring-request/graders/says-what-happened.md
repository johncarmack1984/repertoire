---
type: llm
focus: { source: file, path: tickets.svg }
weight: 2
---
You are reading the source of an SVG chart. It goes on a one-page request asking a VP to approve hiring two people for an IT support team that lost two people in May 2014. The data was tickets received and tickets processed for each month of 2014. The team kept up through July, and from August on it processed fewer tickets than it received every month (46, 34, 35, 25, and 37 fewer).

PASS if words on the chart say what happened: that two people left in May, and that the team has been behind since, or by how much.

FAIL if the chart shows the two lines with no words explaining the gap between them.
