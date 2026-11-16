"""Origin-destination flows (Jenny et al. 2018; Slocum ch. 20; Yang et al. 2019): filtering, geometry, widths, arrows, nodes.

Curves are quadratic Béziers on the sphere: the control point sits off the great-circle midpoint, to the
right of travel, so A to B and B to A bow apart. Flows are placed largest first, and a curve that passes
too near a node it does not connect flips side, then bends more.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

from . import geo, symbols

CURVE_MIN, CURVE_MAX = 0.12, 0.30
GC_OFFSET = 0.05
CLEARANCE_SHARE = 0.04
DENSIFY_DEG = 1.0
TURN_DEG = 2.5
TILE = 512
# The template's fit pads the view by FIT_PAD px past the largest node's radius (fitView in datamap.js).
FIT_PAD = 14.0
CLEAR_PX = 2.0
# The maplibre template's map cell in a 1200 x 800 window (datamap.css): 1200 less 2 x 28 px of padding, the
# 28 px gap and the 272 px side column is 844 wide; 800 less the padding, a two-line title, and the footer is 634.
VIEW = (844, 634)
ARROW_RATIO, ARROW_MIN_PX = 2.5, 6.0
NODE_RMAX = 10.0
# A dark warm orange-brown: warm hues are for the data, blue sinks on thin lines, and red reads as alarm.
FLOW_COLOR = "#a63603"
FADE_MIN = 0.45
NODE_COLOR = "#525252"
# ColorBrewer's BrBG teal and Purples violet: under normal vision and simulated protan, deutan, and tritan
# vision they stay at least 36 CIE76 apart, and 39 from FLOW_COLOR; their L* differ by 8, so neither a gain
# nor a loss outweighs the other.
GAIN_COLOR, LOSS_COLOR = "#018571", "#6a51a3"
HAIRBALL = {"curved": 100, "great-circle": 300}
CANDIDATES = [(1, 1.0), (-1, 1.0), (1, 1.5), (-1, 1.5), (1, 2.0), (-1, 2.0), (1, 2.5), (-1, 2.5), (1, 3.0), (-1, 3.0)]


@dataclass(frozen=True)
class Node:
    id: str
    lon: float
    lat: float
    label: str

    @property
    def pos(self) -> list:
        return [self.lon, self.lat]


@dataclass(frozen=True)
class Flow:
    o: str
    d: str
    value: float
    forward: float | None = None
    reverse: float | None = None


@dataclass
class Placed:
    flow: Flow
    coords: list
    km: float
    side: int
    curvature: float
    near: dict = field(default_factory=dict)

    @property
    def clear(self) -> bool:
        return not self.near

    @property
    def worst(self) -> float:
        """The smallest gap to a node it comes too near, in the clearance's unit; inf when clear."""
        return min(self.near.values(), default=math.inf)


def aggregate(pairs: list) -> tuple:
    """Sums duplicate (o, d, value) rows and drops flows from a place to itself."""
    totals, loops = {}, 0
    for o, d, v in pairs:
        if o == d:
            loops += 1
            continue
        totals[(o, d)] = totals.get((o, d), 0.0) + v
    flows = [Flow(o, d, v) for (o, d), v in totals.items() if v > 0]
    return sorted(flows, key=lambda f: (-f.value, f.o, f.d)), loops


def net(flows: list) -> list:
    """One flow per pair, in the larger direction, carrying the gross values both ways."""
    by_pair = {(f.o, f.d): f.value for f in flows}
    out, seen = [], set()
    for f in flows:
        key = frozenset((f.o, f.d))
        if key in seen:
            continue
        seen.add(key)
        back = by_pair.get((f.d, f.o), 0.0)
        if back == 0:
            out.append(Flow(f.o, f.d, f.value, f.value, 0.0))
        elif f.value >= back:
            out.append(Flow(f.o, f.d, f.value - back, f.value, back))
        else:
            out.append(Flow(f.d, f.o, back - f.value, back, f.value))
    return sorted([f for f in out if f.value > 0], key=lambda f: (-f.value, f.o, f.d))


def keep_top(flows: list, top: int | None = None, share: float | None = None) -> tuple:
    """The largest flows by count or by the share of the total they carry, with that share."""
    total = sum(f.value for f in flows)
    ranked = sorted(flows, key=lambda f: (-f.value, f.o, f.d))
    if top is not None:
        kept = ranked[:top]
    elif share is not None:
        kept, run = [], 0.0
        for f in ranked:
            if run >= share * total:
                break
            kept.append(f)
            run += f.value
    else:
        kept = ranked
    kept_share = sum(f.value for f in kept) / total if total else 1.0
    return kept, kept_share


