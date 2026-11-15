---
type: llm
focus: { source: file, path: headcount.svg }
weight: 2
---
You are reading the source of an SVG chart for a VP of Engineering who asked why her headcount went up when people kept transferring out. The data: 100 people on 1 January, 30 hires, 8 transfers in, 12 transfers out, 10 exits, 116 on 31 December.

PASS if the most prominent text in the chart, the first or the largest, answers her question in words: that headcount grew (by 16%, or from 100 to 116) because hiring outpaced the transfers out and the exits. A plain label for what is plotted may appear as well, smaller.

FAIL if the only title names what is plotted, such as "Headcount" or "2014 headcount", or if the text claims something the numbers don't show, such as more transfers in than out.
