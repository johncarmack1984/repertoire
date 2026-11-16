"""Goldens for data-map's levers. Expected values are worked by hand from the sources, not taken from a run."""

import io
import itertools
import json
import math
import random
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "skills" / "data-map" / "scripts"))

import datamap  # noqa: E402
from dm import classify, color, commands, crs, data, flows, geo, symbols  # noqa: E402

FIX = HERE / "fixtures"
EVALS = HERE.parent / "evals"
SLOCUM = [11, 12, 13, 14, 31, 32, 33, 99, 100]


def cli(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = datamap.main([str(a) for a in argv])
    return code, out.getvalue()


def haversine_km(p, q):
    lon1, lat1, lon2, lat2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def ssd(groups):
    return sum(sum((x - sum(g) / len(g)) ** 2 for x in g) for g in groups if g)


def midpoint(coords):
    return coords[len(coords) // 2]


def midpoint_lat(placed):
    return midpoint(placed.coords)[1]


def mercator(p):
    """Web Mercator at zoom 0, in 512 px tiles: what a flat map draws, with angles kept."""
    lat = math.radians(p[1])
    return ((p[0] + 180) / 360 * 512, (0.5 - math.log(math.tan(math.pi / 4 + lat / 2)) / (2 * math.pi)) * 512)


def turns(line):
    """The angle, in degrees, through which a line turns at each inner vertex, as drawn in Web Mercator."""
    xy = [mercator(p) for p in line]
    out = []
    for a, b, c in zip(xy, xy[1:], xy[2:]):
        h = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0])
        out.append(abs((math.degrees(h) + 180) % 360 - 180))
    return out



def screen_gaps(out, layer, view, top=None):
    """Fits a flows layer the way the maplibre template does (every vertex and node, padded 14 px past the largest
    circle) and returns, per line, its smallest gap in px from its edge to the circle of a node it doesn't connect.
    Each line is sampled every quarter pixel, shifted by its dm_offset, and left out under its two end circles."""
    lines = json.loads((Path(out) / f"{layer}.geojson").read_text())["features"]
    nodes = json.loads((Path(out) / f"{layer}-nodes.geojson").read_text())["features"]
    parts = lambda g: g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    xy = [mercator(c) for f in lines for part in parts(f["geometry"]) for c in part] + [mercator(n["geometry"]["coordinates"]) for n in nodes]
    pad = 14 + max(n["properties"]["dm_r"] for n in nodes)
    k = min((view[0] - 2 * pad) / (max(x for x, _ in xy) - min(x for x, _ in xy)), (view[1] - 2 * pad) / (max(y for _, y in xy) - min(y for _, y in xy)))
    at = {n["properties"]["dm_key"]: (tuple(v * k for v in mercator(n["geometry"]["coordinates"])), n["properties"]["dm_r"]) for n in nodes}
    gaps = {}
    for f in lines:
        p = f["properties"]
        if top is not None and p["dm_rank"] > top:
            continue
        ends = [at[p["dm_o"]], at[p["dm_d"]]]
        shown = []
        for part in parts(f["geometry"]):
            q = [(x * k, y * k) for x, y in map(mercator, part)]
            for a, b in zip(q, q[1:]):
                n = max(1, int(math.dist(a, b) / 0.25))
                nx, ny = -(b[1] - a[1]) / math.dist(a, b), (b[0] - a[0]) / math.dist(a, b)
                for i in range(n + 1):
                    c = (a[0] + (b[0] - a[0]) * i / n + nx * p["dm_offset"], a[1] + (b[1] - a[1]) * i / n + ny * p["dm_offset"])
                    if all(math.dist(c, e) > r for e, r in ends):
                        shown.append(c)
        others = [(e, r) for key, (e, r) in at.items() if key not in (p["dm_o"], p["dm_d"])]
        gaps[(p["dm_o"], p["dm_d"])] = min((math.dist(c, e) - r - p["dm_width"] / 2 for e, r in others for c in shown), default=math.inf)
    return gaps


class BikeCase:
    """The bike-share eval's own data, scaffolded once: 20 Portland stations and 380 OD pairs."""

    tmp = None

    @classmethod
    def folder(cls) -> Path:
        if cls.tmp is None:
            cls.tmp = tempfile.TemporaryDirectory()
            subprocess.run(["bash", str(EVALS / "bike-share-od-flows" / "scaffold.sh")], cwd=cls.tmp.name, check=True)
        return Path(cls.tmp.name) / "bike-data"

    @classmethod
    def flows(cls, out, *args):
        d = cls.folder()
        return cli("flows", d / "trips_od.csv", "--nodes", d / "stations.csv", "--origin", "start_station_id", "--dest", "end_station_id",
                   "--value", "trips", "--id", "station_id", "--unit", "trips", "--layer", "bike", "--out-dir", out, *args)


