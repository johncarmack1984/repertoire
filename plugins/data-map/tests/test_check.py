"""Tests for new, sync, check, and the PNG reader, driven through datamap.py as a user runs them.

The fixture projects in pages/ must pass check; each bad page is a fixture copy with one defect, and must
fail with the pitfall that defect is. Browser tests run when Chrome is installed and skip otherwise.
"""
from __future__ import annotations

import io
import json
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
