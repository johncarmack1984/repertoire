"""Classing: methods, goodness of fit (GVF, GADF), skew, automatic method and class count, and rounded breaks.

A break is the lower limit of the class above it: class i holds inner[i-1] <= v < inner[i].
Values are compared at the legend's display precision, so a value always lands in the class its label names.
"""

from __future__ import annotations

import math
from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal

SAMPLE_CAP = 3000
GADF_TARGET = 0.80
MIN_K = 3
HEAD_SHARE = 0.40
# One class holding more than this share of the units spreads one color over much of the map, and a pale lowest class
# that size reads as none. A third is the even share at the fewest classes (3), so only a class well past it trips this.
SWALLOW_SHARE = 0.40
# Positive values spanning this many orders of magnitude make geometric breaks a candidate (Slocum §5.12).
SPAN_DECADES = 2.0
# Readable break values: a mantissa times a power of ten. A geometric progression climbs a whole number of rungs per
# class, so its ratio is about 2 (one rung), 4 to 5 (two), or 10 (three). 2.5 adds a decimal to every label, so its
# ladder serves only when the first can't fill every class.
LADDERS = ((1, 2, 5), (1, 2.5, 5))
RATIO_WORDS = {1: "2 to 2.5", 2: "4 to 5", 3: "10"}
# The top geometric class holds as few units as it can, so the darkest color isolates the highest values, but two at
# least: a top break just under the maximum leaves a class of one outlier, often a tiny place with an unstable rate.
TOP_MIN = 2


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
    """Rounds inner breaks to the fewest significant figures (two at least) that keep every value in its class.

    A break rounds to the nearest value at that precision, or else down or up, whichever stays in the gap
    between the classes it separates, so a class's lowest member never drops a class.
    """
    e_min = precision_floor(xs)
    lo, hi = xs[0], xs[-1]
    members = [assign(x, inner) for x in xs]
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
            i = bisect_left(xs, b)
            below, above = xs[i - 1] if i else -math.inf, xs[i] if i < len(xs) else math.inf
            options = [round_to(b, e, mode) for mode in (ROUND_HALF_UP, ROUND_FLOOR, ROUND_CEILING)]
            rounded.append(next((r for r in options if below < r <= above), options[0]))
            es.append(e)
        e = min(es) if es else (max(span_e, e_min) if e_min is not None else span_e)
        e = min([e] + [Decimal(repr(b)).normalize().as_tuple().exponent for b in pinned if b in rounded])
        c = Classing("", rounded, e, lo, hi, [], 0)
        if all(a < b for a, b in zip(rounded, rounded[1:])) and all(c.index(x) == m for x, m in zip(xs, members)):
            return rounded, e
    return list(inner), min([_exp(b, 7) for b in inner if b] or [span_e])


def own_precision(inner: list) -> int:
    """The precision of breaks that aren't rounded, as geometric and hand-set ones: their own, with two significant
    figures at the smallest at least, as nice() keeps. Values are classed as they're shown, and at a break of 2's own
    precision a value of 1.6 would show as 2 and fill the class above it."""
    nonzero = [abs(b) for b in inner if b]
    return min([0] + [Decimal(repr(b)).normalize().as_tuple().exponent for b in inner] + ([_exp(min(nonzero), 2)] if nonzero else []))


def finish(method: str, raw_inner: list, xs: list, slots: list | None = None, palette_k: int | None = None,
           pinned: frozenset = frozenset(), round_breaks: bool = True) -> Classing:
    xs = sorted(xs)
    inner = [b for b in raw_inner if xs[0] < b <= xs[-1] or b in pinned]
    dropped = len(raw_inner) - len(inner)
    if round_breaks:
        inner, e = nice(inner, xs, pinned)
    else:
        e = own_precision(inner)
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


def decades(xs: list) -> float | None:
    """Orders of magnitude the positive values span; None when a value is negative or fewer than two positive values differ."""
    pos = [x for x in xs if x > 0]
    if min(xs) < 0 or len(set(pos)) < 2:
        return None
    return math.log10(max(pos) / min(pos))