class Classing(unittest.TestCase):
    def test_jenks_finds_slocums_optimal_three_classes(self):
        # Slocum §5.8: the optimal classes are 11-14, 31-33, 99-100, with ADCM 7.
        # ADAM = sum |x - 31| = 20+19+18+17+0+1+2+68+69 = 214, so GADF = 1 - 7/214.
        self.assertEqual(classify.jenks_breaks(SLOCUM, 3), [31, 99])
        self.assertAlmostEqual(classify.gadf(SLOCUM, [31, 99]), 1 - 7 / 214, places=9)

    def test_jenks_is_exact_against_every_partition(self):
        rng = random.Random(7)
        for _ in range(25):
            xs = sorted(round(rng.lognormvariate(1, 1), 2) for _ in range(11))
            for k in (2, 3, 4):
                best = min(ssd([xs[a:b] for a, b in zip((0,) + cuts, cuts + (len(xs),))])
                           for cuts in itertools.combinations(range(1, len(xs)), k - 1))
                got = ssd(classify.groups(xs, classify.jenks_breaks(xs, k)))
                self.assertAlmostEqual(got, best, places=6)

    def test_quantiles_on_slocums_set(self):
        # 9 values in 3 classes of 3: 11-13, 14-32, 33-100; Slocum gives ADCM 87, so GADF = 1 - 87/214.
        self.assertEqual(classify.quantile_breaks(SLOCUM, 3), [14, 33])
        self.assertAlmostEqual(classify.gadf(SLOCUM, [14, 33]), 1 - 87 / 214, places=9)

    def test_quantiles_keep_ties_together_and_give_the_remainder_to_the_first_classes(self):
        # The cut falls among the three 2s; Slocum §5.5 moves all of them up.
        self.assertEqual(classify.quantile_breaks([1, 2, 2, 2, 3, 4], 2), [2])
        # 7 values in 3 classes: 3, 2, 2.
        self.assertEqual(classify.quantile_breaks([1, 2, 3, 4, 5, 6, 7], 3), [4, 6])

    def test_equal_intervals(self):
        xs = list(range(0, 101, 10))
        self.assertEqual(classify.equal_breaks(xs, 4), [25, 50, 75])
        self.assertEqual(classify.method_classing("equal", xs, 4).breaks, [0, 25, 50, 75, 100])

    def test_gvf_on_slocums_set(self):
        # SDAM = sum x^2 - n mean^2 = 23505 - 345^2/9 = 10280; SDCM = 5 + 2 + 0.5 = 7.5.
        self.assertAlmostEqual(classify.gvf(SLOCUM, [31, 99]), 1 - 7.5 / 10280, places=9)

    def test_auto_picks_jenks_for_skewed_and_equal_for_symmetric_data(self):
        skewed = [1, 1, 1, 2, 2, 3, 4, 6, 10, 30]
        # mean 6, m2 = 712/10, m3 = 13350/10, g1 = 1335 / 71.2^1.5 = 2.22.
        self.assertAlmostEqual(classify.skewness(skewed), 1335 / 71.2 ** 1.5, places=9)
        self.assertEqual(classify.auto_method(skewed, ordinal=False, compared=False, center_is_mean=False)[0], "jenks")
        symmetric = list(range(1, 10))
        self.assertEqual(classify.skewness(symmetric), 0)
        self.assertEqual(classify.auto_method(symmetric, ordinal=False, compared=False, center_is_mean=False)[0], "equal")
        self.assertEqual(classify.auto_method(skewed, ordinal=False, compared=True, center_is_mean=False)[0], "quantile")
        self.assertEqual(classify.auto_method(skewed, ordinal=True, compared=False, center_is_mean=False)[0], "quantile")

    def test_rounded_breaks_and_labels_match_the_contract_example(self):
        xs = [0.1, 0.5, 2, 3, 5, 8, 15, 20, 45, 310]
        c = classify.finish("jenks", [1.234, 4.51, 12.3, 39.7], xs)
        self.assertEqual(c.breaks, [0.1, 1.2, 4.5, 12, 40, 310])
        self.assertEqual(c.labels(), ["0.1 to 1.1", "1.2 to 4.4", "4.5 to 11.9", "12 to 39.9", "40 to 310"])

    def test_values_land_in_the_class_their_label_names(self):
        xs = [0.1, 0.5, 2, 3, 5, 8, 15, 20, 45, 310]
        c = classify.finish("jenks", [1.234, 4.51, 12.3, 39.7], xs)
        self.assertEqual(c.index(4.45), 2)
        self.assertEqual(c.index(4.44), 1)
        self.assertEqual(c.index(39.96), 4)
        rng = random.Random(3)
        sample = sorted(round(rng.lognormvariate(2, 1.2), 3) for _ in range(300))
        for method in ("quantile", "equal", "jenks", "headtail"):
            c = classify.method_classing(method, sample, 5)
            labels = c.labels()
            for v in sample:
                shown = classify.round_to(v, c.e)
                limits = [float(s.replace(",", "")) for s in labels[c.index(v)].split(" to ")]
                self.assertTrue(limits[0] <= shown <= limits[-1], f"{method}: {v} shows as {shown}, filed under {labels[c.index(v)]}")

    def test_rounding_a_break_never_drops_a_class_s_lowest_member(self):
        # Jenks puts each break on its class's lowest value; rounding 429.47 up to 430 dropped Kenya a class.
        xs = [5, 20, 42.71, 90, 139.97, 300, 429.47, 610, 964]
        inner = [42.71, 139.97, 429.47]
        c = classify.finish("jenks", inner, xs)
        self.assertEqual(c.inner, [42, 130, 420])
        self.assertEqual([c.index(x) for x in xs], [classify.assign(x, inner) for x in xs])

    def test_manual_breaks_label_at_their_own_precision(self):
        c = classify.finish("manual", [30, 100, 200, 400], [2.5, 31.2, 150.4, 250, 964.3], round_breaks=False)
        self.assertEqual(c.labels(), ["3 to 29", "30 to 99", "100 to 199", "200 to 399", "400 to 964"])


class Counts(unittest.TestCase):
    def test_classes_refuses_a_count_without_a_denominator(self):
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("classes", FIX / "countries-visits.csv", "--field", "visits", "--geo", "countries", "--key", "iso_a3", "--out-dir", out)
            self.assertEqual(code, 1)
            self.assertRegex(text, r"(?m)^FAIL counts \[P1\]: ")
            self.assertEqual(list(Path(out).iterdir()), [])

    def test_a_count_named_as_one_is_caught_by_name(self):
        self.assertEqual(data.guess_kind("total_visits", [1.5, 2.5], {})[0], "count")
        self.assertEqual(data.guess_kind("visits_per_1000", [1, 2], {})[0], "rate")

    def test_classes_with_a_denominator_writes_rates(self):
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("classes", FIX / "countries-visits.csv", "--field", "visits", "--per", "population", "--scale", 1000,
                             "--min-den", 1000000, "--geo", "countries", "--key", "iso_a3", "--layer", "visits", "--out-dir", out)
            self.assertEqual(code, 0, text)
            feats = {f["id"]: f["properties"] for f in json.loads((Path(out) / "visits.geojson").read_text())["features"]}
            # 456,007 visits / 67,059,887 people * 1,000; France joins because world-110m.json fixed its -99.
            self.assertAlmostEqual(feats["FRA"]["dm_value"], 456007 / 67059887 * 1000, places=5)
            self.assertTrue(feats["ISL"]["dm_low_n"])
            self.assertEqual(feats["AFG"]["dm_class"], -1)
            layer = json.loads((Path(out) / "legend.json").read_text())["layers"]["visits"]
            self.assertEqual(len(layer["colors"]), layer["k"])
            self.assertEqual(sum(layer["counts"]), 25 - 1)
            self.assertIn("WARN join [P3]", text)

    def test_a_red_green_diverging_palette_fails_p8(self):
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("classes", FIX / "countries-visits.csv", "--field", "visits", "--per", "population", "--scale", 1000,
                             "--geo", "countries", "--key", "iso_a3", "--scheme", "div:mean", "--palette", "RdYlGn", "--k", 6, "--out-dir", out)
            self.assertEqual(code, 1)
            self.assertRegex(text, r"(?m)^FAIL palette \[P8\]: ")

    def test_a_midpoint_outside_the_data_fails_p7(self):
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("classes", FIX / "countries-visits.csv", "--field", "visits", "--per", "population", "--scale", 1000,
                             "--geo", "countries", "--key", "iso_a3", "--scheme", "div:1000", "--out-dir", out)
            self.assertEqual(code, 1)
            self.assertRegex(text, r"(?m)^FAIL midpoint \[P7\]: ")


