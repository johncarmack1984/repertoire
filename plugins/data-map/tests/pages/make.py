#!/usr/bin/env python3
"""Rebuild the fixture map projects in this folder through the real pipeline: the levers write
data/, `new` copies the template, the slots are filled, and `sync` inlines everything.

  python3 plugins/data-map/tests/pages/make.py [--out DIR] [NAME...]

test_check.py runs it into a temporary folder once per run, so the fixtures always come from the
current levers and templates and nothing generated is committed.
"""
from __future__ import annotations

import csv
import json
import math
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[1] / "skills" / "data-map"
CLI = SKILL / "scripts" / "datamap.py"
COUNTRIES = SKILL / "assets" / "geo" / "world-110m.json"
sys.path.insert(0, str(SKILL / "scripts"))
from dm.crs import WORLD_LON0 as LON0  # noqa: E402


def dm(*args) -> None:
    run = subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True)
    if run.returncode != 0:
        sys.exit(f"datamap.py {' '.join(map(str, args))} failed:\n{run.stdout}{run.stderr}")
    for line in run.stdout.splitlines():
        if line.startswith(("WARN", "FAIL")):
            print(f"  {args[0]}: {line}")


def write_csv(path: Path, header: list, rows: list) -> Path:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def fill(out: Path, *, title: str, subtitle: str, source: str, credits: str, spec: dict) -> None:
    page = out / "index.html"
    text = page.read_text(encoding="utf-8")
    for key, value in (("dm-title", title), ("dm-subtitle", subtitle), ("dm-source", source), ("dm-credits", credits)):
        text = re.sub(rf'(<[a-z0-9]+ id="{key}">).*?(</)', lambda m: m[1] + value + m[2], text, count=1)
    text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text, count=1)
    m = re.search(r'(<script type="application/json" id="dm-spec">\n)(.*?)(\n</script>)', text, re.S)
    current = json.loads(m[2])
    current.update(spec)
    text = text[:m.start(2)] + json.dumps(current, indent=1, ensure_ascii=False) + text[m.end(2):]
    page.write_text(text, encoding="utf-8")
    brief = out / "brief.md"
    brief.write_text(brief.read_text(encoding="utf-8").replace("Reader:\n", f"Reader: anyone reading the fixture page ({out.name})\n"),
                     encoding="utf-8")


def ring_area_km2(ring: list) -> float:
    r = 6371.0088
    total = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        total += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(total) * r * r / 2


def area_km2(geom: dict) -> float:
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    return sum(ring_area_km2(p[0]) - sum(ring_area_km2(h) for h in p[1:]) for p in polys)


PACIFIC = {
    "SYD": ("Sydney", 151.21, -33.87, 5.3), "MEL": ("Melbourne", 144.96, -37.81, 5.1), "AKL": ("Auckland", 174.76, -36.85, 1.7),
    "TYO": ("Tokyo", 139.69, 35.69, 37.0), "SEL": ("Seoul", 126.98, 37.57, 25.0),
    "SHA": ("Shanghai", 121.47, 31.23, 28.0), "MNL": ("Manila", 120.98, 14.60, 14.0), "SIN": ("Singapore", 103.82, 1.35, 5.9),
    "JKT": ("Jakarta", 106.85, -6.21, 11.0), "LAX": ("Los Angeles", -118.24, 34.05, 12.5), "SFO": ("San Francisco", -122.42, 37.77, 6.7),
    "VAN": ("Vancouver", -123.12, 49.28, 2.6), "SEA": ("Seattle", -122.33, 47.61, 4.0), "HNL": ("Honolulu", -157.86, 21.31, 1.0),
    "LIM": ("Lima", -77.04, -12.05, 11.0), "SCL": ("Santiago", -70.67, -33.45, 6.9), "MEX": ("Mexico City", -99.13, 19.43, 22.0),
}


