#!/usr/bin/env bash
# Staffed beds at 40 Minnesota hospitals for a planning council's report. Planted: Riverside University
# Hospital (1,918 beds) dominates and sits inside a dense Twin Cities cluster of 16 hospitals, where a
# big symbol drawn last would hide its small neighbors; outstate hospitals run from 14 to 461 beds.
set -euo pipefail

mkdir -p hospitals

cat > hospitals/NOTES.md <<'EOF'
# Staffed beds by hospital

**Who reads it.** The board and members of the Minnesota Hospital Planning Council, in the capacity chapter of our annual report. The report is published as a web page, and the chapter needs a map of where the beds are.

**Files.**

- `hospitals.csv`: every general acute-care hospital in the state, with an id, a name, its city, its location (WGS84), and its staffed beds.
- `minnesota.geojson`: a simplified state outline for a base layer.

**Staffed beds.** Beds that are set up and staffed for inpatients, as reported to the council's capacity survey on October 1, 2026. Licensed beds that are not staffed are not counted.

**Source line we use.** Minnesota Hospital Planning Council capacity survey, October 1, 2026.
EOF

cat > hospitals/hospitals.csv <<'EOF'
hospital_id,name,city,lat,lon,staffed_beds
H01,Riverside University Hospital,Minneapolis,44.9727,-93.2318,1918
H02,Hennepin Avenue Medical Center,Minneapolis,44.9727,-93.262,486
H03,Northside Community Hospital,Minneapolis,45.0127,-93.2961,142
H04,Lake Street Hospital,Minneapolis,44.9486,-93.2601,118
H05,St. Paul Regional Medical Center,St. Paul,44.9562,-93.1022,612
H06,Capitol Hill Hospital,St. Paul,44.955,-93.111,236
H07,East Side Hospital,St. Paul,44.9665,-93.0627,96
H08,Midway Children's Hospital,St. Paul,44.9529,-93.1653,164
H09,Edina Lakes Hospital,Edina,44.8721,-93.3299,318
H10,Southdale Medical Center,Edina,44.8817,-93.3263,74
H11,Robbinsdale Crystal Hospital,Robbinsdale,45.0181,-93.3263,402
H12,Maplewood Hospital,Maplewood,45.013,-93.0122,222
H13,Burnsville Ridges Hospital,Burnsville,44.7454,-93.2867,138
H14,Coon Rapids Mercy Hospital,Coon Rapids,45.1663,-93.3106,271
H15,Woodbury Lakeview Hospital,Woodbury,44.924,-92.959,88
H16,Westwood Hospital,St. Louis Park,44.9561,-93.351,296
H17,Rochester Zumbro Valley Hospital,Rochester,44.0225,-92.4669,398
H18,St. Cloud Regional Hospital,St. Cloud,45.5608,-94.1499,461
H19,Lake Superior Medical Center,Duluth,46.7944,-92.0945,362
H20,Duluth Harbor Hospital,Duluth,46.7973,-92.1022,248
H21,Mankato Valley Hospital,Mankato,44.1636,-93.9994,184
H22,Brainerd Lakes Hospital,Brainerd,46.358,-94.2008,48
H23,Bemidji Northwoods Hospital,Bemidji,47.4736,-94.8803,22
H24,Willmar Rice Hospital,Willmar,45.1219,-95.0433,44
H25,Alexandria Douglas Hospital,Alexandria,45.8853,-95.3775,16
H26,Fergus Falls Lake Region Hospital,Fergus Falls,46.283,-96.0776,49
H27,Marshall Prairie Hospital,Marshall,44.4469,-95.7884,49
H28,Worthington Nobles Hospital,Worthington,43.62,-95.5964,87
H29,Albert Lea Freeborn Hospital,Albert Lea,43.648,-93.3683,70
H30,Austin Cedar Hospital,Austin,43.6666,-92.9746,16
H31,Red Wing River Hospital,Red Wing,44.5625,-92.5338,48
H32,Winona Bluffs Hospital,Winona,44.0499,-91.6393,34
H33,Hibbing Range Hospital,Hibbing,47.4272,-92.9377,67
H34,Grand Rapids Itasca Hospital,Grand Rapids,47.2372,-93.5302,35
H35,International Falls Rainy Lake Hospital,International Falls,48.6011,-93.4108,45
H36,Thief River Falls Hospital,Thief River Falls,48.1191,-96.1812,63
H37,Crookston Riverview Hospital,Crookston,47.7742,-96.6081,30
H38,Morris Stevens Hospital,Morris,45.5861,-95.9139,30
H39,New Ulm Brown County Hospital,New Ulm,44.3125,-94.4605,40
H40,Fairmont Lakes Hospital,Fairmont,43.6522,-94.4611,33
EOF

cat > hospitals/minnesota.geojson <<'EOF'
{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": "Minnesota"}, "geometry": {"type": "Polygon", "coordinates": [[[-97.23, 49.0], [-95.15, 49.0], [-95.15, 49.38], [-94.82, 49.32], [-94.64, 48.84], [-94.33, 48.67], [-93.46, 48.59], [-92.63, 48.54], [-92.37, 48.23], [-91.42, 48.07], [-90.84, 48.21], [-90.03, 48.1], [-89.49, 48.01], [-90.44, 47.61], [-91.53, 47.06], [-92.1, 46.75], [-92.29, 46.66], [-92.29, 46.08], [-92.89, 45.57], [-92.76, 45.27], [-92.81, 44.75], [-92.31, 44.57], [-91.92, 44.32], [-91.42, 43.98], [-91.22, 43.5], [-96.45, 43.5], [-96.45, 45.3], [-96.56, 45.94], [-96.83, 46.67], [-96.86, 47.55], [-97.14, 48.14], [-97.23, 49.0]]]}}]}
EOF