class Margins(unittest.TestCase):
    def test_inspect_finds_a_margin_of_error_and_the_ranks_it_ties(self):
        code, text = cli("inspect", FIX / "survey-movers.csv", "--json")
        self.assertEqual(code, 0)
        out = json.loads(text)
        # CV = (MOE / 1.645) / estimate x 100: 10, 22.2, 10, 5, and 31.6; the zero estimate has none.
        # Neighbors in rank order tie where the gap is under sqrt(MOE1^2 + MOE2^2): 1000 and 900 (100 < 367.8),
        # and 200 and 190 (10 < 100.1), but not 900 and 500 (400 > 339.1).
        self.assertEqual(out["profiles"]["survey-movers.csv"]["margins"],
                         [{"estimate": "movers", "moe": "moe", "cv": [5.0, 10.0, 31.6], "zeros": 1, "neighbors": 5, "ties": 2}])
        warn = next(f for f in out["findings"] if (f["status"], f["check"]) == ("WARN", "moe"))
        self.assertEqual(warn["pitfall"], 36)
        self.assertIn("ranks 1 to 2 and 4 to 5 tie", warn["message"])
        moe_profile = next(f for f in out["findings"] if f["check"] == "profile" and "column moe:" in f["message"])
        self.assertIn("the margin of error of movers", moe_profile["message"])
        self.assertIn("1 of them zero", next(f["message"] for f in out["findings"] if "column movers:" in f["message"]))

    def test_margins_pair_by_name(self):
        rows = [{"pop": "100", "pop_moe": "20", "moe_rent": "5", "rent": "900"}, {"pop": "80", "pop_moe": "30", "moe_rent": "9", "rent": "700"}]
        lines, facts = commands.moe_lines("t", ["pop", "pop_moe", "moe_rent", "rent"], rows)
        self.assertEqual([(f["estimate"], f["moe"]) for f in facts], [("pop", "pop_moe"), ("rent", "moe_rent")])


class Sphere(unittest.TestCase):
    TOKYO, LOS_ANGELES = [139.6917, 35.6895], [-118.2437, 34.0522]

    def test_densify_across_the_antimeridian(self):
        parts = geo.split_antimeridian(geo.densify_gc([self.TOKYO, self.LOS_ANGELES], 1.0))
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0][-1][0], 180.0)
        self.assertEqual(parts[1][0][0], -180.0)
        self.assertEqual(parts[0][-1][1], parts[1][0][1])
        one_degree_km = 2 * math.pi * 6371.0088 / 360
        for part in parts:
            for p, q in zip(part, part[1:]):
                self.assertLessEqual(haversine_km(p, q), one_degree_km * 1.000001)
        gc = haversine_km(self.TOKYO, self.LOS_ANGELES)
        self.assertAlmostEqual(gc, 8815, delta=30)
        total = sum(haversine_km(p, q) for part in parts for p, q in zip(part, part[1:]))
        self.assertLess(abs(total - gc) / gc, 0.005)


