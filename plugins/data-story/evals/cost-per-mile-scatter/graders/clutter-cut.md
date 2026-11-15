---
type: llm
focus: { source: file, path: fleet.svg }
weight: 1
---
You are reading the source of an SVG scatterplot of 34 delivery vans, miles driven a month against cost per mile.

PASS if there is no border drawn around the plot, gridlines are absent or thin and light grey, and there is no legend box: anything the colors mean is said in a title, a subtitle, or a label beside the points. Axis values with one consistent precision, such as "$0.50", "$1.00", and "$1.50", are fine.

Otherwise FAIL.
