#!/usr/bin/env bash
# Twelve alternated runs per variant where two branch runs are an order of magnitude
# slow: the mean says the branch is 2.75 times slower, the median says 12 percent faster.
set -euo pipefail

mkdir -p bench

cat > bench/NOTES.md <<'EOF'
# Request-loop timings

`latency-runs.csv` holds the wall time of the integration test's request loop (1,000 sequential requests against the local server) for main and for this branch, in the order the runs happened: the two variants alternate, twelve runs each. Columns: `variant` (main or branch), `run` (1 to 12), `ms` (milliseconds for all 1,000 requests).

Machine: x86_64 Linux, 8 cores, server and client on the same host, release build, warm cache.
EOF

cat > bench/latency-runs.csv <<'EOF'
variant,run,ms
main,1,98
branch,1,87
main,2,101
branch,2,89
main,3,100
branch,3,88
main,4,99
branch,4,88
main,5,102
branch,5,90
main,6,100
branch,6,86
main,7,101
branch,7,1240
main,8,99
branch,8,89
main,9,100
branch,9,87
main,10,100
branch,10,1180
main,11,98
branch,11,88
main,12,102
branch,12,88
EOF