class Flows(unittest.TestCase):
    A, B = flows.Node("A", 0, 0, "A"), flows.Node("B", 40, 0, "B")

    def test_reciprocal_flows_bow_to_opposite_sides(self):
        # Eastward along the Equator, the right of travel is south.
        placed = {(p.flow.o, p.flow.d): p for p in flows.place(
            [flows.Flow("A", "B", 100), flows.Flow("B", "A", 60)], {"A": self.A, "B": self.B}, "curved")}
        self.assertLess(midpoint_lat(placed[("A", "B")]), 0)
        self.assertGreater(midpoint_lat(placed[("B", "A")]), 0)

    def test_a_curve_flips_away_from_a_node_on_its_default_side(self):
        flow = flows.Flow("A", "B", 100)
        default = flows.place([flow], {"A": self.A, "B": self.B}, "curved")[0]
        self.assertLess(midpoint_lat(default), 0)
        mid = default.coords[len(default.coords) // 2]
        nodes = {"A": self.A, "B": self.B, "C": flows.Node("C", mid[0], mid[1], "C")}
        moved = flows.place([flow], nodes, "curved")[0]
        self.assertGreater(midpoint_lat(moved), 0)
        self.assertTrue(moved.clear)
        self.assertGreaterEqual(geo.point_line_km(mid, moved.coords), 0.04 * haversine_km(self.A.pos, self.B.pos))

    def test_curves_clear_only_the_nodes_of_kept_flows(self):
        # C sits on A to B's default curve, close enough that the curve flips when C is drawn.
        ab = flows.Flow("A", "B", 100)
        mid = midpoint(flows.place([ab], {"A": self.A, "B": self.B}, "curved")[0].coords)
        c = flows.Node("C", mid[0], mid[1], "C")
        self.assertGreater(midpoint_lat(flows.place([ab], {"A": self.A, "B": self.B, "C": c}, "curved")[0]), 0)
        with tempfile.TemporaryDirectory() as tmp:
            nodes = Path(tmp) / "nodes.csv"
            nodes.write_text(f"id,lon,lat\nA,0,0\nB,40,0\nC,{mid[0]},{mid[1]}\nD,{mid[0]},{mid[1] - 30}\n")
            od = Path(tmp) / "od.csv"
            od.write_text("origin,dest,movers\nA,B,100\nC,D,1\n")
            # --top 1 cuts C to D, so C is never drawn and A to B stays on its default side, south.
            code, text = cli("flows", od, "--nodes", nodes, "--top", 1, "--layer", "f", "--out-dir", tmp)
            self.assertEqual(code, 0, text)
            line = json.loads((Path(tmp) / "f.geojson").read_text())["features"][0]
            self.assertLess(midpoint(line["geometry"]["coordinates"])[1], 0)
            self.assertNotRegex(text, r"(?m)^WARN clearance")
            layer = json.loads((Path(tmp) / "legend.json").read_text())["layers"]["f"]
            self.assertEqual((layer["total"], layer["omitted_note"]), (2, "The 1 largest of 2 flows, 99% of all movers"))
            totals = {f["properties"]["dm_key"]: f["properties"]["dm_value"] for f in json.loads((Path(tmp) / "f-nodes.geojson").read_text())["features"]}
            self.assertEqual(totals, {"A": 100, "B": 100})

    def test_curves_turn_by_at_most_three_degrees_at_any_vertex(self):
        # Nine points per curve kinked the long Sellwood loops by up to 12.8 degrees at the bike map's opening zoom.
        with tempfile.TemporaryDirectory() as out:
            code, text = BikeCase.flows(out, "--top", 40, "--max-width", 10)
            self.assertEqual(code, 0, text)
            lines = json.loads((Path(out) / "bike.geojson").read_text())["features"]
            self.assertEqual(len(lines), 40)
            worst = max(max(turns(f["geometry"]["coordinates"])) for f in lines)
            self.assertLessEqual(worst, 3.0)
            self.assertGreater(worst, 0)

    def test_widths_are_linear_in_value_with_a_floor(self):
        self.assertAlmostEqual(flows.width(3000, 3400, 12, 1), 12 * 3000 / 3400)
        self.assertAlmostEqual(flows.width(1000, 3400, 12, 1), 12 * 1000 / 3400)
        self.assertEqual(flows.width(250, 3400, 12, 1), 1)
        self.assertAlmostEqual(flows.width(1600, 3400, 12, 1), 2 * flows.width(800, 3400, 12, 1))

    def test_arrowheads_grow_on_thin_flows(self):
        self.assertEqual(flows.arrow_size(1), 6)
        self.assertEqual(flows.arrow_size(4), 10)

    def test_top_n_keeps_the_largest_and_states_the_share(self):
        fs = [flows.Flow(str(i), "x", v) for i, v in enumerate([50, 30, 10, 5, 5])]
        kept, share = flows.keep_top(fs, share=0.8)
        self.assertEqual([f.value for f in kept], [50, 30])
        self.assertAlmostEqual(share, 0.8)
        kept, share = flows.keep_top(fs, top=3)
        self.assertAlmostEqual(share, 0.9)
        self.assertEqual(flows.omitted_note(2, 5, 0.8, "movers"), "The 2 largest of 5 flows, 80% of all movers")

    def test_legend_text_separates_thousands_and_says_what_the_circles_count(self):
        self.assertEqual(flows.omitted_note(50, 2097, 0.2281, "movers"), "The 50 largest of 2,097 flows, 23% of all movers")
        self.assertEqual(flows.omitted_note(2097, 2097, 1.0, "movers"), "All 2,097 flows")
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("flows", FIX / "pacific-movers.csv", "--nodes", FIX / "pacific-nodes.csv", "--top", 10, "--unit", "movers",
                             "--layer", "m", "--out-dir", out)
            self.assertEqual(code, 0, text)
            nodes = json.loads((Path(out) / "legend.json").read_text())["layers"]["m"]["nodes"]
            # The circles total every one of the fixture's 30 flows, not only the 10 drawn.
            self.assertEqual(nodes["title"], "Circle area: movers in and out, across all 30 flows")

    def flows_run(self, out, *args):
        code, text = cli("flows", FIX / "pacific-movers.csv", "--nodes", FIX / "pacific-nodes.csv", "--top", 12,
                         "--layer", "m", "--out-dir", out, *args)
        self.assertEqual(code, 0, text)
        lines = [f["properties"] for f in json.loads((Path(out) / "m.geojson").read_text())["features"]]
        arrows = [f["properties"] for f in json.loads((Path(out) / "m-arrows.geojson").read_text())["features"]]
        return lines, arrows, json.loads((Path(out) / "legend.json").read_text())["layers"]["m"]

    def test_flows_fade_by_value_from_fade_min_to_one(self):
        with tempfile.TemporaryDirectory() as out:
            lines, arrows, layer = self.flows_run(out)
            values = [p["dm_value"] for p in lines]
            vmin, vmax = min(values), max(values)
            for p in lines:
                self.assertAlmostEqual(p["dm_opacity"], 0.45 + 0.55 * (p["dm_value"] - vmin) / (vmax - vmin), places=3)
            by_value = sorted(lines, key=lambda p: p["dm_value"])
            self.assertEqual((by_value[0]["dm_opacity"], by_value[-1]["dm_opacity"]), (0.45, 1.0))
            self.assertEqual({(a["dm_o"], a["dm_d"]): a["dm_opacity"] for a in arrows}, {(p["dm_o"], p["dm_d"]): p["dm_opacity"] for p in lines})
            # Each legend width carries its value's opacity, so the swatches match the lines.
            self.assertEqual(len(layer["legend_opacities"]), len(layer["legend_widths"]))
            for v, a in zip(layer["legend_values"], layer["legend_opacities"]):
                self.assertAlmostEqual(a, min(1, max(0.45, 0.45 + 0.55 * (v - vmin) / (vmax - vmin))), places=3)
            self.assertEqual(layer["legend_opacities"], sorted(layer["legend_opacities"], reverse=True))
        with tempfile.TemporaryDirectory() as out:
            lines, _, layer = self.flows_run(out, "--fade-min", 0.2)
            self.assertEqual(min(p["dm_opacity"] for p in lines), 0.2)
        with tempfile.TemporaryDirectory() as out:
            lines, arrows, layer = self.flows_run(out, "--no-fade")
            self.assertEqual({p["dm_opacity"] for p in lines + arrows} | set(layer["legend_opacities"]), {1.0})

    def test_flows_draw_in_one_warm_color_unless_told(self):
        with tempfile.TemporaryDirectory() as out:
            lines, arrows, layer = self.flows_run(out)
            self.assertEqual({p["dm_fill"] for p in lines + arrows} | {layer["color"]}, {"#a63603"})
        with tempfile.TemporaryDirectory() as out:
            lines, arrows, layer = self.flows_run(out, "--color", "#54278F")
            self.assertEqual({p["dm_fill"] for p in lines + arrows} | {layer["color"]}, {"#54278f"})
        with tempfile.TemporaryDirectory() as out, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as stop:
                cli("flows", FIX / "pacific-movers.csv", "--nodes", FIX / "pacific-nodes.csv", "--color", "orange", "--out-dir", out)
            self.assertEqual(stop.exception.code, 2)

    def test_flows_command_orders_small_on_top_and_splits_at_180(self):
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("flows", FIX / "pacific-movers.csv", "--nodes", FIX / "pacific-nodes.csv", "--layer", "movers", "--out-dir", out)
            self.assertEqual(code, 0, text)
            lines = json.loads((Path(out) / "movers.geojson").read_text())["features"]
            self.assertEqual(len(lines), 30)
            for a in lines:
                for b in lines:
                    if a["properties"]["dm_value"] > b["properties"]["dm_value"]:
                        self.assertLess(a["properties"]["dm_order"], b["properties"]["dm_order"])
            syd_lax = next(f for f in lines if (f["properties"]["dm_o"], f["properties"]["dm_d"]) == ("SYD", "LAX"))
            self.assertEqual(syd_lax["geometry"]["type"], "MultiLineString")
            self.assertEqual(abs(syd_lax["geometry"]["coordinates"][0][-1][0]), 180)
            self.assertTrue(all(isinstance(f["id"], int) for f in lines))
            for f in lines:
                parts = f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiLineString" else [f["geometry"]["coordinates"]]
                self.assertTrue(all(-180 <= p[0] <= 180 for part in parts for p in part))
            for name in ("movers-nodes.geojson", "movers-arrows.geojson", "movers-arcs.json"):
                self.assertTrue((Path(out) / name).exists())
            # A value filter on the lines must drop their arrows too, so each arrow carries its flow's value.
            arrows = json.loads((Path(out) / "movers-arrows.geojson").read_text())["features"]
            values = {(f["properties"]["dm_o"], f["properties"]["dm_d"]): f["properties"]["dm_value"] for f in lines}
            for a in arrows:
                self.assertEqual(a["properties"]["dm_value"], values[(a["properties"]["dm_o"], a["properties"]["dm_d"])])

    def test_a_flow_drawn_with_its_reverse_moves_right_by_half_its_width_and_a_pixel_gap(self):
        # A short pair bows a pixel or two apart, so each direction also shifts right of travel in screen space.
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("flows", FIX / "pacific-movers.csv", "--nodes", FIX / "pacific-nodes.csv", "--layer", "movers", "--out-dir", out)
            self.assertEqual(code, 0, text)
            lines = json.loads((Path(out) / "movers.geojson").read_text())["features"]
            arrows = {(a["properties"]["dm_o"], a["properties"]["dm_d"]): a["properties"]
                      for a in json.loads((Path(out) / "movers-arrows.geojson").read_text())["features"]}
            pairs = {(f["properties"]["dm_o"], f["properties"]["dm_d"]) for f in lines}
            self.assertTrue(any((d, o) in pairs for o, d in pairs))
            for f in lines:
                p = f["properties"]
                both = (p["dm_d"], p["dm_o"]) in pairs
                self.assertEqual(p["dm_offset"], round(p["dm_width"] / 2 + 0.5, 2) if both else 0)
                self.assertEqual(arrows[(p["dm_o"], p["dm_d"])]["dm_offset"], p["dm_offset"])



def assert_named_as_measured(case, text, gaps):
    """The flows the clearance WARN names are exactly those the screen shows within 2 px, each with its gap."""
    measured = {pair: g for pair, g in gaps.items() if g < 2 - 0.05}
    warn = re.search(r"(?m)^WARN clearance \[P16\]: (\d+) flows .*$", text)
    case.assertTrue(warn and measured, text)
    named = {(o, d): float(g) for o, d, g in re.findall(r"(S\d+) to (S\d+) \(S\d+ ([-+][\d.]+) px\)", warn.group(0))}
    case.assertEqual(int(warn.group(1)), len(named))
    case.assertEqual(set(named), set(measured))
    for pair, g in named.items():
        case.assertAlmostEqual(g, measured[pair], delta=0.15)


class ScreenClearance(unittest.TestCase):
    """Flows clear the stations they don't serve by 2 px on screen, at the view the page opens on."""

    def test_every_bike_flow_clears_every_station_it_does_not_serve_at_the_default_view(self):
        # Round 2 measured the old rule, 4% of a flow's length in km, at this zoom: five flows ran onto stations,
        # one 3.3 px over Rose Quarter's circle.
        with tempfile.TemporaryDirectory() as out:
            code, text = BikeCase.flows(out, "--top", 40, "--max-width", 10)
            self.assertEqual(code, 0, text)
            gaps = screen_gaps(out, "bike", (844, 634))
            self.assertEqual(len(gaps), 40)
            self.assertGreaterEqual(min(gaps.values()), 2 - 0.05, sorted(gaps.items(), key=lambda kv: kv[1])[:3])
            self.assertRegex(text, r"(?m)^PASS clearance \[P16\]: every flow keeps 2 px at the 844 x 634 px view")
            layer = json.loads((Path(out) / "legend.json").read_text())["layers"]["bike"]
            self.assertEqual(layer["clearance"]["view"], [844, 634])

    def test_a_flow_that_cannot_clear_is_named_with_the_gap_the_screen_shows(self):
        with tempfile.TemporaryDirectory() as out:
            code, text = BikeCase.flows(out, "--top", 40, "--max-width", 10, "--view", "600x450")
            self.assertEqual(code, 0, text)
            assert_named_as_measured(self, text, screen_gaps(out, "bike", (600, 450)))



class Reveal(unittest.TestCase):
    """--reveal writes the flows under the cut for a page control, while the legend still describes the first view."""

    def run_bike(self, out, *args):
        code, text = BikeCase.flows(out, "--top", 40, "--max-width", 10, *args)
        self.assertEqual(code, 0, text)
        read = lambda name: [f["properties"] for f in json.loads((Path(out) / name).read_text())["features"]]
        layer = json.loads((Path(out) / "legend.json").read_text())["layers"]["bike"]
        return read("bike.geojson"), read("bike-arrows.geojson"), read("bike-nodes.geojson"), layer, text

    def test_reveal_writes_every_flow_ranked_and_keeps_the_first_view_in_the_legend(self):
        trips = sorted((float(r["trips"]) for r in data.read_table(BikeCase.folder() / "trips_od.csv").rows), reverse=True)
        with tempfile.TemporaryDirectory() as out:
            _, _, _, plain, _ = self.run_bike(out)
        with tempfile.TemporaryDirectory() as out:
            lines, arrows, nodes, layer, text = self.run_bike(out, "--reveal")
            gaps = screen_gaps(out, "bike", (844, 634), top=40)
        self.assertEqual(layer["reveal"], {"default": 40, "count": 380})
        self.assertEqual((layer["kept"], layer["total"]), (40, 380))
        self.assertAlmostEqual(layer["kept_share"], round(sum(trips[:40]) / sum(trips), 4))
        self.assertEqual(layer["omitted_note"], "The 40 largest of 380 flows, 63% of all trips")
        # The legend samples the first view's widths, and each sample's fade matches the written lines'.
        self.assertEqual(layer["legend_values"], plain["legend_values"])
        self.assertEqual(layer["legend_widths"], plain["legend_widths"])
        for v, a in zip(layer["legend_values"], layer["legend_opacities"]):
            self.assertAlmostEqual(a, 0.45 + 0.55 * (v - 1) / (1486 - 1), places=3)
        for feats in (lines, arrows):
            self.assertEqual(sorted(p["dm_rank"] for p in feats), list(range(1, 381)))
            by_rank = sorted(feats, key=lambda p: p["dm_rank"])
            self.assertEqual([p["dm_value"] for p in by_rank], trips)
            for p in feats:
                self.assertAlmostEqual(p["dm_width"], max(1, 10 * p["dm_value"] / 1486), places=2)
                self.assertAlmostEqual(p["dm_opacity"], 0.45 + 0.55 * (p["dm_value"] - 1) / (1486 - 1), places=3)
                self.assertEqual(p["dm_order"], p["dm_rank"] - 1)
        self.assertEqual(len(nodes), 20)
        # All 20 stations widen the fit. South Waterfront to Union Station must bow opposite its 1,486-trip reverse,
        # and no bend on that side clears Pioneer Square, so it is the one first-view flow the lever names.
        assert_named_as_measured(self, text, gaps)
        self.assertRegex(text, r"of the 340 flows a reader can reveal, \d+ come closer")

    def test_reveal_stops_at_its_cap_and_needs_a_first_view(self):
        with tempfile.TemporaryDirectory() as out:
            lines, _, _, layer, _ = self.run_bike(out, "--reveal", "--reveal-max", 100)
        self.assertEqual((len(lines), layer["reveal"]), (100, {"default": 40, "count": 100}))
        with tempfile.TemporaryDirectory() as out:
            lines, _, _, layer, _ = self.run_bike(out)
        self.assertEqual(len(lines), 40)
        self.assertNotIn("reveal", layer)
        with tempfile.TemporaryDirectory() as out, redirect_stderr(io.StringIO()):
            d = BikeCase.folder()
            code, _ = cli("flows", d / "trips_od.csv", "--nodes", d / "stations.csv", "--origin", "start_station_id", "--dest", "end_station_id",
                          "--value", "trips", "--id", "station_id", "--reveal", "--out-dir", out)
        self.assertEqual(code, 2)


class NodeValues(unittest.TestCase):
    """Circles sized by arrivals, departures, or the balance, from the bike case's 380 pairs."""

    def totals(self):
        rows = list(data.read_table(BikeCase.folder() / "trips_od.csv").rows)
        t = {}
        for r in rows:
            v = float(r["trips"])
            t.setdefault(r["start_station_id"], {"in": 0.0, "out": 0.0})["out"] += v
            t.setdefault(r["end_station_id"], {"in": 0.0, "out": 0.0})["in"] += v
        return t

    def run_bike(self, out, *args):
        code, text = BikeCase.flows(out, "--top", 40, *args)
        self.assertEqual(code, 0, text)
        read = lambda name: [f["properties"] for f in json.loads((Path(out) / name).read_text())["features"]]
        layer = json.loads((Path(out) / "legend.json").read_text())["layers"]["bike"]
        return read("bike-nodes.geojson"), read("bike.geojson"), read("bike-arrows.geojson"), layer, text

    def test_net_sizes_by_the_balance_and_fills_gains_and_losses_apart(self):
        t = self.totals()
        with tempfile.TemporaryDirectory() as out:
            nodes, _, _, layer, text = self.run_bike(out, "--node-value", "net")
        # The scaffold's notes: Rose Quarter gains 1,250 bikes over October and Union Station loses 1,036.
        by_key = {n["dm_key"]: n for n in nodes}
        self.assertEqual((by_key["S09"]["dm_net"], by_key["S01"]["dm_net"]), (1250, -1036))
        for n in nodes:
            net = t[n["dm_key"]]["in"] - t[n["dm_key"]]["out"]
            self.assertEqual(n["dm_net"], net)
            self.assertEqual(n["dm_value"], abs(net))
            self.assertEqual(n["dm_fill"], "#018571" if net > 0 else "#6a51a3" if net < 0 else "#525252")
            self.assertIn(f"net {'+' if net > 0 else ''}{net:,.0f}", n["dm_tip"])
            self.assertAlmostEqual(n["dm_r"], 10 * math.sqrt(abs(net) / 1250), places=2)
        self.assertTrue({"#018571", "#6a51a3"} <= {n["dm_fill"] for n in nodes})
        legend = layer["nodes"]
        self.assertEqual((legend["value"], legend["colors"]), ("net", {"gain": "#018571", "loss": "#6a51a3"}))
        self.assertEqual(legend["title"], "Circle area: trips gained or lost (in minus out), across all 380 flows")
        for v, r in zip(legend["legend_values"], legend["legend_radii"]):
            self.assertAlmostEqual(r, 10 * math.sqrt(v / 1250), places=2)
        self.assertEqual(legend["legend_values"], sorted(legend["legend_values"], reverse=True))
        self.assertRegex(text, r"(?m)^PASS nodes: ")

    def test_in_and_out_size_by_arrivals_and_departures_in_one_gray(self):
        t = self.totals()
        for mode, words in (("in", "arriving"), ("out", "leaving"), ("gross", "in and out")):
            with tempfile.TemporaryDirectory() as out:
                nodes, _, _, layer, _ = self.run_bike(out, "--node-value", mode)
            want = {k: v["in"] + v["out"] if mode == "gross" else v[mode] for k, v in t.items()}
            biggest = max(want[n["dm_key"]] for n in nodes)
            for n in nodes:
                self.assertEqual(n["dm_value"], want[n["dm_key"]])
                self.assertAlmostEqual(n["dm_r"], 10 * math.sqrt(want[n["dm_key"]] / biggest), places=2)
                self.assertEqual(n["dm_fill"], "#525252")
                self.assertNotIn("dm_net", n)
            self.assertEqual(layer["nodes"]["title"], f"Circle area: trips {words}, across all 380 flows")
            self.assertNotIn("colors", layer["nodes"])

    def test_every_line_and_arrow_carries_its_rank_from_one(self):
        with tempfile.TemporaryDirectory() as out:
            _, lines, arrows, _, _ = self.run_bike(out)
        for feats in (lines, arrows):
            ranked = sorted(feats, key=lambda p: p["dm_rank"])
            self.assertEqual([p["dm_rank"] for p in ranked], list(range(1, 41)))
            self.assertEqual(ranked[0]["dm_value"], 1486)
            self.assertEqual([p["dm_value"] for p in ranked], sorted((p["dm_value"] for p in feats), reverse=True))

    def test_node_colors_need_net_and_warn_when_colorblind_readers_cannot_part_them(self):
        with tempfile.TemporaryDirectory() as out, redirect_stderr(io.StringIO()):
            self.assertEqual(BikeCase.flows(out, "--node-colors", "#018571,#88419d")[0], 2)
        with tempfile.TemporaryDirectory() as out:
            code, text = BikeCase.flows(out, "--node-value", "net", "--node-colors", "#1a9641,#d7191c")
            self.assertEqual(code, 0, text)
            self.assertRegex(text, r"(?m)^WARN node colors \[P8\]: ")

    def test_default_gain_and_loss_part_for_every_vision_and_from_the_flows(self):
        pair = (flows.GAIN_COLOR, flows.LOSS_COLOR)
        for vision in (None, "protan", "deutan", "tritan"):
            self.assertGreaterEqual(color.delta_e(*pair, vision), 36)
            for c in pair:
                self.assertGreaterEqual(color.delta_e(c, flows.FLOW_COLOR, vision), 39)
        self.assertLess(abs(color.lab(pair[0])[0] - color.lab(pair[1])[0]), 10)


class Symbols(unittest.TestCase):
    def test_radii_are_true_to_area(self):
        # r = 28 sqrt(v / 2500): 5.6, 11.2, 28, so r^2 / v = 784 / 2500 for every value.
        radii = [symbols.radius(v, 2500, 28) for v in (100, 400, 2500)]
        for r, want in zip(radii, (5.6, 11.2, 28)):
            self.assertAlmostEqual(r, want)
        for r, v in zip(radii, (100, 400, 2500)):
            self.assertAlmostEqual(r * r / v, 784 / 2500)

    def test_nested_legend_values_are_round_and_span_the_data(self):
        values = symbols.legend_values(50, 2400)
        self.assertEqual(values, [2000, 500, 100])
        self.assertEqual([round(symbols.radius(v, 2400, 28), 1) for v in values], [25.6, 12.8, 5.7])

    def test_largest_symbols_draw_first(self):
        self.assertEqual(symbols.order_largest_first([5, 50, 20]), [2, 0, 1])


class Projection(unittest.TestCase):
    PROJ4JS = {"eqearth", "moll", "laea", "aea", "cea", "stere", "lcc", "tmerc"}

    def test_world_is_equal_earth(self):
        rec = crs.recommend(crs.WORLD)
        self.assertEqual(rec.name, "custom:equal-earth")
        self.assertIn("+proj=eqearth", rec.definition)

    def test_conterminous_us_is_albers_near_the_usgs_parallels(self):
        rec = crs.recommend(crs.Extent(-124.8, 24.5, -66.9, 49.4))
        lat1 = float(re.search(r"\+lat_1=([-\d.]+)", rec.definition).group(1))
        lat2 = float(re.search(r"\+lat_2=([-\d.]+)", rec.definition).group(1))
        self.assertIn("+proj=aea", rec.definition)
        self.assertLessEqual(abs(lat1 - 29.5), 1)
        self.assertLessEqual(abs(lat2 - 45.5), 1)

    def test_polar_extent_is_polar_lambert(self):
        rec = crs.recommend(crs.Extent(-180, 60, 180, 90))
        self.assertIn("+proj=laea +lat_0=90", rec.definition)

    def test_every_printed_definition_is_one_proj4_2_22_implements(self):
        extents = ["world", "-124.8,24.5,-66.9,49.4", "-180,60,180,90", "-180,-90,180,-60", "95,-11,141,6",
                   "-18,-35,52,37", "-25,34,45,72", "27,41.7,-170,81.9", "-80,-56,-34,13", FIX / "pacific-nodes.csv"]
        for ext in extents:
            for idiom in ("area", "points", "flows"):
                for interactive in ((), ("--interactive",)):
                    code, text = cli("crs", f"--extent={ext}", "--idiom", idiom, *interactive, "--json")
                    self.assertEqual(code, 0)
                    out = json.loads(text)
                    defs = [out["definition"]] + [a["definition"] for a in out["alternatives"]]
                    for d in filter(None, defs):
                        self.assertIn(re.search(r"\+proj=(\w+)", d).group(1), self.PROJ4JS, d)
                        # Without a false origin, proj4 2.22.0 projects aea, laea, cea, stere, lcc, and tmerc to NaN.
                        self.assertIn("+x_0=0 +y_0=0", d)



def rings_of(geom):
    t, c = geom["type"], geom["coordinates"]
    return [c] if t == "Polygon" else c if t == "MultiPolygon" else []


def lonlat_area(poly):
    """A polygon's area in square degrees of longitude and latitude, holes taken out; cutting and moving by 360 keeps it."""
    shoelace = lambda r: abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:]))) / 2
    return shoelace(poly[0]) - sum(shoelace(h) for h in poly[1:])


