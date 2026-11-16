"""Origin-destination flows (Jenny et al. 2018; Slocum ch. 20; Yang et al. 2019): filtering, geometry, widths, arrows, nodes.

Curves are quadratic Béziers on the sphere: the control point sits off the great-circle midpoint, to the
right of travel, so A to B and B to A bow apart. Flows are placed largest first, and a curve that passes
too near a node it does not connect flips side, then bends more.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import geo, symbols

CURVE_MIN, CURVE_MAX = 0.12, 0.30
GC_OFFSET = 0.05
CLEARANCE_SHARE = 0.04
DENSIFY_DEG = 1.0
ARROW_RATIO, ARROW_MIN_PX = 2.5, 6.0
NODE_RMAX = 10.0
HEIGHT_SHARE = 0.25
FLOW_COLOR = "#08519c"
NODE_COLOR = "#525252"
HAIRBALL = {"curved": 100, "great-circle": 300}
CANDIDATES = [(1, 1.0), (-1, 1.0), (1, 1.5), (-1, 1.5), (1, 2.0), (-1, 2.0)]


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
    clearance_km: float
    threshold_km: float
    near: list = field(default_factory=list)

    @property
    def clear(self) -> bool:
        return not self.near


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
        return f"All {total} flows"
    return f"The {kept} largest of {total} flows, {share:.0%} of all {unit}"


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
    steps = max(8, math.ceil(math.degrees(w * (1 + c)) / DENSIFY_DEG))
    pts = [geo.lonlat(geo.slerp(geo.slerp(va, ctrl, t), geo.slerp(ctrl, vb, t), t)) for t in (i / steps for i in range(steps + 1))]
    pts[0], pts[-1] = list(a), list(b)
    return pts


def side_of(p: list, a: list, b: list) -> int:
    """1 when p lies to the right of travel from a to b, -1 to the left."""
    n = geo.cross(geo.vec(a), geo.vec(b))
    return -1 if geo.dot(geo.vec(p), n) > 0 else 1


def nodes_too_near(coords: list, f: Flow, nodes: dict, threshold_km: float) -> tuple:
    """Unconnected nodes within the threshold of the line, and the line's clearance from all of them."""
    near, clearance = [], math.inf
    ends = (nodes[f.o].pos, nodes[f.d].pos)
    vs = [geo.vec(c) for c in coords]
    mid = vs[len(vs) // 2]
    reach = max(geo.angle(mid, v) for v in (vs[0], vs[-1])) + threshold_km / geo.R_KM
    for nid, node in nodes.items():
        if nid in (f.o, f.d) or min(geo.distance_km(node.pos, e) for e in ends) <= threshold_km:
            continue
        v = geo.vec(node.pos)
        if geo.angle(v, mid) > reach * 1.5:
            continue
        dist = geo.point_polyline_angle(v, vs) * geo.R_KM
        clearance = min(clearance, dist)
        if dist < threshold_km:
            near.append(nid)
    return sorted(near), clearance


def place(flows: list, nodes: dict, geometry: str) -> list:
    """Geometry for every flow, largest first; reciprocal flows always bow to opposite sides."""
    kms = {f: geo.distance_km(nodes[f.o].pos, nodes[f.d].pos) for f in flows}
    dmin, dmax = min(kms.values(), default=0), max(kms.values(), default=0)
    pairs = {(f.o, f.d) for f in flows}
    chosen = {}
    out = []
    for f in sorted(flows, key=lambda f: (-f.value, f.o, f.d)):
        a, b = nodes[f.o].pos, nodes[f.d].pos
        km = kms[f]
        threshold = CLEARANCE_SHARE * km
        reciprocal = (f.d, f.o) in pairs
        if geometry == "great-circle":
            options = [(1, GC_OFFSET)] if reciprocal else [(1, 0.0)]
        else:
            base = curvature_for(km, dmin, dmax)
            partner = chosen.get((f.d, f.o))
            options = [(s, base * m) for s, m in CANDIDATES if partner is None or s == partner]
        best = None
        for s, c in options:
            coords = curve(a, b, s, c) if c else geo.densify_gc([a, b], DENSIFY_DEG)
            near, clearance = nodes_too_near(coords, f, nodes, threshold)
            p = Placed(f, coords, km, s, c, clearance, threshold, near)
            if best is None or (len(near), -clearance) < (len(best.near), -best.clearance_km):
                best = p
            if not near:
                break
        chosen[(f.o, f.d)] = best.side
        out.append(best)
    return out


def width(v: float, vmax: float, max_px: float, min_px: float) -> float:
    """Width linear in value (Jenny §4.2), floored so thin flows stay visible."""
    return max(min_px, max_px * v / vmax) if vmax > 0 else min_px


def arrow_size(w: float) -> float:
    """Arrowheads scale with width and grow on thin flows (Jenny §4.2, Figure 10)."""
    return max(ARROW_RATIO * w, ARROW_MIN_PX)


def height_m(km: float) -> float:
    """Raised-arc apex tied to length alone, never to value (Yang et al. 2019, §4.3)."""
    return HEIGHT_SHARE * km * 1000


def legend_values(vmin: float, vmax: float, max_px: float, min_px: float) -> list:
    floor = max(vmin, vmax * min_px / max_px) if max_px else vmin
    return symbols.legend_values(floor, vmax, floor_share=0)


def node_totals(flows: list) -> dict:
    """In, out, and gross totals per node over every flow, before any top-N cut."""
    t = {}
    for f in flows:
        t.setdefault(f.o, {"in": 0.0, "out": 0.0})["out"] += f.value
        t.setdefault(f.d, {"in": 0.0, "out": 0.0})["in"] += f.value
    for v in t.values():
        v["gross"] = v["in"] + v["out"]
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
