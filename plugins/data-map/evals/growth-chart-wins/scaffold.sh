#!/usr/bin/env bash
# Four sales regions' Q2 and Q3 2026 revenue, plus which states sit in each region. Growth is West +12.4%,
# Midwest +7.9%, Northeast +3.1%, South -2.6%. Four numbers whose message isn't location: a sorted bar
# chart or a table wins over a map, even though the state list makes a map easy to draw.
set -euo pipefail

mkdir -p sales

cat > sales/NOTES.md <<'EOF'
# Regional revenue, Q2 and Q3 2026

`regional_revenue.csv` has each sales region's recognized revenue for Q2 2026 (April to June) and Q3 2026 (July to September), in US dollars. `region_states.csv` lists the states in each region. Finance closed Q3 on October 9, 2026.
EOF

cat > sales/regional_revenue.csv <<'EOF'
region,q2_2026_revenue,q3_2026_revenue
West,18420000,20704000
Midwest,11105000,11982000
Northeast,14850000,15310000
South,16200000,15779000
EOF

cat > sales/region_states.csv <<'EOF'
region,state
West,AK
West,AZ
West,CA
West,CO
West,HI
West,ID
West,MT
West,NM
West,NV
West,OR
West,UT
West,WA
West,WY
Midwest,IA
Midwest,IL
Midwest,IN
Midwest,KS
Midwest,MI
Midwest,MN
Midwest,MO
Midwest,ND
Midwest,NE
Midwest,OH
Midwest,SD
Midwest,WI
Northeast,CT
Northeast,MA
Northeast,ME
Northeast,NH
Northeast,NJ
Northeast,NY
Northeast,PA
Northeast,RI
Northeast,VT
South,AL
South,AR
South,DC
South,DE
South,FL
South,GA
South,KY
South,LA
South,MD
South,MS
South,NC
South,OK
South,SC
South,TN
South,TX
South,VA
South,WV
EOF