def omitted_note(kept: int, total: int, share: float, unit: str) -> str:
    if kept == total:
        return f"All {total:,} flows"
    return f"The {kept:,} largest of {total:,} flows, {share:.0%} of all {unit}"


@dataclass(frozen=True)
class NodeMeasure:
    """What a node's circle area counts: the words after the unit in the legend, and the total from in and out."""

    words: str
    size: Callable[[dict], float]


NODE_VALUES = {
    "gross": NodeMeasure("in and out", lambda t: t["in"] + t["out"]),
    "in": NodeMeasure("arriving", lambda t: t["in"]),
    "out": NodeMeasure("leaving", lambda t: t["out"]),
    "net": NodeMeasure("gained or lost (in minus out)", lambda t: abs(t["in"] - t["out"])),
}


def nodes_title(unit: str, flows: int, value: str = "gross") -> str:
    """The circles count every flow, before any cut, so the heading says so."""
    return f"Circle area: {unit} {NODE_VALUES[value].words}, across all {flows:,} flows"


def node_fill(net: float, colors: tuple | None) -> str:
    """With colors (gain, loss), a node that gains takes the first and one that loses the second; else the plain gray."""
    if colors is None or net == 0:
        return NODE_COLOR
    return colors[0] if net > 0 else colors[1]


def curvature_for(d: float, dmin: float, dmax: float) -> float:
    """Longer flows bend more (Jenny §4.1); every flow gets its own curvature, not one for all."""
    if dmax <= dmin:
        return (CURVE_MIN + CURVE_MAX) / 2
    return CURVE_MIN + (CURVE_MAX - CURVE_MIN) * (d - dmin) / (dmax - dmin)


def curve(a: list, b: list, side: int, c: float) -> list:
    """A quadratic Bézier on the sphere from a to b, bowed to the right of travel (side 1) or the left (-1).

    The control point is the great-circle midpoint moved c times the flow's arc length sideways.
    """
    va, vb = geo.vec(a), geo.vec(b)
    w = geo.angle(va, vb)
    if w < 1e-9:
        return [list(a), list(b)]
    n = geo.unit(geo.cross(va, vb))
    m = geo.slerp(va, vb, 0.5)
    h = c * w
    ctrl = geo.unit(tuple(m[i] * math.cos(h) - side * n[i] * math.sin(h) for i in range(3)))
    steps = math.ceil(math.degrees(w * (1 + c)) / DENSIFY_DEG)
    ts = sorted({round(t, 9) for t in [i / steps for i in range(steps + 1)] + turn_samples(c)})
    pts = [geo.lonlat(geo.slerp(geo.slerp(va, ctrl, t), geo.slerp(ctrl, vb, t), t)) for t in ts]
    pts[0], pts[-1] = list(a), list(b)
    return pts


def turn_samples(c: float) -> list:
    """Bézier parameters at equal steps of the tangent's angle, so no vertex turns more than about TURN_DEG.

    With the control point c times the chord off its middle, the tangent's angle is atan(2c(1 - 2t)), so
    equal steps of t would put the sharpest turns at the apex.
    """
    if c <= 0:
        return [0.0, 1.0]
    top = math.atan(2 * c)
    k = max(2, math.ceil(math.degrees(2 * top) / TURN_DEG))
    return [(1 - math.tan(top - 2 * top * i / k) / (2 * c)) / 2 for i in range(k + 1)]


def mercator(p: list) -> tuple:
    """Web Mercator at zoom 0 in 512 px tiles, as maplibre-gl draws a flat map."""
    lat = math.radians(max(-85.0511, min(85.0511, p[1])))
    return ((p[0] + 180) / 360 * TILE, (0.5 - math.log(math.tan(math.pi / 4 + lat / 2)) / (2 * math.pi)) * TILE)


def fit_scale(points: list, view: tuple, pad: float) -> float:
    """2 ** zoom at which fitBounds puts these points in a view of (width, height) CSS px, padded on every side."""
    xy = [mercator(p) for p in points]
    dx = max(x for x, _ in xy) - min(x for x, _ in xy)
    dy = max(y for _, y in xy) - min(y for _, y in xy)
    fits = [(size - 2 * pad) / span for size, span in zip(view, (dx, dy)) if span > 0]
    return min(fits) if fits else 1.0


