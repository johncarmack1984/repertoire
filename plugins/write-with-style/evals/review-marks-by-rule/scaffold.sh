#!/usr/bin/env bash
# A docs page with five planted faults and two sentences that only a 1918 reading would mark.
set -euo pipefail

mkdir -p docs
cat > docs/overview.md <<'EOF'
# Overview

`tidy` formats and lints a Rust workspace in one pass. Having installed the binary, the config file must be created at the workspace root before the first run. `tidy` reads the config once per run, it never caches it between runs.

Due to the size of a large workspace, `tidy` checks files in parallel. It checks less files when you pass `--changed`, which limits the run to files that differ from the main branch. The fact that the run is limited this way makes `--changed` the right choice for CI.

The cache in `target/tidy` makes repeat runs fast. However, a stale cache can slow the first run after an upgrade, so clear it beforehand with `tidy clean`.
EOF
