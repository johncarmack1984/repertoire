"""check: lint a map page against its dm-spec, render it in headless Chrome, and judge the render.

Every finding cites the pitfall it guards against. Without Chrome, or without a network to load the
pinned libraries from, only the static pass runs and the render is reported as not measured.
"""
from __future__ import annotations

import json
import re
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import FAIL, PASS, WARN, Finding, report
from . import chrome as cdp
from . import png
from .page import DATA_FILE, DATA_REGION, LIB_REGION, SPEC, drift

PINS = {"maplibre-gl": "6.18.0", "proj4": "2.22.0", "pmtiles": "4.5.0", "deck.gl": "9.4.1", "@protomaps/basemaps": "5.7.2"}
AREAL = {"choropleth", "dots-and-density", "multivariate"}
LARGE = {"world", "hemisphere", "continent"}
LARGE_SPAN = (60, 40)
BASE_STEMS = {"frame", "sphere", "graticule", "land", "basemap"}
CONTROL_CLASSES = {"zoom-in": "navigation", "zoom-out": "navigation", "compass": "navigation", "scale": "scale",
                   "fullscreen": "fullscreen", "geolocate": "geolocate", "terrain": "terrain", "globe": "globe", "logo": "logo"}
CONTROL_CTORS = {"NavigationControl": "navigation", "ScaleControl": "scale", "FullscreenControl": "fullscreen",
                 "GeolocateControl": "geolocate", "TerrainControl": "terrain", "GlobeControl": "globe", "LogoControl": "logo"}
MOTION = re.compile(r"\b(setInterval|requestAnimationFrame)\s*\(|\bautoplay\b|\.play\s*\(\s*\)|\bloop\s*:\s*true")
PT = 4 / 3


@dataclass
class Page:
    """One map project as check sees it: the page source, its spec, and the data beside it."""
    folder: Path
    text: str
    spec: dict | None = None
    spec_error: str | None = None
    legend: dict | None = None
    authored: str = ""
    inlined: dict = field(default_factory=dict)
    blocks: dict = field(default_factory=dict)
    standalone: bool = False

    @property
    def is_map(self) -> bool:
        return bool(self.spec and self.spec.get("projection"))

    @property
    def projection(self) -> dict:
        return (self.spec or {}).get("projection") or {}

    @classmethod
    def read(cls, folder: Path) -> "Page":
        text = (folder / "index.html").read_text(encoding="utf-8")
        page = cls(folder, text)
        if m := SPEC.search(text):
            try:
                page.spec = json.loads(m[2])
            except json.JSONDecodeError as err:
                page.spec_error = str(err)
        if region := DATA_REGION.search(text):
            found = list(DATA_FILE.finditer(region[1]))
            page.inlined = {m[3]: m[1] for m in found}
            page.blocks = {m[3]: m[4] for m in found}
        # A page synced and moved away from its data/ folder still holds every file it draws.
        page.standalone = not (folder / "data").is_dir()
        legend = folder / "data" / "legend.json"
        source = legend.read_text(encoding="utf-8") if legend.is_file() else page.blocks.get("legend") if page.standalone else None
        if source is not None:
            try:
                page.legend = json.loads(source)
            except json.JSONDecodeError as err:
                page.spec_error = page.spec_error or f"legend.json is not JSON: {err}"
        page.authored = re.sub(r"<!--.*?-->", "", DATA_REGION.sub("", LIB_REGION.sub("", text)), flags=re.S)
        return page


def layer_stems(name: str, layer: dict) -> set[str]:
    files = layer.get("files") or {}
    stems = {name}
    if layer.get("kind") == "flows":
        stems |= {f"{name}-nodes", f"{name}-arrows", f"{name}-arcs"}
    return stems | {re.sub(r"\.(geo)?json$", "", str(f)) for f in files.values()}


def claimed_stems(page: Page) -> dict[str, str]:
    """Each data stem a page may draw, mapped to what explains it: a legend layer, the base, or a companion."""
    out = {s: "base" for s in BASE_STEMS} | {"legend": "legend"}
    out |= {s: "base" for s in page.inlined if s.startswith("base-")}
    for name, layer in ((page.legend or {}).get("layers") or {}).items():
        for s in layer_stems(name, layer):
            out[s] = name
    for c in (page.spec or {}).get("companions") or []:
        if c.get("data"):
            out[re.sub(r"^data/|\.(geo)?json$", "", c["data"])] = "companion"
    return out


def decided(spec: dict, pitfall: int, words: str) -> bool:
    for d in spec.get("decisions") or []:
        if not isinstance(d, dict):
            continue
        about = d.get("pitfall") == pitfall or re.search(rf"\bP{pitfall}\b|{words}", str(d.get("rule", "")), re.I)
        if about and len(str(d.get("why", "")).split()) >= 3:
            return True
    return False



