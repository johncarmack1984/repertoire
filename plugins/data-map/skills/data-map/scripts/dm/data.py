"""Data at the edges: CSV and GeoJSON reading and writing, numbers, joins, and the count-or-rate guess."""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

MISSING = {"", "na", "n/a", "nan", "null", "none", "-", "..", "nd", "#n/a"}
COUNT_TOKENS = {"count", "counts", "total", "totals", "number", "num", "cases", "pop", "population", "sum", "n"}
RATE_TOKENS = {"per", "rate", "rates", "pct", "percent", "percentage", "share", "ratio", "density", "avg", "mean",
               "median", "index", "prop", "proportion", "capita", "pc", "pp", "per100k", "per1000"}
DENOMINATOR_TOKENS = {"pop", "population", "area", "km2", "sqkm", "households", "hh", "acres"}
LON_NAMES = ("lon", "lng", "long", "longitude", "x")
LAT_NAMES = ("lat", "latitude", "y")
ORIGIN_NAMES = ("origin", "orig", "o", "from", "source", "src", "start")
DEST_NAMES = ("destination", "dest", "d", "to", "target", "dst", "end")
VALUE_NAMES = ("value", "flow", "count", "amount", "weight", "volume", "total", "n")
ID_NAMES = ("id", "iso_a3", "code", "key", "node", "geoid", "fips")
LABEL_NAMES = ("name", "label", "dm_label", "admin", "title")
NE_MINUS_99 = {"FRA", "NOR", "CYN", "SOL", "KOS", "XKX"}
NE_HINT = ("Natural Earth's ISO_A3 is -99 for France, Norway, N. Cyprus, Somaliland, and Kosovo; "
           "the bundled world-110m.json carries FRA, NOR, CYN, SOL, and KOS (World Bank data writes Kosovo as XKX)")


@dataclass
class Table:
    columns: list
    rows: list


def read_table(path: Path) -> Table:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = [dict(r) for r in reader]
        return Table(list(reader.fieldnames or []), rows)


def read_features(path: Path) -> list:
    doc = json.loads(Path(path).read_text())
    if doc.get("type") == "FeatureCollection":
        return doc["features"]
    if doc.get("type") == "Feature":
        return [doc]
    return [{"type": "Feature", "properties": {}, "geometry": doc}]


def is_csv(path: Path) -> bool:
    return Path(path).suffix.lower() in (".csv", ".tsv", ".txt")


def parse_number(s) -> float | None:
    if s is None:
        return None
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return float(s) if s == s else None
    t = str(s).strip()
    if t.lower() in MISSING:
        return None
    t = t.replace(",", "").replace("_", "")
    if t.endswith("%"):
        t = t[:-1]
    try:
        v = float(t)
    except ValueError:
        return None
    return v if v == v and abs(v) != float("inf") else None


def tokens(name: str) -> list:
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if t]


def find_column(columns: list, names: tuple, explicit: str | None = None) -> str | None:
    if explicit:
        return explicit if explicit in columns else None
    lower = {c.lower(): c for c in columns}
    for n in names:
        if n in lower:
            return lower[n]
    return None


def numeric_columns(columns: list, rows: list, min_share: float = 0.8) -> dict:
    """Columns where at least 80% of the non-missing cells are numbers."""
    out = {}
    for c in columns:
        vals = [parse_number(r.get(c)) for r in rows]
        present = [r.get(c) for r in rows if str(r.get(c, "")).strip().lower() not in MISSING]
        nums = [v for v in vals if v is not None]
        if present and len(nums) / len(present) >= min_share:
            out[c] = vals
    return out


def ranks(xs: list) -> list:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for t in range(i, j + 1):
            r[order[t]] = (i + j) / 2
        i = j + 1
    return r


def spearman(xs: list, ys: list) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 5:
        return 0.0
    rx, ry = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx, vy = sum((a - mx) ** 2 for a in rx), sum((b - my) ** 2 for b in ry)
    return cov / (vx * vy) ** 0.5 if vx and vy else 0.0


def ratio(xs: list, ys: list) -> list:
    return [x / y if x is not None and y else None for x, y in zip(xs, ys)]


