"""Tests for new, sync, check, and the PNG reader, driven through datamap.py as a user runs them.

The fixture projects in pages/ must pass check; each bad page is a fixture copy with one defect, and must
fail with the pitfall that defect is. Browser tests run when Chrome is installed and skip otherwise.
"""
from __future__ import annotations

import io
import json
import math
import os
import re
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "pages"
sys.path.insert(0, str(HERE.parent / "skills" / "data-map" / "scripts"))
sys.path.insert(0, str(SOURCE))

import datamap  # noqa: E402
import make  # noqa: E402
from dm import chrome, png  # noqa: E402

GOOD = ["maplibre-crs", "maplibre-globe", "deck-globe", "maplibre-mercator", "maplibre-chart"]
BROWSER = chrome.find_browser()
PAGES = Path(tempfile.mkdtemp(prefix="data-map-pages-"))


def setUpModule():
    # Build the fixtures from the current levers and templates, so they can't drift from them.
    with redirect_stdout(io.StringIO()):
        make.main([], PAGES)
    shutil.copytree(SOURCE / "bare-maplibre", PAGES / "bare-maplibre")


def tearDownModule():
    shutil.rmtree(PAGES, ignore_errors=True)


def cli(*argv) -> tuple[int, dict | str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = datamap.main([str(a) for a in argv])
    text = buf.getvalue()
    try:
        return code, json.loads(text)
    except json.JSONDecodeError:
        return code, text


@contextmanager
def patched_env(**values):
    old = {k: os.environ.get(k) for k in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def copy(name: str, into: Path) -> Path:
    out = into / name
    shutil.copytree(PAGES / name, out, ignore=shutil.ignore_patterns("*.png", "check.json"))
    return out


def findings(result: dict, status: str | None = None) -> list[tuple]:
    return [(f["status"], f["check"], f["pitfall"]) for f in result["findings"] if status is None or f["status"] == status]



def spec(**changes):
    def edit(folder: Path):
        page = folder / "index.html"
        text = page.read_text()
        m = re.search(r'(id="dm-spec">\n)(.*?)(\n</script>)', text, re.S)
        current = json.loads(m[2])
        for key, value in changes.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value
        page.write_text(text[:m.start(2)] + json.dumps(current, indent=1) + text[m.end(2):])
    return edit


def page(old: str, new: str):
    def edit(folder: Path):
        p = folder / "index.html"
        text = p.read_text()
        assert old in text, old
        p.write_text(text.replace(old, new, 1))
    return edit


def module(code: str):
    return page("await DataMap.start(libs);", "await DataMap.start(libs);\n" + code)


def extend(code: str):
    """A page that changes the map in the hook DataMap.start awaits before the map reports ready."""
    return page("await DataMap.start(libs);", f"await DataMap.start(libs, async ({{map}}) => {{ {code}; await map.once('idle'); }});")


ALBERS_NO_ORIGIN = "+proj=aea +lat_1=28.65 +lat_2=45.25 +lat_0=36.95 +lon_0=-95.95 +datum=WGS84 +units=m +no_defs"


def data(stem: str, fn, resync: bool = True):
    def edit(folder: Path):
        f = folder / "data" / f"{stem}.json" if (folder / "data" / f"{stem}.json").exists() else folder / "data" / f"{stem}.geojson"
        doc = json.loads(f.read_text())
        fn(doc)
        f.write_text(json.dumps(doc))
        if resync:
            cli("sync", folder)
    return edit


def remove(rel: str):
    return lambda folder: (folder / rel).unlink()


def add_data(stem: str):
    def edit(folder: Path):
        (folder / "data" / f"{stem}.geojson").write_text('{"type":"FeatureCollection","features":[]}')
        cli("sync", folder)
    return edit


def lib_edit(folder: Path):
    p = folder / "index.html"
    text = p.read_text()
    p.write_text(text.replace("const ARC_APEX = 0.08;", "const ARC_APEX = 0.5;", 1))


def recolor(doc):
    for f in doc["features"]:
        if f["properties"].get("dm_class", -1) >= 0:
            f["properties"]["dm_fill"] = "#ff00ff"


def turn_arrows(doc):
    for f in doc["features"]:
        f["properties"]["dm_bearing"] = (f["properties"]["dm_bearing"] + 90) % 360


def drop_why(folder: Path):
    p = folder / "index.html"
    text = p.read_text()
    p.write_text(re.sub(r'"why": "the arcs[^"]*"', '"why": ""', text, count=1))


STATIC_BAD = [
    ("world choropleth in Web Mercator", "maplibre-crs", spec(projection={"type": "mercator"}), ("FAIL", "projection", 10)),
    ("world choropleth on the globe", "maplibre-crs", spec(projection={"type": "globe"}), ("FAIL", "projection", 10)),
    ("world choropleth in a CRS that isn't equal-area", "maplibre-crs",
     spec(projection={"type": "crs", "name": "custom:robinson", "definition": "+proj=robin", "property": "compromise"}), ("FAIL", "projection", 10)),
    ("a world-wide [W, S, E, N] extent in Web Mercator", "maplibre-crs", spec(extent=[-180, -60, 180, 85], projection={"type": "mercator"}),
     ("FAIL", "projection", 10)),
    ("Web Mercator tiles under a CRS", "maplibre-crs", spec(tiles=[{"source": "basemap", "grid": "web-mercator", "url": "data/basemap.pmtiles"}]),
     ("FAIL", "tiles", 11)),
    ("zoom buttons nobody listed", "maplibre-globe", module("dataMap.map.addControl(new libs.maplibregl.NavigationControl());"), ("WARN", "controls", 23)),
    ("three font families", "maplibre-globe",
     page("</head>", "<style>h1 { font-family: Georgia, serif; } footer { font-family: 'Comic Sans MS'; } aside { font-family: Roboto; }</style>\n</head>"),
     ("WARN", "fonts", 23)),
    ("pitch with no recorded reason", "maplibre-globe", spec(pitch=45), ("FAIL", "pitch", 22)),
    ("raised arcs with no recorded reason", "deck-globe", drop_why, ("FAIL", "raised-arcs", 22)),
    ("an autoplay loop", "maplibre-globe", module("setInterval(() => dataMap.map.panBy([10, 0]), 1000);"), ("FAIL", "motion", 26)),
    ("declared motion with no reduced-motion", "maplibre-globe",
     lambda f: (spec(animation={"trigger": "user", "controls": ["play", "pause"]})(f), module("requestAnimationFrame(() => {});")(f)), ("FAIL", "motion", 26)),
    ("no zoom limits", "maplibre-globe", spec(zoom=None), ("WARN", "zoom", 25)),
    ("legend.json missing", "maplibre-crs", lambda f: (remove("data/legend.json")(f), cli("sync", f)), ("FAIL", "legend", 9)),
    ("a data layer no legend explains", "maplibre-crs", add_data("stations"), ("FAIL", "legend", 9)),
    ("data changed after sync", "maplibre-crs", data("density", recolor, resync=False), ("FAIL", "sync", 9)),
    ("the title still the placeholder", "maplibre-crs", page('id="dm-title">Bangladesh', 'id="dm-title">[A title] Bangladesh'), ("FAIL", "title", 24)),
    ("a title that says map", "maplibre-crs", page('id="dm-title">Bangladesh', 'id="dm-title">A map: Bangladesh'), ("WARN", "title", 24)),
    ("no source line", "maplibre-globe", page('<p id="dm-source">Source: synthetic test data for the data-map plugin.</p>', ""), ("FAIL", "source", 24)),
    ("maplibre-gl off its pin", "maplibre-globe", lambda f: (page("maplibre-gl@6.18.0/dist/maplibre-gl.css", "maplibre-gl@6.17.0/dist/maplibre-gl.css")(f)),
     ("FAIL", "pins", None)),
    ("the library edited by hand", "deck-globe", lib_edit, ("FAIL", "library", None)),
    ("dm-spec that doesn't parse", "maplibre-crs", page('"version": 1,', '"version": 1,,'), ("FAIL", "spec", None)),
]

BROWSER_BAD = [
    ("class colors that disagree with the legend", "maplibre-crs", data("density", recolor), ("FAIL", "legend-colors", 9)),
    ("arrowheads turned off their lines", "maplibre-globe", data("movers-arrows", turn_arrows), ("FAIL", "arrows", 17)),
    ("a map still moving at ready", "maplibre-globe", module("dataMap.map.panBy([300, 0], {duration: 20000});"), ("FAIL", "motion", 26)),
    ("an Albers definition with no false origin", "maplibre-crs",
     spec(projection={"type": "crs", "name": "custom:albers", "definition": ALBERS_NO_ORIGIN, "property": "equal-area"}), ("FAIL", "ready", 33)),
    ("a page that throws", "maplibre-mercator", page("const spec = DataMap.spec;", "throw new Error('the page broke');\nconst spec = DataMap.spec;"),
     ("FAIL", "ready", 33)),
]


class Static(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_good_pages_pass_the_static_pass_and_say_the_render_was_not_measured(self):
        for name in GOOD:
            with self.subTest(name):
                code, result = cli("check", copy(name, self.tmp), "--no-browser", "--json")
                self.assertEqual(code, 0, findings(result, "FAIL"))
                self.assertIn(("WARN", "render", 33), findings(result))

    def test_each_bad_page_fails_with_its_pitfall(self):
        for what, name, edit, want in STATIC_BAD:
            with self.subTest(what):
                folder = copy(name, self.tmp / what.replace(" ", "-"))
                edit(folder)
                code, result = cli("check", folder, "--no-browser", "--json")
                self.assertIn(want, findings(result), f"{what}: {findings(result)}")
                self.assertEqual(code, 1 if want[0] == "FAIL" else 0)

    def test_a_box_extent_is_large_from_60_degrees_of_longitude_or_40_of_latitude(self):
        for box, status in (([-10, 35, 49, 74], "PASS"), ([-10, 35, 50, 60], "FAIL"), ([-10, 20, 30, 60], "FAIL"), ([170, 0, -131, 10], "PASS"),
                            ([170, 0, -129, 10], "FAIL")):
            with self.subTest(box):
                folder = copy("maplibre-crs", self.tmp / "-".join(map(str, box)))
                spec(extent=box, projection={"type": "mercator"})(folder)
                code, result = cli("check", folder, "--no-browser", "--json")
                self.assertIn((status, "projection", 10), findings(result))
                self.assertEqual(code, 1 if status == "FAIL" else 0)

    def test_dm_spec_figure_sets_the_size_and_scale_unless_flags_do(self):
        folder = copy("maplibre-mercator", self.tmp)
        spec(figure={"size": "1000x600", "scale": 2})(folder)
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual((code, result["size"], result["scale"]), (0, [1000, 600], 2))
        code, result = cli("check", folder, "--no-browser", "--json", "--size", "800x500")
        self.assertEqual((result["size"], result["scale"]), ([800, 500], 2))
        code, result = cli("check", folder, "--no-browser", "--json", "--scale", "1")
        self.assertEqual((result["size"], result["scale"]), ([1000, 600], 1))
        spec(figure=None)(folder)
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual((result["size"], result["scale"]), ([1200, 800], 1))
        spec(figure={"size": "wide"})(folder)
        self.assertEqual(cli("check", folder, "--no-browser")[0], 2)

    def test_a_synced_page_without_data_is_checked_from_its_inlined_blocks(self):
        folder = copy("maplibre-globe", self.tmp)
        shutil.rmtree(folder / "data")
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertIn(("PASS", "legend", 9), findings(result))
        self.assertIn("inlined data files are its data", next(f["message"] for f in result["findings"] if f["check"] == "sync"))
        # sync would drop every inlined file, so it refuses and leaves the page alone.
        before = (folder / "index.html").read_text()
        self.assertEqual(cli("sync", folder)[0], 2)
        self.assertEqual((folder / "index.html").read_text(), before)
        page('"layers":{"movers"', '"layers":{"movers"}{')(folder)
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual(code, 1)

    def test_the_worked_example_passes_the_static_pass(self):
        example = HERE.parent / "skills" / "data-map" / "assets" / "example" / "movers"
        folder = self.tmp / "movers"
        shutil.copytree(example, folder)
        self.assertFalse((folder / "data").exists())
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertEqual((result["size"], result["scale"]), ([1200, 700], 2))

    def test_a_page_without_dm_spec_is_judged_on_its_render_only(self):
        code, result = cli("check", copy("bare-maplibre", self.tmp), "--no-browser", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(findings(result)[0], ("WARN", "spec", None))
        self.assertNotIn("legend", {f[1] for f in findings(result)})

    def test_a_chart_page_skips_the_map_rules(self):
        code, result = cli("check", copy("maplibre-chart", self.tmp), "--no-browser", "--json")
        checks = {f[1] for f in findings(result)}
        self.assertEqual(code, 0)
        self.assertIn("chart", checks)
        self.assertFalse(checks & {"projection", "legend", "zoom", "tiles"})

    def test_sync_check_reports_drift_and_sync_repairs_it(self):
        folder = copy("maplibre-globe", self.tmp)
        self.assertEqual(cli("sync", folder, "--check")[0], 0)
        data("movers", lambda doc: doc["features"].pop(), resync=False)(folder)
        code, out = cli("sync", folder, "--check")
        self.assertEqual(code, 1)
        self.assertIn("data/movers.geojson changed since the last sync", out)
        cli("sync", folder)
        self.assertEqual(cli("sync", folder, "--check")[0], 0)

    def test_sync_inlines_data_that_opens_from_file(self):
        folder = copy("maplibre-globe", self.tmp)
        (folder / "data" / "note.json").write_text('{"text": "</script><script>alert(1)</script>"}')
        cli("sync", folder)
        text = (folder / "index.html").read_text()
        block = re.search(r'<script type="application/json" id="dm-data-note">(.*?)</script>', text)[1]
        self.assertEqual(json.loads(block), {"text": "</script><script>alert(1)</script>"})


class New(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def spec_of(self, folder: Path) -> dict:
        return json.loads(re.search(r'id="dm-spec">\n(.*?)\n</script>', (folder / "index.html").read_text(), re.S)[1])

    def test_presets_set_the_projection(self):
        for stack, preset, want in (("maplibre", None, "crs"), ("maplibre", "globe", "globe"), ("maplibre", "mercator", "mercator"),
                                    ("deck-gl", None, "globe")):
            with self.subTest(f"{stack} {preset}"):
                out = self.tmp / f"{stack}-{preset}"
                args = ["new", stack, out] + (["--preset", preset] if preset else [])
                self.assertEqual(cli(*args)[0], 0)
                self.assertEqual(self.spec_of(out)["projection"]["type"], want)
                self.assertTrue((out / "brief.md").is_file() and (out / "data").is_dir())
                self.assertEqual(cli("sync", out, "--check")[0], 0)

    def test_every_template_brief_holds_the_brief_lines_in_one_block(self):
        want = ["Reader:", "Task:", "Question:", "Data:", "Supports:", "Location:", "Candidates:", "Idiom:", "Companions:",
                "Visual plan:", "Interface:", "Projection:", "Stack:", "Sensitive:", "Answer key:", "Departures:"]
        for stack in ("maplibre", "deck-gl", "mln-rs"):
            with self.subTest(stack):
                out = self.tmp / stack
                self.assertEqual(cli("new", stack, out)[0], 0)
                head, intro, blocks = re.fullmatch(r"(# Brief)\n\n([^\n]+)\n\n((?:```[a-z]*\n.*?```\n)+)", (out / "brief.md").read_text(), re.S).groups()
                self.assertEqual(blocks.count("```"), 2)
                self.assertEqual(blocks.splitlines()[1:-1], want)

    def test_the_chart_preset_has_no_map(self):
        out = self.tmp / "chart"
        self.assertEqual(cli("new", "maplibre", out, "--preset", "chart")[0], 0)
        s = self.spec_of(out)
        self.assertIsNone(s["projection"])
        self.assertEqual(s["idiom"], ["no-map"])

    def test_deck_gl_refuses_a_crs(self):
        self.assertEqual(cli("new", "deck-gl", self.tmp / "d", "--preset", "equal-earth")[0], 2)

    def test_new_will_not_write_into_a_folder_with_files(self):
        out = self.tmp / "taken"
        out.mkdir()
        (out / "keep.txt").write_text("x")
        self.assertEqual(cli("new", "maplibre", out)[0], 2)
        self.assertEqual(cli("new", "maplibre", out, "--force")[0], 0)

    def test_mln_rs_gets_its_own_package_name_and_fresh_files(self):
        template = HERE.parent / "skills" / "data-map" / "assets" / "templates" / "mln-rs"
        if not (template / "Cargo.toml").is_file():
            self.skipTest("no mln-rs template")
        out = self.tmp / "3 Lakes Demo"
        self.assertEqual(cli("new", "mln-rs", out)[0], 0)
        self.assertRegex((out / "Cargo.toml").read_text(), r'\[package\]\nname = "map-3-lakes-demo"')
        if (out / "Cargo.lock").is_file():
            self.assertIn('name = "map-3-lakes-demo"', (out / "Cargo.lock").read_text())
        self.assertGreater((out / "Cargo.toml").stat().st_mtime, (template / "Cargo.toml").stat().st_mtime)
        self.assertEqual(cli("new", "mln-rs", self.tmp / "x", "--preset", "globe")[0], 2)


def encode_png(w: int, h: int, rows: list[bytes], ctype: int, filters: list[int]) -> bytes:
    """A reference PNG encoder that applies each scanline filter, so decoding must invert every one."""
    bpp = {2: 3, 6: 4}[ctype]
    raw, prev = b"", bytes(w * bpp)
    for row, f in zip(rows, filters):
        out = bytearray()
        for i, x in enumerate(row):
            a = row[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            pred = {0: 0, 1: a, 2: b, 3: (a + b) // 2,
                    4: (a if abs(b - c) <= abs(a - c) and abs(b - c) <= abs(a + b - 2 * c) else b if abs(a - c) <= abs(a + b - 2 * c) else c)}[f]
            out.append((x - pred) & 255)
        raw += bytes([f]) + bytes(out)
        prev = row

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class Png(unittest.TestCase):
    def test_every_filter_type_decodes_to_the_original_pixels(self):
        w, h = 7, 5
        rows = [bytes((x * 37 + y * 91 + c * 53) % 256 for x in range(w) for c in range(3)) for y in range(h)]
        img = png.read(encode_png(w, h, rows, 2, [0, 1, 2, 3, 4]))
        got = [bytes(img.rgba[(y * w + x) * 4 + c] for x in range(w) for c in range(3)) for y in range(h)]
        self.assertEqual(got, rows)

    def test_transparent_pixels_blend_onto_the_page_background(self):
        rows = [bytes([255, 0, 0, 128, 0, 0, 255, 0])]
        img = png.read(encode_png(2, 1, rows, 6, [0]), background="#ffffff")
        self.assertEqual(list(img.rgba[0:3]), [255, 127, 127])
        self.assertEqual(list(img.rgba[4:7]), [255, 255, 255])

    def test_color_counts_honor_the_tolerance(self):
        rows = [bytes([10, 20, 30] * 3 + [14, 24, 34] * 2 + [200, 200, 200])]
        counts = png.read(encode_png(6, 1, rows, 2, [0])).histogram()
        self.assertEqual(png.near(counts, "#0a141e", 0), 3)
        self.assertEqual(png.near(counts, "#0a141e", 4), 5)


class PngCheck(unittest.TestCase):
    """check --png judges a snapshot another renderer wrote, such as mln-rs."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        layer = {"kind": "classes", "colors": ["#fee5d9", "#a50f15"], "labels": ["low", "high"], "counts": [3, 2],
                 "nodata": {"color": "#d9d9d9", "label": "No data", "count": 0}}
        (self.tmp / "legend.json").write_text(json.dumps({"version": 1, "layers": {"v": layer}}))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def snapshot(self, row: list[tuple], h: int = 40, alpha: bool = False) -> Path:
        """Every row of the snapshot is ROW, one tuple per pixel."""
        f = self.tmp / "snap.png"
        f.write_bytes(encode_png(len(row), h, [b"".join(bytes(p) for p in row)] * h, 6 if alpha else 2, [0] * h))
        return f

    def test_a_blank_snapshot_fails(self):
        snap = self.snapshot([(255, 255, 255)] * 40)
        code, result = cli("check", "--png", snap, "--legend", self.tmp / "legend.json", "--json")
        self.assertEqual(code, 1)
        self.assertIn(("FAIL", "blank", 33), findings(result))

    def test_a_snapshot_with_every_legend_color_passes(self):
        snap = self.snapshot([(0xfe, 0xe5, 0xd9)] * 15 + [(0xa5, 0x0f, 0x15)] * 15 + [(255, 255, 255)] * 10)
        code, result = cli("check", "--png", snap, "--legend", self.tmp / "legend.json", "--json")
        self.assertEqual(code, 0, findings(result))
        self.assertIn(("PASS", "legend-colors", 9), findings(result))

    def test_a_missing_class_color_fails(self):
        snap = self.snapshot([(0xfe, 0xe5, 0xd9)] * 30 + [(255, 255, 255)] * 10)
        code, result = cli("check", "--png", snap, "--legend", self.tmp / "legend.json", "--json")
        self.assertEqual(code, 1)
        self.assertIn(("FAIL", "legend-colors", 9), findings(result))

    def test_transparent_space_around_a_globe_counts_as_page(self):
        snap = self.snapshot([(0xfe, 0xe5, 0xd9, 255)] * 15 + [(0xa5, 0x0f, 0x15, 255)] * 15 + [(0, 0, 0, 0)] * 10, alpha=True)
        code, result = cli("check", "--png", snap, "--legend", self.tmp / "legend.json", "--json")
        self.assertEqual(code, 0, findings(result))
        self.assertIn("#ffffff", json.dumps(result))

    def test_a_snapshot_taken_while_moving_fails(self):
        snap = self.snapshot([(0xfe, 0xe5, 0xd9)] * 15 + [(0xa5, 0x0f, 0x15)] * 15 + [(255, 255, 255)] * 10)
        (self.tmp / "r.json").write_text(json.dumps({"moving": True, "pitch": 0, "controls": [], "fonts": ["system-ui"]}))
        code, result = cli("check", "--png", snap, "--legend", self.tmp / "legend.json", "--report", self.tmp / "r.json", "--json")
        self.assertEqual(code, 1)
        self.assertIn(("FAIL", "motion", 26), findings(result))


def degrees(a: list, b: list) -> float:
    """The angle between two [lon, lat] points, in degrees."""
    (x1, y1), (x2, y2) = [map(math.radians, p) for p in (a, b)]
    return math.degrees(math.acos(min(1, math.sin(y1) * math.sin(y2) + math.cos(y1) * math.cos(y2) * math.cos(x2 - x1))))


def blobs(img, rgb: tuple, tol: int = 60) -> list[tuple]:
    """Each connected patch of RGB in the image, as (pixels, width, height)."""
    w, h, px = img.w, img.h, img.rgba
    hit = {i // 4 for i in range(0, len(px), 4) if all(abs(px[i + k] - rgb[k]) <= tol for k in range(3))}
    out = []
    while hit:
        stack = [hit.pop()]
        seen = list(stack)
        while stack:
            i = stack.pop()
            x, y = i % w, i // w
            for j in (i - 1 if x else None, i + 1 if x < w - 1 else None, i - w if y else None, i + w if y < h - 1 else None):
                if j is not None and j in hit:
                    hit.discard(j)
                    stack.append(j)
                    seen.append(j)
        xs, ys = [i % w for i in seen], [i // w for i in seen]
        out.append((len(seen), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
    return out


@unittest.skipUnless(BROWSER, "no Chrome, Chromium, Edge, or Brave to render with")
class Render(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def render(self, folder: Path, *args) -> tuple[int, dict]:
        code, result = cli("check", folder, "--json", *args)
        if ("WARN", "render", 33) in findings(result):
            self.skipTest("render not measured here: " + next(f["message"] for f in result["findings"] if f["check"] == "render"))
        return code, result

    def test_good_pages_pass_a_real_render_at_scales_1_and_2(self):
        for name in GOOD + ["bare-maplibre"]:
            for scale in ("1", "2"):
                with self.subTest(f"{name} @{scale}x"):
                    folder = copy(name, self.tmp / scale)
                    code, result = self.render(folder, "--scale", scale)
                    self.assertEqual(code, 0, findings(result, "FAIL"))
                    self.assertTrue(Path(result["png"]).is_file())
                    if name != "bare-maplibre":
                        self.assertEqual(findings(result, "WARN"), [], name)

    def test_a_side_panel_that_cuts_off_its_companions_fails(self):
        folder = copy("maplibre-mercator", self.tmp)
        spec(companions=[{"type": "table", "layer": "capacity", "title": "Capacity by reservoir", "top": 6}] * 6)(folder)
        code, result = self.render(folder, "--size", "1200x600")
        self.assertEqual(code, 1)
        self.assertIn(("FAIL", "clipped", 24), findings(result))

    def test_a_crs_with_no_false_origin_fails_with_the_fix(self):
        folder = copy("maplibre-crs", self.tmp)
        spec(projection={"type": "crs", "name": "custom:albers", "definition": ALBERS_NO_ORIGIN, "property": "equal-area"})(folder)
        code, result = self.render(folder)
        ready = next(f for f in result["findings"] if f["check"] == "ready")
        self.assertEqual((code, ready["status"]), (1, "FAIL"))
        self.assertIn(ALBERS_NO_ORIGIN, ready["message"])
        self.assertIn("add +x_0=0 +y_0=0 to the definition", ready["message"])

    def test_base_files_draw_under_the_data_with_no_legend(self):
        folder = copy("maplibre-mercator", self.tmp)
        code, result = self.render(folder)
        self.assertEqual(code, 0, findings(result, "FAIL"))
        rep = result["report"]
        ids = [layer["id"] for layer in rep["layers"]]
        self.assertLess(ids.index("base-rivers-line"), ids.index("capacity"))
        self.assertGreater(rep["rendered"]["base-rivers"], 0)
        self.assertNotIn("base-rivers", {e["layer"] for e in rep["legendEntries"]})

    def test_tooltips_false_takes_the_tooltips_off(self):
        for value, want in ((None, True), (False, False)):
            with self.subTest(tooltips=value):
                folder = copy("maplibre-globe", self.tmp / str(value))
                spec(tooltips=value)(folder)
                code, result = self.render(folder)
                self.assertEqual((code, result["report"]["tooltips"]), (0, want))

    def test_labels_warn_on_a_name_that_did_not_render_or_sits_under_a_head(self):
        cases = [("a name under an arrowhead", "map.setLayoutProperty('movers-labels', 'text-radial-offset', undefined); "
                  "map.setLayoutProperty('movers-labels', 'text-anchor', 'center'); map.setLayoutProperty('movers-labels', 'text-offset', [0, 0])",
                  "arrowheads cover", "Tokyo under the head of"),
                 ("names too big to fit", "map.setLayoutProperty('movers-labels', 'text-size', 40)", "didn't render", "names of movers-labels")]
        for what, code, says, names in cases:
            with self.subTest(what):
                folder = copy("maplibre-globe", self.tmp / what.replace(" ", "-"))
                extend(code)(folder)
                status, result = self.render(folder)
                warns = [f["message"] for f in result["findings"] if (f["status"], f["check"]) == ("WARN", "labels")]
                self.assertEqual(status, 0, findings(result, "FAIL"))
                self.assertTrue(any(says in m and names in m for m in warns), warns)

    def test_the_globe_keeps_its_size_and_its_zoom_range_as_it_turns(self):
        folder = copy("maplibre-globe", self.tmp / "load")
        fitted = self.render(folder)[1]["report"]["globe"]["radius"]
        for lat, zoom, limit, factor in ((0, -10, "minZoom", 1), (0, 30, "maxZoom", 8), (70, 30, "maxZoom", 8)):
            with self.subTest(lat=lat, zoom=zoom):
                folder = copy("maplibre-globe", self.tmp / f"{lat}-{zoom}")
                extend(f"map.jumpTo({{center: [150, {lat}]}}); map.setZoom({zoom})")(folder)
                rep = self.render(folder)[1]["report"]
                self.assertAlmostEqual(rep["globe"]["radius"] / fitted, factor, delta=0.02 * factor)
                self.assertAlmostEqual(rep["zoom"], rep[limit], places=3)

    def test_globe_circles_keep_their_legend_size_out_to_the_rim(self):
        folder = copy("maplibre-globe", self.tmp)
        extend("for (const l of map.getStyle().layers) if (l.id !== 'movers-nodes') map.setLayoutProperty(l.id, 'visibility', 'none'); "
               "map.setPaintProperty('movers-nodes', 'circle-color', '#ff00ff'); map.setPaintProperty('movers-nodes', 'circle-stroke-width', 0); "
               "map.setPaintProperty('movers-nodes', 'circle-radius', 8); map.jumpTo({center: [175, 10]})")(folder)
        result = self.render(folder, "--scale", "2")[1]
        img = png.read(Path(result["png"]).read_bytes())
        # Round patches only: two circles that touch merge into one patch.
        radii = [round((n / 3.14159) ** 0.5 / 2, 2) for n, w, h in blobs(img, (255, 0, 255)) if abs(w - h) <= 2]
        self.assertGreaterEqual(len(radii), 6, radii)
        self.assertTrue(all(7.4 <= r <= 8.4 for r in radii), radii)

    def test_the_globe_opens_on_its_largest_destinations_unless_dm_spec_centers_it(self):
        def into_mexico_city(doc):
            for f in doc["features"]:
                if f["properties"]["dm_d"] == "MEX":
                    f["properties"]["dm_value"] *= 1000
        mexico_city = make.PACIFIC["MEX"][1:3]
        for center, want in ((None, mexico_city), ([120, 30], [120, 30])):
            with self.subTest(center=center):
                folder = copy("maplibre-globe", self.tmp / str(center))
                data("movers", into_mexico_city)(folder)
                spec(center=center)(folder)
                rep = self.render(folder)[1]["report"]
                self.assertLess(degrees(rep["center"], want), 64 if center is None else 0.01, rep["center"])

    def test_raised_arcs_say_in_the_legend_that_height_is_distance(self):
        for name, want in (("deck-globe", True), ("maplibre-globe", False)):
            with self.subTest(name):
                rep = self.render(copy(name, self.tmp / name))[1]["report"]
                said = any(b["text"] == "Arc height shows distance, not movers." for b in rep["textBoxes"])
                self.assertEqual(said, want)

    def test_a_synced_page_without_data_renders_and_passes(self):
        folder = copy("maplibre-globe", self.tmp)
        shutil.rmtree(folder / "data")
        code, result = self.render(folder)
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertEqual(findings(result, "WARN"), [])

    def test_without_a_network_the_render_is_reported_not_measured(self):
        folder = copy("maplibre-globe", self.tmp)
        with patched_env(DM_CHROME_FLAGS="--proxy-server=127.0.0.1:9"):
            code, result = cli("check", folder, "--json")
        self.assertEqual(code, 0, findings(result, "FAIL"))
        render = next(f for f in result["findings"] if f["check"] == "render")
        self.assertEqual((render["status"], render["pitfall"]), ("WARN", 33))
        self.assertIn("no network", render["message"])

    def test_a_chrome_that_cannot_start_is_reported_not_measured(self):
        folder = copy("maplibre-crs", self.tmp)
        with patched_env(DM_BROWSER="/usr/bin/false"):
            code, result = cli("check", folder, "--json")
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertIn(("WARN", "render", 33), findings(result))

    def test_each_bad_render_fails_with_its_pitfall(self):
        for what, name, edit, want in BROWSER_BAD:
            with self.subTest(what):
                folder = copy(name, self.tmp / what.replace(" ", "-"))
                edit(folder)
                code, result = self.render(folder)
                self.assertEqual(code, 1)
                self.assertIn(want, findings(result), f"{what}: {findings(result)}")


if __name__ == "__main__":
    unittest.main()