def rule_pins(page: Page) -> list:
    found = re.findall(r"cdn\.jsdelivr\.net/npm/((?:@[\w.-]+/)?[\w.-]+)@([^/'\"\s?#]+)", page.authored)
    out = [FAIL("pins", f"{lib}@{ver} is loaded, but the pin is {PINS[lib]}", f"load {lib}@{PINS[lib]}, or update the pin in check.py and the stack recipe together")
           for lib, ver in sorted(set(found)) if lib in PINS and ver != PINS[lib]]
    elsewhere = sorted({h for h in re.findall(r"https?://(unpkg\.com|esm\.sh|cdnjs\.cloudflare\.com|cdn\.skypack\.dev|api\.mapbox\.com)/", page.authored)})
    if elsewhere:
        out.append(WARN("pins", f"libraries load from {', '.join(elsewhere)}, where check can't hold them to the pins",
                        "load the pinned libraries from jsDelivr's /npm/<name>@<version> URLs"))
    if not out:
        pinned = sorted({f"{lib}@{ver}" for lib, ver in found if lib in PINS})
        out.append(PASS("pins", f"{', '.join(pinned) or 'no pinned library'} loaded at the pinned versions"))
    return out


def rule_library(page: Page) -> list:
    said = [s for s in drift(page.text, page.folder)]
    lib = [s for s in said if "library" in s]
    data = [s for s in said if "library" not in s]
    out = []
    if not LIB_REGION.search(page.text):
        out.append(FAIL("library", "the page has no data-map:lib regions", "start from datamap.py new"))
    elif any("by hand" in s or "empty" in s for s in lib):
        out.append(FAIL("library", "; ".join(lib), "change assets/templates/lib, not the page, and run datamap.py sync"))
    elif lib:
        out.append(WARN("library", "; ".join(lib), "run datamap.py sync"))
    if data:
        out.append(FAIL("sync", "; ".join(data), f"run datamap.py sync {page.folder}", 9))
    if page.standalone:
        bad = []
        for stem, body in page.blocks.items():
            try:
                json.loads(body)
            except json.JSONDecodeError:
                bad.append(stem)
        if bad:
            out.append(FAIL("sync", f"inlined data that is not JSON: {', '.join(bad)}", "restore data/ and run datamap.py sync", 9))
        elif not out:
            out.append(PASS("sync", f"library current; with no data/ folder, the page's {len(page.inlined)} inlined data files are its data"))
    if not out:
        out.append(PASS("sync", f"library current, {len(page.inlined)} data files inlined and unchanged"))
    return out


def is_box(extent) -> bool:
    return isinstance(extent, list) and len(extent) == 4 and all(isinstance(v, (int, float)) for v in extent)


def large(extent) -> bool:
    """A named large extent, or a [W, S, E, N] box spanning 60 degrees of longitude or 40 of latitude."""
    if is_box(extent):
        w, s, e, n = extent
        return (e - w if e >= w else e - w + 360) >= LARGE_SPAN[0] or n - s >= LARGE_SPAN[1]
    return isinstance(extent, str) and extent in LARGE


def rule_projection(page: Page) -> list:
    spec, proj = page.spec, page.projection
    kind, idioms, extent = proj.get("type"), set(spec.get("idiom") or []), spec.get("extent")
    out = []
    if kind not in ("crs", "globe", "mercator"):
        return [FAIL("projection", f"dm-spec projection.type is {kind!r}", "use crs, globe, or mercator")]
    if isinstance(extent, list) and not is_box(extent):
        out.append(FAIL("extent", f"dm-spec extent {extent} is not [W, S, E, N]", "write four numbers in degrees, or a name such as region"))
    if kind == "crs" and not (proj.get("name", "").startswith("custom:") and proj.get("definition")):
        out.append(FAIL("projection", "a crs projection needs a custom:<name> and a proj4 definition", "copy them from datamap.py crs"))
    if not idioms:
        out.append(WARN("idiom", "dm-spec names no idiom, so the projection can't be judged against it", "name the idiom from the chooser", 10))
    areal = sorted(idioms & AREAL)
    if areal and large(extent) and (kind != "crs" or proj.get("property") != "equal-area"):
        what = {"mercator": "Web Mercator", "globe": "the globe"}.get(kind, f"{proj.get('name')}, which is not equal-area")
        out.append(FAIL("projection", f"{'/'.join(areal)} at {extent} extent drawn in {what}; areas compare falsely",
                        "use the equal-area crs preset (datamap.py new maplibre OUT --preset equal-earth) or datamap.py crs", 10))
    elif not out or all(f.status == "PASS" for f in out):
        out.append(PASS("projection", f"{proj.get('name') or kind} for {'/'.join(sorted(idioms)) or 'the map'} at {extent or 'data'} extent", 10))
    return out