def pacific_inputs(tmp: Path) -> tuple[Path, Path]:
    """Movers between Pacific Rim cities: a gravity model with a seeded lean in each direction. Synthetic."""
    rng = random.Random(20261115)
    nodes = write_csv(tmp / "nodes.csv", ["id", "name", "lon", "lat"], [[k, v[0], v[1], v[2]] for k, v in PACIFIC.items()])
    rows = []
    for o, (_, lon1, lat1, p1) in PACIFIC.items():
        for d, (_, lon2, lat2, p2) in PACIFIC.items():
            if o == d:
                continue
            a, b = math.radians(lat1), math.radians(lat2)
            km = 6371 * math.acos(min(1, math.sin(a) * math.sin(b) + math.cos(a) * math.cos(b) * math.cos(math.radians(lon2 - lon1))))
            lean = 1.0 + 0.9 * rng.random()
            rows.append([o, d, round(9000 * p1 * p2 * lean / (km / 1000 + 1.5) ** 1.1 / 40)])
    od = write_csv(tmp / "od.csv", ["origin", "dest", "movers"], rows)
    return od, nodes


def movers_series(out: Path) -> None:
    years = list(range(2016, 2026))
    trans = [41, 43, 44, 46, 31, 35, 44, 49, 52, 55]
    within = [88, 90, 93, 95, 79, 84, 92, 96, 99, 101]
    (out / "data" / "movers-by-year.json").write_text(json.dumps({
        "unit": "thousand movers", "x": years,
        "series": [{"name": "Across the Pacific", "values": trans}, {"name": "Within Asia", "values": within}]}, indent=1) + "\n")


def build_maplibre_crs(out: Path, tmp: Path) -> None:
    world = json.loads(COUNTRIES.read_text())
    rows = []
    for f in world["features"]:
        if f["id"] == "ATA":
            continue
        p = f["properties"]
        rows.append([f["id"], p["name"], p["pop_est"], round(area_km2(f["geometry"]))])
    src = write_csv(tmp / "population.csv", ["iso_a3", "name", "pop_est", "area_km2"], rows)
    dense = tmp / "countries.geojson"
    dm("geo", "--countries", "--densify", 250, "--lon0", LON0, "--out", dense)
    # Antarctica has no permanent population, so it is left off, as a world rate map usually leaves it.
    countries = json.loads(dense.read_text())
    countries["features"] = [f for f in countries["features"] if f.get("id") != "ATA"]
    dense.write_text(json.dumps(countries))
    dm("new", "maplibre", out, "--preset", "equal-earth", "--force")
    dm("geo", "--sphere", "--graticule", 30, "--lon0", LON0, "--out", out / "data" / "frame.geojson")
    dm("classes", src, "--field", "pop_est", "--per", "area_km2", "--scale", 1, "--geo", dense, "--key", "iso_a3=id",
       "--method", "quantile", "--k", 5, "--palette", "YlGnBu", "--layer", "density", "--out-dir", out / "data",
       "--title", "People per square kilometer", "--unit", "people per km²", "--label-field", "name")
    fill(out, title="Bangladesh packs more people into each square kilometer than any other country",
         subtitle="People per square kilometer of land, by country, 2019",
         source="Source: Natural Earth, Admin 0 Countries 1:110m, v5.1.2 (population estimates for 2019); land area measured from the same boundaries.",
         credits="Equal Earth projection. Antarctica, with no permanent population, is left off.",
         spec={"idiom": ["choropleth"], "extent": "world",
               "companions": [{"type": "bars", "layer": "density", "title": "The ten most crowded countries", "top": 10}]})


def build_maplibre_globe(out: Path, tmp: Path) -> None:
    od, nodes = pacific_inputs(tmp)
    dm("new", "maplibre", out, "--preset", "globe", "--force")
    dm("geo", "--countries", "--out", out / "data" / "land.geojson")
    dm("geo", "--graticule", 30, "--out", out / "data" / "graticule.geojson")
    dm("flows", od, "--nodes", nodes, "--origin", "origin", "--dest", "dest", "--value", "movers", "--label-field", "name",
       "--geometry", "great-circle", "--top", 30, "--max-width", 8, "--layer", "movers", "--out-dir", out / "data",
       "--title", "Movers per year", "--unit", "movers")
    fill(out, title="Two thirds of moves around the Pacific stay on its western side",
         subtitle="People moving between 17 Pacific Rim cities in a year, the 30 largest flows",
         source="Source: synthetic test data for the data-map plugin.",
         credits="Boundaries: Natural Earth.",
         spec={"idiom": ["flows"], "extent": "world",
               "companions": [{"type": "bars", "layer": "movers", "title": "The largest flows", "top": 8},
                              {"type": "matrix", "layer": "movers", "title": "From each city to each city", "top": 7}]})


