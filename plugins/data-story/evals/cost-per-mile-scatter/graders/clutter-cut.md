---
type: llm
focus: { source: file, path: fleet.svg }
weight: 1
---
You are reading the source of an SVG scatterplot of 34 delivery vans, miles driven a month against cost per mile.

PASS if there is no border drawn around the plot, gridlines are absent or thin and light grey, there is no legend box for the single series of vans, and the axis values carry no needless trailing zeros (such as "$2.00" where "$2" would do).

Otherwise FAIL.