def rule_tiles(page: Page) -> list:
    proj = page.projection
    if proj.get("type") != "crs":
        return []
    tiles = page.spec.get("tiles") or []
    wrong = [t for t in tiles if t.get("grid") != proj.get("name")]
    if wrong:
        return [FAIL("tiles", f"tile source {', '.join(str(t.get('source')) for t in wrong)} is cut in {', '.join(str(t.get('grid')) for t in wrong)}, not {proj.get('name')}",
                     "draw GeoJSON under a CRS, or tiles cut in its grid (martin tile_grids)", 11)]
    if not tiles and re.search(r"pmtiles://|type\s*:\s*['\"](vector|raster)['\"]", page.authored):
        return [FAIL("tiles", "the page adds tile sources that dm-spec.tiles doesn't list, under a CRS", "list each with its grid, or draw GeoJSON", 11)]
    return [PASS("tiles", "no Web Mercator tiles under the CRS", 11)]


def rule_controls(page: Page) -> list:
    declared = set(page.spec.get("controls") or [])
    used = {CONTROL_CTORS[c] for c in re.findall(r"new\s+(?:[\w$]+\.)*(\w+Control)\s*\(", page.authored) if c in CONTROL_CTORS}
    extra = sorted(used - declared)
    if extra:
        return [WARN("controls", f"the page adds {', '.join(extra)} controls that dm-spec.controls doesn't list", "remove them, or list each with the question it answers", 23)]
    return [PASS("controls", f"controls: {', '.join(sorted(used)) or 'none'} beyond compact attribution", 23)]


def rule_fonts(page: Page) -> list:
    families = set()
    for decl in re.findall(r"font(?:-family)?\s*:\s*([^;}\n]+)", page.authored):
        if "var(" in decl:
            continue
        stack = re.sub(r"^(?:(?:italic|bold|normal|\d{3}|[\d.]+(?:px|pt|em|rem|%)(?:/[\d.]+\w*)?)\s+)+", "", decl.strip())
        first = stack.split(",")[0].strip().strip("'\"")
        if first and not re.fullmatch(r"inherit|initial|unset|[\d.]+\w*", first):
            families.add(first)
    families |= {"system-ui"} if "var(--dm-font)" in page.text or LIB_REGION.search(page.text) else set()
    if len(families) > 2:
        return [WARN("fonts", f"the page's CSS names {len(families)} font families: {', '.join(sorted(families))}", "use at most two; the template's one system stack is enough", 23)]
    return []


def rule_pitch(page: Page) -> list:
    spec = page.spec
    pitch = spec.get("pitch") or 0
    m = re.findall(r"\bpitch\s*:\s*([\d.]+)", page.authored)
    pitch = max([pitch, *map(float, m)])
    apex = (spec.get("arcs") or {}).get("apex") or 0
    out = []
    if pitch > 0 and not decided(spec, 22, "pitch|3-?d|tilt"):
        out.append(FAIL("pitch", f"the map is tilted to pitch {pitch:g} with no recorded reason", "set pitch 0, or record the decision in dm-spec.decisions with pitfall 22 and a why", 22))
    if apex > 0 and not decided(spec, 22, "raised|arc|3-?d"):
        out.append(FAIL("raised-arcs", f"arcs rise to {apex:g} of the Earth's radius with no recorded reason", "set arcs.apex to 0 for flat great circles, or fill in the why of the pitfall 22 decision", 22))
    return out or [PASS("flat", "pitch 0" + (f"; raised arcs recorded: {apex:g} of the radius at the longest flow" if apex else ""), 22)]


def rule_motion(page: Page) -> list:
    found = sorted({m.group(0).strip("(. ") for m in MOTION.finditer(page.authored)})
    anim = page.spec.get("animation")
    if not found:
        return [PASS("motion", "nothing moves on its own", 26)] if not anim else []
    if not anim:
        return [FAIL("motion", f"the page animates ({', '.join(found)}) but dm-spec.animation is null", "draw small multiples, or add user-started motion with pause and reduced-motion and declare it", 26)]
    missing = [k for k, ok in (("trigger user", anim.get("trigger") == "user"), ("a pause or stop control", bool({"pause", "stop"} & set(anim.get("controls") or []))),
                                ("reduced_motion", anim.get("reduced_motion") is True)) if not ok]
    if missing:
        return [FAIL("motion", f"dm-spec.animation lacks {', '.join(missing)}", "start motion only on the reader's action, give it pause, and honor prefers-reduced-motion", 26)]
    return [PASS("motion", "motion starts on the reader's action, pauses, and honors reduced motion", 26)]


