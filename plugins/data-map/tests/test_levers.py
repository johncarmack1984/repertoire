"""Goldens for data-map's levers. Expected values are worked by hand from the sources, not taken from a run."""

import io
import itertools
import json
import math
import random
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "skills" / "data-map" / "scripts"))

import datamap  # noqa: E402
from dm import classify, commands, crs, data, flows, geo, symbols  # noqa: E402

FIX = HERE / "fixtures"
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
