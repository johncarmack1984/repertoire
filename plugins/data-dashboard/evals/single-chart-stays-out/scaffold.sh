#!/usr/bin/env bash
# A small project with a README and a CSV of monthly signups. One bar chart for the README is a
# single chart, not a dashboard, so the data-dashboard skill should stay out of it.
set -euo pipefail

mkdir -p data

cat > README.md <<'EOF'
# fieldnote

fieldnote is a notebook app for birders: log a sighting with a photo, a place, and a time, and it syncs across your devices.

## Getting started

Install the CLI with `cargo install fieldnote`, then run `fieldnote init` in an empty folder.

## Growth

We launched publicly in January. Signups by month are in `data/signups.csv`.
EOF

cat > data/signups.csv <<'EOF'
month,signups
2026-01,412
2026-02,538
2026-03,701
2026-04,866
2026-05,1043
2026-06,982
2026-07,1127
2026-08,1309
2026-09,1488
2026-10,1652
EOF
