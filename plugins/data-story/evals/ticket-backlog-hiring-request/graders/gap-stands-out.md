---
type: llm
focus: { source: file, path: tickets.svg }
weight: 2
---
You are reading the source of an SVG chart. It goes on a one-page request asking a VP to approve hiring two people for an IT support team that lost two people in May 2014. The data was tickets received and tickets processed for each month of 2014. The team kept up through July, and from August on it processed fewer tickets than it received every month (46, 34, 35, 25, and 37 fewer).

PASS if both series are drawn as lines across the twelve months (polyline or path elements) and the gap that opens in the second half of the year is what stands out: for example one accent color or a heavier stroke on one line or on that stretch, shading between the two lines, or value labels on only those months or on the gap itself.

FAIL if the series are drawn as bars, if every point of both series has a value label, or if the two series are simply two bright colors with nothing else emphasized.
