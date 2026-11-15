#!/usr/bin/env bash
# Terse notes on a new CLI flag: the README section is written from scratch, every fact in, nothing invented.
set -euo pipefail

cat > notes.md <<'EOF'
--watch notes (for the README)

tool is `tidy` (formats + lints a rust workspace). new flag `tidy --watch`:
- re-runs tidy whenever a file under the workspace changes
- debounce: waits 300 ms after the last change before re-running, so a burst of saves = one run
- always ignores .git/ and target/. more ignores via `watch.ignore` (list of globs) in tidy.toml
- prints a one-line summary after each run: pass/fail + how long it took
- Ctrl-C stops it; exit code = the last run's status
- macOS + Linux only (FSEvents / inotify). no Windows yet, tracked in #88
EOF
