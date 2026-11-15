---
type: llm
focus: { source: file, path: dashboard/index.html }
weight: 3
---
You are reading the source of a sales dashboard after a redesign. The original showed these numbers, all quarter to date, and the redesign must keep every one of them. Rounding is expected and fine ($4.18M, $4,182K, 94.4%, 4.2), and so is moving a number into a JSON data block that the page draws from.

- Revenue by region, with targets: North America $4,182,377.45 of $4,050,000; Europe $2,946,105.18 of $3,100,000; Asia Pacific $1,873,662.90 of $1,950,000; Latin America $812,419.37 of $780,000; Middle East & Africa $455,231.64 of $560,000. Total $10,269,796.54 of $10,440,000.
- Revenue by product line: Hardware $3,104,882.12; Support $3,019,690.60; Software $2,215,903.77; Services $1,488,320.05; Training $441,000.00.
- KPIs with targets: on-time delivery 94.37% (target 95%); customer satisfaction 4.21 of 5 (target 4.30); gross margin 31.84% (target 33%); order fill rate 97.12% (target 98%).

PASS if every region's revenue and target, every product line's revenue, and every KPI's value and target are still on the page, in any rounding, and each region and each KPI is still shown against its target. Dropping the separate total row is fine if the page can still be read for the total, or if the reply says it was dropped and why.

FAIL if any of those numbers is missing, if a value is changed beyond rounding, or if a KPI or region has lost its target. Name what is missing or wrong.
