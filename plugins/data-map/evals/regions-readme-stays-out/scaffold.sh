#!/usr/bin/env bash
# A small project with a README and a CSV of Q3 revenue for four regions, each with a centroid latitude and
# longitude. One chart for a README is not a map request, so the data-map skill should stay out of it.
set -euo pipefail

mkdir -p data

cat > README.md <<'EOF'
# ledgerline

ledgerline is invoicing and accounts receivable for small accounting firms: send invoices, chase late payments, and reconcile against the bank feed.

## Getting started

Run `npm install`, copy `.env.example` to `.env`, and start the dev server with `npm run dev`.

## Revenue

We sell through four regional teams. Quarterly revenue by region is in `data/q3_revenue_by_region.csv`.

## License

Proprietary. Copyright 2026 Ledgerline, Inc.
EOF

cat > data/q3_revenue_by_region.csv <<'EOF'
region,q3_2026_revenue,centroid_lat,centroid_lon
Pacific,2840000,47.6062,-122.3321
Mountain,1120000,39.7392,-104.9903
Central,1960000,41.8781,-87.6298
Atlantic,3410000,40.7128,-74.006
EOF
