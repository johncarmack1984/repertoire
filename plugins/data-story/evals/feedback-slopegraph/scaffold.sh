#!/usr/bin/env bash
# Employee feedback across two survey years, from Storytelling with Data (chapter 2's slopegraph):
# seven categories, one of which fell while the rest rose or held, and a default clustered column
# chart that hides it.
set -euo pipefail

mkdir -p survey

cat > survey/NOTES.md <<'EOF'
# Engagement survey: notes for the offsite pre-read

I run People Operations. The engagement survey goes to everyone each October, and about 1,300 people answered in each of the last two years.

- `favorable.csv` has the percent of answers that were favorable in each survey category, for 2014 and 2015.
- The leadership team picks next year's people programs at the offsite next Tuesday. Each proposal gets one chart on a one-page pre-read that the team reads the night before.
- I'm proposing a career development program: mentoring, internal job postings, and a training budget per person. Nobody on the leadership team has seen the 2015 results yet.

`chart.py` draws the chart I made to look at the data. It isn't what I want in the pre-read.
EOF

cat > survey/favorable.csv <<'EOF'
category,2014,2015
Peers,85,91
Culture,80,96
Work environment,76,75
Leadership,59,62
Career development,49,33
Rewards & recognition,41,45
Performance management,33,42
EOF

cat > survey/chart.py <<'EOF'
import csv

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("favorable.csv")))
names = [r["category"] for r in rows]
x = range(len(names))
plt.bar([i - 0.2 for i in x], [int(r["2014"]) for r in rows], width=0.4, label="2014", color="tab:blue")
plt.bar([i + 0.2 for i in x], [int(r["2015"]) for r in rows], width=0.4, label="2015", color="tab:orange")
plt.xticks(list(x), names, rotation=45, ha="right")
plt.ylabel("Percent favorable")
plt.grid(True)
plt.legend()
plt.title("Survey Results")
plt.tight_layout()
plt.savefig("survey.png")
EOF
