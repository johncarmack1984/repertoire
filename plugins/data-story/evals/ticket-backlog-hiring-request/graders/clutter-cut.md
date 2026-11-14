---
type: llm
focus: { source: file, path: tickets.svg }
weight: 1
---
You are reading the source of an SVG chart. It goes on a one-page request asking a VP to approve hiring two people for an IT support team that lost two people in May 2014. The data was tickets received and tickets processed for each month of 2014. The team kept up through July, and from August on it processed fewer tickets than it received every month (46, 34, 35, 25, and 37 fewer).

PASS if there is no border drawn around the plot, gridlines are absent or thin and light grey, there is no marker on every data point, and the month labels are horizontal and abbreviated.

Otherwise FAIL.
