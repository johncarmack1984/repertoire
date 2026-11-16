"""Classing: methods, goodness of fit (GVF, GADF), skew, automatic method and class count, and rounded breaks.

A break is the lower limit of the class above it: class i holds inner[i-1] <= v < inner[i].
Values are compared at the legend's display precision, so a value always lands in the class its label names.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

SAMPLE_CAP = 3000
GADF_TARGET = 0.80
MIN_K = 3
HEAD_SHARE = 0.40


def mean(xs: list) -> float:
    return sum(xs) / len(xs)


def median(xs_sorted: list) -> float:
    n = len(xs_sorted)
    mid = n // 2
    return xs_sorted[mid] if n % 2 else (xs_sorted[mid - 1] + xs_sorted[mid]) / 2


def skewness(xs: list) -> float:
    """The moment coefficient of skewness, g1 = m3 / m2^1.5."""
    m = mean(xs)
    m2 = sum((x - m) ** 2 for x in xs) / len(xs)
    if m2 == 0:
        return 0.0
    return (sum((x - m) ** 3 for x in xs) / len(xs)) / m2 ** 1.5


def sample(xs_sorted: list, cap: int = SAMPLE_CAP) -> list:
    """Evenly spaced order statistics, so a large set keeps its distribution and the result never varies."""
    n = len(xs_sorted)
    if n <= cap:
        return xs_sorted
    return [xs_sorted[round(i * (n - 1) / (cap - 1))] for i in range(cap)]


def _increasing(breaks: list, floor: float) -> list:
    out = []
    for b in breaks:
        if b > floor and (not out or b > out[-1]):
            out.append(b)
    return out


def equal_breaks(xs: list, k: int) -> list:
    lo, hi = xs[0], xs[-1]
    return _increasing([lo + i * (hi - lo) / k for i in range(1, k)], lo)


def quantile_breaks(xs: list, k: int) -> list:
    """n/k values per class, the remainder to the first classes; tied values move up together (Slocum §5.5)."""
    n = len(xs)
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    cuts, pos = [], 0
    for size in sizes[:-1]:
        pos += size
        if pos < n:
            cuts.append(xs[pos])
    return _increasing(cuts, xs[0])


def jenks_breaks(xs: list, k: int) -> list:
    """Exact Fisher-Jenks: the partition with the least squared deviation about class means.

    A dynamic program over prefix sums, with the divide-and-conquer row fill of Ckmeans.1d.dp,
    which holds because the best start of the last class never moves left as the prefix grows.
    """
    xs = sample(xs)
    n = len(xs)
    k = min(k, len(set(xs)))
    if k <= 1:
        return []
    s1, s2 = [0.0], [0.0]
    for x in xs:
        s1.append(s1[-1] + x)
        s2.append(s2[-1] + x * x)

    def ssd(i: int, j: int) -> float:
        s = s1[j + 1] - s1[i]
        return (s2[j + 1] - s2[i]) - s * s / (j - i + 1)

    cost = [ssd(0, j) for j in range(n)]
    back = [[0] * n for _ in range(k)]
    for m in range(1, k):
        row = [math.inf] * n

        def fill(lo: int, hi: int, optlo: int, opthi: int) -> None:
            if lo > hi:
                return
            mid = (lo + hi) // 2
            best, bestj = math.inf, max(optlo, m)
            for j in range(max(optlo, m), min(mid, opthi) + 1):
                c = cost[j - 1] + ssd(j, mid)
                if c < best:
                    best, bestj = c, j
            row[mid], back[m][mid] = best, bestj
            fill(lo, mid - 1, optlo, bestj)
            fill(mid + 1, hi, bestj, opthi)

        fill(m, n - 1, m, n - 1)
        cost = row
    starts, j = [], n - 1
    for m in range(k - 1, 0, -1):
        starts.append(back[m][j])
        j = back[m][j] - 1
    return _increasing([xs[s] for s in reversed(starts)], xs[0])


def stddev_offsets(k: int) -> list:
    """Breaks in standard deviations from the center: one at the center for even k; odd k centers the middle class."""
    if k % 2 == 0:
        return list(range(-(k // 2 - 1), k // 2))
    h = (k - 1) // 2
    return [j for j in range(-h, h + 1) if j != 0]


def stddev_breaks(xs: list, k: int, center: float | None = None) -> list:
    m = mean(xs) if center is None else center
    s = math.sqrt(sum((x - mean(xs)) ** 2 for x in xs) / (len(xs) - 1)) if len(xs) > 1 else 0.0
    return [m + o * s for o in stddev_offsets(k)]


def headtail_breaks(xs: list, k: int) -> list:
    """Split at the mean and recurse on the head while it holds under 40% of the values (Jiang; Slocum §5.9)."""
    out, cur = [], xs
    while len(out) < k - 1:
        m = mean(cur)
        head = [x for x in cur if x > m]
        if not head or len(head) / len(cur) >= HEAD_SHARE:
            break
        out.append(head[0])
        if len(head) == 1:
            break
        cur = head
    return out


METHODS = {
    "quantile": quantile_breaks,
    "equal": equal_breaks,
    "jenks": jenks_breaks,
    "stddev": stddev_breaks,
    "headtail": headtail_breaks,
}


def assign(v: float, inner: list) -> int:
    return bisect_right(inner, v)


def groups(xs: list, inner: list) -> list:
    out = [[] for _ in range(len(inner) + 1)]
    for x in xs:
        out[assign(x, inner)].append(x)
    return out


def gvf(xs: list, inner: list) -> float:
    """1 - SDCM/SDAM: squared deviations about class means against those about the mean of all."""
    m = mean(xs)
    sdam = sum((x - m) ** 2 for x in xs)
    if sdam == 0:
        return 1.0
    sdcm = sum(sum((x - mean(g)) ** 2 for x in g) for g in groups(xs, inner) if g)
    return 1 - sdcm / sdam


def gadf(xs: list, inner: list) -> float:
    """1 - ADCM/ADAM. Slocum §5.8.3 prints ADCM/ADAM, which contradicts its own 0-for-one-class reading."""
    xs = sorted(xs)
    md = median(xs)
    adam = sum(abs(x - md) for x in xs)
    if adam == 0:
        return 1.0
    adcm = 0.0
    for g in groups(xs, inner):
        if g:
            gm = median(g)
            adcm += sum(abs(x - gm) for x in g)
    return 1 - adcm / adam


# Rounding to meaningful values.

def _exp(x: float, sig: int) -> int:
    return math.floor(math.log10(abs(x))) - sig + 1 if x else 0


def round_to(x: float, e: int, rounding: str = ROUND_HALF_UP) -> float:
    return float(Decimal(repr(x)).quantize(Decimal(1).scaleb(e), rounding=rounding))


def fmt(v: float, e: int) -> str:
    """A limit at precision 10^e, with thousands separators and no trailing zeros."""
    s = f"{v:,.{max(0, -e)}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


@dataclass
class Classing:
    method: str
    inner: list
    e: int
    lo: float
    hi: float
    slots: list
    palette_k: int
    reason: str = ""
    notes: list = field(default_factory=list)

    @property
    def k(self) -> int:
        return len(self.inner) + 1

    @property
    def breaks(self) -> list:
        return [self.lo] + list(self.inner) + [self.hi]

    def index(self, v: float) -> int:
        return assign(round_to(v, self.e), self.inner)

    def counts(self, xs: list) -> list:
        out = [0] * self.k
        for x in xs:
            out[self.index(x)] += 1
        return out

    def labels(self) -> list:
        lims = self.breaks
        step = Decimal(1).scaleb(self.e)
        out = []
        for i in range(self.k):
            lo = lims[i]
            hi = lims[i + 1] if i == self.k - 1 else float(Decimal(repr(lims[i + 1])) - step)
            out.append(fmt(lo, self.e) if lo == hi else f"{fmt(lo, self.e)} to {fmt(hi, self.e)}")
        return out

    def fit(self, xs: list) -> tuple:
        rounded = [round_to(x, self.e) for x in xs]
        return gvf(rounded, self.inner), gadf(rounded, self.inner)


def precision_floor(xs: list) -> int | None:
    """Integer data never gets fractional limits."""
    return 0 if all(float(x).is_integer() for x in xs) else None


def nice(inner: list, xs: list, pinned: frozenset = frozenset()) -> tuple:
    """Rounds inner breaks to the fewest significant figures (two at least) that keep them increasing and empty no class."""
    e_min = precision_floor(xs)
    lo, hi = xs[0], xs[-1]
    populated = [len(g) > 0 for g in groups(xs, inner)]
    span_e = _exp(hi - lo, 2) if hi > lo else _exp(hi, 2)
    for sig in range(2, 8):
        rounded, es = [], []
        for b in inner:
            if b in pinned:
                rounded.append(b)
                continue
            e = _exp(b, sig) if b else span_e
            if e_min is not None:
                e = max(e, e_min)
            rounded.append(round_to(b, e))
            es.append(e)
        e = min(es) if es else (max(span_e, e_min) if e_min is not None else span_e)
        e = min([e] + [Decimal(repr(b)).normalize().as_tuple().exponent for b in pinned if b in rounded])
        ok = all(a < b for a, b in zip(rounded, rounded[1:]))
        counts = Classing("", rounded, e, lo, hi, [], 0).counts(xs)
        ok = ok and all(c > 0 for c, was in zip(counts, populated) if was)
        if ok:
            return rounded, e
    return list(inner), min([_exp(b, 7) for b in inner if b] or [span_e])


def finish(method: str, raw_inner: list, xs: list, slots: list | None = None, palette_k: int | None = None,
           pinned: frozenset = frozenset(), round_breaks: bool = True) -> Classing:
    xs = sorted(xs)
    inner = [b for b in raw_inner if xs[0] < b <= xs[-1] or b in pinned]
    dropped = len(raw_inner) - len(inner)
    if round_breaks:
        inner, e = nice(inner, xs, pinned)
    else:
        e = min([_exp(b, 3) for b in inner if b] or [0])
        if precision_floor(xs) is not None:
            e = max(e, 0)
    k = len(inner) + 1
    if slots is None:
        slots = list(range(k))
        palette_k = k
    c = Classing(method, inner, e, round_to(xs[0], e), round_to(xs[-1], e), slots, palette_k)
    if dropped:
        c.notes.append(f"{dropped} break(s) fell outside the data and were dropped")
    return c


def stddev_classing(xs: list, k: int, center: float | None) -> Classing:
    """Mean-standard deviation classes, keeping each class's place on the k-class ramp when outer breaks fall outside the data."""
    xs = sorted(xs)
    raw = stddev_breaks(xs, k, center)
    first = sum(1 for b in raw if b <= xs[0])
    kept = [b for b in raw if xs[0] < b <= xs[-1]]
    slots = list(range(first, first + len(kept) + 1))
    pinned = frozenset([center]) if center is not None and center in raw else frozenset()
    return finish("stddev", raw, xs, slots, k, pinned)