def rung(ladder: tuple, j: int) -> float:
    """The ladder's j-th readable value, with 1 at j = 0: 0.5, 1, 2, 5, 10 on the first ladder for j = -1 to 3."""
    return float(Decimal(repr(ladder[j % 3])).scaleb(j // 3))


def geometric_steps(d: float, k: int) -> int:
    """Rungs per class that spread d decades over k classes, from one to three."""
    return max(1, min(3, int(3 * d / k + 0.5)))


def geometric_breaks(xs: list, k: int) -> list:
    """Breaks that climb the same number of rungs per class. Of the placements that leave every class a value and none
    more than SWALLOW_SHARE of them, the one whose top class holds the fewest, TOP_MIN at least; when none qualifies,
    the one whose wider end class spans the fewest decades. Empty when no placement fills k classes."""
    pos = [x for x in xs if x > 0]
    lo, hi = pos[0], pos[-1]
    s = geometric_steps(math.log10(hi / lo), k)
    first, last = math.floor(3 * math.log10(lo)) - 3, math.ceil(3 * math.log10(hi)) + 3
    for ladder in LADDERS:
        best = None
        for j in range(first, last):
            inner = [rung(ladder, j + i * s) for i in range(k - 1)]
            sizes = [len(g) for g in groups(xs, inner)]
            if 0 in sizes:
                continue
            top = sizes[-1] if sizes[-1] >= TOP_MIN and max(sizes) <= SWALLOW_SHARE * len(xs) else math.inf
            key = (top, max(math.log10(inner[0] / lo), math.log10(hi / inner[-1])), sum(n * n for n in sizes))
            if best is None or key < best[0]:
                best = (key, inner)
        if best:
            return best[1]
    return []


def geometric_classing(xs: list, k: int) -> Classing:
    """Geometric breaks for k classes, or the most under k that leave every class a value, labeled at own_precision."""
    xs = sorted(xs)
    m, inner = k, []
    while m > 1 and not inner:
        inner = geometric_breaks(xs, m)
        m -= 0 if inner else 1
    e = own_precision(inner)
    if precision_floor(xs) is not None:
        e = max(e, 0)
    c = Classing("geometric", inner, e, round_to(xs[0], e), round_to(xs[-1], e), list(range(m)), m)
    if m < k:
        c.notes.append(f"no geometric placement of {k} classes leaves every class a value, so {m} classes")
    return c


def geometric_auto(xs: list, max_k: int) -> tuple:
    """The finest ratio whose classes cover the positive values' span in at most max_k classes."""
    d = decades(xs)
    k = next((m for m in (max(MIN_K, int(3 * d / s + 0.5)) for s in (1, 2, 3)) if m <= max_k), max_k)
    c = geometric_classing(xs, k)
    return c, (f"k = {c.k}: the positive values span {d:.1f} orders of magnitude, and breaks rising by a ratio of "
               f"{RATIO_WORDS[geometric_steps(d, c.k)]} per class cover them in {c.k} classes")


def method_classing(method: str, xs: list, k: int, center: float | None = None) -> Classing:
    xs = sorted(xs)
    if method == "stddev":
        return stddev_classing(xs, k, center)
    if method == "geometric":
        return geometric_classing(xs, k)
    return finish(method, METHODS[method](xs, k), xs)


def largest(c: Classing, xs: list) -> tuple:
    """The class holding the most values, as (index, count, share)."""
    counts = c.counts(xs)
    i = max(range(len(counts)), key=counts.__getitem__)
    return i, counts[i], counts[i] / len(xs)


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
    """GVF, GADF, and the largest class's share for each method at k, for the legend's record."""
    out = []
    names = ("quantile", "equal", "jenks", "stddev", "headtail") + (("geometric",) if decades(xs) is not None else ())
    for name in names:
        c = method_classing(name, xs, k)
        g, a = c.fit(xs)
        out.append({"method": name, "k": c.k, "gvf": round(g, 3), "gadf": round(a, 3), "largest": round(largest(c, xs)[2], 3)})
    return out


def auto_method(xs: list, *, ordinal: bool, compared: bool, center_is_mean: bool, max_k: int = 7, sequential: bool = True) -> tuple:
    if ordinal:
        return "quantile", "ordinal data; quantiles is the only method fit for ranks (Slocum §5.13)"
    if compared:
        return "quantile", "a compared or bivariate map; quantiles keep the maps comparable, Jenks hides correlation (Slocum ch. 21)"
    g1 = skewness(xs)
    d = decades(xs) if sequential and g1 > 1 else None
    if d is not None and d >= SPAN_DECADES:
        return jenks_or_geometric(xs, g1, d, max_k)
    if abs(g1) > 1:
        return "jenks", f"skewness {g1:.2f}; Jenks optimal groups like values on a skewed distribution (Slocum §5.8)"
    if center_is_mean:
        return "stddev", f"skewness {g1:.2f}, near normal, with the mean as the midpoint (Slocum §5.6)"
    return "equal", f"skewness {g1:.2f}, near normal; equal intervals give round, readable limits (Slocum §5.4)"


def jenks_or_geometric(xs: list, g1: float, d: float, max_k: int) -> tuple:
    """Skewed data spanning orders of magnitude: Jenks unless its largest class swallows the map and geometric breaks
    hold fewer in theirs."""
    jn, js = largest(auto_k(lambda k: method_classing("jenks", xs, k), xs, max_k)[0], xs)[1:]
    gn, gs = largest(geometric_auto(xs, max_k)[0], xs)[1:]
    span = f"skewness {g1:.2f}, with positive values spanning {d:.1f} orders of magnitude"
    held = f"Jenks would put {jn} of {len(xs)} places ({js:.0%}) in one class, geometric breaks at most {gn} ({gs:.0%})"
    if js > SWALLOW_SHARE and gs < js:
        return "geometric", f"{span}; {held}, so breaks in a constant ratio (Slocum §5.12)"
    if js > SWALLOW_SHARE:
        return "jenks", f"{span}; {held}, so Jenks optimal stands (Slocum §5.8)"
    return "jenks", f"{span}; Jenks optimal groups like values and holds at most {jn} of {len(xs)} ({js:.0%}) in a class (Slocum §5.8)"


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