class WorldCenter(unittest.TestCase):
    """A world map's central meridian, measured on the bundled countries rather than assumed."""

    WORLD = json.loads((HERE.parent / "skills" / "data-map" / "assets" / "geo" / "world-110m.json").read_text())

    def cut_countries(self, lon0):
        """Countries whose land the map's edge, the meridian opposite lon0, runs through. Rings that meet at 180
        are one piece of land, so a cut between Chukotka's -180 and its eastern tip runs through Russia."""
        edge = (lon0 + 360) % 360 - 180
        hit = set()
        for f in self.WORLD["features"]:
            spans = [(min(x for x, _ in poly[0]), max(x for x, _ in poly[0])) for poly in rings_of(f["geometry"])]
            if any(lo < edge < hi for lo, hi in spans):
                hit.add(f["id"])
            if any(hi >= 180 for _, hi in spans) and any(edge < hi for lo, hi in spans if lo <= -180):
                hit.add(f["id"])
        return hit - {"ATA"}

    def test_the_world_center_keeps_russia_whole_and_cuts_no_country_but_antarctica(self):
        self.assertEqual(self.cut_countries(crs.WORLD_LON0), set())
        # At 0 the edge runs through Russia and Fiji; at 10, Cape Dezhnev (-169.9 here) and St. Lawrence Island;
        # at 11, St. Lawrence Island (-171.79 to -168.69) alone.
        self.assertEqual(self.cut_countries(0), {"RUS", "FJI"})
        self.assertEqual(self.cut_countries(10), {"RUS", "USA"})
        self.assertEqual(self.cut_countries(11), {"USA"})
        rec = crs.recommend(crs.WORLD)
        self.assertIn(f"+lon_0={crs.WORLD_LON0:g} ", rec.definition)
        self.assertTrue(all(f"+lon_0={crs.WORLD_LON0:g} " in a["definition"] for a in rec.alternatives))

    def test_crs_prints_the_geo_runs_that_match_its_center(self):
        code, text = cli("crs", "--extent", "world", "--json")
        self.assertEqual(code, 0)
        out = json.loads(text)
        self.assertEqual(len(out["geo"]), 2)
        self.assertTrue(all(re.search(rf" geo .*--lon0 {crs.WORLD_LON0:g} ", line) for line in out["geo"]))
        self.assertIn("--countries", out["geo"][0])
        self.assertIn("--sphere", out["geo"][1])
        self.assertIn(f"forward([{crs.WORLD_LON0 + 180:g}, 0])", out["snippet"])
        code, text = cli("crs", "--extent=-124.8,24.5,-66.9,49.4", "--json")
        self.assertEqual(json.loads(text)["geo"], [])

    def test_geo_cuts_every_country_and_the_frame_at_the_edge(self):
        lon0 = crs.WORLD_LON0
        with tempfile.TemporaryDirectory() as out:
            code, text = cli("geo", "--countries", "--lon0", lon0, "--out", Path(out) / "c.geojson")
            self.assertEqual(code, 0, text)
            cut = {f["id"]: f["geometry"] for f in json.loads((Path(out) / "c.geojson").read_text())["features"]}
            self.assertEqual(cli("geo", "--sphere", "--graticule", 30, "--lon0", lon0, "--out", Path(out) / "f.geojson")[0], 0)
            frame = json.loads((Path(out) / "f.geojson").read_text())["features"]
        src = {f["id"]: f["geometry"] for f in self.WORLD["features"]}
        for fid, geom in cut.items():
            xs = [x for poly in rings_of(geom) for ring in poly for x, _ in ring]
            self.assertTrue(lon0 - 180 - 1e-9 <= min(xs) and max(xs) <= lon0 + 180 + 1e-9, fid)
            # No edge spans half the world, so nothing draws from one side of the map to the other; an edge along
            # a pole is the frame's flat top or bottom under Equal Earth, which Antarctica's ring follows.
            for poly in rings_of(geom):
                for ring in poly:
                    wide = [(a, b) for a, b in zip(ring, ring[1:]) if abs(b[0] - a[0]) >= 180]
                    self.assertTrue(all(abs(a[1]) == abs(b[1]) == 90 for a, b in wide), fid)
            self.assertAlmostEqual(sum(map(lonlat_area, rings_of(geom))), sum(map(lonlat_area, rings_of(src[fid]))), places=3)
        # Russia runs unbroken from Kaliningrad to Chukotka at 190.1, the right edge; nothing of it sits on the left.
        russia = [x for poly in rings_of(cut["RUS"]) for x, _ in poly[0]]
        self.assertEqual((round(min(russia), 2), round(max(russia), 2)), (19.66, 190.1))
        sphere = next(f for f in frame if f["id"] == "sphere")["geometry"]["coordinates"][0]
        self.assertEqual((min(x for x, _ in sphere), max(x for x, _ in sphere)), (round(lon0 - 180, 5), round(lon0 + 180, 5)))
        for f in frame:
            parts = f["geometry"]["coordinates"] if f["geometry"]["type"] != "LineString" else [f["geometry"]["coordinates"]]
            for part in parts:
                self.assertTrue(all(lon0 - 180 - 1e-9 <= x <= lon0 + 180 + 1e-9 for x, _ in part), f["id"])

    def test_a_center_west_of_greenwich_moves_eastern_land_west_and_zero_changes_nothing(self):
        for lon0 in (-150.0, 75.0):
            for f in self.WORLD["features"]:
                g = geo.recenter(f["geometry"], lon0)
                xs = [x for poly in rings_of(g) for ring in poly for x, _ in ring]
                self.assertTrue(lon0 - 180 - 1e-9 <= min(xs) and max(xs) <= lon0 + 180 + 1e-9, (lon0, f["id"]))
                self.assertAlmostEqual(sum(map(lonlat_area, rings_of(g))), sum(map(lonlat_area, rings_of(f["geometry"]))), places=3)
        with tempfile.TemporaryDirectory() as out:
            cli("geo", "--countries", "--sphere", "--graticule", 30, "--out", Path(out) / "a.geojson")
            cli("geo", "--countries", "--sphere", "--graticule", 30, "--lon0", 0, "--out", Path(out) / "b.geojson")
            self.assertEqual((Path(out) / "a.geojson").read_text(), (Path(out) / "b.geojson").read_text())


class Legend(unittest.TestCase):
    def test_levers_merge_into_one_legend_and_reruns_change_nothing(self):
        args = ["classes", FIX / "countries-visits.csv", "--field", "visits", "--per", "population", "--scale", 1000,
                "--geo", "countries", "--key", "iso_a3", "--layer", "visits"]
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(cli(*args, "--out-dir", out)[0], 0)
            self.assertEqual(cli("sizes", FIX / "countries-visits.csv", "--field", "visits", "--geo", "countries",
                                 "--key", "iso_a3", "--layer", "totals", "--out-dir", out)[0], 0)
            first = (Path(out) / "legend.json").read_text()
            geojson = (Path(out) / "visits.geojson").read_text()
            self.assertEqual(cli(*args, "--out-dir", out)[0], 0)
            self.assertEqual((Path(out) / "legend.json").read_text(), first)
            self.assertEqual((Path(out) / "visits.geojson").read_text(), geojson)
            doc = json.loads(first)
            self.assertEqual(sorted(doc["layers"]), ["totals", "visits"])
            self.assertEqual(doc["layers"]["totals"]["kind"], "sizes")


if __name__ == "__main__":
    unittest.main()
