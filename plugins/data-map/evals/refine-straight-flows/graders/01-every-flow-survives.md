---
type: llm
focus: { source: file, path: freight-map/index.html }
weight: 3
---
You are reading the source of a freight flow map after a redesign. The original showed 12 flows of pallets per week between 8 distribution centers, and pallets handled per week at each center. The redesign must keep every one of them with its value. Moving the numbers into a JSON or GeoJSON block that the page draws from is fine, and so is a different property name.

The flows: Chicago to Indianapolis 2,140; Indianapolis to Chicago 610; Chicago to Detroit 1,580; Detroit to Chicago 1,420; Chicago to St. Louis 1,760; St. Louis to Chicago 390; Milwaukee to Chicago 980; Indianapolis to Columbus 870; Detroit to Columbus 1,130; St. Louis to Kansas City 1,290; Kansas City to Des Moines 640; Des Moines to Chicago 450.

The centers: Chicago 9,400; Milwaukee 2,300; Indianapolis 4,100; Columbus 3,200; Detroit 3,600; St. Louis 3,900; Kansas City 2,700; Des Moines 1,150.

PASS only if all of these hold:

1. All 12 flows are still on the page, each with its direction (from and to) and its exact value.
2. All 8 centers are still on the page, each with its exact value.
3. No flow or center was added.

FAIL otherwise, and name what is missing, changed, or added.
