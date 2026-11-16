"""Read dashboard.css's light and dark tokens and check the palette rules in both themes.

  python3 palette.py            prints each token's contrast against its theme's background, then the rules
Exit status 1 when a rule fails.
"""
import colorsys
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parents[3] / "plugins/data-dashboard/skills/data-dashboard/assets/dashboard.css"


def tokens(block: str) -> dict:
    return {k: v.upper() for k, v in re.findall(r"--dd-([\w-]+):\s*(#[0-9A-Fa-f]{6})", block)}


def themes() -> dict:
    css = CSS.read_text()
    light = tokens(re.search(r"^:root \{(.*?)^\}", css, re.S | re.M)[1])
    media = re.search(r'@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme="light"\]\) \{(.*?)\}\s*\}', css, re.S)
    forced = re.search(r':root\[data-theme="dark"\] \{(.*?)\}', css, re.S)
    if not media or not forced:
        sys.exit("no dark blocks")
    a, b = tokens(media[1]), tokens(forced[1])
    if a != b:
        sys.exit(f"the two dark blocks differ: {sorted(set(a.items()) ^ set(b.items()))}")
    if set(a) != set(light):
        sys.exit(f"dark and light define different tokens: {sorted(set(a) ^ set(light))}")
    return {"light": light, "dark": a}


def rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def lum(h):
    return sum(w * (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for w, c in zip((0.2126, 0.7152, 0.0722), rgb(h)))


def ratio(a, b):
    x, y = lum(a) + 0.05, lum(b) + 0.05
    return max(x, y) / min(x, y)


def lstar(h):
    y = lum(h)
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else 24389 / 27 * y


def hue(h):
    return colorsys.rgb_to_hls(*rgb(h))[0] * 360


def rules(t: dict, name: str) -> list:
    bg = t["bg"]
    c = {k: ratio(v, bg) for k, v in t.items()}
    marks = ["bar", "fill", "fill-hi", "tone-0", "tone-1", "tone-2", "spark", "alert", "warn"]
    bands = [f"band-{i}" for i in range(5)]
    out = [
        ("background is not pure black or white", t["bg"] not in ("#000000", "#FFFFFF")),
        ("text ink, ink-2, ink-3 at 4.5:1 or more", all(c[k] >= 4.5 for k in ("ink", "ink-2", "ink-3"))),
        ("section-title accent at 4.5:1 or more", c["accent"] >= 4.5),
        ("page title at 3:1 or more (large text), quieter than the accent and the ink", 3 <= c["title"] < c["accent"] < c["ink"]),
        ("bands step from the worst (most contrast) to the best (closest to the background)", all(c[a] > c[b] for a, b in zip(bands, bands[1:])) and c["band-4"] > 1.05),
        ("bar and target are the bullet graph's highest-contrast marks, above the projection and every band", c["bar"] > c["proj"] > c["band-0"]),
        ("bar at 3:1 or more on the worst band", ratio(t["bar"], t["band-0"]) >= 3),
        ("every mark at 3:1 or more", all(c[k] >= 3 for k in marks)),
        ("critical more prominent than warning", c["alert"] > c["warn"]),
        ("the two reds clearly apart in lightness (10 L* or more)", abs(lstar(t["alert"]) - lstar(t["warn"])) >= 10),
        ("the two reds one hue (within 12 degrees)", min(abs(hue(t["alert"]) - hue(t["warn"])), 360 - abs(hue(t["alert"]) - hue(t["warn"]))) <= 12),
        ("hairline just visible (1.2 to 1.8:1)", 1.2 <= c["rule"] <= 1.8),
        ("axis just visible, above the hairline (1.6 to 2.6:1)", c["rule"] < c["axis"] and 1.6 <= c["axis"] <= 2.6),
        ("normal band, tint and box are quiet fills (under 1.6:1)", all(1.05 < c[k] < 1.6 for k in ("norm", "tint", "box"))),
        ("treemap: the neutral cell is just visible (1.1 to 1.6:1)", 1.1 <= c["heat-0"] <= 1.6),
        ("treemap: each tint steps further from the background, 4 L* or more", all(abs(lstar(t[f"heat-{i + 1}"]) - lstar(bg)) - abs(lstar(t[f"heat-{i}"]) - lstar(bg)) >= 4 for i in range(4))),
        ("treemap: text at 4.5:1 or more on every tint", all(ratio(t["ink"], t[f"heat-{i}"]) >= 4.5 for i in range(5))),
        ("treemap: background-colored text at 4.5:1 or more on the alert red", ratio(t["bg"], t["alert"]) >= 4.5),
        ("treemap: alert cells more prominent than the strongest tint", c["alert"] > c["heat-4"]),
        ("treemap: tints are the alert hue (within 12 degrees)", all(min(abs(hue(t[f"heat-{i}"]) - hue(t["alert"])), 360 - abs(hue(t[f"heat-{i}"]) - hue(t["alert"]))) <= 12 for i in range(1, 5))),
    ]
    return [(f"{name}: {r}", ok) for r, ok in out]


def main() -> int:
    ts = themes()
    print(f"{'token':10} {'light':>8} {'ratio':>6}   {'dark':>8} {'ratio':>6}  L* dark")
    for k in ts["light"]:
        if k == "bg":
            continue
        print(f"{k:10} {ts['light'][k]:>8} {ratio(ts['light'][k], ts['light']['bg']):6.2f}   {ts['dark'][k]:>8} {ratio(ts['dark'][k], ts['dark']['bg']):6.2f}  {lstar(ts['dark'][k]):5.1f}")
    print(f"{'bg':10} {ts['light']['bg']:>8} {'':6}   {ts['dark']['bg']:>8}")
    failed = 0
    for name, t in ts.items():
        for r, ok in rules(t, name):
            failed += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {r}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