def rule_zoom(page: Page) -> list:
    z = page.spec.get("zoom") or {}
    if z.get("min") is None or z.get("max") is None:
        return [WARN("zoom", "dm-spec.zoom has no min or max, so the reader can zoom past what the data can say", 'set "zoom": {"min": "fit", "max": "fit+3"}', 25)]
    return [PASS("zoom", f"zoom held to {z['min']} through {z['max']}", 25)]


def rule_legend(page: Page) -> list:
    if page.legend is None:
        return [FAIL("legend", "data/legend.json is missing, so nothing explains the map's symbols", "write the layers with the levers (--out-dir OUT/data)", 9)]
    layers = page.legend.get("layers") or {}
    out = []
    for name, layer in layers.items():
        main = re.sub(r"\.(geo)?json$", "", str((layer.get("files") or {}).get("lines", name)))
        if main not in page.inlined:
            out.append(FAIL("legend", f"legend layer {name!r} has no data/{main}.geojson inlined", f"write it with --layer {name}, then sync", 9))
    claimed = claimed_stems(page)
    for stem in sorted(set(page.inlined) - set(claimed)):
        out.append(FAIL("legend", f"data/{stem} is inlined but no legend layer, base layer, or companion explains it", "give it a legend entry through its lever, or remove it", 9))
    return out or [PASS("legend", f"{len(layers)} legend layers: {', '.join(layers) or 'none'}", 9)]


def rule_text(page: Page) -> list:
    out = []
    text = lambda key: (m[1].strip() if (m := re.search(rf'id="{key}"[^>]*>(.*?)</', page.text, re.S)) else None)
    title, subtitle, source = text("dm-title"), text("dm-subtitle"), text("dm-source")
    for key, value, what in (("title", title, "a title that states the point"), ("subtitle", subtitle, "a subtitle saying what, where, and when"),
                             ("source", source, "a source line with the date")):
        if not value or "[" in value:
            out.append(FAIL(key, f"the {key} is {'missing' if not value else 'still the placeholder'}", f"write {what}", 24))
    if title and re.search(r"\bmap\b", title, re.I):
        out.append(WARN("title", f'the title says "map": "{title}"', "state the point instead; the reader can see it is a map", 24))
    if re.search(r">\s*(Legend|Key)\s*<", page.authored):
        out.append(WARN("legend-label", 'a heading reads "Legend" or "Key"', "title the legend with what it measures and its unit", 23))
    return out or [PASS("text", f'title "{title}"', 24)]


def rule_companions(page: Page) -> list:
    kinds = {"bars", "table", "matrix", "series"}
    bad = [c.get("type") for c in page.spec.get("companions") or [] if c.get("type") not in kinds]
    if bad:
        return [FAIL("companions", f"companion types {', '.join(map(str, bad))} aren't drawn by the page", f"use {', '.join(sorted(kinds))}")]
    return []


MAP_RULES = [rule_projection, rule_tiles, rule_controls, rule_pitch, rule_zoom, rule_legend]
PAGE_RULES = [rule_pins, rule_library, rule_fonts, rule_motion, rule_text, rule_companions]


def static_pass(page: Page) -> list:
    if page.spec_error:
        return [FAIL("spec", f"dm-spec or legend.json does not parse: {page.spec_error}", "fix the JSON")]
    if page.spec is None:
        return [WARN("spec", "no dm-spec block; judged the render only", "start from datamap.py new to get the full check")]
    rules = PAGE_RULES + (MAP_RULES if page.is_map else [])
    out = [f for rule in rules for f in rule(page)]
    if not page.is_map:
        out.insert(0, PASS("chart", f"no map: {'/'.join(page.spec.get('idiom') or [])} drawn as {', '.join(c.get('type', '?') for c in page.spec.get('companions') or []) or 'nothing yet'}", 2))
    return out



def judge_run(run: dict, page: Page | None, w: int, h: int, scale: float) -> list:
    out = []
    probs = run.get("problems", [])
    offline = [p for p in probs if p.get("offline")]
    if offline:
        return [WARN("render", f"render not measured: no network ({offline[0]['message']})", "rerun check on a machine that reaches jsDelivr", 33)]
    if "launch_error" in run:
        return [WARN("render", f"render not measured: Chrome did not start ({run['launch_error']})", "rerun check where headless Chrome can run, or set DM_BROWSER", 33)]
    if "error" in run:
        out.append(FAIL("render", run["error"], "open the page in a browser and read its console", 33))
    if "ready_error" in run:
        out.append(FAIL("ready", f"dataMap.ready rejected: {run['ready_error']}", "read the console errors below; the map never finished drawing", 33))
    elif "ready" in run["seconds"]:
        how = "dataMap.ready resolved" if run.get("hook") else "no readiness hook; waited for the network to go quiet, then 3 s"
        out.append(PASS("ready", f"{how} {run['seconds']['ready']:.1f} s after load", 33))
    for p in probs:
        status = WARN if p["level"] == "warning" else FAIL
        out.append(status(p["kind"], p["message"], "fix what the page logs; a map with errors may be missing layers", 33))
    if probe := run.get("probe"):
        laid = (probe["w"], probe["h"], probe["dpr"])
        if laid != (w, h, scale):
            out.append(FAIL("viewport", f"laid out at {laid[0]}x{laid[1]} @{laid[2]}x, asked {w}x{h} @{scale}x", "set DM_BROWSER to a Chrome that honors device metrics"))
        if not probe["renderer"] and (page is None or page.is_map):
            out.append(WARN("webgl2", "no WebGL2 context, so the map may not draw", "rerun with --gl swiftshader"))
    if page and page.spec and run.get("hook"):
        if "report_error" in run:
            out.append(FAIL("report", f"dataMap.report() threw: {run['report_error']}", "restore the library region with datamap.py sync"))
        elif not run.get("report"):
            out.append(FAIL("report", "dataMap.report() returned nothing", "restore the library region with datamap.py sync"))
        else:
            out += judge_report(run["report"], page)
    return out