@dataclass(frozen=True)
class ShareOfLength:
    """On a globe no one view holds, so a line keeps a share of its own length from each node it doesn't connect."""

    nodes: dict
    share: float = CLEARANCE_SHARE

    def gaps(self, coords: list, f: Flow) -> dict:
        """Each unconnected node nearer than the share asks, with its distance in km less that share."""
        threshold = self.share * geo.distance_km(self.nodes[f.o].pos, self.nodes[f.d].pos)
        ends = (self.nodes[f.o].pos, self.nodes[f.d].pos)
        vs = [geo.vec(c) for c in coords]
        mid = vs[len(vs) // 2]
        reach = max(geo.angle(mid, v) for v in (vs[0], vs[-1])) + threshold / geo.R_KM
        out = {}
        for nid, node in self.nodes.items():
            if nid in (f.o, f.d) or min(geo.distance_km(node.pos, e) for e in ends) <= threshold:
                continue
            v = geo.vec(node.pos)
            if geo.angle(v, mid) > reach * 1.5:
                continue
            dist = geo.point_polyline_angle(v, vs) * geo.R_KM
            if dist < threshold:
                out[nid] = dist - threshold
        return out


@dataclass(frozen=True)
class OnScreen:
    """At the view the page opens on, a line keeps CLEAR_PX between its edge and the circle of each node it doesn't
    connect. It is measured where the line shows: shifted by its offset, and outside the circles at its two ends."""

    nodes: dict
    scale: float
    radius: dict
    width: dict
    offset: dict

    def px(self, p: list) -> tuple:
        x, y = mercator(p)
        return x * self.scale, y * self.scale

    def gaps(self, coords: list, f: Flow) -> dict:
        """Each unconnected node whose circle comes within CLEAR_PX of the line, with the pixels between their edges."""
        half, shift = self.width[f] / 2, self.offset.get(f, 0)
        ends = [(self.px(self.nodes[k].pos), self.radius[k]) for k in (f.o, f.d)]
        segs = [s for a, b in zip(coords, coords[1:]) for s in visible(shifted(self.px(a), self.px(b), shift), ends)]
        if not segs:
            return {}
        reach = max(self.radius.values()) + half + CLEAR_PX
        xs = [x for s in segs for x, _ in s]
        ys = [y for s in segs for _, y in s]
        box = (min(xs) - reach, min(ys) - reach, max(xs) + reach, max(ys) + reach)
        out = {}
        for nid, node in self.nodes.items():
            if nid in (f.o, f.d):
                continue
            q = self.px(node.pos)
            if not (box[0] <= q[0] <= box[2] and box[1] <= q[1] <= box[3]):
                continue
            gap = min(point_segment(q, a, b) for a, b in segs) - self.radius[nid] - half
            if gap < CLEAR_PX:
                out[nid] = gap
        return out


def shifted(a: tuple, b: tuple, d: float) -> tuple:
    """The screen segment a-b moved d px to the right of travel, as line-offset moves it (y grows downward)."""
    if not d:
        return a, b
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    ox, oy = -dy / n * d, dx / n * d
    return (a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)


def visible(seg: tuple, circles: list) -> list:
    """The parts of a screen segment outside every (center, radius) circle, which draws over the line."""
    parts = [seg]
    for c, r in circles:
        parts = [q for s in parts for q in outside(s, c, r)]
    return parts


def outside(seg: tuple, c: tuple, r: float) -> list:
    (ax, ay), (bx, by) = seg
    dx, dy = bx - ax, by - ay
    fx, fy = ax - c[0], ay - c[1]
    qa, qb, qc = dx * dx + dy * dy, 2 * (fx * dx + fy * dy), fx * fx + fy * fy - r * r
    disc = qb * qb - 4 * qa * qc
    if qa == 0 or disc <= 0:
        return [seg] if qc > 0 else []
    root = math.sqrt(disc)
    t1, t2 = max(0.0, (-qb - root) / (2 * qa)), min(1.0, (-qb + root) / (2 * qa))
    if t1 >= t2:
        return [seg]
    at = lambda t: (ax + t * dx, ay + t * dy)
    return [s for s in ((seg[0], at(t1)) if t1 > 0 else None, (at(t2), seg[1]) if t2 < 1 else None) if s]


def point_segment(q: tuple, a: tuple, b: tuple) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = 0.0 if n == 0 else max(0.0, min(1.0, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n))
    return math.hypot(q[0] - a[0] - t * dx, q[1] - a[1] - t * dy)


def place(flows: list, nodes: dict, geometry: str, clearance=None) -> list:
    """Geometry for every flow, largest first; reciprocal flows always bow to opposite sides. A curve tries each
    candidate side and bend until one keeps its clearance, else keeps the one nearest to it."""
    clearance = clearance or ShareOfLength(nodes)
    kms = {f: geo.distance_km(nodes[f.o].pos, nodes[f.d].pos) for f in flows}
    dmin, dmax = min(kms.values(), default=0), max(kms.values(), default=0)
    pairs = {(f.o, f.d) for f in flows}
    chosen = {}
    out = []
    for f in sorted(flows, key=lambda f: (-f.value, f.o, f.d)):
        a, b = nodes[f.o].pos, nodes[f.d].pos
        reciprocal = (f.d, f.o) in pairs
        if geometry == "great-circle":
            options = [(1, GC_OFFSET)] if reciprocal else [(1, 0.0)]
        else:
            base = curvature_for(kms[f], dmin, dmax)
            partner = chosen.get((f.d, f.o))
            options = [(s, base * m) for s, m in CANDIDATES if partner is None or s == partner]
        best = None
        for s, c in options:
            coords = curve(a, b, s, c) if c else geo.densify_gc([a, b], DENSIFY_DEG)
            p = Placed(f, coords, kms[f], s, c, clearance.gaps(coords, f))
            if best is None or (len(p.near), -p.worst) < (len(best.near), -best.worst):
                best = p
            if p.clear:
                break
        chosen[(f.o, f.d)] = best.side
        out.append(best)
    return out


def place_in_view(flows: list, nodes: dict, view: tuple, radius: dict, width: dict, offset: dict) -> tuple:
    """Curves placed to clear nodes on screen at the view a page fits them to, with that view's 2 ** zoom.

    The page fits the curves as well as the nodes, and the curves bend to the fit, so a few rounds settle both;
    each round fits a smaller or equal scale, which only asks for more room.
    """
    pad = FIT_PAD + max(radius.values())
    points = [n.pos for n in nodes.values()]
    scale = fit_scale(points, view, pad)
    for _ in range(4):
        placed = place(flows, nodes, "curved", OnScreen(nodes, scale, radius, width, offset))
        fitted = fit_scale(points + [c for p in placed for c in p.coords], view, pad)
        if fitted >= scale * 0.999:
            break
        scale = fitted
    return placed, scale


def width(v: float, vmax: float, max_px: float, min_px: float) -> float:
    """Width linear in value (Jenny §4.2), floored so thin flows stay visible."""
    return max(min_px, max_px * v / vmax) if vmax > 0 else min_px


def opacity(v: float, vmin: float, vmax: float, fade_min: float) -> float:
    """Opacity linear in value, from fade_min at the smallest kept flow to 1 at the largest: larger flows
    darker (Jenny §4.2), faded by magnitude and never by length (Slocum §20.7.2.1)."""
    if fade_min >= 1 or vmax <= vmin:
        return 1.0
    return round(min(1.0, max(fade_min, fade_min + (1 - fade_min) * (v - vmin) / (vmax - vmin))), 3)


def arrow_size(w: float) -> float:
    """Arrowheads scale with width and grow on thin flows (Jenny §4.2, Figure 10)."""
    return max(ARROW_RATIO * w, ARROW_MIN_PX)


def side_offset(w: float) -> float:
    """Pixels a flow moves to the right of travel when its reverse is drawn too. A curve bows by a share of
    its length, so a short pair bows a pixel or two apart and draws as one line; this keeps a 1 px gap."""
    return round(w / 2 + 0.5, 2)


def legend_values(vmin: float, vmax: float, max_px: float, min_px: float) -> list:
    floor = max(vmin, vmax * min_px / max_px) if max_px else vmin
    return symbols.legend_values(floor, vmax, floor_share=0)


def node_totals(flows: list) -> dict:
    """In, out, gross, and net (in minus out) totals per node over every flow, before any top-N cut."""
    t = {}
    for f in flows:
        t.setdefault(f.o, {"in": 0.0, "out": 0.0})["out"] += f.value
        t.setdefault(f.d, {"in": 0.0, "out": 0.0})["in"] += f.value
    for v in t.values():
        v["gross"] = v["in"] + v["out"]
        v["net"] = v["in"] - v["out"]
    return t


def answers(flows: list, nodes: dict, totals: dict, n: int = 5) -> dict:
    by_pair = {(f.o, f.d): f.value for f in flows}
    ranked = sorted(flows, key=lambda f: (-f.value, f.o, f.d))

    def top(key: str) -> list:
        ids = sorted(totals, key=lambda i: (-totals[i][key], i))[:n]
        return [{"id": i, "name": nodes[i].label if i in nodes else i, "value": totals[i][key]} for i in ids if totals[i][key] > 0]

    asym = [
        {"o": f.o, "d": f.d, "value": f.value, "reverse": by_pair[(f.d, f.o)]}
        for f in ranked if (f.d, f.o) in by_pair and by_pair[(f.d, f.o)] < 0.5 * f.value
    ]
    return {
        "largest": [{"o": f.o, "d": f.d, "value": f.value} for f in ranked[:n]],
        "top_origins": top("out"),
        "top_destinations": top("in"),
        "asymmetric_pairs": asym[:10],
    }
