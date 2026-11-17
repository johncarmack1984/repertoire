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
from dm import chrome, png, vendor  # noqa: E402

GOOD = ["maplibre-crs", "maplibre-globe", "deck-globe", "maplibre-mercator", "maplibre-flows", "maplibre-chart"]
# The warnings each good page renders with. A great circle can't bend around a node, and three of the Pacific
# globe's run over Seoul, Los Angeles, and San Francisco at the opening view; the lever warns of it as well.
EXPECTED_WARNS = {"maplibre-globe": [("WARN", "flows-over-nodes", 16)]}
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


def tab_title(text: str):
    def edit(folder: Path):
        p = folder / "index.html"
        p.write_text(re.sub(r"<title>.*?</title>", f"<title>{text}</title>", p.read_text(), count=1))
    return edit


def working_file(name: str):
    return lambda folder: (folder / name).write_text("x")


def from_jsdelivr(folder: Path):
    """The page as round 3 shipped it: MapLibre imported from jsDelivr, nothing in vendor/."""
    p = folder / "index.html"
    text = re.sub(r"<!-- data-map:vendor -->\n.*?<!-- /data-map:vendor -->\n", "", p.read_text(), count=1, flags=re.S)
    text = text.replace("const libs = await DataMap.libs();",
                        "const libs = {maplibregl: await import('https://cdn.jsdelivr.net/npm/maplibre-gl@6.18.0/dist/maplibre-gl.mjs')};")
    p.write_text(text)
    shutil.rmtree(folder / "vendor")


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
    ("the tab's title still the placeholder", "maplibre-crs", tab_title("[A title that states the point]"), ("FAIL", "title", 24)),
    ("no tab title", "maplibre-globe", tab_title(""), ("FAIL", "title", 24)),
    ("the brief beside the page", "maplibre-crs", working_file("brief.md"), ("WARN", "deliverable", None)),
    ("an old screenshot beside the page", "maplibre-globe", working_file("index.1200x800@2x.png"), ("WARN", "deliverable", None)),
    ("a title that says map", "maplibre-crs", page('id="dm-title">Bangladesh', 'id="dm-title">A map: Bangladesh'), ("WARN", "title", 24)),
    ("no source line", "maplibre-globe", page('<p id="dm-source">Source: synthetic test data for the data-map plugin.</p>', ""), ("FAIL", "source", 24)),
    ("maplibre-gl off its pin", "maplibre-globe", page('href="vendor/maplibre-gl@6.18.0/maplibre-gl.css"', 'href="vendor/maplibre-gl@6.17.0/maplibre-gl.css"'),
     ("FAIL", "pins", None)),
    ("a vendored library edited", "maplibre-crs", lambda f: (f / "vendor/proj4@2.22.0/proj4.text.js").write_text(
        (f / "vendor/proj4@2.22.0/proj4.text.js").read_text().replace("6378137", "6378138", 1)), ("FAIL", "pins", None)),
    ("a vendored library missing", "deck-globe", remove("vendor/deck.gl@9.4.1/dist.min.js"), ("FAIL", "pins", None)),
    ("a library loaded from jsDelivr", "maplibre-globe", from_jsdelivr, ("WARN", "offline", 33)),
    ("a CRS page whose vendor region lost proj4", "maplibre-crs", lambda f: (f / "vendor/proj4@2.22.0/proj4.text.js").unlink() or
     page('<script src="vendor/proj4@2.22.0/proj4.text.js"></script>\n', "")(f), ("FAIL", "sync", 9)),
    ("the library edited by hand", "deck-globe", lib_edit, ("FAIL", "library", None)),
    ("dm-spec that doesn't parse", "maplibre-crs", page('"version": 1,', '"version": 1,,'), ("FAIL", "spec", None)),
    ("a note with no place", "maplibre-crs", spec(annotations=[{"text": "Bangladesh"}]), ("FAIL", "annotations", 24)),
    ("a reveal control with nothing to reveal", "maplibre-globe", spec(controls=["reveal"]), ("WARN", "controls", 23)),
    ("a highlight that isn't a list of keys", "maplibre-globe", spec(highlight="TYO"), ("FAIL", "highlight", 24)),
    ("a focus template with a field the page doesn't fill", "maplibre-flows", spec(focus={"title": "{name} sends most to {nme}"}), ("FAIL", "focus", 24)),
    ("focus on a layer that holds only its largest flows", "maplibre-globe", spec(controls=["focus"], focus={"title": "{name}"}), ("WARN", "focus", 24)),
    ("focus with no flows to focus", "maplibre-crs", spec(controls=["focus"]), ("WARN", "controls", 23)),
    ("a hint that is neither words nor false", "maplibre-globe", spec(hint=True), ("FAIL", "hint", 23)),
]