def judge_report(rep: dict, page: Page) -> list:
    out = []
    spec = page.spec
    if page.is_map:
        proj = page.projection
        want = proj.get("name") if proj.get("type") == "crs" else proj.get("type")
        if rep.get("projection") != want:
            out.append(FAIL("projection", f"the map draws {rep.get('projection')}, dm-spec says {want}", "make the style's projection match dm-spec", 10))
        shown = {CONTROL_CLASSES[c[len("maplibregl-ctrl-"):]] for c in rep.get("controls", []) if c[len("maplibregl-ctrl-"):] in CONTROL_CLASSES}
        if extra := sorted(shown - set(spec.get("controls") or [])):
            out.append(WARN("controls", f"the render shows {', '.join(extra)} controls that dm-spec doesn't list", "remove them, or list each with the question it answers", 23))
        if (rep.get("pitch") or 0) > 0 and not decided(spec, 22, "pitch|3-?d|tilt"):
            out.append(FAIL("pitch", f"the map renders at pitch {rep['pitch']:g} with no recorded reason", "set pitch 0", 22))
        if rep.get("moving"):
            out.append(FAIL("motion", "the map was still moving when it said it was ready", "drop the animation, or start it only on the reader's action", 26))
        lo, hi = rep.get("minZoom"), rep.get("maxZoom")
        if lo is None or hi is None or hi >= 22 or (lo <= 0 and (rep.get("zoom") or 0) > 1):
            out.append(WARN("zoom", f"zoom runs {lo} to {hi}, which the data can't support", 'set "zoom": {"min": "fit", "max": "fit+3"}', 25))
        else:
            out.append(PASS("zoom", f"zoom {lo:.2f} to {hi:.2f}; fitted at {rep.get('zoom', 0):.2f}", 25))
        out += judge_layers(rep, page)
        out += judge_labels(rep)
    fonts = rep.get("fonts") or []
    if len(fonts) > 2:
        out.append(WARN("fonts", f"{len(fonts)} font families in use: {', '.join(fonts)}", "use at most two families", 23))
    sizes = sorted(set(rep.get("fontSizes") or []))
    close = [(a, b) for a, b in zip(sizes, sizes[1:]) if b - a < 2 * PT - 0.01]
    if close:
        out.append(WARN("type-scale", f"type sizes {', '.join(f'{a:g} and {b:g} px' for a, b in close)} differ by less than 2 pt, too little to read as levels",
                        "make each level at least 2 pt (2.7 px) from the next, or the same size", 23))
    if not close and len(fonts) <= 2:
        out.append(PASS("type", f"{', '.join(fonts)}; sizes {', '.join(f'{s:g}' for s in sizes)} px", 23))
    if clipped := rep.get("clipped"):
        out.append(FAIL("clipped", f"{len(clipped)} lines of the side panel are cut off at {(rep.get('viewport') or {}).get('w')}x{(rep.get('viewport') or {}).get('h')}: {'; '.join(clipped[:3])}",
                        "cut the companions to what fits beside the map at this size, or move one below the map", 24))
    vw, vh = (rep.get("viewport") or {}).get("w"), (rep.get("viewport") or {}).get("h")
    if vw and (off := [b["text"] for b in rep.get("textBoxes", []) if b["x"] < -1 or b["y"] < -1 or b["x"] + b["w"] > vw + 1 or b["y"] + b["h"] > vh + 1]):
        if (page.spec or {}).get("figure"):
            out.append(FAIL("offscreen", f"text runs off the {vw}x{vh} figure: {'; '.join(off[:3])}",
                            "a static figure has one size: cut a companion or a note until everything fits, keeping the map at least half the height", 24))
        else:
            out.append(WARN("offscreen", f"text runs off the page: {'; '.join(off[:3])}", "shorten it, or let it wrap", 24))
    return out


