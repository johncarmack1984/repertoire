#!/usr/bin/env bash
# Raw timings of a build-script change: five interleaved runs per configuration
# on main and on the branch, two profiles by three -j values, wall and CPU seconds.
set -euo pipefail

mkdir -p bench

cat > bench/NOTES.md <<'EOF'
# Build-script timings

`runs.csv` holds every timed run of the crate's build script, on main and on this branch, in the order the runs happened: the two variants alternate, five runs each per configuration. Columns: `variant` (main or branch), `profile` (debug or release), `jobs` (the `-j` passed to cargo), `run` (1 to 5), `wall_s` (wall-clock seconds), `cpu_s` (user plus system CPU seconds).

Machine: x86_64 Linux, 16 cores, gcc 15.2, cargo 1.91, `default-features = false`. Every run started from a clean target directory.
EOF

cat > bench/runs.csv <<'EOF'
variant,profile,jobs,run,wall_s,cpu_s
main,debug,1,1,22.03,21.47
branch,debug,1,1,11.2,10.92
main,debug,1,2,21.28,21.3
branch,debug,1,2,11.29,11.0
main,debug,1,3,21.77,20.98
branch,debug,1,3,11.12,10.83
main,debug,1,4,21.45,21.15
branch,debug,1,4,11.42,11.22
main,debug,1,5,21.6,21.73
branch,debug,1,5,11.03,11.09
main,debug,4,1,6.85,24.8
branch,debug,4,1,4.84,12.51
main,debug,4,2,6.9,24.6
branch,debug,4,2,4.9,12.85
main,debug,4,3,7.04,25.09
branch,debug,4,3,4.8,12.41
main,debug,4,4,6.96,24.43
branch,debug,4,4,4.73,12.7
main,debug,4,5,6.8,24.23
branch,debug,4,5,4.77,12.6
main,debug,16,1,5.36,29.89
branch,debug,16,1,4.1,13.59
main,debug,16,2,5.32,30.34
branch,debug,16,2,4.18,13.8
main,debug,16,3,5.44,30.1
branch,debug,16,3,4.13,13.91
main,debug,16,4,5.4,29.65
branch,debug,16,4,4.07,13.7
main,debug,16,5,5.51,30.7
branch,debug,16,5,4.04,14.08
main,release,1,1,37.43,37.8
branch,release,1,1,22.74,22.06
main,release,1,2,37.73,38.25
branch,release,1,2,23.08,22.4
main,release,1,3,38.76,37.5
branch,release,1,3,22.56,22.24
main,release,1,4,38.3,36.94
branch,release,1,4,23.36,22.58
main,release,1,5,38.0,37.24
branch,release,1,5,22.9,22.85
main,release,4,1,15.2,43.89
branch,release,4,1,13.41,24.92
main,release,4,2,14.8,45.08
branch,release,4,2,13.57,25.5
main,release,4,3,15.02,44.2
branch,release,4,3,13.1,25.12
main,release,4,4,14.68,43.54
branch,release,4,4,13.3,25.3
main,release,4,5,14.9,44.55
branch,release,4,5,13.21,25.81
main,release,16,1,13.49,55.44
branch,release,16,1,12.3,27.68
main,release,16,2,13.6,54.62
branch,release,16,2,12.2,28.1
main,release,16,3,13.7,55.0
branch,release,16,3,12.11,27.9
main,release,16,4,13.81,56.1
branch,release,16,4,12.44,28.32
main,release,16,5,13.97,54.17
branch,release,16,5,12.02,28.66
EOF
