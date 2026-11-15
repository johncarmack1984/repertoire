#!/usr/bin/env bash
# Cost per mile against miles driven, from Storytelling with Data (chapter 2's scatterplot): the
# vans driven least and most cost more per mile than average, the middle costs less, and a default
# scatter in one bright color shows none of it.
set -euo pipefail

mkdir -p fleet

cat > fleet/NOTES.md <<'EOF'
# Van costs: notes for the route proposal

I run the regional delivery fleet: 34 vans.

- `vans.csv` has each van's average miles a month over the last twelve months and its cost per mile over the same period (fuel, maintenance, and lease), from the fleet system.
- The vans driven least sit on short urban routes and idle a lot; the ones driven most run the long rural loops and go through tires and brakes.
- The operations director approves route changes from a one-page proposal at the fleet review on Thursday. I'm proposing to rebalance routes so that no van runs under about 1,700 or over about 3,300 miles a month. She knows the fleet but hasn't seen these numbers.

`chart.py` draws the chart I made to look at the data. It isn't what I want on the page.
EOF

cat > fleet/vans.csv <<'EOF'
van,miles_per_month,cost_per_mile
V01,1110,2.40
V02,1180,2.80
V03,1220,2.20
V04,1290,2.50
V05,1390,1.90
V06,1480,2.00
V07,1550,2.20
V08,1660,2.00
V09,1750,1.35
V10,1820,1.30
V11,1850,1.20
V12,1940,1.10
V13,1960,1.20
V14,2140,1.35
V15,2190,1.30
V16,2210,1.20
V17,2260,1.10
V18,2310,1.20
V19,2440,1.40
V20,2460,1.20
V21,2540,1.10
V22,2590,1.10
V23,2620,0.80
V24,2750,1.00
V25,2850,1.30
V26,2990,1.00
V27,3050,1.25
V28,3100,1.10
V29,3190,1.30
V30,3400,1.65
V31,3450,2.20
V32,3500,1.80
V33,3560,1.90
V34,3750,1.70
EOF

cat > fleet/chart.py <<'EOF'
import csv

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("vans.csv")))
miles = [int(r["miles_per_month"]) for r in rows]
cost = [float(r["cost_per_mile"]) for r in rows]
plt.scatter(miles, cost, color="tab:red", label="Vans")
plt.yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], ["0.00", "0.50", "1.00", "1.50", "2.00", "2.50", "3.00"])
plt.grid(True)
plt.legend()
plt.title("Scatter Plot")
plt.savefig("vans.png")
EOF