def build_deck_globe(out: Path, tmp: Path) -> None:
    od, nodes = pacific_inputs(tmp)
    dm("new", "deck-gl", out, "--preset", "globe", "--force")
    dm("geo", "--countries", "--out", out / "data" / "land.geojson")
    dm("flows", od, "--nodes", nodes, "--origin", "origin", "--dest", "dest", "--value", "movers", "--label-field", "name",
       "--geometry", "great-circle", "--top", 30, "--max-width", 8, "--layer", "movers", "--out-dir", out / "data",
       "--title", "Movers per year", "--unit", "movers")
    movers_series(out)
    page = out / "index.html"
    spec = json.loads(re.search(r'id="dm-spec">\n(.*?)\n</script>', page.read_text(), re.S)[1])
    decisions = spec["decisions"]
    decisions[0]["why"] = "the arcs separate the many flows that share Tokyo, Seoul, and Los Angeles, which flat lines stack on top of each other"
    fill(out, title="Two thirds of moves around the Pacific stay on its western side",
         subtitle="People moving between 17 Pacific Rim cities in a year, the 30 largest flows, as raised arcs",
         source="Source: synthetic test data for the data-map plugin.",
         credits="Boundaries: Natural Earth.",
         spec={"decisions": decisions,
               "companions": [{"type": "series", "data": "movers-by-year", "title": "Movers per year, in thousands"},
                              {"type": "bars", "layer": "movers", "title": "The largest flows", "top": 8}]})


def build_maplibre_mercator(out: Path, tmp: Path) -> None:
    rng = random.Random(7)
    sites = [("North Fork", -121.9, 46.9), ("Cedar Gap", -120.6, 44.1), ("Rim Lake", -119.2, 47.8), ("Pine Hollow", -117.4, 45.6),
             ("Dry Creek", -116.1, 43.5), ("Stone Bend", -122.6, 42.4), ("Elk Flats", -118.3, 42.9), ("Blue Canyon", -115.2, 46.2),
             ("Mill Pond", -123.4, 44.9), ("Twin Buttes", -114.6, 44.1), ("Hollow Rock", -120.9, 41.8), ("Lower Basin", -116.9, 48.3)]
    rows = [[f"R{i:02d}", n, lon, lat, round(2400 * rng.random() ** 2.2 + 40)] for i, (n, lon, lat) in enumerate(sites)]
    src = write_csv(tmp / "reservoirs.csv", ["id", "name", "lon", "lat", "capacity"], rows)
    dm("new", "maplibre", out, "--preset", "mercator", "--force")
    world = json.loads(COUNTRIES.read_text())
    near = {**world, "features": [f for f in world["features"] if f["id"] in ("USA", "CAN", "MEX")]}
    (tmp / "near.geojson").write_text(json.dumps(near))
    dm("geo", tmp / "near.geojson", "--out", out / "data" / "land.geojson")
    rivers = [[(-123.9, 46.2), (-121.5, 45.6), (-119.3, 46.1), (-116.9, 46.4), (-114.9, 47.6)],
              [(-119.3, 46.1), (-117.0, 44.0), (-115.0, 42.6)]]
    (tmp / "rivers.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "id": f"river-{i}", "properties": {}, "geometry": {"type": "LineString", "coordinates": line}}
        for i, line in enumerate(rivers)]}))
    dm("geo", tmp / "rivers.geojson", "--densify", 50, "--out", out / "data" / "base-rivers.geojson")
    dm("sizes", src, "--field", "capacity", "--lon", "lon", "--lat", "lat", "--label-field", "name", "--rmax", 26,
       "--layer", "capacity", "--out-dir", out / "data", "--title", "Reservoir capacity", "--unit", "million m³")
    fill(out, title="Rim Lake alone holds more than a quarter of the region's storage",
         subtitle="Storage capacity of 12 reservoirs, million cubic meters",
         source="Source: synthetic test data for the data-map plugin.",
         credits="Boundaries: Natural Earth.",
         spec={"idiom": ["proportional-symbols"], "extent": "region",
               "companions": [{"type": "table", "layer": "capacity", "title": "Capacity by reservoir", "top": 6}]})


