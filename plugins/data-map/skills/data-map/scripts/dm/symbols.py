"""Proportional symbols (Slocum ch. 17): radii true to area, perceptual and range-graded radii, nested legend values."""

from __future__ import annotations

import math

FLANNERY = 0.5716
# Dent's five smallest range-graded circle radii, in inches (Slocum §17.5.3, note 3): K classes take the K largest.
DENT = [0.025, 0.045, 0.065, 0.110, 0.170]


def scaling_name(spec: str) -> tuple:
    """Parses area, flannery, or graduated:K into (kind, K)."""
    if spec in ("area", "flannery"):
        return spec, None
    if spec.startswith("graduated:"):
        k = int(spec.split(":", 1)[1])
        if not 3 <= k <= 5:
            raise ValueError("graduated takes 3 to 5 sizes")
        return "graduated", k
    raise ValueError(f"unknown scaling {spec}; use area, flannery, or graduated:K")


def radius(v: float, vmax: float, rmax: float, kind: str = "area") -> float:
    """r = rmax * (v / vmax) ** 0.5 makes area proportional to value; Flannery's 0.5716 offsets underestimation."""
    if v <= 0 or vmax <= 0:
        return 0.0
    exponent = FLANNERY if kind == "flannery" else 0.5
    return rmax * (v / vmax) ** exponent


def graded_radii(k: int, rmax: float) -> list:
    sizes = DENT[-k:]
    return [rmax * s / sizes[-1] for s in sizes]


def nice_floor(x: float) -> float:
    """The largest number with one significant digit that does not exceed x."""
    e = 10 ** math.floor(math.log10(x))
    return math.floor(x / e) * e


def nice_round(x: float) -> float:
    """The nearest of 1, 2, 2.5, 5 times a power of ten, by ratio."""
    e = 10 ** math.floor(math.log10(x))
    options = [m * e for m in (1, 2, 2.5, 5, 10)]
    return min(options, key=lambda o: abs(math.log(o / x)))


def legend_values(vmin: float, vmax: float, floor_share: float = 0.05) -> list:
    """Three round values spanning the data, largest first, for a nested legend (Slocum §17.6.2)."""
    hi = nice_floor(vmax)
    lo = nice_round(max(vmin, hi * floor_share))
    lo = min(lo, hi)
    mid = nice_round(math.sqrt(hi * lo))
    out = []
    for v in (hi, mid, lo):
        v = float(f"{v:.6g}")
        if v not in out:
            out.append(v)
    return out


def order_largest_first(values: list) -> list:
    """Draw order: the largest symbol gets 0 and draws first, so small symbols sit on top."""
    ranked = sorted(range(len(values)), key=lambda i: (-(values[i] if values[i] is not None else -math.inf), i))
    order = [0] * len(values)
    for rank, i in enumerate(ranked):
        order[i] = rank
    return order
