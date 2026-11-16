#!/usr/bin/env bash
# Build the mln-rs template on fixture flows, render it offscreen, and judge the snapshot with check --png.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
cli="$here/../skills/data-map/scripts/datamap.py"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
map="$work/native-check"

python3 "$cli" new mln-rs "$map"
python3 "$cli" geo --countries --out "$map/data/countries.geojson"
python3 "$cli" flows "$here/fixtures/pacific-movers.csv" --nodes "$here/fixtures/pacific-nodes.csv" \
  --dest destination --value movers --geometry great-circle --layer flows --out-dir "$map/data"

export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$work/target}"
cargo build --release --locked --manifest-path "$map/Cargo.toml"
"$CARGO_TARGET_DIR/release/native-check" --snapshot "$work/map.png" --size 1200x800
python3 "$cli" check --png "$work/map.png" --legend "$map/data/legend.json" --report "$work/map.report.json"