STATIONS = {
    "S01": ("Union Station", -122.6766, 45.5318, 1), "S02": ("Pearl District", -122.6828, 45.5290, 1),
    "S03": ("Pioneer Square", -122.6790, 45.5190, 1), "S04": ("PSU Urban Center", -122.6823, 45.5120, 1),
    "S05": ("Waterfront Park", -122.6716, 45.5150, 1), "S06": ("Rose Quarter", -122.6668, 45.5310, 1),
    "S07": ("Lloyd Center", -122.6535, 45.5320, 0), "S08": ("Buckman", -122.6540, 45.5160, 0),
    "S09": ("Hosford", -122.6490, 45.5050, 0), "S10": ("South Waterfront", -122.6713, 45.4990, 1),
    "S11": ("Goose Hollow", -122.6930, 45.5180, 0), "S12": ("Northwest 23rd", -122.6985, 45.5300, 0),
    "S13": ("Eliot", -122.6650, 45.5440, 0), "S14": ("Kerns", -122.6440, 45.5235, 0),
}
# Both apart from the flows' orange-brown, so a circle never reads as the end of a line.
GAIN, LOSS = "#2166ac", "#762a83"


def build_maplibre_flows(out: Path, tmp: Path) -> None:
    """Trips between bike stations: curved flows with the flows lever's --reveal and net-node contract added by hand.

    Until the lever writes them, this adds what the page reads: dm_rank on every line and arrow, a reveal block for
    the 25 largest of 100 written flows, and nodes in net mode (signed dm_net, a gain or loss dm_fill, sizes by the
    size of the net, and the legend's value, legend_values, legend_radii, and colors). Synthetic.
    """
    rng = random.Random(20261116)
    nodes = write_csv(tmp / "stations.csv", ["id", "name", "lon", "lat"], [[k, v[0], v[1], v[2]] for k, v in STATIONS.items()])
    rows = []
    for o, (_, lon1, lat1, low1) in STATIONS.items():
        for d, (_, lon2, lat2, low2) in STATIONS.items():
            if o != d:
                km = math.hypot((lon2 - lon1) * 78.0, (lat2 - lat1) * 111.2)
                # Riders coast down into the low stations and take the bus back up.
                lean = (1.7 if low2 and not low1 else 1.0) * (0.6 + 0.8 * rng.random())
                rows.append([o, d, max(1, round(900 * lean / (km + 0.6) ** 1.6))])
    od = write_csv(tmp / "trips.csv", ["origin", "dest", "trips"], rows)
    dm("new", "maplibre", out, "--preset", "mercator", "--force")
    dm("flows", od, "--nodes", nodes, "--origin", "origin", "--dest", "dest", "--value", "trips", "--label-field", "name",
       "--geometry", "curved", "--top", 100, "--max-width", 7, "--layer", "trips", "--out-dir", out / "data",
       "--title", "Trips in October", "--unit", "trips")
    folder = out / "data"
    shown = 25
    lines, arrows, node_fc = (json.loads((folder / f).read_text()) for f in ("trips.geojson", "trips-arrows.geojson", "trips-nodes.geojson"))
    legend = json.loads((folder / "legend.json").read_text())
    L = legend["layers"]["trips"]
    for fc in (lines, arrows):
        for f in fc["features"]:
            f["properties"]["dm_rank"] = f["properties"]["dm_order"] + 1
    written = sorted(f["properties"]["dm_value"] for f in lines["features"])[::-1]
    whole = sum(written) / L["kept_share"]
    share = sum(written[:shown]) / whole
    L.update(kept=shown, kept_share=round(share, 4), omitted_note=f"The {shown} largest of {L['total']:,} flows, {share:.0%} of all trips",
             reveal={"default": shown, "count": len(written)})
    net = {k: 0 for k in STATIONS}
    for o, d, v in rows:
        net[d] += v
        net[o] -= v
    top = max(abs(v) for v in net.values())
    radius = {k: round(max(2.0, 10 * math.sqrt(abs(v) / top)), 2) for k, v in net.items()}
    for f in node_fc["features"]:
        p = f["properties"]
        v = net[p["dm_key"]]
        p.update(dm_net=v, dm_value=abs(v), dm_r=radius[p["dm_key"]], dm_fill=GAIN if v > 0 else LOSS,
                 dm_tip=f"{p['dm_label']}: {v:+,} trips, more {'in than out' if v > 0 else 'out than in'}")
    for f in arrows["features"]:
        f["properties"]["dm_setback"] = radius[f["properties"]["dm_d"]]
    values = [v for v in (1000, 500, 100) if v <= top]
    L["nodes"] = {"rmax": 10, "scaling": "area", "value": "net", "title": "Circle area: trips gained or lost in October",
                  "legend_values": values, "legend_radii": [round(10 * math.sqrt(v / top), 2) for v in values], "colors": {"gain": GAIN, "loss": LOSS}}
    for name, doc in (("trips.geojson", lines), ("trips-arrows.geojson", arrows), ("trips-nodes.geojson", node_fc), ("legend.json", legend)):
        (folder / name).write_text(json.dumps(doc))
    gainer = max(net, key=net.get)
    fill(out, title="Riders coast downtown and leave the east side short of bikes",
         subtitle="Trips between 14 bike-share stations in October, the largest of every route",
         source="Source: synthetic test data for the data-map plugin.",
         credits="Basemap: none.",
         spec={"idiom": ["flows"], "extent": "region", "controls": ["reveal"],
               "annotations": [{"text": f"{STATIONS[gainer][0]} gains the most bikes", "at": f"node:{gainer}"}],
               "companions": [{"type": "bars", "layer": "trips", "title": "The largest routes", "top": 6}]})