def judge_layers(rep: dict, page: Page) -> list:
    out = []
    claimed = claimed_stems(page)
    legend_layers = ((page.legend or {}).get("layers") or {})
    drawn = {}
    for layer in rep.get("layers", []):
        src = layer.get("source")
        if src is None:
            continue
        owner = claimed.get(src) or ("base" if src.startswith("base-") else None)
        if owner is None:
            out.append(FAIL("layers", f"layer {layer['id']} draws source {src}, which no legend entry explains", "give it a legend entry through its lever, or remove the layer", 9))
        elif owner in legend_layers:
            drawn.setdefault(owner, []).append(layer["id"])
    for name in legend_layers:
        if name not in drawn:
            out.append(FAIL("layers", f"legend layer {name!r} has no layer on the map", "write its data and run datamap.py sync", 33))
    for a in rep.get("arrows") or []:
        if a.get("maxOff") is None:
            continue
        if a["maxOff"] > 15:
            out.append(FAIL("arrows", f"an arrowhead of {a['layer']!r} turns {a['maxOff']:g} degrees from its line ({a['worst']})",
                            "draw arrows with the template's arrow layer, which turns each head to its line on screen", 17))
        else:
            out.append(PASS("arrows", f"{a['checked']} of {a['of']} arrowheads of {a['layer']!r} in view, each within {a['maxOff']:g} degrees of its line's last segment", 17))
    for name, layer in legend_layers.items():
        if layer.get("kind") == "classes":
            shown = [e for e in rep.get("legendEntries", []) if e["layer"] == name and e["kind"] == "class"]
            if len(shown) != len(layer.get("colors") or []):
                out.append(FAIL("legend", f"the legend shows {len(shown)} classes of {name!r}, legend.json has {len(layer.get('colors') or [])}", "redraw the legend from legend.json", 9))
    return out or [PASS("layers", f"{', '.join(f'{k}: {len(v)}' for k, v in drawn.items())} map layers, each explained by the legend", 9)]


def judge_labels(rep: dict) -> list:
    out = []
    for lab in rep.get("labels") or []:
        layer, hidden, covered = lab["layer"], lab.get("hidden") or [], lab.get("covered") or []
        if hidden:
            out.append(WARN("labels", f"{len(hidden)} of {lab['nodes']} names of {layer} didn't render: {', '.join(hidden)}",
                            "MapLibre hid them in every corner the page tried; draw fewer flows or points, give the map more room, or shorten the names"))
        if covered:
            out.append(WARN("labels", f"arrowheads cover {len(covered)} names of {layer}: " + "; ".join(f"{c['name']} under the head of {c['arrow']}" for c in covered),
                            "let the library place the names (drop any text-anchor or text-offset the page sets), or draw fewer flows"))
        if not hidden and not covered and lab["nodes"]:
            out.append(PASS("labels", f"all {lab['nodes']} names of {layer} rendered, and no arrowhead covers one"))
    return out


def judge_png(path: Path, rep: dict | None, run: dict | None, scale: float, legend: dict | None = None,
              data_dir: Path | None = None, background: str = "#ffffff") -> list:
    try:
        img = png.read(path.read_bytes(), background)
    except (OSError, ValueError) as err:
        return [FAIL("png", f"{path} can't be read: {err}", "rerun the render")]
    out = []
    if run and (img.w, img.h) != (round(run["viewport"][0] * scale), round(run["viewport"][1] * scale)):
        out.append(FAIL("png", f"the PNG is {img.w}x{img.h}, expected {round(run['viewport'][0] * scale)}x{round(run['viewport'][1] * scale)}", "rerun the render"))
    box = (rep or {}).get("mapBox") or (rep or {}).get("chartBox")
    if box:
        rect = (box["x"] * scale, box["y"] * scale, box["w"] * scale, box["h"] * scale)
    elif run and run.get("probe"):
        a = run["probe"]["area"]
        rect = (a[0] * scale, a[1] * scale, a[2] * scale, a[3] * scale)
    else:
        rect = None
    counts = img.histogram(rect)
    stats = png.summary(counts)
    shares = [s for _, s in stats["top"]]
    where = "map" if (rep or {}).get("mapBox") or not rep else "chart area"
    text = f"{stats['colors']} colors in the {where}; " + ", ".join(f"{c} {v:.1%}" for c, v in stats["top"])
    if not shares or shares[0] >= 0.99:
        out.append(FAIL("blank", f"the {where} is one color: {text}", "the frame was captured before anything drew; read the console errors", 33))
        return out
    entries = expected_colors(rep, legend, data_dir)
    if not entries:
        out.append(PASS("blank", text, 33) if sum(shares[:2]) < 0.995 else WARN("blank", f"the {where} is nearly two flat colors: {text}", "check that every layer drew", 33))
        return out
    need = max(4, round(4 * scale * scale))
    base = [c for c in (rep or {}).get("baseColors", []) if c]
    by_layer: dict = {}
    for color, (layer, label) in entries.items():
        n = png.near(counts, color, 4)
        by_layer.setdefault(layer, []).append((color, label, n))
        clash = [b for b in base if max(abs(x - y) for x, y in zip(png.hex_rgb(color), png.hex_rgb(b))) <= 6]
        if clash:
            out.append(WARN("contrast", f"legend color {color} ({label}) can't be told from the base color {clash[0]}", "pick a no-data or symbol color apart from the ocean, land, and page", 9))
    # With the report's count of rendered features, a layer that drew in the wrong colors is told apart from one
    # that never drew.
    rendered = (rep or {}).get("rendered") or {}
    missing_layers = [layer for layer, found in by_layer.items() if all(n < need for _, _, n in found) and not rendered.get(layer)]
    for layer in missing_layers:
        out.append(FAIL("drawn", f"none of layer {layer!r}'s legend colors ({', '.join(c for c, _, _ in by_layer[layer])}) is in the {where}", "the layer did not draw; check its data and the console", 33))
    for layer, found in by_layer.items():
        if layer in missing_layers:
            continue
        for color, label, n in found:
            if n < need:
                out.append(FAIL("legend-colors", f"legend color {color} ({label}, layer {layer}) is not in the {where}", "the legend and the map disagree; redraw both from legend.json", 9))
    if not any(f.status == "FAIL" for f in out):
        out.append(PASS("legend-colors", f"all {len(entries)} legend colors found in the {where}; {text}", 9))
    return out


