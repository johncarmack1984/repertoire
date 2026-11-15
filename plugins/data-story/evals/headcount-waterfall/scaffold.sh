#!/usr/bin/env bash
# A year of headcount, from Storytelling with Data (chapter 2's waterfall): a start, four changes,
# and an end, for a reader who wants to know why headcount went up while people kept leaving,
# and a default bar chart that draws every step from zero.
set -euo pipefail

mkdir -p headcount

cat > headcount/NOTES.md <<'EOF'
# Engineering headcount, 2014

I'm the HR business partner for the engineering group.

- `steps.csv` is the group's headcount on 1 January, what changed it during the year, and the headcount on 31 December, from the HR system as of 31 December. Transfers are moves between engineering and other parts of the company; exits are people who left the company.
- At the quarterly review the VP of Engineering asked why her headcount is up when she keeps hearing about people transferring out. I'm answering in an email, and she wants one chart she can forward to her directors.

`chart.py` draws the chart I made to check the numbers. It isn't what I want to send.
EOF

cat > headcount/steps.csv <<'EOF'
step,people
Headcount on 1 January,100
Hires,30
Transfers in,8
Transfers out,-12
Exits,-10
Headcount on 31 December,116
EOF

cat > headcount/chart.py <<'EOF'
import csv

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("steps.csv")))
names = [r["step"] for r in rows]
values = [abs(int(r["people"])) for r in rows]
colors = ["tab:blue", "tab:green", "tab:green", "tab:red", "tab:red", "tab:blue"]
plt.bar(range(len(names)), values, color=colors)
for i, v in enumerate(values):
    plt.text(i, v + 1, str(v), ha="center")
plt.xticks(range(len(names)), names, rotation=45, ha="right")
plt.grid(True)
plt.title("Headcount")
plt.tight_layout()
plt.savefig("headcount.png")
EOF