def build_maplibre_chart(out: Path, tmp: Path) -> None:
    dm("new", "maplibre", out, "--preset", "chart", "--force")
    rows = [["Bergen", 2250], ["Glasgow", 1240], ["Dublin", 760], ["Paris", 640], ["Madrid", 420], ["Athens", 400]]
    (out / "data" / "rainfall.json").write_text(json.dumps({"unit": "mm a year", "columns": ["City", "Rainfall, mm"], "rows": rows}, indent=1) + "\n")
    fill(out, title="Bergen gets almost twice the rain of Glasgow",
         subtitle="Average yearly rainfall in six European cities, millimeters",
         source="Source: synthetic test data for the data-map plugin.", credits="",
         spec={"companions": [{"type": "bars", "data": "rainfall", "title": "Rainfall, mm a year"},
                              {"type": "table", "data": "rainfall", "title": "The same values"}]})


FIXTURES = {"maplibre-crs": build_maplibre_crs, "maplibre-globe": build_maplibre_globe, "deck-globe": build_deck_globe,
            "maplibre-mercator": build_maplibre_mercator, "maplibre-flows": build_maplibre_flows, "maplibre-chart": build_maplibre_chart}


def main(names: list, root: Path = HERE) -> int:
    for name in names or FIXTURES:
        out = root / name
        print(name)
        if out.exists():
            shutil.rmtree(out)
        with tempfile.TemporaryDirectory() as tmp:
            FIXTURES[name](out, Path(tmp))
        dm("sync", out)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    root = HERE
    if args[:1] == ["--out"]:
        root, args = Path(args[1]), args[2:]
    sys.exit(main(args, root))