def expected_colors(rep: dict | None, legend: dict | None, data_dir: Path | None) -> dict:
    """color -> (layer, label) for each legend color the frame must contain."""
    out = {}
    for e in (rep or {}).get("legendEntries") or []:
        if e.get("expect") and e.get("color"):
            out.setdefault(e["color"].lower(), (e["layer"], e.get("label", "")))
    if out or not legend:
        return out
    for name, layer in (legend.get("layers") or {}).items():
        if layer.get("kind") == "classes":
            for c, label, n in zip(layer.get("colors") or [], layer.get("labels") or [], layer.get("counts") or [1] * 99):
                if n:
                    out.setdefault(c.lower(), (name, label))
            nd = layer.get("nodata") or {}
            if nd.get("count") and nd.get("color"):
                out.setdefault(nd["color"].lower(), (name, nd.get("label", "No data")))
        elif data_dir and (data_dir / f"{name}.geojson").is_file():
            feats = json.loads((data_dir / f"{name}.geojson").read_text()).get("features") or []
            if fill := next((f["properties"].get("dm_fill") for f in feats if f.get("properties", {}).get("dm_fill")), None):
                out.setdefault(fill.lower(), (name, layer.get("title", name)))
    return out



def size_arg(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)x(\d+)", text or "")
    if not m:
        raise ValueError(f'"{text}" is not WIDTHxHEIGHT, such as 1200x800')
    return int(m[1]), int(m[2])


def judge_file_url(browser: str, folder: Path, w: int, h: int, timeout: float, flags: list) -> Finding:
    """A reader may open index.html straight from disk, and a CRS page loads proj4 into the map's workers there too."""
    with tempfile.TemporaryDirectory() as tmp:
        run = cdp.capture(browser, folder.resolve(), "index.html", Path(tmp) / "file.png", w, h, 1, timeout, flags,
                          url=(folder.resolve() / "index.html").as_uri())
    if why := run.get("ready_error") or run.get("error"):
        return FAIL("file", f"opened from file://, the page doesn't draw: {why}", "load anything the workers import from a data: URL, not a blob: URL", 33)
    return PASS("file", "the page also draws when opened from file://", 33)


