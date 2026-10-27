#!/usr/bin/env bash
# One before/after pair, already summarized: two numbers belong in a sentence, not a table.
set -euo pipefail

mkdir -p bench

cat > bench/results.txt <<'EOF'
cargo test --lib, wall time, same machine (aarch64 macOS, rustc 1.91), warm cache.
Ten runs per variant, alternating main and branch. Medians, with the range of the ten runs:

main:   1.84 s  (1.80 to 1.90)
branch: 1.21 s  (1.18 to 1.25)
EOF