BROWSER_BAD = [
    ("class colors that disagree with the legend", "maplibre-crs", data("density", recolor), ("FAIL", "legend-colors", 9)),
    ("arrowheads turned off their lines", "maplibre-globe", data("movers-arrows", turn_arrows), ("FAIL", "arrows", 17)),
    ("a map still moving at ready", "maplibre-globe", module("dataMap.map.panBy([300, 0], {duration: 20000});"), ("FAIL", "motion", 26)),
    ("an Albers definition with no false origin", "maplibre-crs",
     spec(projection={"type": "crs", "name": "custom:albers", "definition": ALBERS_NO_ORIGIN, "property": "equal-area"}), ("FAIL", "ready", 33)),
    ("a page that throws", "maplibre-mercator", page("const libs = await DataMap.libs();", "throw new Error('the page broke');\nconst libs = await DataMap.libs();"),
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
        # sync keeps every inlined file and puts back the libraries the page can't travel without.
        before = (folder / "index.html").read_text()
        shutil.rmtree(folder / "vendor")
        self.assertEqual(cli("sync", folder)[0], 0)
        self.assertEqual((folder / "index.html").read_text(), before)
        self.assertTrue((folder / "vendor").is_dir())
        page('"layers":{"movers"', '"layers":{"movers"}{')(folder)
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual(code, 1)

    def test_the_worked_example_passes_the_static_pass(self):
        example = HERE.parent / "skills" / "data-map" / "assets" / "example" / "movers"
        folder = self.tmp / "movers"
        shutil.copytree(example, folder)
        self.assertFalse((folder / "data").exists() or (folder / "vendor").exists())
        self.assertEqual(cli("sync", folder)[0], 0)
        code, result = cli("check", folder, "--no-browser", "--json")
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertEqual({f[1] for f in findings(result, "WARN")}, {"render"})
        self.assertEqual((result["size"], result["scale"]), ([1200, 654], 2))

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

    def test_sync_vendors_exactly_the_libraries_the_page_draws_with(self):
        folder = copy("maplibre-crs", self.tmp)
        held = lambda: sorted(d.name for d in (folder / "vendor").iterdir())
        self.assertEqual(held(), ["maplibre-gl@6.18.0", "proj4@2.22.0"])
        spec(projection={"type": "globe"}, idiom=["flows"])(folder)
        self.assertEqual(cli("sync", folder, "--check")[0], 1)
        self.assertEqual(cli("sync", folder)[0], 0)
        self.assertEqual(held(), ["maplibre-gl@6.18.0"])
        self.assertNotIn("proj4", (folder / "index.html").read_text().split("<!-- /data-map:vendor -->")[0])
        (folder / "vendor" / "maplibre-gl@6.18.0" / "maplibre-gl.css").unlink()
        code, out = cli("sync", folder, "--check")
        self.assertEqual(code, 1)
        self.assertIn("vendor/maplibre-gl@6.18.0/maplibre-gl.css is missing", out)

    def test_a_second_project_syncs_from_the_cache_with_no_network(self):
        npm = {"DM_NPM": "http://127.0.0.1:9"}
        with patched_env(DM_CACHE=str(self.tmp / "empty"), **npm):
            code, out = cli("new", "maplibre", self.tmp / "nothing-cached")
        self.assertEqual(code, 2)
        self.assertIn("can't fetch http://127.0.0.1:9/maplibre-gl@6.18.0/dist/maplibre-gl.mjs", out)
        self.assertIn(str(self.tmp / "empty"), out)
        shutil.copytree(vendor.cache_dir(), self.tmp / "cache")
        with patched_env(DM_CACHE=str(self.tmp / "cache"), **npm):
            self.assertEqual(cli("new", "deck-gl", self.tmp / "second")[0], 0)
            self.assertEqual(cli("sync", self.tmp / "second", "--check")[0], 0)
        self.assertTrue((self.tmp / "second" / "vendor" / "deck.gl@9.4.1" / "dist.min.js").is_file())

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
                self.assertTrue((out / ".dm" / "brief.md").is_file() and (out / "data").is_dir())
                self.assertFalse((out / "brief.md").exists(), "the brief is a working file, kept out of the deliverable")
                self.assertEqual(cli("sync", out, "--check")[0], 0)

    def test_every_template_brief_holds_the_brief_lines_in_one_block(self):
        want = ["Reader:", "Task:", "Question:", "Data:", "Supports:", "Location:", "Candidates:", "Idiom:", "Companions:",
                "Visual plan:", "Interface:", "Projection:", "Stack:", "Sensitive:", "Answer key:", "Departures:"]
        for stack in ("maplibre", "deck-gl", "mln-rs"):
            with self.subTest(stack):
                out = self.tmp / stack
                self.assertEqual(cli("new", stack, out)[0], 0)
                head, intro, blocks = re.fullmatch(r"(# Brief)\n\n([^\n]+)\n\n((?:```[a-z]*\n.*?```\n)+)", (out / ".dm" / "brief.md").read_text(), re.S).groups()
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


def crop(img, box: dict, scale: float):
    """The part of the image under a CSS-px box, with the w, h, and rgba blobs reads."""
    x0, y0 = round(box["x"] * scale), round(box["y"] * scale)
    w, h = min(round(box["w"] * scale), img.w - x0), min(round(box["h"] * scale), img.h - y0)
    rgba = b"".join(bytes(img.rgba[((y0 + y) * img.w + x0) * 4:((y0 + y) * img.w + x0 + w) * 4]) for y in range(h))
    return type("Crop", (), {"w": w, "h": h, "rgba": rgba})


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
                    self.assertEqual(Path(result["png"]).parent, folder.resolve() / ".dm", "screenshots are working files")
                    self.assertTrue((folder / ".dm" / "check.json").is_file())
                    self.assertEqual(sorted(p.name for p in folder.iterdir() if not p.name.startswith(".")),
                                     sorted(p.name for p in (PAGES / name).iterdir() if not p.name.startswith(".")), "check adds nothing beside the page")
                    if name != "bare-maplibre":
                        self.assertEqual(findings(result, "WARN"), EXPECTED_WARNS.get(name, []), name)

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

    def test_labels_warn_on_a_name_that_did_not_render_sits_under_a_head_or_strays(self):
        cases = [("a name under an arrowhead", "map.setLayoutProperty('movers-labels', 'text-radial-offset', undefined); "
                  "map.setLayoutProperty('movers-labels', 'text-anchor', 'center'); map.setLayoutProperty('movers-labels', 'text-offset', [0, 0])",
                  "arrowheads cover", "Tokyo under the head of"),
                 ("names too big to fit", "map.setLayoutProperty('movers-labels', 'text-size', 40)", "didn't render", "names of movers-labels"),
                 ("names pushed toward their neighbors", "map.setLayoutProperty('movers-labels', 'text-radial-offset', undefined); "
                  "map.setLayoutProperty('movers-labels', 'text-anchor', 'left'); map.setLayoutProperty('movers-labels', 'text-offset', [3, 0])",
                  "nearer another circle than their own", "Shanghai, nearer Tokyo"),
                 ("names pushed off the frame", "map.setLayoutProperty('movers-labels', 'text-radial-offset', undefined); "
                  "map.setLayoutProperty('movers-labels', 'text-anchor', 'left'); map.setLayoutProperty('movers-labels', 'text-offset', [12, 0])",
                  "run past the map's edge", "Los Angeles")]
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

    def test_notes_draw_on_the_map_wrapped_and_clear_of_the_names(self):
        long = "Bangladesh packs about 1,200 people into each square kilometer, more than any other large country"
        for name, at, text in (("maplibre-crs", [90.4, 23.7], long), ("maplibre-globe", "node:TYO", "Tokyo draws the most movers")):
            with self.subTest(name):
                folder = copy(name, self.tmp / name)
                spec(annotations=[{"text": text, "at": at}])(folder)
                code, result = self.render(folder)
                self.assertEqual(code, 0, findings(result, "FAIL"))
                (note,) = result["report"]["annotations"]
                self.assertEqual((note["drawn"], note["farSide"], note["covers"]), (True, False, []), note)
                box, frame = note["box"], result["report"]["mapBox"]
                self.assertTrue(frame["x"] <= box["x"] and box["x"] + box["w"] <= frame["x"] + frame["w"], (box, frame))
                self.assertEqual(note["node"], None if name == "maplibre-crs" else "Tokyo")
                if text == long:
                    self.assertGreaterEqual(box["h"], 2 * 11 * 1.25, "a long note wraps")
                    self.assertLessEqual(box["w"], 181)
                self.assertIn(("PASS", "annotations", 24), findings(result))

    def test_notes_keep_off_land_and_off_raised_arcs(self):
        hide_text = page("</head>", "<style>.dm-notes text { fill: none; stroke: none; }</style>\n</head>")

        def magenta(doc):
            for f in doc["features"]:
                f["properties"].update(dm_fill="#ff00ff", dm_opacity=1)
        for name, edits, notes, ink in (
                ("maplibre-crs", [hide_text], [{"text": "Mongolia: about 2 people per square kilometer", "at": [103, 47]}], None),
                ("deck-globe", [hide_text, data("movers", magenta)], [{"text": "Seoul and Tokyo trade the most movers", "at": "node:SEL"},
                                                                       {"text": "Los Angeles draws from all of Asia", "at": "node:LAX"},
                                                                       {"text": "Manila", "at": "node:MNL"}], "#ff00ff")):
            with self.subTest(name):
                folder = copy(name, self.tmp / name)
                spec(annotations=notes)(folder)
                for edit in edits:
                    edit(folder)
                result = self.render(folder)[1]
                img = png.read(Path(result["png"]).read_bytes())
                colors = [ink] if ink else json.loads((folder / "data" / "legend.json").read_text())["layers"]["density"]["colors"]
                for note in result["report"]["annotations"]:
                    b = note["box"]
                    counts = img.histogram((round(b["x"]), round(b["y"]), round(b["w"]), round(b["h"])))
                    under = sum(png.near(counts, c, 60 if ink else 6) for c in colors) / sum(counts.values())
                    self.assertLess(under, 0.05, f"{note['text']} sits {under:.0%} over {'an arc' if ink else 'land'}")

    def test_a_note_that_cannot_render_warns(self):
        for what, at in (("a place outside the view", [10, 50]), ("a node that doesn't exist", "node:NOPE")):
            with self.subTest(what):
                folder = copy("maplibre-mercator", self.tmp / what.replace(" ", "-"))
                spec(annotations=[{"text": "Somewhere", "at": at}])(folder)
                code, result = self.render(folder)
                warns = [f["message"] for f in result["findings"] if (f["status"], f["check"]) == ("WARN", "annotations")]
                self.assertEqual(code, 0, findings(result, "FAIL"))
                self.assertEqual(len(warns), 1, warns)
                self.assertIn('the note "Somewhere" didn\'t render', warns[0])

    def test_a_far_side_note_sits_at_the_rim_toward_its_place_and_turns_the_globe_there(self):
        lima = list(make.PACIFIC["LIM"][1:3])
        folder = copy("maplibre-globe", self.tmp / "far")
        spec(annotations=[{"text": "Lima", "at": "node:LIM"}])(folder)
        rep = self.render(folder)[1]["report"]
        (note,) = rep["annotations"]
        self.assertEqual((note["text"], note["drawn"], note["farSide"]), ("Lima (far side)", True, True))
        frame, box = rep["mapBox"], note["box"]
        cx, cy = frame["x"] + frame["w"] / 2, frame["y"] + frame["h"] / 2
        near = math.hypot(max(box["x"] - cx, 0, cx - box["x"] - box["w"]), max(box["y"] - cy, 0, cy - box["y"] - box["h"]))
        self.assertGreater(near, 0.6 * min(frame["w"], frame["h"]) / 2, "the note sits out by the rim")
        self.assertGreater(box["x"] + box["w"] / 2, cx, "Lima lies east of the opening center, so its note sits on the right")
        click = "document.querySelector('.dm-note-far').dispatchEvent(new MouseEvent('click', {bubbles: true}))"
        for what, code in (("eases there", f"{click}; await map.once('moveend')"),
                           ("jumps under reduced motion", f"window.matchMedia = () => ({{matches: true}}); {click}; "
                                                          "if (map.isMoving()) throw new Error('the globe animated under reduced motion')")):
            with self.subTest(what):
                folder = copy("maplibre-globe", self.tmp / what.replace(" ", "-"))
                spec(annotations=[{"text": "Lima", "at": "node:LIM"}])(folder)
                extend(code)(folder)
                result = self.render(folder)[1]
                self.assertIn(("PASS", "ready", 33), findings(result))
                rep = result["report"]
                self.assertLess(degrees(rep["center"], lima), 0.01)
                self.assertEqual(rep["annotations"][0]["farSide"], False)

    def test_a_flow_over_a_node_it_does_not_connect_warns_with_the_overlap(self):
        nodes = {}

        def through_tokyo(doc):
            for f in doc["features"]:
                p = f["properties"]
                if (p["dm_o"], p["dm_d"]) == ("SHA", "MNL"):
                    # The last segment stays, so the arrowhead still agrees with its line.
                    f["geometry"] = {"type": "LineString", "coordinates": [nodes["SHA"]["at"], nodes["TYO"]["at"], *f["geometry"]["coordinates"][-2:]]}
                    nodes["line"] = p

        folder = copy("maplibre-globe", self.tmp)
        for f in json.loads((folder / "data" / "movers-nodes.geojson").read_text())["features"]:
            nodes[f["properties"]["dm_key"]] = {"at": f["geometry"]["coordinates"], "r": f["properties"]["dm_r"]}
        data("movers", through_tokyo)(folder)
        code, result = self.render(folder)
        line = nodes["line"]
        # Through Tokyo's center, then moved dm_offset px to the right of travel as MapLibre draws it.
        px = round(nodes["TYO"]["r"] + line["dm_width"] / 2 - line["dm_offset"], 1)
        warns = [f["message"] for f in result["findings"] if (f["status"], f["check"], f["pitfall"]) == ("WARN", "flows-over-nodes", 16)]
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertEqual(len(warns), 1, warns)
        self.assertIn(f"Shanghai to Manila over Tokyo by {px:g} px", warns[0])

    def test_a_world_map_with_no_frame_crops_to_its_latitudes_on_the_bare_page(self):
        ocean, page_white = (0xed, 0xf1, 0xf4), (255, 255, 255)
        for frame in (None, "sphere"):
            with self.subTest(frame=frame):
                folder = copy("maplibre-crs", self.tmp / str(frame))
                # A figure's map row hugs the map, so the crop shows at its edges.
                spec(frame=frame, figure={"size": "640x700"}, companions=[])(folder)
                code, result = self.render(folder)
                self.assertEqual(code, 0, findings(result, "FAIL"))
                rep, img = result["report"], png.read(Path(result["png"]).read_bytes())
                box = rep["mapBox"]
                x0, y0, x1, y1 = (round(v) for v in (box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"]))
                inked = [y for y in range(y0, y1) if any(img.rgba[(y * img.w + x) * 4:(y * img.w + x) * 4 + 3] != bytes(page_white) for x in range(x0, x1, 2))]
                counts = img.histogram((x0, y0, x1 - x0, y1 - y0))
                if frame is None:
                    # The fit pads 14 px, so the land runs from about 14 px below the top to 14 px above the bottom.
                    self.assertLessEqual(inked[0] - y0, 17)
                    self.assertLessEqual(y1 - 1 - inked[-1], 17)
                    # A few edge pixels blend to the ocean's gray; a drawn ocean fills tens of thousands.
                    self.assertLess(png.near(counts, "#%02x%02x%02x" % ocean, 2), 50, "no ocean drawn")
                else:
                    self.assertGreater(png.near(counts, "#%02x%02x%02x" % ocean, 2), 10000, "the sphere's ocean is drawn")

    def test_a_world_map_shows_its_whole_edge_around_its_own_central_meridian(self):
        for frame, zoom_in, want in ((None, False, 0), ("sphere", False, 0), ("sphere", True, None)):
            with self.subTest(frame=frame, zoom_in=zoom_in):
                folder = copy("maplibre-crs", self.tmp / f"{frame}-{zoom_in}")
                spec(frame=frame)(folder)
                self.assertIn("+lon_0=11.6", (folder / "index.html").read_text())
                if zoom_in:
                    extend("map.setZoom(map.getZoom() + 0.1)")(folder)
                code, result = self.render(folder)
                if want == 0:
                    self.assertEqual((code, result["report"]["edgeCut"]), (0, 0), findings(result, "FAIL"))
                else:
                    self.assertGreater(result["report"]["edgeCut"], 1)
                    self.assertIn(("FAIL", "edge", 33), findings(result))

    def test_a_map_crowded_by_the_side_panel_or_a_companion_warns_and_names_what_crowds_it(self):
        wide_side = page("</head>", "<style>:root { --dm-side: 700px; }</style>\n</head>")
        for what, name, edits, says in (
                ("a side panel 700 px wide", "maplibre-flows", [wide_side], ("across", 'the companion "The largest routes"')),
                ("a bar chart under a world figure", "maplibre-crs", [spec(figure={"size": "640x780"})],
                 ("of the 780 px figure", 'the companion "The ten most crowded countries"'))):
            with self.subTest(what):
                folder = copy(name, self.tmp / what.replace(" ", "-"))
                for edit in edits:
                    edit(folder)
                result = self.render(folder)[1]
                warns = [f["message"] for f in result["findings"] if (f["status"], f["check"]) == ("WARN", "map-leads")]
                self.assertEqual(len(warns), 1, warns)
                self.assertTrue(all(s in warns[0] for s in says), warns[0])
        # The same figure with no companion, at the height its content fills, leads with its map.
        folder = copy("maplibre-crs", self.tmp / "tall")
        spec(figure={"size": "640x900"}, companions=[])(folder)
        size = re.search(r'figure.size to "(\d+x\d+)"', next(f["fix"] for f in self.render(folder)[1]["findings"] if f["check"] == "figure"))[1]
        folder = copy("maplibre-crs", self.tmp / "fits")
        spec(figure={"size": size}, companions=[])(folder)
        code, result = self.render(folder)
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertNotIn("map-leads", {f["check"] for f in result["findings"]}, (size, findings(result)))

    def test_a_figure_taller_than_its_content_warns_with_the_height_that_fits(self):
        folder = copy("maplibre-crs", self.tmp / "tall")
        spec(figure={"size": "640x900"}, companions=[])(folder)
        result = self.render(folder)[1]
        warn = next(f for f in result["findings"] if f["check"] == "figure")
        self.assertEqual(warn["status"], "WARN")
        size = re.search(r'figure.size to "(\d+x\d+)"', warn["fix"])[1]
        folder = copy("maplibre-crs", self.tmp / "fits")
        spec(figure={"size": size}, companions=[])(folder)
        code, result = self.render(folder)
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertNotIn("figure", {f["check"] for f in result["findings"]})
        self.assertLessEqual(result["report"]["figure"]["slack"], 2)

    def test_the_reveal_slider_draws_the_n_largest_flows_and_keeps_the_kept_line_true(self):
        folder = copy("maplibre-flows", self.tmp / "default")
        layer = json.loads((folder / "data" / "legend.json").read_text())["layers"]["trips"]
        lines = [f["properties"] for f in json.loads((folder / "data" / "trips.geojson").read_text())["features"]]
        values = sorted((p["dm_value"] for p in lines), reverse=True)
        whole = sum(values[:layer["reveal"]["default"]]) / layer["kept_share"]

        def kept(n):
            return f"The {n} largest of {layer['total']} flows, {round(100 * sum(values[:n]) / whole)}% of all trips"
        for n in (25, 60, 100):
            with self.subTest(n=n):
                folder = copy("maplibre-flows", self.tmp / str(n))
                if n != 25:
                    extend(f"const s = document.getElementById('dm-reveal-trips'); s.value = {n}; "
                           "s.dispatchEvent(new Event('input')); s.dispatchEvent(new Event('change'))")(folder)
                code, result = self.render(folder)
                self.assertEqual(code, 0, findings(result, "FAIL"))
                (reveal,) = result["report"]["reveal"]
                self.assertEqual((reveal["shown"], reveal["of"], reveal["drawn"], reveal["note"]), (n, layer["reveal"]["count"], n, kept(n)))
                # A station shows only while a drawn flow starts or ends there.
                ends = {k for p in lines if p["dm_rank"] <= n for k in (p["dm_o"], p["dm_d"])}
                self.assertEqual(result["report"]["labels"][0]["nodes"], len(ends))
                self.assertEqual(result["report"]["rendered"]["trips-nodes"], len(ends))
                self.assertTrue(reveal["label"])
                self.assertIn("reveal", result["report"]["dmControls"])
                self.assertNotIn("controls", {f["check"] for f in result["findings"] if f["status"] == "WARN"})

    def test_the_reveal_slider_filters_deck_arcs_too(self):
        def ranked(doc):
            for f in doc["features"]:
                f["properties"]["dm_rank"] = f["properties"]["dm_order"] + 1

        def reveal(doc):
            doc["layers"]["movers"]["reveal"] = {"default": 10, "count": 30}
        for n in (10, 30):
            with self.subTest(n=n):
                folder = copy("deck-globe", self.tmp / str(n))
                for stem in ("movers", "movers-arrows"):
                    data(stem, ranked, resync=False)(folder)
                data("legend", reveal)(folder)
                spec(controls=["reveal"])(folder)
                if n != 10:
                    extend(f"const s = document.getElementById('dm-reveal-movers'); s.value = {n}; s.dispatchEvent(new Event('input'))")(folder)
                rep = self.render(folder)[1]["report"]
                self.assertEqual((rep["reveal"][0]["shown"], rep["reveal"][0]["drawn"]), (n, n))

    def test_net_nodes_take_the_gain_and_loss_colors_with_a_key_for_each(self):
        folder = copy("maplibre-flows", self.tmp)
        colors = json.loads((folder / "data" / "legend.json").read_text())["layers"]["trips"]["nodes"]["colors"]
        code, result = self.render(folder)
        self.assertEqual(code, 0, findings(result, "FAIL"))
        signs = {e["color"]: e["expect"] for e in result["report"]["legendEntries"] if e["kind"] == "sign"}
        self.assertEqual(signs, {colors["gain"]: True, colors["loss"]: True})
        self.assertIn(("PASS", "legend-colors", 9), findings(result))

    def test_a_faint_flow_s_arrowhead_draws_at_full_strength(self):
        # The smallest flow the slider can reveal draws its line at the fade's floor, 0.45. With every layer hidden but
        # that flow's arrowhead, the head is the only thing in the flows' color on the map, so its color shows whether it
        # faded with its line.
        folder = copy("maplibre-flows", self.tmp)
        rank = json.loads((folder / "data" / "legend.json").read_text())["layers"]["trips"]["reveal"]["count"]
        line = next(f["properties"] for f in json.loads((folder / "data" / "trips.geojson").read_text())["features"] if f["properties"]["dm_rank"] == rank)
        self.assertEqual(line["dm_opacity"], 0.45)
        extend("for (const l of map.getStyle().layers) if (l.id !== 'trips-arrows') map.setLayoutProperty(l.id, 'visibility', 'none'); "
               f"map.setFilter('trips-arrows', ['==', ['get', 'dm_rank'], {rank}])")(folder)
        result = self.render(folder)[1]
        box, dpr = result["report"]["mapBox"], result["report"]["viewport"]["dpr"]
        counts = png.read(Path(result["png"]).read_bytes()).histogram(tuple(box[k] * dpr for k in ("x", "y", "w", "h")))
        self.assertEqual((result["report"]["rendered"]["trips"], result["report"]["rendered"]["trips-nodes"]), (0, 0))
        # How far each pixel in the flows' hue runs from the white page to the flow color, by its green channel. The
        # soft edge of a 6 px icon keeps even a full head's core a little short of 1, while a head faded with its line
        # stays under 0.45.
        green = png.hex_rgb(line["dm_fill"])[1]
        head = [(255 - g) / (255 - green) for r, g, b in map(png.key_rgb, counts) if r > g + 30 and r > b + 50]
        self.assertGreater(max(head, default=0), 0.9)

    def test_a_title_place_hidden_at_load_warns_until_a_note_marks_it(self):
        retitle = page('stay on its western side</h1>', 'stay on its western side, and few reach Lima</h1>')
        for notes, warned in (([], True), ([{"text": "Lima", "at": "node:LIM"}], False)):
            with self.subTest(notes=notes):
                folder = copy("maplibre-globe", self.tmp / str(len(notes)))
                retitle(folder)
                spec(annotations=notes)(folder)
                code, result = self.render(folder)
                warns = [f["message"] for f in result["findings"] if (f["status"], f["check"]) == ("WARN", "title-places")]
                self.assertEqual(code, 0, findings(result, "FAIL"))
                self.assertEqual(warns, ["the title names Lima, which is on the far side of the globe at load"] if warned else [])

    def test_highlighted_places_draw_outlined_on_the_map_and_bold_in_the_companions_that_name_them(self):
        def hosts(folder: Path):
            (folder / "data" / "hosts.json").write_text(json.dumps({"rows": [["Tokyo", 900], ["Seoul", 700], ["Lima", 50]]}))
        folder = copy("maplibre-globe", self.tmp / "on")
        hosts(folder)
        spec(highlight=["TYO", "NOPE"], companions=[{"type": "bars", "data": "hosts", "title": "Arrivals"}])(folder)
        cli("sync", folder)
        # Only the circles draw, filled with the page's white, so a dark ring is a highlight's outline.
        extend("const weights = [...document.querySelectorAll('aside svg text')].filter(e => ['Tokyo', 'Seoul'].includes(e.textContent)) "
               ".map(e => getComputedStyle(e).fontWeight).join(); "
               "if (weights !== '700,400') throw new Error(`the bars' names weigh ${weights}`); "
               "for (const l of map.getStyle().layers) if (l.id !== 'movers-nodes') map.setLayoutProperty(l.id, 'visibility', 'none'); "
               "map.setPaintProperty('movers-nodes', 'circle-color', '#ffffff')")(folder)
        result = self.render(folder, "--scale", "2")[1]
        self.assertIn(("PASS", "ready", 33), findings(result))
        self.assertEqual(result["report"]["highlight"], [{"key": "TYO", "name": "Tokyo", "companions": 1}, {"key": "NOPE", "name": None, "companions": 0}])
        warns = [f["message"] for f in result["findings"] if (f["status"], f["check"]) == ("WARN", "highlight")]
        self.assertEqual(warns, ["dm-spec.highlight names NOPE, which no node or area has"])
        nodes = json.loads((folder / "data" / "movers-nodes.geojson").read_text())["features"]
        tokyo = next(f["properties"]["dm_r"] for f in nodes if f["properties"]["dm_key"] == "TYO")
        rings = [(n, w, h) for n, w, h in blobs(crop(png.read(Path(result["png"]).read_bytes()), result["report"]["mapBox"], 2), (0x1f, 0x1f, 0x1f), 40)
                 if n > 20]
        self.assertEqual(len(rings), 1, rings)
        self.assertAlmostEqual(rings[0][1] / 2, 2 * (tokyo + 2), delta=4, msg=rings)
        # An area the title names gets a dark outline on a white casing, which shows on the darkest class too.
        for keys, dark in (([], False), (["IND"], True)):
            with self.subTest(keys=keys):
                folder = copy("maplibre-crs", self.tmp / f"area-{len(keys)}")
                spec(highlight=keys)(folder)
                result = self.render(folder, "--scale", "2")[1]
                box = result["report"]["mapBox"]
                counts = png.read(Path(result["png"]).read_bytes()).histogram(tuple(2 * box[k] for k in ("x", "y", "w", "h")))
                outline = png.near(counts, "#1f1f1f", 40)
                self.assertEqual(outline > 300, dark, outline)

    def test_focus_draws_one_places_flows_out_and_in_ranks_its_partners_and_rewrites_the_title(self):
        folder = copy("maplibre-flows", self.tmp / "data")
        lines = [f["properties"] for f in json.loads((folder / "data" / "trips.geojson").read_text())["features"]]
        names = {f["properties"]["dm_key"]: f["properties"]["dm_label"] for f in json.loads((folder / "data" / "trips-nodes.geojson").read_text())["features"]}
        key = "S01"
        # The fixture ranks by trips out, and the flows file holds every flow, so these are Union Station's true figures.
        out = {}
        for p in lines:
            if p["dm_o"] == key:
                out[p["dm_d"]] = out.get(p["dm_d"], 0) + p["dm_value"]
        top = max(out, key=lambda k: (out[k], -ord(names[k][0])))
        total = sum(out.values())
        title = f"Riders leaving {names[key]} most often ride to {names[top]}"
        subtitle = f"{out[top]:,.0f} of its {total:,.0f} trips out in October, {round(100 * out[top] / total)}%, and every route to and from it"
        click = ("const at = map.project(DataMap.data['trips-nodes'].features.find(f => f.properties.dm_key === 'S01').geometry.coordinates); "
                 "const r = map.getCanvas().getBoundingClientRect(), xy = {clientX: r.left + at.x, clientY: r.top + at.y, bubbles: true, button: 0}; "
                 "for (const kind of ['mousedown', 'mouseup', 'click']) map.getCanvas().dispatchEvent(new MouseEvent(kind, xy))")
        ways = (("the page's hook", "await dataMap.focus('S01')"),
                ("the picker", "const s = document.getElementById('dm-focus-pick'); s.value = 'S01'; s.dispatchEvent(new Event('change'))"),
                ("a click on its circle", click))
        overview = copy("maplibre-flows", self.tmp / "overview")
        before = self.render(overview)[1]["report"]
        for what, code in ways:
            with self.subTest(what):
                folder = copy("maplibre-flows", self.tmp / what.replace(" ", "-"))
                extend(code + "; await new Promise(r => setTimeout(r, 300)); map.triggerRepaint()")(folder)
                result = self.render(folder)[1]
                focus = result["report"]["focus"]
                self.assertEqual((focus["key"], focus["title"], focus["subtitle"]), (key, title, subtitle))
                self.assertEqual(focus["drawn"], sum(1 for p in lines if key in (p["dm_o"], p["dm_d"])))
                self.assertEqual(focus["partners"][0]["name"], names[top])
                self.assertEqual([r["out"] for r in focus["partners"]], sorted((r["out"] for r in focus["partners"]), reverse=True))
                counts = png.read(Path(result["png"]).read_bytes()).histogram(tuple(result["report"]["mapBox"][k] for k in ("x", "y", "w", "h")))
                self.assertGreater(png.near(counts, focus["colors"]["out"], 30), 40, "flows out in their color")
                self.assertGreater(png.near(counts, focus["colors"]["in"], 30), 40, "flows in in theirs")
                self.assertEqual(result["report"]["annotations"][0]["drawn"], False, "the overview's note steps aside")
        with self.subTest("deck.gl arcs"):
            folder = copy("deck-globe", self.tmp / "deck")
            spec(controls=["focus"], focus={"by": "in", "title": "Most movers to {name} come from {top}"})(folder)
            extend("await dataMap.focus('TYO'); await new Promise(r => setTimeout(r, 300)); map.triggerRepaint()")(folder)
            result = self.render(folder)[1]
            focus = result["report"]["focus"]
            movers = [f["properties"] for f in json.loads((folder / "data" / "movers.geojson").read_text())["features"]]
            into = {}
            for p in movers:
                if p["dm_d"] == "TYO":
                    into[p["dm_o"]] = into.get(p["dm_o"], 0) + p["dm_value"]
            nodes = {f["properties"]["dm_key"]: f["properties"]["dm_label"] for f in json.loads((folder / "data" / "movers-nodes.geojson").read_text())["features"]}
            self.assertEqual(focus["title"], f"Most movers to Tokyo come from {nodes[max(into, key=into.get)]}")
            self.assertEqual(focus["drawn"], sum(1 for p in movers if "TYO" in (p["dm_o"], p["dm_d"])))
            counts = png.read(Path(result["png"]).read_bytes()).histogram(tuple(result["report"]["mapBox"][k] for k in ("x", "y", "w", "h")))
            self.assertGreater(png.near(counts, focus["colors"]["in"], 30), 40, "arcs into Tokyo in the inbound color")
        with self.subTest("Escape"):
            folder = copy("maplibre-flows", self.tmp / "escape")
            extend("await dataMap.focus('S01'); dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'})); "
                   "await new Promise(r => setTimeout(r, 300)); map.triggerRepaint()")(folder)
            rep = self.render(folder)[1]["report"]
            self.assertEqual({k: rep["focus"][k] for k in ("key", "title", "subtitle", "drawn", "note")},
                             {k: before["focus"][k] for k in ("key", "title", "subtitle", "drawn", "note")})
            self.assertTrue(rep["annotations"][0]["drawn"])

    def test_the_legend_names_each_classing_method(self):
        folder = copy("maplibre-crs", self.tmp)
        data("legend", lambda doc: doc["layers"]["density"].update(method="geometric"))(folder)
        texts = [b["text"] for b in self.render(folder)[1]["report"]["textBoxes"]]
        self.assertIn("5 classes in a constant ratio", texts)

    def test_on_a_phone_a_vertical_swipe_scrolls_past_the_globe_and_a_sideways_one_turns_it(self):
        def swipe(x0, y0, x1, y1, steps=12):
            pts = [(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps) for i in range(steps + 1)]
            touch = lambda kind, at: ("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": at[0], "y": at[1]}] if at else []}, 0.02)
            return [touch("touchStart", pts[0]), *(touch("touchMove", at) for at in pts[1:]), ("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}, 1.0)]
        folder = copy("maplibre-globe", self.tmp)
        reports = {}
        for what, actions in (("still", []), ("up", swipe(195, 650, 195, 350)), ("sideways", swipe(300, 500, 100, 500))):
            run = chrome.capture(BROWSER, folder.resolve(), "index.html", self.tmp / f"{what}.png", 390, 844, 1, 60, [], phone=True, actions=actions)
            if "launch_error" in run:
                self.skipTest(run["launch_error"])
            self.assertNotIn("ready_error", run)
            reports[what] = run["report"]
        still, up, sideways = reports["still"], reports["up"], reports["sideways"]
        self.assertGreater(up["viewport"]["scrollY"], 150, "the page scrolled")
        self.assertLess(degrees(up["center"], still["center"]), 0.5, "the globe stayed put")
        self.assertEqual(sideways["viewport"]["scrollY"], 0)
        self.assertGreater(degrees(sideways["center"], still["center"]), 20, "the globe turned")

    def test_a_hint_under_an_interactive_map_says_what_the_reader_can_do(self):
        tap = ("const f = DataMap.data.capacity.features[0], at = map.project(f.geometry.coordinates), r = map.getCanvas().getBoundingClientRect(); "
               "const xy = {clientX: r.left + at.x, clientY: r.top + at.y, bubbles: true, button: 0}; "
               "for (const kind of ['mousedown', 'mouseup', 'click']) map.getCanvas().dispatchEvent(new MouseEvent(kind, xy)); "
               "if (document.querySelector('.dm-tip').style.display !== 'block') throw new Error('a tap showed no tooltip')")
        cases = (("a flows map with focus", "maplibre-flows", [], "Hover or tap for numbers; click or tap a place for its flows alone, Esc to go back; drag to pan; scroll or pinch to zoom."),
                 ("a globe", "maplibre-globe", [], "Hover or tap for numbers; drag to turn the globe; scroll or pinch to zoom."),
                 ("a globe that tilts", "maplibre-globe", [extend("map.setMaxPitch(60); map.dragRotate.enable()")],
                  "Hover or tap for numbers; drag to turn the globe; scroll or pinch to zoom; right-drag to tilt."),
                 ("a tap on a circle", "maplibre-mercator", [extend(tap)], "Hover or tap for numbers; drag to pan; scroll or pinch to zoom."),
                 ("words of the page's own", "maplibre-crs", [spec(hint="Hover a country for its rate.")], "Hover a country for its rate."),
                 ("no hint", "maplibre-crs", [spec(hint=False)], None),
                 ("a static figure", "maplibre-crs", [spec(figure={"size": "640x617"}, companions=[])], None))
        for what, name, edits, want in cases:
            with self.subTest(what):
                folder = copy(name, self.tmp / what.replace(" ", "-"))
                for edit in edits:
                    edit(folder)
                result = self.render(folder)[1]
                self.assertIn(("PASS", "ready", 33), findings(result))
                rep = result["report"]
                self.assertEqual(rep["hint"], want)
                if want:
                    box = next(b for b in rep["textBoxes"] if b["text"] == want[:60])
                    self.assertGreaterEqual(box["y"], rep["mapBox"]["y"] + rep["mapBox"]["h"], "the hint sits under the map")

    def test_a_tap_just_beside_a_hairline_flow_shows_its_numbers(self):
        # MapLibre hits a line only within half its width, so a pointer 4 px off a 1 px flow lands on nothing drawn.
        tap = ("const thin = map.queryRenderedFeatures({layers: ['trips']})[0]; "
               "const line = thin.geometry.type === 'LineString' ? thin.geometry.coordinates : thin.geometry.coordinates[0]; "
               "const mid = map.project(line[Math.floor(line.length / 2)]); "
               "const at = [...Array(24).keys()].map(i => [mid.x + 4 * Math.cos(i * Math.PI / 12), mid.y + 4 * Math.sin(i * Math.PI / 12)])"
               ".find(p => !map.queryRenderedFeatures(p, {layers: ['trips', 'trips-nodes']}).length); "
               "if (!at) throw new Error('no spot beside the flow is clear of drawn features'); "
               "const r = map.getCanvas().getBoundingClientRect(), xy = {clientX: r.left + at[0], clientY: r.top + at[1], bubbles: true, button: 0}; "
               "for (const kind of ['mousedown', 'mouseup', 'click']) map.getCanvas().dispatchEvent(new MouseEvent(kind, xy)); "
               "const tip = document.querySelector('.dm-tip'), tips = new Set(DataMap.data.trips.features.map(f => f.properties.dm_tip)); "
               "if (tip.style.display !== 'block' || !tips.has(tip.textContent)) throw new Error(`a tap beside a hairline flow showed ${tip.style.display === 'block' ? tip.textContent : 'nothing'}`)")

        def hairlines(fc):
            for f in fc["features"]:
                f["properties"].update(dm_width=1, dm_offset=1 if f["properties"].get("dm_offset") else 0)

        folder = copy("maplibre-flows", self.tmp)
        data("trips", hairlines, resync=False)(folder)
        extend(tap)(folder)
        cli("sync", folder)
        code, result = self.render(folder)
        self.assertIn(("PASS", "ready", 33), findings(result), [f["message"] for f in result["findings"] if f["check"] == "ready"])

    def test_a_synced_page_without_data_renders_and_passes(self):
        folder = copy("maplibre-globe", self.tmp)
        shutil.rmtree(folder / "data")
        code, result = self.render(folder)
        self.assertEqual(code, 0, findings(result, "FAIL"))
        self.assertEqual(findings(result, "WARN"), EXPECTED_WARNS["maplibre-globe"])

    def test_with_no_network_a_synced_page_renders_and_a_page_from_elsewhere_is_not_measured(self):
        for name in ("maplibre-crs", "deck-globe", "bare-maplibre"):
            with self.subTest(name):
                folder = copy(name, self.tmp / name)
                with patched_env(DM_CHROME_FLAGS="--proxy-server=127.0.0.1:9"):
                    code, result = cli("check", folder, "--json")
                self.assertEqual(code, 0, findings(result, "FAIL"))
                render = [f for f in result["findings"] if f["check"] == "render"]
                if name == "bare-maplibre":
                    self.assertEqual([(f["status"], f["pitfall"]) for f in render], [("WARN", 33)])
                    self.assertIn("no network", render[0]["message"])
                else:
                    self.assertEqual(render, [])
                    self.assertIn(("PASS", "ready", 33), findings(result))
                    self.assertIn(("PASS", "offline", 33), findings(result))

    def test_opened_from_disk_with_no_network_a_page_that_loads_from_jsdelivr_fails(self):
        folder = copy("maplibre-globe", self.tmp)
        from_jsdelivr(folder)
        code, result = self.render(folder)
        offline = next(f for f in result["findings"] if f["check"] == "offline" and f["status"] != "WARN")
        self.assertEqual((code, offline["status"]), (1, "FAIL"))
        self.assertIn("cdn.jsdelivr.net/npm/maplibre-gl@6.18.0/dist/maplibre-gl.mjs", offline["message"])
        self.assertTrue((folder / ".dm" / "index.1200x800.offline.png").is_file())

    def test_a_pmtiles_basemap_that_cannot_load_from_disk_warns_and_the_map_still_draws(self):
        folder = copy("maplibre-mercator", self.tmp)
        spec(tiles=[{"source": "basemap", "grid": "web-mercator", "url": "data/basemap.pmtiles", "flavor": "white"}])(folder)
        self.assertEqual(cli("sync", folder)[0], 0)
        self.assertTrue((folder / "vendor" / "pmtiles@4.5.0" / "pmtiles.js").is_file())
        self.assertTrue((folder / "vendor" / "protomaps-basemaps@5.7.2" / "basemaps.js").is_file())
        code, result = self.render(folder)
        offline = next(f for f in result["findings"] if f["check"] == "offline")
        self.assertEqual(offline["status"], "WARN", offline)
        self.assertIn("can't load from a file", offline["message"])

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