def method_classing(method: str, xs: list, k: int, center: float | None = None) -> Classing:
    xs = sorted(xs)
    if method == "stddev":
        return stddev_classing(xs, k, center)
    return finish(method, METHODS[method](xs, k), xs)


def diverging_classing(method: str, xs: list, k_side: int, mid: float) -> Classing:
    """Classes each side of the midpoint on its own (Slocum §5.3), with the midpoint as a fixed break."""
    xs = sorted(xs)
    below = [x for x in xs if x < mid]
    above = [x for x in xs if x >= mid]
    lo_inner = METHODS[method](below, min(k_side, len(set(below)))) if below else []
    hi_inner = METHODS[method](above, min(k_side, len(set(above)))) if above else []
    m_lo, m_hi = len(lo_inner) + 1, len(hi_inner) + 1
    slots = list(range(k_side - m_lo, k_side)) + list(range(k_side, k_side + m_hi))
    return finish(method, lo_inner + [mid] + hi_inner, xs, slots, 2 * k_side, frozenset([mid]))


def candidates(xs: list, k: int) -> list:
    """GVF and GADF for each method at k, for the legend's record."""
    out = []
    for name in ("quantile", "equal", "jenks", "stddev", "headtail"):
        c = method_classing(name, xs, k)
        g, a = c.fit(xs)
        out.append({"method": name, "k": c.k, "gvf": round(g, 3), "gadf": round(a, 3)})
    return out


