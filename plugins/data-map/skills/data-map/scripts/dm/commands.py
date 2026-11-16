"""The lever subcommands: inspect, geo, crs, classes, sizes, flows. Reading and writing happen here; the rules live in the modules."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from . import FAIL, PASS, WARN, classify, color, crs, data, flows, geo, legend, symbols
from . import report as emit

COUNTRIES = Path(__file__).resolve().parents[2] / "assets" / "geo" / "world-110m.json"
SCALES = [1, 100, 1000, 10000, 100000, 1000000]
SYMBOL_COLOR = "#3182bd"


class InputError(Exception):
    """Bad input: exit 2."""


def num(v: float, e: int | None = None) -> str:
    if v is None:
        return "no data"
    if e is None:
        e = 0 if float(v).is_integer() or abs(v) >= 100 else (-1 if abs(v) >= 10 else -2)
    return classify.fmt(classify.round_to(v, e), e)


def geo_path(name: str) -> Path:
    return COUNTRIES if name == "countries" else Path(name)


def load_layer(args, findings: list) -> list:
    """Features from GeoJSON, from a CSV with lon/lat, or from a CSV joined to GeoJSON (--geo, --key)."""
    src = Path(args.input)
    if not src.exists():
        raise InputError(f"no such file: {src}")
    if not data.is_csv(src):
        return data.read_features(src)
    table = data.read_table(src)
    if getattr(args, "geo", None):
        left, _, right = (args.key or "").partition("=")
        right = right or left
        if left not in table.columns:
            raise InputError(f"--key: no column {left!r} in {src}; columns: {', '.join(table.columns)}")
        feats = data.read_features(geo_path(args.geo))
        pairs, lost_rows, bare = data.join(table.rows, left, feats, right)
        if lost_rows:
            hint = data.ne_hint(lost_rows)
            findings.append(WARN("join", f"{len(lost_rows)} of {len(table.rows)} rows matched no feature and are dropped: {', '.join(lost_rows[:12])}" + (f". {hint}" if hint else ""),
                                 "fix the keys so every row finds its place, or say in the notes which places are missing", 3))
        else:
            findings.append(PASS("join", f"all {len(table.rows)} rows matched a feature on {left} = {right}", 3))
        out = []
        for row, f in pairs:
            props = dict(f.get("properties") or {})
            props.update(row)
            out.append({"type": "Feature", "id": f.get("id", row[left]), "properties": props, "geometry": f["geometry"]})
        matched = {id(f) for _, f in pairs}
        for f in feats:
            if id(f) not in matched:
                out.append({"type": "Feature", "id": f.get("id"), "properties": dict(f.get("properties") or {}), "geometry": f["geometry"]})
        if bare:
            findings.append(PASS("join", f"{len(bare)} features have no row and draw as no data", 9))
        return out
    lon = data.find_column(table.columns, data.LON_NAMES, getattr(args, "lon", None))
    lat = data.find_column(table.columns, data.LAT_NAMES, getattr(args, "lat", None))
    if not (lon and lat):
        raise InputError(f"{src} is a CSV with no lon/lat columns; join it to shapes with --geo G --key K")
    return data.table_points(table, lon, lat)


def feature_id(f: dict, i: int, key: str | None) -> str:
    props = f.get("properties") or {}
    v = f.get("id") if f.get("id") is not None else props.get(key) if key else None
    return str(v) if v is not None else str(i)


def kind_of(field: str, feats: list) -> tuple:
    props = [f.get("properties") or {} for f in feats]
    columns = sorted({k for p in props for k in p})
    numeric = data.numeric_columns(columns, props)
    values = numeric.get(field) or [data.parse_number(p.get(field)) for p in props]
    return data.guess_kind(field, values, numeric)


def auto_scale(rates: list) -> int:
    positive = sorted(r for r in rates if r and r > 0)
    if not positive:
        return 1
    m = classify.median(positive)
    return next((s for s in SCALES if m * s >= 1), SCALES[-1])


# inspect

def profile_lines(name: str, columns: list, rows: list) -> list:
    out = []
    numeric = data.numeric_columns(columns, rows)
    margins = {m: e for e, m in moe_pairs(columns, numeric)}
    for c, vals in numeric.items():
        nums = sorted(v for v in vals if v is not None)
        if not nums:
            continue
        zeros = sum(1 for v in nums if v == 0)
        skew = classify.skewness(nums)
        msg = (f"{name} column {c}: {len(nums):,} values, {len(vals) - len(nums):,} missing" + (f", {zeros:,} of them zero" if zeros else "")
               + f", min {num(nums[0])}, max {num(nums[-1])}, mean {num(classify.mean(nums))}, median {num(classify.median(nums))}, skewness {skew:.2f}")
        if c in margins:
            out.append(PASS("profile", f"{msg}; the margin of error of {margins[c]}", 36))
            continue
        kind, why = data.guess_kind(c, vals, numeric)
        msg += f"; {kind}: {why}"
        if kind == "count":
            out.append(PASS("profile", msg + "; on an area idiom, divide it with classes --per, or draw it as sizes", 1))
        else:
            out.append(PASS("profile", msg))
    return out


MOE_BARE = re.compile(r"(?i)moe|margin|margin_of_error")
MOE_AFFIXED = re.compile(r"(?i)(?:moe|margin)_(?P<a>.+)|(?P<b>.+?)_(?:moe|margin|margin_of_error)")
Z90 = 1.645


def moe_pairs(columns: list, numeric: dict) -> list:
    """(estimate, margin) column pairs: x_moe or moe_x beside x, or a bare moe or margin beside the estimate on its left."""
    pairs = []
    for i, c in enumerate(columns):
        if c not in numeric:
            continue
        m = MOE_AFFIXED.fullmatch(c)
        if m and (m["a"] or m["b"]) in numeric:
            pairs.append((m["a"] or m["b"], c))
        elif MOE_BARE.fullmatch(c):
            left = [x for x in columns[:i] if x in numeric and not (MOE_BARE.fullmatch(x) or MOE_AFFIXED.fullmatch(x))]
            if left:
                pairs.append((left[-1], c))
    return pairs


def runs(indices: list) -> list:
    """Consecutive tied neighbors as 1-based rank runs: ties at 0 and 1 become (1, 3)."""
    out = []
    for i in indices:
        if out and out[-1][1] == i + 1:
            out[-1] = (out[-1][0], i + 2)
        else:
            out.append((i + 1, i + 2))
    return out


def moe_lines(name: str, columns: list, rows: list) -> tuple:
    """For each estimate with a margin of error: the range of its coefficient of variation, and the neighboring
    ranks its margins tie (Slocum §26.6.1). The margins are taken as 90%, as the ACS publishes them."""
    out, facts = [], []
    numeric = data.numeric_columns(columns, rows)
    for est, moe in moe_pairs(columns, numeric):
        pairs = [(e, m) for e, m in zip(numeric[est], numeric[moe]) if e is not None and m is not None]
        cv = sorted((m / Z90) / e * 100 for e, m in pairs if e > 0)
        zeros = sum(1 for e, _ in pairs if e == 0)
        if not cv:
            continue
        ranked = sorted(pairs, key=lambda p: -p[0])
        ties = [i for i, (a, b) in enumerate(zip(ranked, ranked[1:])) if a[0] - b[0] < math.hypot(a[1], b[1])]
        facts.append({"estimate": est, "moe": moe, "cv": [round(cv[0], 1), round(classify.median(cv), 1), round(cv[-1], 1)],
                      "zeros": zeros, "neighbors": len(ranked) - 1, "ties": len(ties)})
        out.append(PASS("moe", f"{name} column {moe} is the margin of error of {est}: coefficient of variation {cv[0]:.0f}% to {cv[-1]:.0f}% "
                               f"(median {classify.median(cv):.0f}%) over {len(cv):,} nonzero estimates, as (MOE / {Z90}) / estimate x 100"
                               + (f"; {zeros:,} zero {'estimate has' if zeros == 1 else 'estimates have'} no CV" if zeros else ""), 36))
        if ties:
            top = [f"{a} to {b}" for a, b in runs([i for i in ties if i < 9])]
            out.append(WARN("moe", f"{len(ties):,} of the {len(ranked) - 1:,} pairs of neighboring ranks of {est} differ by less than the margin of their difference, so they tie"
                                   + (f"; among the 10 largest, ranks {' and '.join(top)} tie" if top else ""),
                            "claim a rank only where the difference beats sqrt(MOE1^2 + MOE2^2), print the margins beside exact values, and say what they mean in the source line", 36))
    return out, facts


def extent_lines(name: str, positions: list) -> list:
    if not positions:
        return []
    lons, lats = [p[0] for p in positions], [p[1] for p in positions]
    if any(abs(y) > 90 for y in lats):
        flipped = all(abs(x) <= 90 for x in lons)
        return [FAIL("lonlat", f"{name} has latitudes beyond 90" + ("; the columns look swapped" if flipped else ""),
                     "put longitude first and latitude second, in degrees")]
    w, e = geo.extent_lons(lons)
    ext = crs.Extent(w, min(lats), e, max(lats))
    cross = " and crosses 180 (west > east)" if ext.crosses_antimeridian else ""
    return [PASS("extent", f"{name} spans {num(w, -2)}, {num(ext.south, -2)} to {num(e, -2)}, {num(ext.north, -2)}{cross}")]


def run_inspect(args) -> int:
    findings, profiles = [], {}
    for path in args.data:
        p = geo_path(path)
        if not p.exists():
            raise InputError(f"no such file: {p}")
        if data.is_csv(p):
            t = data.read_table(p)
            findings.append(PASS("rows", f"{p.name}: {len(t.rows)} rows, columns {', '.join(t.columns)}"))
            findings += profile_lines(p.name, t.columns, t.rows)
            lines, margins = moe_lines(p.name, t.columns, t.rows)
            findings += lines
            lon = data.find_column(t.columns, data.LON_NAMES)
            lat = data.find_column(t.columns, data.LAT_NAMES)
            if lon and lat:
                pts = [[data.parse_number(r[lon]), data.parse_number(r[lat])] for r in t.rows]
                findings += extent_lines(p.name, [q for q in pts if None not in q])
            o = data.find_column(t.columns, data.ORIGIN_NAMES)
            d = data.find_column(t.columns, data.DEST_NAMES)
            if o and d:
                findings.append(PASS("od", f"{p.name} reads as origin-destination pairs: {o} to {d}; draw it with flows"))
            profiles[p.name] = {"rows": len(t.rows), "columns": t.columns, "margins": margins}
        else:
            feats = data.read_features(p)
            types = sorted({(f.get("geometry") or {}).get("type", "None") for f in feats})
            findings.append(PASS("features", f"{p.name}: {len(feats)} features, geometry {', '.join(types)}"))
            props = [f.get("properties") or {} for f in feats]
            columns = sorted({k for q in props for k in q})
            findings += profile_lines(p.name, columns, props)
            lines, margins = moe_lines(p.name, columns, props)
            findings += lines
            findings += extent_lines(p.name, [q for f in feats if f.get("geometry") for q in geo.all_positions(f["geometry"])])
            profiles[p.name] = {"features": len(feats), "geometry": types, "properties": columns, "margins": margins}
    for spec in args.join or []:
        findings += join_lines(spec)
    return emit(findings, args.json, {"profiles": profiles})


def join_lines(spec: str) -> list:
    left, _, right = spec.partition("=")
    csv_path, _, col = left.rpartition(":")
    geo_name, _, prop = right.rpartition(":")
    if not (csv_path and col and geo_name and prop):
        raise InputError("--join takes CSV:COL=GEOJSON:PROP")
    t = data.read_table(Path(csv_path))
    if col not in t.columns:
        raise InputError(f"--join: no column {col!r} in {csv_path}")
    _, lost_rows, bare = data.join(t.rows, col, data.read_features(geo_path(geo_name)), prop)
    out = []
    if lost_rows:
        hint = data.ne_hint(lost_rows + bare)
        out.append(WARN("join", f"{len(lost_rows)} of {len(t.rows)} rows match no feature: {', '.join(lost_rows[:20])}" + (f". {hint}" if hint else ""),
                        "fix the keys (codes, spelling, -99) before mapping; a dropped row is a place missing from the map", 3))
    else:
        out.append(PASS("join", f"all {len(t.rows)} rows of {Path(csv_path).name} match {geo_name}:{prop}", 3))
    if bare:
        out.append(PASS("join", f"{len(bare)} features have no row and will draw as no data: {', '.join(bare[:20])}", 9))
    return out


# geo

def run_geo(args) -> int:
    findings, feats = [], []
    if args.input or args.countries:
        src = COUNTRIES if args.countries else Path(args.input)
        if not src.exists():
            raise InputError(f"no such file: {src}")
        for i, f in enumerate(data.read_features(src)):
            g = f.get("geometry")
            if not g:
                continue
            if args.densify:
                g = geo.map_coords(g, lambda c: geo.densify_planar(c, args.densify))
            feats.append(data.feature(f.get("id", str(i)), dict(f.get("properties") or {}), g))
        longest = max((geo.distance_km(p, q) for f in feats for line in parts(f["geometry"]) for p, q in zip(line, line[1:]) if abs(q[0] - p[0]) <= 180), default=0)
        if args.densify:
            findings.append(PASS("densify", f"{len(feats)} features densified to at most {num(args.densify)} km per edge; longest edge now {num(longest)} km", 12))
        elif longest > 200:
            findings.append(WARN("densify", f"edges up to {num(longest)} km long will draw straight under a CRS or on a globe",
                                 "pass --densify 100", 12))
    if args.graticule:
        feats += [data.feature(f["id"], f["properties"], f["geometry"]) for f in geo.graticule(args.graticule)]
        findings.append(PASS("graticule", f"meridians and parallels every {num(args.graticule)} degrees, a vertex every degree", 12))
    if args.sphere:
        s = geo.sphere()
        feats.append(data.feature(s["id"], s["properties"], s["geometry"]))
        findings.append(PASS("sphere", "the world outline, a vertex every degree along 180 and the poles", 12))
    if not feats:
        raise InputError("geo needs IN, --countries, --graticule, or --sphere")
    data.write_geojson(Path(args.out), feats)
    findings.append(PASS("write", f"wrote {len(feats)} features to {args.out}"))
    return emit(findings, args.json, {"out": str(args.out), "features": len(feats)})


def parts(g: dict) -> list:
    t, c = g["type"], g["coordinates"]
    if t == "LineString":
        return [c]
    if t in ("MultiLineString", "Polygon"):
        return c
    if t == "MultiPolygon":
        return [r for poly in c for r in poly]
    return []


# crs

def parse_extent(text: str) -> crs.Extent:
    if text == "world":
        return crs.WORLD
    bits = text.split(",")
    if len(bits) == 4:
        try:
            w, s, e, n = (float(b) for b in bits)
        except ValueError:
            raise InputError("--extent takes world, W,S,E,N, or a data file")
        return crs.Extent(w, s, e, n)
    p = geo_path(text)
    if not p.exists():
        raise InputError(f"--extent: no such file {p}")
    if data.is_csv(p):
        t = data.read_table(p)
        lon = data.find_column(t.columns, data.LON_NAMES)
        lat = data.find_column(t.columns, data.LAT_NAMES)
        if not (lon and lat):
            raise InputError(f"--extent: {p} has no lon/lat columns")
        pos = [[data.parse_number(r[lon]), data.parse_number(r[lat])] for r in t.rows]
        pos = [q for q in pos if None not in q]
    else:
        pos = [q for f in data.read_features(p) if f.get("geometry") for q in geo.all_positions(f["geometry"])]
    if not pos:
        raise InputError(f"--extent: {p} has no coordinates")
    w, e = geo.extent_lons([q[0] for q in pos])
    return crs.Extent(w, min(q[1] for q in pos), e, max(q[1] for q in pos))


def run_crs(args) -> int:
    ext = parse_extent(args.extent)
    rec = crs.recommend(ext, args.idiom, args.interactive)
    findings = [PASS("projection", f"{rec.name}: {rec.reason}", 10)]
    if rec.definition:
        findings.append(PASS("definition", rec.definition))
    for alt in rec.alternatives:
        findings.append(PASS("alternative", f"{alt['name']} ({alt['definition']}): {alt['why']}"))
    if rec.type == "crs" and args.idiom == "area":
        findings.append(WARN("tiles", f"GL JS can't draw Web Mercator tiles under {rec.name}; they land in the wrong place",
                             "draw GeoJSON layers, or tiles cut in this CRS's grid (martin's tile_grids), and list each source's grid in dm-spec", 11))
    snippet = crs.snippet(rec)
    extra = {"type": rec.type, "name": rec.name, "definition": rec.definition, "property": rec.property,
             "reason": rec.reason, "alternatives": rec.alternatives, "snippet": snippet,
             "extent": [ext.west, ext.south, ext.east, ext.north]}
    code = emit(findings, args.json, extra)
    if not args.json:
        print(snippet)
    return code


# classes

def parse_scheme(text: str) -> tuple:
    if text in ("seq", "qual"):
        return text, None
    if text.startswith("div:"):
        mid = text[4:]
        if mid == "mean":
            return "div", "mean"
        value = data.parse_number(mid)
        if value is None:
            raise InputError("--scheme div:MID takes a number or mean")
        return "div", value
    raise InputError("--scheme takes seq, div:MID, or qual")


def palette_check(pal: color.Palette, kind: str, scheme: str, allow: bool) -> list:
    out = []
    if pal.type != "custom" and pal.type != scheme:
        want = {"seq": "a sequential", "div": "a diverging", "qual": "a qualitative"}[scheme]
        out.append(FAIL("scheme", f"{pal.name} is {pal.type}, but the data calls for {want} scheme",
                        f"pick {want} palette, such as {color.DEFAULT_PALETTE[scheme]}", 7))
    worst = color.worst_pair(pal.colors, kind)
    detail = f"least separable pair {pal.colors[worst[2]]} and {pal.colors[worst[3]]}, delta E {worst[0]:.1f} ({worst[1]})"
    safe = pal.blind == 1 if pal.blind is not None else worst[0] >= color.MIN_DELTA_E
    source = f"ColorBrewer rates {pal.name} at {len(pal.colors)} classes " + {1: "colorblind-safe", 2: "maybe colorblind-safe", 0: "not colorblind-safe"}[pal.blind] if pal.blind is not None else f"the simulation needs delta E {color.MIN_DELTA_E:g}"
    if safe:
        out.append(PASS("palette", f"{source}; {detail}", 8))
    elif allow:
        out.append(WARN("palette", f"{source}; {detail}; kept by --allow-unsafe-palette", "label the classes directly, or pick a safe palette", 8))
    else:
        out.append(FAIL("palette", f"{source}; {detail}", "pick a colorblind-safe palette, fewer classes, or pass --allow-unsafe-palette with a reason", 8))
    return out


def run_classes(args) -> int:
    findings = []
    feats = load_layer(args, findings)
    field = args.field
    props = [f.get("properties") or {} for f in feats]
    if not any(field in p for p in props):
        raise InputError(f"--field: no property {field!r}; properties: {', '.join(sorted({k for p in props for k in p}))}")
    scheme, mid = parse_scheme(args.scheme)
    if scheme == "qual":
        return classes_qual(args, feats, findings)
    kind, why = kind_of(field, feats)
    if args.per:
        findings.append(PASS("standardize", f"{field} divided by {args.per}", 1))
    elif args.already_normalized:
        findings.append(PASS("standardize", f"{field} is used as is: {args.already_normalized}", 1))
    elif kind == "count":
        findings.append(FAIL("counts", f"{field} looks like a count ({why}); an area fill of totals shows how big each place is, not how intense",
                             "pass --per with a denominator (population, area) and --scale, draw the totals with sizes, or pass --already-normalized REASON", 1))
        return emit(findings, args.json)
    elif kind == "unknown":
        findings.append(WARN("counts", f"{field}: {why}", "pass --per, or --already-normalized REASON to record that it is a rate", 1))
    raw = [data.parse_number(p.get(field)) for p in props]
    den = [data.parse_number(p.get(args.per)) for p in props] if args.per else [None] * len(props)
    if args.per:
        rates = [r / d if r is not None and d else None for r, d in zip(raw, den)]
        scale = whole(args.scale) if args.scale else auto_scale(rates)
        if not args.scale:
            findings.append(PASS("scale", f"rates shown per {scale:,} {args.per}, so the median rate reads at 1 or more"))
        values = [r * scale if r is not None else None for r in rates]
    else:
        scale, values = None, raw
    present = sorted(v for v in values if v is not None)
    if not present:
        raise InputError(f"no numeric values in {field}")
    if args.per and args.min_den is None:
        dens = sorted(d for d in den if d)
        tiny = [d for d in dens if d < 0.01 * classify.median(dens)]
        if tiny:
            findings.append(WARN("denominators", f"{len(tiny)} denominators are under 1% of the median; their rates swing on a handful of events",
                                 "pass --min-den N to flag them", 4))
    if scheme == "div":
        center = classify.mean(present) if mid == "mean" else mid
        if not present[0] < center < present[-1]:
            findings.append(FAIL("midpoint", f"the midpoint {num(center)} is outside the data ({num(present[0])} to {num(present[-1])}), so one side of the diverging scheme would be empty",
                                 "use a sequential scheme, or a midpoint the data straddles", 7))
            return emit(findings, args.json)
    else:
        center = None
    pal_name = args.palette or color.DEFAULT_PALETTE[scheme]
    one_hue = pal_name in color.schemes() and color.schemes()[pal_name]["one_hue"]
    max_k = 6 if one_hue else 7
    c, method_reason, k_reason = choose_classes(args, present, scheme, center, max_k, mid == "mean")
    if c.palette_k < 3:
        c.slots, c.palette_k = [round(i * 2 / max(1, c.k - 1)) for i in range(c.k)] if c.k > 1 else [2], 3
    try:
        pal = color.palette(pal_name, c.palette_k, args.reverse)
    except (KeyError, ValueError) as err:
        raise InputError(str(err))
    if pal.type == "custom" and len(pal.colors) != c.palette_k:
        raise InputError(f"--palette lists {len(pal.colors)} colors for {c.palette_k} classes")
    colors = [pal.colors[s] for s in c.slots]
    counts = c.counts(present)
    g, a = c.fit(present)
    skew = classify.skewness(present)
    findings.append(PASS("method", f"{c.method}: {method_reason}", 5))
    if c.method == "equal" and abs(skew) > 1:
        findings.append(WARN("method", f"equal intervals on skewed data (skewness {skew:.2f}) crowd most places into one class",
                             "use --method jenks or quantile", 5))
    labels = c.labels()
    empty = [labels[i] for i, n in enumerate(counts) if n == 0]
    if not 3 <= c.k <= 7 or empty:
        why_k = f"k = {c.k}" + (f"; empty: {', '.join(empty)}" if empty else "")
        findings.append(WARN("classes", why_k, "use 3 to 7 classes, each holding places", 6))
    findings.append(PASS("classes", f"{k_reason}; {', '.join(f'{l} ({n})' for l, n in zip(labels, counts))}; GVF {g:.2f}, GADF {a:.2f}", 6))
    for note in c.notes:
        findings.append(PASS("breaks", note))
    findings += palette_check(pal, scheme, scheme, args.allow_unsafe_palette)
    nodata = color.nodata_color(tuple(colors))
    unit = args.unit if args.unit is not None else (f"per {scale:,} {args.per}" if args.per else "")
    low = set()
    if args.min_den is not None:
        low = {i for i, d in enumerate(den) if d is not None and d < args.min_den}
    out, nodata_ids, low_ids, records = [], [], [], []
    for i, f in enumerate(feats):
        fid = feature_id(f, i, args.key.partition("=")[0] if getattr(args, "key", None) else None)
        p = dict(props[i])
        v = values[i]
        label = data.label_of(p, args.label_field, fid)
        cls = c.index(v) if v is not None else -1
        p.update({
            "dm_value": round(v, 6) if v is not None else None,
            "dm_raw": whole(raw[i]),
            "dm_den": whole(den[i]),
            "dm_class": cls,
            "dm_fill": colors[cls] if cls >= 0 else nodata,
            "dm_label": label,
            "dm_tip": tip(label, v, c.e, unit, args, raw[i], den[i]),
        })
        if args.per:
            p["dm_low_n"] = i in low
        if cls < 0:
            nodata_ids.append(fid)
        if i in low:
            low_ids.append(fid)
        if v is not None:
            records.append({"id": fid, "name": label, "value": classify.round_to(v, c.e)})
        if f.get("geometry"):
            out.append(data.feature(fid, p, f["geometry"]))
    findings.append(PASS("nodata", f"{len(nodata_ids)} places with no data draw in {nodata}, apart from every class color", 9))
    if low_ids:
        findings.append(WARN("small-denominators", f"{len(low_ids)} places have {args.per} under {num(args.min_den)}: {', '.join(low_ids[:12])}",
                             "mark them on the map (dm_low_n) and in the legend", 4))
    title = args.title or (f"{field} per {scale:,} {args.per}" if args.per else field)
    layer = {
        "kind": "classes", "title": title, "unit": unit,
        "source": {"value": field, "per": args.per, "scale": scale},
        "method": c.method, "method_reason": method_reason, "k": c.k, "k_reason": k_reason,
        "breaks": c.breaks, "labels": labels, "colors": colors, "counts": counts,
        "gvf": round(g, 3), "gadf": round(a, 3), "candidates": classify.candidates(present, c.k),
        "nodata": {"color": nodata, "label": "No data", "count": len(nodata_ids)},
        "low_n": {"threshold": args.min_den, "count": len(low_ids), "ids": low_ids} if args.min_den is not None else None,
        "scheme": {"type": scheme, "name": pal.name, "midpoint": center, "cvd_safe": pal.blind == 1 if pal.blind is not None else None,
                   "why": scheme_why(scheme, center)},
    }
    records.sort(key=lambda r: (-r["value"], r["id"]))
    answers = {"highest": records[:5], "lowest": records[::-1][:5], "low_n": low_ids, "nodata": nodata_ids}
    decisions = [
        legend.decision("method", c.method, method_reason, "Slocum §5.10"),
        legend.decision("classes", f"k = {c.k}", k_reason, "Slocum §5.8.3"),
        legend.decision("scheme", f"{scheme} {pal.name}", scheme_why(scheme, center), "Slocum §14", "ColorBrewer"),
    ]
    if args.per:
        decisions.insert(0, legend.decision("standardize", f"{field} per {scale:,} {args.per}", "an area fill shows intensity, not totals", "Slocum §4.6.1"))
    elif args.already_normalized:
        decisions.insert(0, legend.decision("standardize", "already normalized", args.already_normalized, "Slocum §4.6.1"))
    return write_layer(args, out, layer, answers, decisions, findings)


def choose_classes(args, xs: list, scheme: str, center: float | None, max_k: int, center_is_mean: bool) -> tuple:
    if args.method == "manual":
        if not args.breaks:
            raise InputError("--method manual needs --breaks B1,B2,...")
        inner = [data.parse_number(b) for b in args.breaks.split(",")]
        if None in inner or any(a >= b for a, b in zip(inner, inner[1:])):
            raise InputError("--breaks must be increasing numbers")
        c = classify.finish("manual", inner, xs, round_breaks=False)
        return c, "breaks given by hand", f"k = {c.k}, from the breaks given"
    if args.method == "auto":
        method, method_reason = classify.auto_method(xs, ordinal=args.ordinal, compared=args.compared, center_is_mean=center_is_mean and scheme == "div")
    else:
        method, method_reason = args.method, "chosen by hand"
    if scheme == "div" and method != "stddev":
        def build(k):
            return classify.diverging_classing(method, xs, max(1, k // 2), center)
        if args.k:
            return build(args.k + args.k % 2), method_reason, f"k = {args.k + args.k % 2}, split evenly around the midpoint"
        c, why = classify.auto_k(build, xs, max_k - max_k % 2, lo_k=4)
        return c, method_reason, why
    def build(k):
        return classify.method_classing(method, xs, k, center)
    if args.k:
        return build(args.k), method_reason, f"k = {args.k}, given"
    if method == "headtail":
        c = build(max_k)
        return c, method_reason, f"k = {c.k}, where the head stopped holding under 40% of the values"
    c, why = classify.auto_k(build, xs, max_k)
    return c, method_reason, why


def scheme_why(scheme: str, center: float | None) -> str:
    if scheme == "div":
        return f"values diverge from a meaningful midpoint ({num(center)}); two hues meet there"
    if scheme == "qual":
        return "categories with no order; hue alone, at even lightness"
    return "a unipolar value; darker means more"


def whole(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


def tip(label: str, v: float | None, e: int, unit: str, args, raw, den) -> str:
    if v is None:
        return f"{label}: no data"
    text = f"{label}: {classify.fmt(classify.round_to(v, e), e)}"
    if unit:
        text += f" {unit}"
    if args.per and raw is not None and den is not None:
        text += f" ({num(raw)} {args.field} / {num(den)} {args.per})"
    return text


def classes_qual(args, feats: list, findings: list) -> int:
    props = [f.get("properties") or {} for f in feats]
    cats = [str(p.get(args.field)) if p.get(args.field) not in (None, "") else None for p in props]
    counts = {}
    for cat in cats:
        if cat is not None:
            counts[cat] = counts.get(cat, 0) + 1
    order = sorted(counts, key=lambda x: (-counts[x], x))
    k = len(order)
    pal_name = args.palette or color.DEFAULT_PALETTE["qual"]
    try:
        pal = color.palette(pal_name, max(3, k), args.reverse)
    except (KeyError, ValueError) as err:
        raise InputError(f"{err}; {k} categories need fewer categories or a longer palette")
    colors = list(pal.colors[:k])
    if k > 7:
        findings.append(WARN("classes", f"{k} categories; readers hold about 7 hues apart", "group small categories into Other", 6))
    findings.append(PASS("classes", f"{k} categories: {', '.join(f'{c} ({counts[c]})' for c in order)}", 6))
    findings += palette_check(color.Palette(pal.name, pal.type, pal.one_hue, tuple(colors), pal.blind), "qual", "qual", args.allow_unsafe_palette)
    nodata = color.nodata_color(tuple(colors))
    out, nodata_ids = [], []
    for i, f in enumerate(feats):
        fid = feature_id(f, i, None)
        p = dict(props[i])
        label = data.label_of(p, args.label_field, fid)
        cls = order.index(cats[i]) if cats[i] is not None else -1
        p.update({"dm_value": None, "dm_raw": None, "dm_den": None, "dm_class": cls,
                  "dm_fill": colors[cls] if cls >= 0 else nodata, "dm_label": label,
                  "dm_tip": f"{label}: {cats[i] if cats[i] is not None else 'no data'}"})
        if cls < 0:
            nodata_ids.append(fid)
        if f.get("geometry"):
            out.append(data.feature(fid, p, f["geometry"]))
    findings.append(PASS("nodata", f"{len(nodata_ids)} places with no data draw in {nodata}", 9))
    layer = {"kind": "classes", "title": args.title or args.field, "unit": args.unit or "",
             "source": {"value": args.field, "per": None, "scale": None}, "method": "categories",
             "method_reason": "nominal data: one class per category", "k": k, "breaks": None,
             "labels": order, "colors": colors, "counts": [counts[c] for c in order],
             "nodata": {"color": nodata, "label": "No data", "count": len(nodata_ids)},
             "scheme": {"type": "qual", "name": pal.name, "cvd_safe": pal.blind == 1 if pal.blind is not None else None,
                        "why": scheme_why("qual", None)}}
    decisions = [legend.decision("scheme", f"qual {pal.name}", scheme_why("qual", None), "Slocum §4.5.2.3")]
    return write_layer(args, out, layer, {"nodata": nodata_ids}, decisions, findings)


def write_layer(args, feats: list, layer: dict, answers: dict, decisions: list, findings: list,
                extra_files: dict | None = None) -> int:
    if any(f.status == "FAIL" for f in findings):
        return emit(findings, args.json)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = args.layer or default_layer(args)
    data.write_geojson(out_dir / f"{name}.geojson", feats)
    written = [f"{name}.geojson"]
    for fname, content in (extra_files or {}).items():
        if isinstance(content, list) and content and content[0].get("type") == "Feature":
            data.write_geojson(out_dir / fname, content)
        else:
            data.write_json(out_dir / fname, content)
        written.append(fname)
    legend.update(out_dir / "legend.json", name, layer, answers, decisions)
    findings.append(PASS("write", f"wrote {', '.join(written)} and merged layer {name!r} into legend.json in {out_dir}"))
    return emit(findings, args.json, {"layer": name, "out_dir": str(out_dir), "legend": layer})


def default_layer(args) -> str:
    return {"classes": "classes", "sizes": "sizes", "flows": "flows"}[args.command]


# sizes

def run_sizes(args) -> int:
    findings = []
    feats = load_layer(args, findings)
    try:
        kind, k = symbols.scaling_name(args.scaling)
    except ValueError as err:
        raise InputError(str(err))
    props = [f.get("properties") or {} for f in feats]
    values = [data.parse_number(p.get(args.field)) for p in props]
    present = sorted(v for v in values if v is not None)
    if not present:
        raise InputError(f"no numeric values in {args.field}")
    if present[0] < 0:
        findings.append(FAIL("negative", f"{args.field} has negative values; a circle's area can't be negative",
                             "map the sign with color, or draw gains and losses as two layers"))
        return emit(findings, args.json)
    vkind, why = kind_of(args.field, feats)
    if vkind == "rate":
        findings.append(WARN("totals", f"{args.field} reads as a rate ({why}); proportional symbols show totals",
                             "size by the count, and put the rate in a choropleth or the tooltip"))
    vmax = present[-1]
    if kind == "graduated":
        c = classify.method_classing("jenks", present, k)
        radii = symbols.graded_radii(c.k, args.rmax)
        rad = [radii[c.index(v)] if v is not None else 0.0 for v in values]
        lvals = c.labels()[::-1]
        lradii = radii[::-1]
        findings.append(PASS("scaling", f"range-graded: {c.k} Jenks classes drawn at Dent's radii, scaled to {num(args.rmax)} px", 13))
    else:
        rad = [symbols.radius(v, vmax, args.rmax, kind) if v is not None else 0.0 for v in values]
        lvals = symbols.legend_values(present[0], vmax)
        lradii = [round(symbols.radius(v, vmax, args.rmax, kind), 2) for v in lvals]
        how = "area true to value: r = rmax * sqrt(v / vmax)" if kind == "area" else "Flannery: r = rmax * (v / vmax)^0.5716"
        findings.append(PASS("scaling", f"{how}, rmax {num(args.rmax)} px at {num(vmax)}", 13))
    if args.rmin:
        raised = sum(1 for r, v in zip(rad, values) if v is not None and r < args.rmin)
        rad = [max(r, args.rmin) if v is not None else r for r, v in zip(rad, values)]
        if raised:
            findings.append(WARN("rmin", f"{raised} symbols raised to {num(args.rmin)} px overstate their values",
                                 "say so in the legend, or drop --rmin", 13))
    order = symbols.order_largest_first(values)
    findings.append(PASS("order", "largest symbols draw first, so small ones stay on top", 14))
    findings.append(PASS("legend", f"nested values {', '.join(str(v) if isinstance(v, str) else num(v) for v in lvals)} at radii {', '.join(num(r, -1) for r in lradii)} px, by the same scaling", 14))
    out, records = [], []
    key = args.key.partition("=")[0] if getattr(args, "key", None) else None
    for i, f in enumerate(feats):
        if not f.get("geometry") or values[i] is None:
            continue
        fid = feature_id(f, i, key)
        p = dict(props[i])
        label = data.label_of(p, args.label_field, fid)
        p.update({"dm_value": values[i], "dm_r": round(rad[i], 2), "dm_order": order[i], "dm_fill": args.color,
                  "dm_label": label, "dm_tip": f"{label}: {num(values[i])}" + (f" {args.unit}" if args.unit else "")})
        out.append(data.feature(fid, p, {"type": "Point", "coordinates": geo.representative_point(f["geometry"])}))
        records.append({"id": fid, "name": label, "value": values[i]})
    records.sort(key=lambda r: (-r["value"], r["id"]))
    layer = {"kind": "sizes", "title": args.title or args.field, "unit": args.unit or "", "scaling": args.scaling,
             "rmax": args.rmax, "rmin": args.rmin, "vmax": vmax, "legend_values": lvals, "legend_radii": [round(r, 2) for r in lradii],
             "fill": args.color}
    decisions = [legend.decision("scaling", args.scaling, "symbol area carries the value" if kind == "area" else "chosen by hand", "Slocum §17.5"),
                 legend.decision("order", "largest first", "small symbols stay visible on top", "Slocum §17.7.2")]
    answers = {"largest": records[:5], "smallest": records[::-1][:5]}
    return write_layer(args, out, layer, answers, decisions, findings)


# flows

def read_nodes(args) -> dict:
    t = data.read_table(Path(args.nodes))
    nid = data.find_column(t.columns, data.ID_NAMES, args.id)
    lon = data.find_column(t.columns, data.LON_NAMES, args.lon)
    lat = data.find_column(t.columns, data.LAT_NAMES, args.lat)
    if not (nid and lon and lat):
        raise InputError(f"--nodes needs id, lon, and lat columns (--id, --lon, --lat); it has {', '.join(t.columns)}")
    label = data.find_column(t.columns, data.LABEL_NAMES)
    nodes = {}
    for r in t.rows:
        x, y = data.parse_number(r[lon]), data.parse_number(r[lat])
        if x is None or y is None:
            continue
        key = str(r[nid]).strip()
        nodes[key] = flows.Node(key, x, y, r[label] if label else key)
    return nodes


def run_flows(args) -> int:
    findings = []
    t = data.read_table(Path(args.input))
    o = data.find_column(t.columns, data.ORIGIN_NAMES, args.origin)
    d = data.find_column(t.columns, data.DEST_NAMES, args.dest)
    vcol = data.find_column(t.columns, data.VALUE_NAMES, args.value)
    if not vcol and not args.value:
        rest = [c for c in data.numeric_columns(t.columns, t.rows) if c not in (o, d)]
        vcol = rest[0] if len(rest) == 1 else None
    if not (o and d and vcol):
        raise InputError(f"{args.input} needs origin, destination, and value columns (--origin, --dest, --value); it has {', '.join(t.columns)}")
    nodes = read_nodes(args)
    findings += extent_lines(Path(args.nodes).name, [n.pos for n in nodes.values()])
    if any(f.status == "FAIL" for f in findings):
        return emit(findings, args.json)
    rows, unknown, bad = [], set(), 0
    for r in t.rows:
        a, b, v = str(r[o]).strip(), str(r[d]).strip(), data.parse_number(r[vcol])
        if v is None or v < 0:
            bad += 1
            continue
        missing = [x for x in (a, b) if x not in nodes]
        if missing:
            unknown.update(missing)
            continue
        rows.append((a, b, v))
    if unknown:
        findings.append(WARN("nodes", f"flows to or from {len(unknown)} ids with no node are dropped: {', '.join(sorted(unknown)[:12])}",
                             "add those nodes, or say which places are missing", 3))
    if bad:
        findings.append(WARN("values", f"{bad} rows with no value or a negative one are dropped", "check the value column"))
    all_flows, loops = flows.aggregate(rows)
    if loops:
        findings.append(PASS("loops", f"{loops} flows from a place to itself left out; show them on the node, not as lines"))
    if not all_flows:
        raise InputError("no flows to draw")
    totals = flows.node_totals(all_flows)
    drawn = flows.net(all_flows) if args.net else all_flows
    kept, share = flows.keep_top(drawn, args.top, args.share)
    unit = args.unit or vcol
    note = flows.omitted_note(len(kept), len(drawn), share, unit)
    limit = flows.HAIRBALL[args.geometry]
    if args.top is None and args.share is None and len(drawn) > limit:
        findings.append(WARN("top-n", f"{len(drawn)} flows drawn at once tangle into a hairball", f"pass --top or --share; past {limit} flows the lines stop reading", 18))
    else:
        findings.append(PASS("top-n", note, 18))
    # Curves clear only the nodes the map draws, which are the ends of the kept flows.
    drawn_nodes = {x for f in kept for x in (f.o, f.d)}
    placed = flows.place(kept, {k: n for k, n in nodes.items() if k in drawn_nodes}, args.geometry)
    vmax = max(f.value for f in kept)
    vmin = min(f.value for f in kept)
    fade_min = 1.0 if args.no_fade else args.fade_min
    color = args.color
    order = {p.flow: rank for rank, p in enumerate(sorted(placed, key=lambda p: (-p.flow.value, p.flow.o, p.flow.d)))}
    pair_set = {(p.flow.o, p.flow.d) for p in placed}
    reciprocal = sum(1 for p in placed if (p.flow.d, p.flow.o) in pair_set) // 2
    lines, arrows, arcs = [], [], []
    node_ids = {key: i + 1 for i, key in enumerate(sorted({x for p in placed for x in (p.flow.o, p.flow.d)}))}
    gross_max = max(totals[k]["gross"] for k in node_ids)
    node_r = {k: symbols.radius(totals[k]["gross"], gross_max, flows.NODE_RMAX) for k in node_ids}
    split = 0
    for fid, p in enumerate(sorted(placed, key=lambda p: order[p.flow]), start=1):
        f = p.flow
        w = round(flows.width(f.value, vmax, args.max_width, args.min_width), 2)
        g = geo.line_geometry(p.coords)
        split += g["type"] == "MultiLineString"
        label = f"{nodes[f.o].label} to {nodes[f.d].label}"
        text = f"{label}: {num(f.value)} {unit}"
        if f.forward is not None and f.reverse:
            text += f" net ({num(f.forward)} out, {num(f.reverse)} back)"
        alpha = flows.opacity(f.value, vmin, vmax, fade_min)
        offset = flows.side_offset(w) if (f.d, f.o) in pair_set else 0
        props = {"dm_o": f.o, "dm_d": f.d, "dm_value": f.value, "dm_width": w, "dm_offset": offset, "dm_opacity": alpha,
                 "dm_order": order[f], "dm_km": round(p.km, 1), "dm_fill": color,
                 "dm_label": label, "dm_tip": text}
        # Six decimals, about 0.1 m: at five, rounding turns the vertices of a short curve by several degrees.
        lines.append(data.feature(fid, props, g, nd=6))
        arrows.append(data.feature(fid, {"dm_o": f.o, "dm_d": f.d, "dm_value": f.value, "dm_bearing": round(geo.end_bearing(p.coords), 2),
                                         "dm_arrow": round(flows.arrow_size(w), 2), "dm_width": w, "dm_offset": offset, "dm_opacity": alpha,
                                         "dm_order": order[f], "dm_setback": round(node_r[f.d], 2), "dm_fill": color},
                                   {"type": "Point", "coordinates": nodes[f.d].pos}))
        arcs.append({"source": data.round_coords(nodes[f.o].pos), "target": data.round_coords(nodes[f.d].pos), "value": f.value,
                     "width": w, "color": color, "opacity": alpha, "km": round(p.km, 1)})
    node_order = symbols.order_largest_first([totals[k]["gross"] for k in node_ids])
    node_feats = []
    for (key, nid), rank in zip(node_ids.items(), node_order):
        tt = totals[key]
        node_feats.append(data.feature(nid, {"dm_key": key, "dm_label": nodes[key].label, "dm_value": tt["gross"],
                                             "dm_r": round(node_r[key], 2), "dm_order": rank, "dm_fill": flows.NODE_COLOR,
                                             "dm_tip": f"{nodes[key].label}: {num(tt['out'])} out, {num(tt['in'])} in, {num(tt['gross'])} in all"},
                                       {"type": "Point", "coordinates": nodes[key].pos}))
    if args.geometry == "curved":
        findings.append(PASS("curves", f"each flow bows to the right of travel, more for longer flows (curvature {flows.CURVE_MIN} to {flows.CURVE_MAX}); {reciprocal} reciprocal {'pair sits' if reciprocal == 1 else 'pairs sit'} on opposite sides", 15))
    else:
        findings.append(PASS("great-circles", f"great circles densified every {flows.DENSIFY_DEG:g} degree; {reciprocal} reciprocal {'pair' if reciprocal == 1 else 'pairs'} offset to either side", 15))
    moved = [p for p in placed if p.clear and (p.side, p.curvature) != (1, flows.curvature_for(p.km, *km_range(placed)))]
    stuck = [p for p in placed if not p.clear]
    if args.geometry == "curved":
        findings.append(PASS("clearance", f"{len(moved)} flows flipped or bent further to clear nodes they don't connect", 16))
    if stuck:
        names = ", ".join(f"{p.flow.o} to {p.flow.d} (near {', '.join(p.near)})" for p in stuck[:8])
        findings.append(WARN("clearance", f"{len(stuck)} flows still pass within {flows.CLEARANCE_SHARE:.0%} of their length of an unconnected node: {names}",
                             "move or drop the node, use --net, or pick another geometry", 16))
    else:
        findings.append(PASS("clearance", f"no flow passes within {flows.CLEARANCE_SHARE:.0%} of its length of a node it doesn't connect", 16))
    findings.append(PASS("antimeridian", f"{split} flows split into two parts at 180, with a vertex on the meridian", 20))
    findings.append(PASS("arrows", f"one arrowhead per flow at its destination, {flows.ARROW_RATIO:g} times the width and at least {flows.ARROW_MIN_PX:g} px", 17))
    findings.append(PASS("order", "small flows draw on top of large ones", 19))
    if fade_min < 1:
        findings.append(PASS("fade", f"opacity runs from {fade_min:g} at the smallest kept flow ({num(vmin)}) to 1 at the largest ({num(vmax)}), linear in value"))
    lvals = flows.legend_values(vmin, vmax, args.max_width, args.min_width)
    lwidths = [round(flows.width(v, vmax, args.max_width, args.min_width), 2) for v in lvals]
    lopacities = [flows.opacity(v, vmin, vmax, fade_min) for v in lvals]
    name = args.layer or "flows"
    layer = {"kind": "flows", "title": args.title or unit, "unit": unit, "geometry": args.geometry, "color": color,
             "kept": len(kept), "total": len(drawn), "kept_share": round(share, 4), "omitted_note": note, "net": bool(args.net),
             "width": {"min_px": args.min_width, "max_px": args.max_width, "vmax": vmax, "scale": "linear"},
             "fade": {"min": fade_min, "vmin": vmin, "vmax": vmax, "scale": "linear"},
             "legend_values": lvals, "legend_widths": lwidths, "legend_opacities": lopacities,
             "arrow": {"ratio": flows.ARROW_RATIO, "min_px": flows.ARROW_MIN_PX},
             "nodes": {"rmax": flows.NODE_RMAX, "scaling": "area", "value": "gross", "title": flows.nodes_title(unit, len(all_flows))},
             "files": {"lines": f"{name}.geojson", "nodes": f"{name}-nodes.geojson", "arrows": f"{name}-arrows.geojson", "arcs": f"{name}-arcs.json"}}
    decisions = [
        legend.decision("geometry", args.geometry, "curves separate reciprocal and overlapping flows" if args.geometry == "curved" else "great circles on a globe", "Jenny et al. 2018 §4.1"),
        legend.decision("width", "linear in value", "the accepted quantity encoding for flows", "Jenny et al. 2018 §4.2"),
        legend.decision("fade", f"opacity {fade_min:g} to 1, linear in value" if fade_min < 1 else "none",
                        "larger flows darker, faded by magnitude and never by length" if fade_min < 1 else "--no-fade",
                        "Jenny et al. 2018 §4.2", "Slocum §20.7.2.1"),
        legend.decision("top-n", note, "fewer flows read; the cut is stated", "Jenny et al. 2018", "Yang et al. 2019"),
    ]
    files = {f"{name}-nodes.geojson": node_feats, f"{name}-arrows.geojson": arrows, f"{name}-arcs.json": arcs}
    return write_layer(args, lines, layer, flows.answers(all_flows, nodes, totals), decisions, findings, files)


def km_range(placed: list) -> tuple:
    kms = [p.km for p in placed]
    return min(kms), max(kms)


# registration

def add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--json", action="store_true", help="print one JSON object instead of lines")


def add_layer_output(p: argparse.ArgumentParser) -> None:
    p.add_argument("--layer", help="layer name; names the output file and the legend.json entry")
    p.add_argument("--out-dir", required=True, help="the project's data folder, such as OUT/data")
    p.add_argument("--title", help="legend title")
    p.add_argument("--unit", help="unit for the legend and tooltips")
    p.add_argument("--label-field", help="property that names each place")


def add_input(p: argparse.ArgumentParser) -> None:
    p.add_argument("input", metavar="IN", help="GeoJSON, a CSV with lon/lat, or a CSV joined with --geo")
    p.add_argument("--field", required=True, help="the numeric property to map")
    p.add_argument("--geo", help="GeoJSON to join a CSV to, or 'countries' for the bundled Natural Earth 110m")
    p.add_argument("--key", help="join key: COL (same name both sides) or CSVCOL=PROP; PROP 'id' means the feature id")
    p.add_argument("--lon", help="longitude column of a point CSV")
    p.add_argument("--lat", help="latitude column of a point CSV")


def positive(text: str) -> float:
    v = float(text)
    if v <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return v


def share(text: str) -> float:
    v = float(text)
    if not 0 < v <= 1:
        raise argparse.ArgumentTypeError("a share between 0 and 1")
    return v


def hex_color(text: str) -> str:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        raise argparse.ArgumentTypeError("a color as #rrggbb")
    return text.lower()


def register(sub) -> None:
    p = sub.add_parser("inspect", help="profile data: columns, skew, count or rate, extent, OD columns, unmatched join keys",
                       description="Profiles CSV and GeoJSON files before anything is drawn.")
    p.add_argument("data", nargs="+", metavar="DATA", help="CSV or GeoJSON files ('countries' for the bundled world)")
    p.add_argument("--join", action="append", metavar="CSV:COL=GEOJSON:PROP", help="report keys on either side that match nothing")
    add_common(p)
    p.set_defaults(run=run_inspect)

    p = sub.add_parser("geo", help="densified boundaries, graticule, and sphere outline for a CRS or a globe",
                       description="Writes boundaries densified along their own edges, a graticule, or the world outline.")
    p.add_argument("input", nargs="?", metavar="IN", help="GeoJSON to densify")
    p.add_argument("--countries", action="store_true", help="use the bundled Natural Earth 110m countries")
    p.add_argument("--densify", type=positive, metavar="KM", help="add vertices so no edge is longer than KM")
    p.add_argument("--graticule", type=positive, metavar="DEG", help="meridians and parallels every DEG degrees")
    p.add_argument("--sphere", action="store_true", help="the world outline polygon, for an ocean fill under a CRS")
    p.add_argument("--out", required=True, metavar="F", help="output GeoJSON")
    add_common(p)
    p.set_defaults(run=run_geo)

    p = sub.add_parser("crs", help="recommend a projection from the extent and idiom",
                       description="Recommends an equal-area projection (or the globe) from the data's extent, with its proj4 definition.")
    p.add_argument("--extent", required=True, help="world, W,S,E,N, or a data file; write --extent=W,S,E,N when W is negative")
    p.add_argument("--idiom", choices=["area", "points", "flows"], default="area")
    p.add_argument("--interactive", action="store_true", help="the reader can pan and rotate")
    add_common(p)
    p.set_defaults(run=run_crs)

    p = sub.add_parser("classes", help="class breaks, colors, and legend for a choropleth; refuses raw counts",
                       description="Classes a rate for an area fill and writes dm_class and dm_fill into each feature.")
    add_input(p)
    p.add_argument("--per", help="denominator column; the map shows field / per * scale")
    p.add_argument("--scale", type=positive, help="multiplier for the rate, such as 100000; chosen from the data when left out")
    p.add_argument("--method", choices=["auto", "quantile", "equal", "jenks", "stddev", "headtail", "manual"], default="auto")
    p.add_argument("--breaks", help="inner breaks for --method manual, as B1,B2,...")
    p.add_argument("--k", type=int, help="number of classes; chosen by GADF when left out")
    p.add_argument("--scheme", default="seq", help="seq, div:MID (a number or mean), or qual")
    p.add_argument("--palette", help="a ColorBrewer name, or #rrggbb,#rrggbb,...")
    p.add_argument("--reverse", action="store_true", help="reverse the palette")
    p.add_argument("--allow-unsafe-palette", action="store_true", help="keep a palette that colorblind readers can't separate")
    p.add_argument("--min-den", type=float, metavar="N", help="flag places whose denominator is under N")
    p.add_argument("--already-normalized", metavar="REASON", help="the field is already a rate; say why")
    p.add_argument("--ordinal", action="store_true", help="the values are ranks")
    p.add_argument("--compared", action="store_true", help="the map will be compared with others or paired in a bivariate map")
    add_layer_output(p)
    add_common(p)
    p.set_defaults(run=run_classes)

    p = sub.add_parser("sizes", help="proportional symbol radii true to area, a nested legend, and draw order",
                       description="Sizes a symbol per feature so its area carries the value.")
    add_input(p)
    p.add_argument("--rmax", type=positive, default=28.0, help="radius of the largest symbol in CSS px")
    p.add_argument("--rmin", type=positive, help="smallest radius drawn; raising small symbols overstates them")
    p.add_argument("--scaling", default="area", help="area, flannery, or graduated:K (K from 3 to 5)")
    p.add_argument("--color", default=SYMBOL_COLOR, help="symbol fill")
    add_layer_output(p)
    add_common(p)
    p.set_defaults(run=run_sizes)

    p = sub.add_parser("flows", help="flow lines, arrows, nodes, and deck.gl arcs from an OD table",
                       description="Builds curved or great-circle flows with widths, arrows, and draw order from origin-destination pairs.")
    p.add_argument("input", metavar="OD.csv", help="origin, destination, value rows")
    p.add_argument("--nodes", required=True, metavar="N.csv", help="id, lon, lat (and name) per place")
    p.add_argument("--origin", metavar="C")
    p.add_argument("--dest", metavar="C")
    p.add_argument("--value", metavar="C")
    p.add_argument("--id", metavar="C", help="node id column")
    p.add_argument("--lon", metavar="C")
    p.add_argument("--lat", metavar="C")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--top", type=int, metavar="N", help="keep the N largest flows")
    g.add_argument("--share", type=share, metavar="S", help="keep the largest flows carrying share S of the total")
    p.add_argument("--net", action="store_true", help="one flow per pair, in the net direction")
    p.add_argument("--geometry", choices=["curved", "great-circle"], default="curved")
    p.add_argument("--max-width", type=positive, default=12.0, metavar="PX")
    p.add_argument("--min-width", type=positive, default=1.0, metavar="PX")
    p.add_argument("--color", type=hex_color, default=flows.FLOW_COLOR, metavar="HEX",
                   help=f"one color for every flow and arrowhead (default {flows.FLOW_COLOR}, a dark warm orange-brown)")
    p.add_argument("--fade-min", type=share, default=flows.FADE_MIN, metavar="A",
                   help=f"opacity of the smallest kept flow; the largest is 1 (default {flows.FADE_MIN:g})")
    p.add_argument("--no-fade", action="store_true", help="draw every flow fully opaque")
    add_layer_output(p)
    add_common(p)
    p.set_defaults(run=run_flows)
