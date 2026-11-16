#!/usr/bin/env python3
"""Build and check one-screen dashboards drawn with the data-dashboard library.

  dashboard.py new OUT [--viewport WxH] [--title T] [--data D.json] [--force]
  dashboard.py sync OUT [--data D.json] [--check]
  dashboard.py check OUT [--viewport WxH] [--phone WxH] [--theme light|dark|both] [--json] [--no-browser]

`new` writes the page with dashboard.css and dashboard.js inlined between
version and sha256 markers. `sync` rewrites those regions from assets/ and
optionally the data block. `check` runs a static pass over the file, then
renders a temporary copy of it with assets/check.js inlined after the library
in headless Chrome, reads the report check.js writes, and saves a screenshot
of the page itself at the design viewport and one at phone width,
<page>.phone.png, the full length of the one scrolling column. The desktop pass
runs in the light and the dark color scheme, and saves the dark screenshot as
<page>.<W>x<H>.dark.png; the phone pass runs in light.
Each finding cites the mistake it guards against, numbered as in chapter 3 of
Stephen Few's Information Dashboard Design. Exit status 1 means a FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

VERSION = "0.1.0"
ASSETS = Path(__file__).resolve().parent.parent / "assets"
LIB = {"css": ("style", "dashboard.css"), "lib": ("script", "dashboard.js")}
UNIT = 20
SCHEMES = {"light": 1, "dark": 0}
EMPTY_DATA = '{"asOf": "", "locale": "en-US", "policy": {"warn": 0.95, "alert": 0.85}, "measures": {}}'
REGION = re.compile(
    r"<!-- data-dashboard:(css|lib) (\S+) sha256:([0-9a-f]{64}) -->\n<(style|script)>\n(.*?)</\4>\n<!-- /data-dashboard:\1 -->", re.S)
DATA = re.compile(r'(<script type="application/json" id="dd-data">\n?)(.*?)(\n?</script>)', re.S)
REPORT = re.compile(r'<script[^>]*id="dd-report"[^>]*>(.*?)</script>', re.S)
SHAPES = re.compile(r"<(rect|circle|path|line|polyline|polygon|ellipse)\b", re.I)
REFUSED = re.compile(r"\b(?:dd|DataDashboard)(?:\.svg)?\.(pie|donut|gauge|radar|area)\s*\(")
NETWORK = re.compile(r"""(?:src|href)\s*=\s*["']?(?:https?:)?//|url\(\s*["']?(?:https?:)?//|@import|\bfetch\s*\(""", re.I)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="dd-viewport" content="@W@x@H@">
<title>@TITLE@</title>
@CSS@
<!-- data-dashboard:page-style -->
<style>
:root { --dd-cols: @COLS@; --dd-rows: @ROWS@; }
.dd-grid {
  grid-template-columns: 1fr;
  /* One area per section, the always-important group top left. Few's sales dashboard:
  grid-template-columns: 55fr 39fr;
  grid-template-areas: "key share" "key regions" "products customers"; */
}
</style>
<!-- /data-dashboard:page-style -->
</head>
<body class="dd-page">
<!-- data-dashboard:page -->
<header class="dd-head">
<h1 class="dd-title">@TITLE@</h1>
<p class="dd-asof" id="dd-asof"></p>
<p class="dd-flags" id="dd-flags"></p>
</header>
<main class="dd-grid">
<!-- One section per group:
<section class="dd-sec" style="grid-area: key">
<h2 class="dd-sec-title">Key metrics <span class="dd-qual">(year to date)</span><span class="dd-legend" id="key-legend"></span></h2>
<div id="key"></div>
</section>
-->
</main>
<footer class="dd-foot"></footer>
<script type="application/json" id="dd-data">
@DATA@
</script>
<script type="module">
const dd = DataDashboard
const d = dd.data()
document.querySelector('#dd-asof').textContent = d.asOf ? `Data as of ${dd.asOf(d.asOf, d.tz, d.locale)}` : ''
dd.flags('#dd-flags')
</script>
<!-- /data-dashboard:page -->
@LIB@
</body>
</html>
"""


def die(msg: str) -> None:
    sys.exit(f"dashboard.py: {msg}")


def size(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)x(\d+)", text or "")
    if not m:
        die(f'"{text}" is not WIDTHxHEIGHT, such as 1440x800')
    return int(m[1]), int(m[2])


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def asset(name: str) -> str:
    return (ASSETS / LIB[name][1]).read_text(encoding="utf-8")


def inline(tag: str, name: str) -> str:
    body = (ASSETS / name).read_text(encoding="utf-8")
    if f"</{tag}" in body:
        die(f"{name} contains </{tag}, which would end the inlined region early")
    return body


def block(name: str) -> str:
    tag, body = LIB[name][0], inline(*LIB[name])
    return f"<!-- data-dashboard:{name} {VERSION} sha256:{sha(body)} -->\n<{tag}>\n{body}</{tag}>\n<!-- /data-dashboard:{name} -->"


def read_data(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8").strip()
    try:
        json.loads(text)
    except json.JSONDecodeError as err:
        die(f"{path} is not JSON: {err}")
    return text.replace("</", "<\\/")


def synced(text: str, data: str | None) -> str:
    found = {m[1] for m in REGION.finditer(text)}
    for name in LIB:
        if name not in found:
            die(f"no data-dashboard:{name} region with intact markers; start from `dashboard.py new`")
    text = REGION.sub(lambda m: block(m[1]), text)
    if data is not None:
        if not DATA.search(text):
            die('no <script type="application/json" id="dd-data"> block to replace')
        text = DATA.sub(lambda m: m[1] + data + m[3], text, count=1)
    return text


def cmd_new(a) -> int:
    out = Path(a.out)
    if out.exists() and not a.force:
        die(f"{out} exists; pass --force to overwrite it")
    w, h = size(a.viewport)
    title = html.escape(a.title)
    page = TEMPLATE
    for key, value in {"W": w, "H": h, "COLS": f"{w / UNIT:g}", "ROWS": f"{h / UNIT:g}", "TITLE": title,
                       "DATA": read_data(a.data) if a.data else EMPTY_DATA, "CSS": block("css"), "LIB": block("lib")}.items():
        page = page.replace(f"@{key}@", str(value))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out.resolve()}")
    return 0


def cmd_sync(a) -> int:
    path = Path(a.out)
    old = path.read_text(encoding="utf-8")
    new = synced(old, read_data(a.data) if a.data else None)
    if a.check:
        stale = [m[1] for m in REGION.finditer(old) if m[3] != sha(asset(m[1])) or sha(m[5]) != m[3] or m[2] != VERSION]
        if a.data and DATA.search(old)[2] != DATA.search(new)[2]:
            stale.append(f"the data block ({a.data})")
        if new != old:
            print(f"FAIL sync: {path} differs from assets/ in {', '.join(stale) or 'region layout'}. Fix: run dashboard.py sync {a.out}" + (f" --data {a.data}" if a.data else ""))
            return 1
        print(f"PASS sync: {path} matches assets/ ({VERSION})" + (f", and its data block matches {a.data}" if a.data else ""))
        return 0
    if new == old:
        print(f"{path} already matches assets/ ({VERSION})")
    else:
        path.write_text(new, encoding="utf-8")
        print(f"updated {path.resolve()}")
    return 0


def finding(status: str, name: str, mistake: int | None, msg: str, fix: str = "") -> dict:
    return {"status": status, "check": name, "mistake": mistake, "message": msg, "fix": fix}


def rgb(token: str) -> tuple[int, int, int] | None:
    token = token.strip().lower()
    if m := re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", token):
        hx = m[1] if len(m[1]) == 6 else "".join(c * 2 for c in m[1])
        return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))
    if m := re.fullmatch(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+).*\)", token):
        return int(m[1]), int(m[2]), int(m[3])
    return None


def hue(c: tuple[int, int, int]) -> str | None:
    r, g, b = (v / 255 for v in c)
    hi, lo = max(r, g, b), min(r, g, b)
    if hi - lo < 0.25:
        return None
    deg = (60 * ((g - b) / (hi - lo)) % 360) if hi == r else 60 * ((b - r) / (hi - lo)) + (120 if hi == g else 240)
    return "red" if deg < 20 or deg >= 340 else "green" if 80 <= deg < 170 else "other"


def tokens() -> set[tuple[int, int, int]]:
    css = asset("css")
    return {rgb(m[1]) for m in re.finditer(r"--dd-(?:alert|warn):\s*(#[0-9A-Fa-f]{3,6})", css)}


def static_pass(text: str) -> list[dict]:
    out = []
    regions = {m[1]: m for m in REGION.finditer(text)}
    for name in LIB:
        m = regions.get(name)
        if not m:
            out.append(finding("FAIL", "library", None, f"no data-dashboard:{name} region with intact markers", "start from dashboard.py new, or restore the markers and run sync"))
        elif sha(m[5]) != m[3]:
            out.append(finding("FAIL", "library", None, f"the {name} region was edited by hand (its sha256 no longer matches the marker)", f"run dashboard.py sync; change {LIB[name][1]} in assets/ instead"))
        elif m[3] != sha(asset(name)) or m[2] != VERSION:
            out.append(finding("WARN", "library", None, f"the {name} region is {m[2]} {m[3][:12]}, older than assets/", "run dashboard.py sync"))
        else:
            out.append(finding("PASS", "library", None, f"{name} region matches assets/ {VERSION}"))
    authored = re.sub(r"<!--.*?-->", "", REGION.sub("", text), flags=re.S)
    if dm := DATA.search(text):
        try:
            data = json.loads(dm[2] or "{}")
        except json.JSONDecodeError as err:
            data = None
            out.append(finding("FAIL", "data", None, f"#dd-data is not JSON: {err}", "fix the JSON, or regenerate it and run sync --data"))
        if data is not None:
            measures = data.get("measures") or {}
            items = measures.items() if isinstance(measures, dict) else enumerate(measures)
            bare = [str(m.get("label", k)) for k, m in items if not any(m.get(f) is not None for f in ("target", "forecast", "prior", "norm", "ranges"))]
            if bare:
                out.append(finding("FAIL", "context", 2, f"{len(bare)} measure(s) with nothing to compare against: {', '.join(bare)}", "give each a target, forecast, prior, norm or ranges, or drop it"))
            else:
                out.append(finding("PASS", "context", 2, f"all {len(measures)} measures carry a comparison"))
            when = str(data.get("asOf") or "")
            if not re.search(r"T\d\d:\d\d.*(Z|[+-]\d\d:?\d\d)$", when):
                out.append(finding("WARN", "as-of", 2, f'asOf "{when}" has no time with a zone', 'write it as ISO 8601 with an offset, such as "2026-10-13T08:00:00-07:00"'))
    else:
        out.append(finding("FAIL", "data", None, 'no <script type="application/json" id="dd-data"> block', "start from dashboard.py new"))
    if found := sorted({m[1] for m in REFUSED.finditer(authored)}):
        out.append(finding("FAIL", "media", 5, f"the page calls {', '.join('dd.' + f for f in found)}", "pie and donut become dd.bars sorted with pctTotal; gauge becomes dd.bullet; radar becomes dd.bars; area becomes dd.line"))
    if shapes := sorted({m[1].lower() for m in SHAPES.finditer(authored)}):
        out.append(finding("FAIL", "hand-drawn", 7, f"the page draws {', '.join('<' + s + '>' for s in shapes)} itself", "draw every graph with a dd medium, so geometry, state and accessible names come from the library"))
    if NETWORK.search(authored):
        out.append(finding("FAIL", "self-contained", None, f'the page loads from the network: "{NETWORK.search(authored)[0]}"', "inline everything; the page must open from file:// offline"))
    styles = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", authored, re.S) + re.findall(r'style="([^"]*)"', authored))
    for pattern, what, mistake in ((r"gradient\(", "gradient", 11), (r"box-shadow", "shadow", 11), (r"<canvas", "canvas", 7),
                                   (r"rotate\(|writing-mode", "rotated text", 7)):
        if re.search(pattern, styles if what != "canvas" else authored, re.I):
            out.append(finding("FAIL", "decoration", mistake, f"the page's own CSS or markup uses {what}", "remove it; Few's displays use flat fills, horizontal text and white space"))
    if re.search(r"(?:^|[;{\s\"])(?:border|outline)\s*:\s*(?!none|0\b)", styles):
        out.append(finding("FAIL", "decoration", 11, "the page's CSS draws a border on every side of a box", "separate groups with white space; a hairline under a title is the most a section gets"))
    for m in re.finditer(r"border-radius\s*:\s*([\d.]+)px", styles):
        if float(m[1]) > 3:
            out.append(finding("FAIL", "decoration", 11, f"border-radius {m[1]}px rounds a panel", "drop it; sections are separated by white space"))
    colors = {c for c in (rgb(t) for t in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)", styles)) if c and hue(c)}
    hues = {hue(c) for c in colors}
    if {"red", "green"} <= hues:
        out.append(finding("FAIL", "color", 12, "the page's CSS sets both a red and a green", "use one red, at two intensities, for alerts only; nothing is green"))
    elif extra := sorted("#%02X%02X%02X" % c for c in colors - tokens()):
        out.append(finding("WARN", "color", 12, f"the page's CSS sets saturated color {', '.join(extra)}", "keep everything gray; only alert dots carry saturated red"))
    meta = re.search(r'<meta name="dd-viewport" content="(\d+)x(\d+)"', text)
    cols = re.search(r"--dd-cols:\s*([\d.]+);\s*--dd-rows:\s*([\d.]+)", authored)
    if meta and cols and (abs(float(cols[1]) - int(meta[1]) / UNIT) > 0.01 or abs(float(cols[2]) - int(meta[2]) / UNIT) > 0.01):
        out.append(finding("FAIL", "viewport", 1, f"dd-viewport {meta[1]}x{meta[2]} disagrees with --dd-cols {cols[1]} / --dd-rows {cols[2]}", f"set --dd-cols: {int(meta[1]) / UNIT:g}; --dd-rows: {int(meta[2]) / UNIT:g}"))
    return out


def find_browser() -> str | None:
    if env := os.environ.get("DD_BROWSER"):
        return env if Path(env).exists() else shutil.which(env)
    for base in (Path("/Applications"), Path.home() / "Applications"):
        for app in ("Google Chrome", "Chromium", "Microsoft Edge", "Brave Browser"):
            exe = base / f"{app}.app" / "Contents" / "MacOS" / app
            if exe.exists():
                return str(exe)
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
        if found := shutil.which(name):
            return found
    names = {"Chromium", "Google Chrome for Testing", "chrome", "chrome-headless-shell", "headless_shell"}
    for cache in (Path.home() / "Library/Caches/ms-playwright", Path.home() / ".cache/ms-playwright"):
        dirs = sorted(cache.glob("chromium*"), key=lambda d: ("headless" not in d.name, -int(re.sub(r"\D", "", d.name) or 0)))
        for d in dirs:
            for exe in sorted(d.rglob("*")):
                if exe.name in names and exe.is_file() and os.access(exe, os.X_OK):
                    return str(exe)
    return None


class Hung(Exception):
    pass


def chrome(browser: str, extra: list[str], w: int, h: int, url: str, theme: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory(prefix="dd-chrome-") as profile:
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
               "--no-first-run", "--no-default-browser-check", "--disable-extensions", f"--user-data-dir={profile}",
               f"--window-size={w},{h}", "--virtual-time-budget=5000", f"--blink-settings=preferredColorScheme={SCHEMES[theme]}", *extra, url]
        if os.environ.get("CI") or (hasattr(os, "geteuid") and os.geteuid() == 0):
            cmd.insert(1, "--no-sandbox")
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            raise Hung(f"{browser} did not finish within 60 s") from None


def probe(page: Path, text: str) -> Path:
    """Write a copy of the page beside it with check.js inlined after the library, so the
    page keeps its relative paths and the page itself never carries the check."""
    end = "<!-- /data-dashboard:lib -->"
    script = f"{end}\n<script>\n{inline('script', 'check.js')}</script>"
    fd, name = tempfile.mkstemp(prefix=f".{page.stem}.", suffix=".dd-check.html", dir=page.parent)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text.replace(end, script, 1))
    return Path(name)


def measure(browser: str, page: Path, w: int, h: int, theme: str, delta=(0, 0)):
    """Lay the page out at w x h and return its report. --dump-dom lays out shorter than
    --window-size on some platforms (87 px on Chrome 157 for macOS), so read the real
    inner size back and relaunch with the difference added."""
    dw, dh = delta
    for _ in range(3):
        run = chrome(browser, ["--dump-dom"], w + dw, h + dh, page.as_uri(), theme)
        m = REPORT.search(run.stdout)
        if not m:
            return None, (dw, dh), run.stderr.strip().splitlines()[-3:]
        rep = json.loads(m[1])
        iw, ih = rep["viewport"]["w"], rep["viewport"]["h"]
        if (iw, ih) == (w, h):
            break
        dw, dh = dw + w - iw, dh + h - ih
    return rep, (dw, dh), []


def screenshot(browser: str, page: Path, w: int, h: int, out: Path, theme: str) -> tuple[int, int] | None:
    out.unlink(missing_ok=True)
    chrome(browser, [f"--screenshot={out}"], w, h, page.as_uri(), theme)
    if not out.exists():
        return None
    head = out.read_bytes()[:24]
    return struct.unpack(">II", head[16:24])


def judge(rep: dict, w: int, h: int, theme: str) -> list[dict]:
    out = []
    if rep.get("scheme") != theme:
        out.append(finding("WARN", "theme", None, f"Chrome laid the page out in {rep.get('scheme')}, not {theme}, so {theme} was not judged", "set DD_BROWSER to a current Chrome"))
    vp = rep["viewport"]
    if (vp["w"], vp["h"]) != (w, h):
        out.append(finding("WARN", "viewport", None, f"Chrome laid the page out at {vp['w']}x{vp['h']}, not {w}x{h}", "set DD_BROWSER to a current Chrome"))
    if rep["layout"] != "grid":
        out.append(finding("FAIL", "fit", 1, f"at {w}x{h} the page fell back to one scrolling column (body text {rep['fontPx']} px)", "check the dd-viewport meta and --dd-cols"))
    page_w, page_h = rep["page"]["w"], rep["page"]["h"]
    lowest = max((s["bottom"] for s in rep["sections"]), default=0)
    if page_h > h or page_w > w:
        past = [f'"{s["name"]}" ends at {s["bottom"]}' for s in rep["sections"] if s["bottom"] > h]
        wide = [f'"{s["name"]}" ends at x {s["right"]}' for s in rep["sections"] if s["right"] > w]
        over = page_h - h
        out.append(finding("FAIL", "fit", 1, f"the page is {page_w}x{page_h} in a {w}x{h} screen, {over} px too tall" + (f" and {page_w - w} px too wide" if page_w > w else "")
                           + (f"; past the edge: {', '.join(past + wide)}" if past or wide else ""),
                           f"drop about {max(1, -(-over // UNIT))} rows of 1u ({UNIT} px) or a whole section, or move one to a shorter column; the page is refused, never squeezed"))
    else:
        floor = min(h, rep.get("footTop") or h)
        slack = floor - lowest
        edge = "the footer" if floor < h else "the bottom"
        status = "FAIL" if slack < 0 else "PASS" if slack >= 0.05 * h else "WARN"
        out.append(finding(status, "fit", 1, f"fits {w}x{h}; the lowest section ends at {lowest} px, {abs(slack)} px ({abs(slack) / h:.0%}) {'above' if slack >= 0 else 'into'} {edge}",
                           "drop a row or a section; sections may not run into the footer" if slack < 0 else "keep 5% slack, since Linux fonts set wider than macOS ones" if status == "WARN" else ""))
    for o in rep["overlaps"]:
        out.append(finding("FAIL", "overlap", 9, f'sections "{o["a"]}" and "{o["b"]}" overlap by {o["w"]}x{o["h"]} px', "give each section its own grid area"))
    for c in rep["clipped"]:
        out.append(finding("FAIL", "clipped", 7, f"{c['text']} is cut off by {c['px']} px", "widen the column, shorten the label, or let the library ellipsize it"))
    for c in rep["collide"]:
        out.append(finding("FAIL", "text overlap", 7, f"{c['a']} overlaps {c['b']}", "give the section more width or fewer rows"))
    for s in rep["small"]:
        out.append(finding("FAIL", "type size", 7, f"{s['text']} is {s['px']} px", "nothing under 9 px; scale with --u instead of fixed sizes"))
    for c in rep["contrast"]:
        out.append(finding("FAIL", "contrast", 12, f"{c['text']} is {c['color']} on {c['bg']}, {c['ratio']}:1 (needs {c['need']}:1)", "give the text more contrast; color it with --dd-ink, --dd-ink-2 or --dd-ink-3"))
    for c in rep["marks"]:
        out.append(finding("FAIL", "contrast", 12, f"mark {c['el']} is {c['color']}, {c['ratio']}:1 on the background (needs 3:1)", "color it with a gray token that has more contrast"))
    if not (rep["overlaps"] or rep["clipped"] or rep["collide"] or rep["small"] or rep["contrast"] or rep["marks"]):
        out.append(finding("PASS", "legibility", 7, f"no overlapping sections, clipped or colliding text, type under 9 px (body {rep['fontPx']} px), or contrast below 4.5:1 for text and 3:1 for marks"))
    alert_rgb = tokens()
    sat = [c for c in rep["colors"] if rgb(c["color"]) not in alert_rgb]
    hues = {hue(rgb(c["color"])) for c in rep["colors"]}
    if {"red", "green"} <= hues:
        out.append(finding("FAIL", "color", 12, "red and green both appear on the page", "drop the green; good needs no color"))
    for c in sat:
        out.append(finding("FAIL", "color", 12, f"saturated {c['color']} on {c['count']} element(s), first at {c['where']}", "keep everything gray; only alerts carry saturated red"))
    if not sat and "green" not in hues:
        out.append(finding("PASS", "color", 12, f"the only saturated colors are the alert tokens ({', '.join(c['color'] for c in rep['colors']) or 'none drawn'})"))
    rows, warn, alert = rep["rows"]["total"], rep["rows"]["warn"], rep["rows"]["alert"]
    if rows:
        share = (len(warn) + len(alert)) / rows
        status = "PASS" if share <= 0.2 else "WARN"
        names = ", ".join(alert + warn)
        out.append(finding(status, "alerts", 10, f"{len(alert)} critical and {len(warn)} warning of {rows} rows ({share:.0%})" + (f": {names}" if names else ""),
                           "highlight only true exceptions; raise the thresholds in the policy" if status == "WARN" else ""))
    groups = rep["groups"]
    out.append(finding("PASS" if 3 <= groups <= 9 else "WARN", "groups", 9, f"{groups} sections",
                       "" if 3 <= groups <= 9 else "aim for 3 to 9 groups, near 4, so the screen reads as a few chunks"))
    for el in rep.get("empty", []):
        out.append(finding("FAIL", "empty", 2, f"{el} drew nothing", "pass the mount its data; a section with no display gives no context"))
    for err in rep["errors"]:
        m = re.search(r"mistake (\d+)", err)
        out.append(finding("FAIL", "script", int(m[1]) if m else None, f"the page threw: {err}", "fix the page script; read the message for the medium to use"))
    return out


def judge_phone(rep: dict, w: int) -> list[dict]:
    vw = rep["viewport"]["w"]
    at = f"{vw} px, the narrowest window --dump-dom lays out," if vw > w else f"{w} px,"
    if rep["layout"] != "column":
        return [finding("FAIL", "phone", 1, f"at {at} the grid did not reflow to one column", "keep the dd-viewport meta and --dd-cols in the page-style region")]
    fits = rep["page"]["w"] <= vw
    out = [finding("PASS" if fits else "FAIL", "phone", 1, f"one scrolling column at {at} {rep['page']['h']} px tall and {rep['page']['w']} px wide",
                   "" if fits else "something is wider than the screen; let it shrink")]
    for c in rep["clipped"] + rep["collide"]:
        out.append(finding("WARN", "phone", 7, f"at {at} {c.get('text') or c['a'] + ' overlaps ' + c['b']}", "shorten labels; the library ellipsizes long ones"))
    return out


def merge(judged: dict[str, list[dict]]) -> list[dict]:
    """Print a finding once when every theme gave it, and name the themes it holds in."""
    out, seen = [], {}
    for theme, fs in judged.items():
        for f in fs:
            key = (f["status"], f["check"], f["mistake"], f["message"], f["fix"])
            if key not in seen:
                seen[key] = {**f, "themes": []}
                out.append(seen[key])
            seen[key]["themes"].append(theme)
    first = {}
    for f in out:
        first.setdefault(f["check"], len(first))
    out.sort(key=lambda f: first[f["check"]])
    for f in out:
        f["check"] = f"{f['check']} in {' and '.join(f['themes'])}"
    return out


def cmd_check(a) -> int:
    page = Path(a.out).resolve()
    text = page.read_text(encoding="utf-8")
    meta = re.search(r'<meta name="dd-viewport" content="(\d+x\d+)"', text)
    w, h = size(a.viewport or (meta[1] if meta else "1440x800"))
    pw, ph = size(a.phone)
    out, shots, reports = static_pass(text), [], {}
    browser = None if a.no_browser else find_browser()
    if not browser:
        why = "--no-browser" if a.no_browser else "no Chrome, Chromium, Edge or Brave found (set DD_BROWSER)"
        out.append(finding("WARN", "fit", 1, f"{why}: fit, overlap, type and contrast were not measured", "do the row budget by hand, or install Chrome and rerun"))
    else:
        copy = probe(page, text)
        try:
            out, shots, reports = browser_pass(browser, page, copy, w, h, pw, ph, out, ["light", "dark"] if a.theme == "both" else [a.theme])
        except Hung as hung:
            out.append(finding("WARN", "fit", 1, f"{hung}: fit, overlap, type and contrast were not measured", "set DD_BROWSER to a Chrome that runs headless here"))
        finally:
            copy.unlink(missing_ok=True)
    failed = any(f["status"] == "FAIL" for f in out)
    if a.json:
        print(json.dumps({"page": str(page), "ok": not failed, "findings": out, "screenshots": shots, "reports": reports}, indent=1))
    else:
        for f in out:
            mistake = f" [mistake {f['mistake']}]" if f["mistake"] else ""
            fix = f" Fix: {f['fix']}" if f["fix"] and f["status"] != "PASS" else ""
            print(f"{f['status']:<4} {f['check']}{mistake}: {f['message']}.{fix}")
        for s in shots:
            print(f"screenshot {s}")
    return 1 if failed else 0


def browser_pass(browser: str, page: Path, copy: Path, w: int, h: int, pw: int, ph: int, out: list[dict], themes: list[str]):
    shots, reports, judged, delta = [], {}, {}, (0, 0)
    for theme in themes:
        rep, delta, err = measure(browser, copy, w, h, theme, delta)
        if rep is None:
            judged[theme] = [finding("FAIL", "browser", None, "check.js wrote no #dd-report in the page" + (f" ({'; '.join(err)})" if err else ""), "check that the lib region is intact; run sync")]
            break
        reports[theme] = rep
        judged[theme] = judge(rep, w, h, theme)
        png = page.with_name(f"{page.stem}.{w}x{h}{'.dark' if theme == 'dark' else ''}.png")
        if screenshot(browser, page, w, h, png, theme):
            shots.append(str(png))
        else:
            judged[theme].append(finding("WARN", "screenshot", None, f"no screenshot at {png}"))
    out += merge(judged)
    if len(reports) < len(themes):
        return out, shots, reports
    phone, _, _ = measure(browser, copy, pw, ph, "light", delta)
    if phone:
        reports["phone"] = phone
        out += judge_phone(phone, pw)
        laid = max(pw, phone["viewport"]["w"])
        full = min(max(phone["page"]["h"], ph), 6000)
        png = page.with_name(f"{page.stem}.phone.png")
        if screenshot(browser, page, laid, full, png, "light"):
            shots.append(str(png))
    return out, shots, reports


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new", help="write a new page with the library inlined")
    p.add_argument("out")
    p.add_argument("--viewport", default="1440x800", help="design viewport in CSS px (default 1440x800)")
    p.add_argument("--title", default="Dashboard")
    p.add_argument("--data", help="JSON file for the #dd-data block")
    p.add_argument("--force", action="store_true", help="overwrite an existing file")
    p.set_defaults(run=cmd_new)
    p = sub.add_parser("sync", help="rewrite the library regions, and optionally the data block")
    p.add_argument("out")
    p.add_argument("--data", help="JSON file to put in the #dd-data block")
    p.add_argument("--check", action="store_true", help="write nothing; exit 1 when the page differs")
    p.set_defaults(run=cmd_sync)
    p = sub.add_parser("check", help="static pass, then render in headless Chrome and judge the report")
    p.add_argument("out")
    p.add_argument("--viewport", help="design viewport (default: the page's dd-viewport meta)")
    p.add_argument("--phone", default="390x844", help="phone viewport (default 390x844)")
    p.add_argument("--theme", choices=("light", "dark", "both"), default="both", help="color scheme of the desktop pass (default both; the phone pass runs in light)")
    p.add_argument("--json", action="store_true", help="print findings, screenshots and reports as JSON")
    p.add_argument("--no-browser", action="store_true", help="static pass only")
    p.set_defaults(run=cmd_check)
    a = ap.parse_args()
    return a.run(a)


if __name__ == "__main__":
    sys.exit(main())