def auto_method(xs: list, *, ordinal: bool, compared: bool, center_is_mean: bool) -> tuple:
    if ordinal:
        return "quantile", "ordinal data; quantiles is the only method fit for ranks (Slocum §5.13)"
    if compared:
        return "quantile", "a compared or bivariate map; quantiles keep the maps comparable, Jenks hides correlation (Slocum ch. 21)"
    g1 = skewness(xs)
    if abs(g1) > 1:
        return "jenks", f"skewness {g1:.2f}; Jenks optimal groups like values on a skewed distribution (Slocum §5.8)"
    if center_is_mean:
        return "stddev", f"skewness {g1:.2f}, near normal, with the mean as the midpoint (Slocum §5.6)"
    return "equal", f"skewness {g1:.2f}, near normal; equal intervals give round, readable limits (Slocum §5.4)"


def auto_k(build, xs: list, max_k: int, lo_k: int = MIN_K) -> tuple:
    """The smallest k whose GADF reaches 0.80, from lo_k up to max_k (Slocum §5.8.3)."""
    last = None
    for k in range(lo_k, max_k + 1):
        c = build(k)
        a = gadf(xs, c.inner)
        last = (c, k, a)
        if a >= GADF_TARGET:
            return c, f"k = {c.k}, the smallest class count whose GADF reaches {GADF_TARGET:.2f} ({a:.2f})"
    c, k, a = last
    return c, f"k = {c.k}, the most this ramp allows; GADF {a:.2f} stays under {GADF_TARGET:.2f}"