def log_spread(xs: list) -> float:
    """Variance of the logs of the positive values: how many orders of magnitude they span."""
    logs = [math.log(x) for x in xs if x is not None and x > 0]
    if len(logs) < 2:
        return 0.0
    m = sum(logs) / len(logs)
    return sum((v - m) ** 2 for v in logs) / len(logs)


def guess_kind(name: str, values: list, others: dict) -> tuple:
    """('count' | 'rate' | 'unknown', reason) for a numeric column, from its name, its values, and its neighbors."""
    toks = set(tokens(name))
    if toks & RATE_TOKENS:
        return "rate", f"the name {name!r} reads as a rate ({', '.join(sorted(toks & RATE_TOKENS))})"
    if toks & COUNT_TOKENS or name.lower().startswith("n_"):
        return "count", f"the name {name!r} reads as a count ({', '.join(sorted(toks & COUNT_TOKENS) or ['n_'])})"
    nums = [v for v in values if v is not None]
    if not nums:
        return "unknown", "no numeric values"
    integers = all(float(v).is_integer() for v in nums)
    if integers:
        for other, ovals in others.items():
            if other == name or not set(tokens(other)) & DENOMINATOR_TOKENS:
                continue
            rho = spearman(values, ovals)
            if rho >= 0.7:
                return "count", f"whole numbers that rise with {other!r} (Spearman {rho:.2f}), as totals do"
            if rho >= 0.5 and log_spread(ratio(values, ovals)) < log_spread(values):
                return "count", (f"whole numbers that rise with {other!r} (Spearman {rho:.2f}) and spread less once "
                                 f"divided by it, as totals do")
        return "unknown", "whole numbers with no rate in the name; if they are totals, standardize them"
    if all(0 <= v <= 1 for v in nums):
        return "rate", "fractions between 0 and 1"
    return "rate", "non-integer values"


def label_of(props: dict, explicit: str | None, fallback: str) -> str:
    key = find_column(list(props), LABEL_NAMES, explicit)
    v = props.get(key) if key else None
    return str(v) if v not in (None, "") else fallback


def index_features(features: list, prop: str) -> dict:
    out = {}
    for f in features:
        key = f.get("id") if prop == "id" else (f.get("properties") or {}).get(prop)
        if key is not None:
            out.setdefault(str(key).strip(), f)
    return out


def join(rows: list, column: str, features: list, prop: str) -> tuple:
    """Pairs each row with its feature; returns the pairs and the keys on each side that matched nothing."""
    index = index_features(features, prop)
    pairs, unmatched_rows = [], []
    used = set()
    for r in rows:
        key = str(r.get(column, "")).strip()
        f = index.get(key)
        if f is None:
            unmatched_rows.append(key)
        else:
            pairs.append((r, f))
            used.add(key)
    unmatched_features = sorted(k for k in index if k not in used)
    return pairs, unmatched_rows, unmatched_features


def ne_hint(unmatched: list) -> str | None:
    if NE_MINUS_99 & set(unmatched) or "-99" in unmatched:
        return NE_HINT
    return None


def table_points(table: Table, lon: str, lat: str) -> list:
    feats = []
    for r in table.rows:
        x, y = parse_number(r.get(lon)), parse_number(r.get(lat))
        if x is None or y is None:
            continue
        props = {k: v for k, v in r.items() if k not in (lon, lat)}
        feats.append({"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": [x, y]}})
    return feats


def round_coords(c, nd: int = 5):
    if isinstance(c, (int, float)):
        return round(c, nd)
    return [round_coords(x, nd) for x in c]


def feature(fid, props: dict, geom: dict, nd: int = 5) -> dict:
    return {"type": "Feature", "id": fid, "properties": props,
            "geometry": {"type": geom["type"], "coordinates": round_coords(geom["coordinates"], nd)}}


def sort_key(f: dict) -> tuple:
    fid = f.get("id")
    return (f["properties"].get("dm_order", 0), (0, fid, "") if isinstance(fid, int) else (1, 0, str(fid)))


def write_geojson(path: Path, features: list) -> None:
    feats = sorted(features, key=sort_key)
    doc = {"type": "FeatureCollection", "features": feats}
    Path(path).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")


def write_json(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
