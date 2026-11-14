#!/usr/bin/env bash
# The ticket backlog from Storytelling with Data (chapters 3 to 5): a year of tickets received
# and processed, two people who left in May, a default clustered column chart, and a hiring
# request the chart has to support.
set -euo pipefail

mkdir -p tickets

cat > tickets/NOTES.md <<'EOF'
# Ticket volume, 2014: notes for the headcount request

I run the IT support team. Two people left in May and we decided at the time not to replace them. Since then the rest of the team has been telling me they can't keep up.

- `volume.csv` has tickets received and tickets processed for each month of 2014, from the help desk dashboard, as of 31 December.
- Next year's headcount requests go to the VP of Operations on Friday. I'm asking to hire two people to backfill the two who left. She approves or denies each request from a one-page summary, and she hasn't seen these numbers.
- I also have an analysis of tickets processed per person and time to resolve, if she asks for it.

`chart.py` draws the chart I made to look at the data. It isn't what I want to send.
EOF

cat > tickets/volume.csv <<'EOF'
month,received,processed
January,160,160
February,184,184
March,241,237
April,149,148
May,180,181
June,161,150
July,132,123
August,202,156
September,160,126
October,139,104
November,149,124
December,177,140
EOF

cat > tickets/chart.py <<'EOF'
import csv

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("volume.csv")))
months = [r["month"] for r in rows]
x = range(len(months))
plt.bar([i - 0.2 for i in x], [int(r["received"]) for r in rows], width=0.4, label="Ticket Volume Received", color="blue")
plt.bar([i + 0.2 for i in x], [int(r["processed"]) for r in rows], width=0.4, label="Ticket Volume Processed", color="red")
for i, r in enumerate(rows):
    plt.text(i - 0.2, int(r["received"]) + 2, r["received"], ha="center")
    plt.text(i + 0.2, int(r["processed"]) + 2, r["processed"], ha="center")
plt.xticks(list(x), months, rotation=45)
plt.yticks([0, 50, 100, 150, 200, 250, 300], ["0.00", "50.00", "100.00", "150.00", "200.00", "250.00", "300.00"])
plt.grid(True)
plt.legend(loc="lower center", ncol=2)
plt.title("Ticket Trend")
plt.savefig("tickets.png")
EOF
