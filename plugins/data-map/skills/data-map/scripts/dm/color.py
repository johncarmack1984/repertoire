"""Color: ColorBrewer palettes, scheme choice, CIELAB, and color-vision-deficiency checks."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PALETTES = Path(__file__).resolve().parents[2] / "assets" / "palettes.json"

DEFAULT_PALETTE = {"seq": "YlGnBu", "div": "RdBu", "qual": "Set2"}
NODATA_CANDIDATES = ["#d9d9d9", "#bdbdbd", "#f0f0f0", "#969696"]

# Machado, Oliveira and Fernandes (2009), severity 1.0, applied to linear RGB.
CVD = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}
# Smallest CIE76 difference, under normal vision and the three simulations, that a custom palette's
# class pairs must keep. Every ColorBrewer scheme rated colorblind-safe at k <= 7 clears it (lowest 5.3,
# BrBG at 7); RdYlGn at 6 and 7 (1.3) and Spectral at 7 (4.5) do not. Named schemes use Brewer's own rating.
MIN_DELTA_E = 5.0


@dataclass(frozen=True)
class Palette:
    name: str
    type: str
    one_hue: bool
    colors: tuple
    blind: int | None

    @property
    def max_k(self) -> int:
        return 6 if self.one_hue else 7


@lru_cache(maxsize=1)
def schemes() -> dict:
    return json.loads(PALETTES.read_text())["schemes"]


def palette(name: str, k: int, reverse: bool = False) -> Palette:
    """A named ColorBrewer scheme at k classes, or a comma-separated list of hex colors."""
    if name.startswith("#"):
        colors = tuple(normalize_hex(c) for c in name.split(","))
        colors = colors[::-1] if reverse else colors
        return Palette(name="custom", type="custom", one_hue=False, colors=colors, blind=None)
    entry = schemes().get(name)
    if entry is None:
        raise KeyError(f"unknown palette {name}; known: {', '.join(sorted(schemes()))}")
    if str(k) not in entry["colors"]:
        raise KeyError(f"{name} has no {k}-class version; it has {', '.join(entry['colors'])}")
    colors = tuple(entry["colors"][str(k)])
    colors = colors[::-1] if reverse else colors
    return Palette(name=name, type=entry["type"], one_hue=entry["one_hue"], colors=colors, blind=entry["blind"][str(k)])


def normalize_hex(c: str) -> str:
    c = c.strip().lower()
    if len(c) == 4:
        c = "#" + "".join(ch * 2 for ch in c[1:])
    if len(c) != 7 or c[0] != "#" or any(ch not in "0123456789abcdef" for ch in c[1:]):
        raise ValueError(f"not a #rrggbb color: {c}")
    return c


def hex_to_rgb(c: str) -> tuple:
    return tuple(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))


def _linear(u: float) -> float:
    return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4


def _lab_from_linear(r: float, g: float, b: float) -> tuple:
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lab(c: str, cvd: str | None = None) -> tuple:
    """CIELAB (D65) of a hex color, optionally as a reader with the named deficiency sees it."""
    rgb = [_linear(u) for u in hex_to_rgb(c)]
    if cvd:
        m = CVD[cvd]
        rgb = [min(1.0, max(0.0, sum(m[i][j] * rgb[j] for j in range(3)))) for i in range(3)]
    return _lab_from_linear(*rgb)


def delta_e(a: str, b: str, cvd: str | None = None) -> float:
    return math.dist(lab(a, cvd), lab(b, cvd))


def pairs_to_separate(colors: tuple, kind: str) -> list:
    """Class pairs a reader must tell apart: neighbors on a ramp, mirrored classes on a diverging one, all pairs otherwise."""
    n = len(colors)
    if kind == "seq":
        return [(i, i + 1) for i in range(n - 1)]
    if kind == "div":
        return [(i, i + 1) for i in range(n - 1)] + [(i, n - 1 - i) for i in range(n // 2)]
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def worst_pair(colors: tuple, kind: str) -> tuple:
    """The (delta E, vision, i, j) of the least separable class pair across normal vision and the three simulations."""
    worst = (math.inf, "", 0, 0)
    for vision in (None, "protan", "deutan", "tritan"):
        for i, j in pairs_to_separate(colors, kind):
            d = delta_e(colors[i], colors[j], vision)
            if d < worst[0]:
                worst = (d, vision or "normal", i, j)
    return worst


def nodata_color(colors: tuple, clear: float = 12.0) -> str:
    """The lightest gray that stays clear of every class color, so no data recedes and never reads as a class."""
    def gap(g: str) -> float:
        return min(delta_e(g, c) for c in colors)
    return next((g for g in NODATA_CANDIDATES if gap(g) >= clear), max(NODATA_CANDIDATES, key=gap))


def rgb_list(c: str) -> list:
    return [round(u * 255) for u in hex_to_rgb(c)]
