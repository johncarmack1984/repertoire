---
type: llm
focus: { source: file, path: tickets.svg }
weight: 2
---
You are reading the source of an SVG chart. It goes on a one-page request asking a VP to approve hiring two people for an IT support team that lost two people in May 2014. The data was tickets received and tickets processed for each month of 2014. The team kept up through July, and from August on it processed fewer tickets than it received every month (46, 34, 35, 25, and 37 fewer).

PASS if the most prominent text in the chart, the first or the largest, states the request or the conclusion in words: approve or hire two people, or that the team has been behind since the two left. A label for what is plotted, such as "Ticket volume over time", may appear as well.

FAIL if the only title is a label for what is plotted, such as "Ticket trend" or "Ticket volume over time".