def check_page(args) -> int:
    folder = Path(args.out)
    if folder.is_file():
        folder = folder.parent
    if not (folder / "index.html").is_file():
        raise ValueError(f"{folder / 'index.html'} does not exist; mln-rs projects are judged with check --png")
    page = Page.read(folder)
    figure = (page.spec or {}).get("figure") or {}
    w, h = size_arg(args.size or figure.get("size") or "1200x800")
    scale = args.scale if args.scale is not None else figure.get("scale", 1)
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or scale <= 0:
        raise ValueError(f"dm-spec figure.scale {scale!r} is not a positive number")
    scale = int(scale) if scale == int(scale) else scale
    findings = static_pass(page)
    shot = folder / (f"index.{w}x{h}.png" if scale == 1 else f"index.{w}x{h}@{scale:g}x.png")
    run = None
    browser = None if args.no_browser else cdp.find_browser()
    if args.no_browser or not browser:
        why = "--no-browser" if args.no_browser else "no Chrome, Chromium, Edge, or Brave found"
        findings.append(WARN("render", f"render not measured: {why}", "rerun check where headless Chrome runs and jsDelivr is reachable, or set DM_BROWSER", 33))
    else:
        flags = cdp.GL_FLAGS[args.gl]
        run = cdp.capture(browser, folder.resolve(), "index.html", shot.resolve(), w, h, scale, args.timeout, flags)
        if args.gl == "default" and (run.get("probe") or {}).get("renderer") is None and "launch_error" not in run and page.is_map:
            run = cdp.capture(browser, folder.resolve(), "index.html", shot.resolve(), w, h, scale, args.timeout, cdp.GL_FLAGS["swiftshader"])
        verdict = judge_run(run, page, w, h, scale)
        findings += verdict
        measured = not any(f.check == "render" and f.status == "WARN" for f in verdict)
        if measured and shot.exists():
            findings += judge_png(shot, run.get("report"), run, scale, page.legend, folder / "data")
            findings.append(PASS("screenshot", str(shot.resolve())))
        if measured and page.is_map and page.projection.get("type") == "crs":
            findings.append(judge_file_url(browser, folder, w, h, args.timeout, run.get("flags") or flags))
    record = {"page": str((folder / "index.html").resolve()), "png": str(shot.resolve()) if run and shot.exists() else None,
              "size": [w, h], "scale": scale, "report": (run or {}).get("report"),
              "run": {k: v for k, v in (run or {}).items() if k not in ("report",)}}
    ok = not any(f.status == "FAIL" for f in findings)
    (folder / "check.json").write_text(json.dumps({"ok": ok, "findings": [asdict(f) for f in findings], **record}, indent=1, ensure_ascii=False) + "\n")
    return report(findings, args.json, record)


def check_png(args) -> int:
    path = Path(args.png)
    if not path.is_file():
        raise ValueError(f"{path} does not exist")
    legend = json.loads(Path(args.legend).read_text()) if args.legend else None
    rep = json.loads(Path(args.report).read_text()) if args.report else None
    findings = []
    if rep:
        if rep.get("moving"):
            findings.append(FAIL("motion", "the snapshot was taken while the map moved", "snapshot only after the frame settles", 26))
        if (rep.get("pitch") or 0) > 0:
            findings.append(WARN("pitch", f"the snapshot is tilted to pitch {rep['pitch']:g}", "keep pitch 0 unless the brief records why", 22))
        if extra := [c for c in rep.get("controls") or [] if "attrib" not in c]:
            findings.append(WARN("controls", f"the snapshot shows controls: {', '.join(extra)}", "leave out controls nobody asked for", 23))
        if len(rep.get("fonts") or []) > 2:
            findings.append(WARN("fonts", f"{len(rep['fonts'])} font families: {', '.join(rep['fonts'])}", "use at most two", 23))
    scale = (rep or {}).get("viewport", {}).get("dpr", 1) if rep else 1
    findings += judge_png(path, rep, None, scale, legend, Path(args.legend).parent if args.legend else None, args.background)
    return report(findings, args.json, {"png": str(path.resolve())})


def run(args) -> int:
    try:
        if not args.png and not args.out:
            raise ValueError("name the project folder OUT, or a snapshot with --png")
        return check_png(args) if args.png else check_page(args)
    except ValueError as err:
        print(f"datamap.py check: {err}")
        return 2


def register(sub) -> None:
    p = sub.add_parser("check", help="lint a map page, render it in headless Chrome, and judge the render",
                       description="Lints the page against its dm-spec, then renders it and judges the screenshot. "
                                   "With --png, judges a snapshot another renderer wrote, such as mln-rs.")
    p.add_argument("out", nargs="?", metavar="OUT", help="the project folder (or its index.html)")
    p.add_argument("--size", help="viewport in CSS px (default: dm-spec figure.size, else 1200x800)")
    p.add_argument("--scale", type=float, help="device scale; 2 writes an @2x PNG (default: dm-spec figure.scale, else 1)")
    p.add_argument("--timeout", type=float, default=60, help="seconds to wait for the map to be ready")
    p.add_argument("--gl", choices=sorted(cdp.GL_FLAGS), default="default", help="WebGL backend; swiftshader renders without a GPU")
    p.add_argument("--no-browser", action="store_true", help="static pass only")
    p.add_argument("--png", metavar="PNG", help="judge this PNG instead of rendering a page")
    p.add_argument("--legend", metavar="L", help="with --png: the legend.json whose colors the PNG must hold")
    p.add_argument("--report", metavar="R", help="with --png: the renderer's report JSON")
    p.add_argument("--background", default="#ffffff", help="with --png: the color behind transparent pixels")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    p.set_defaults(run=run)
