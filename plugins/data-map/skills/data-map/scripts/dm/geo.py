"""Sphere geometry: distance, slerp, bearings, densifying, antimeridian splits, graticule, sphere outline, point-to-line distance.

Points are [lon, lat] in degrees; vectors are unit (x, y, z) with x toward lon 0 and z toward the north pole.
"""

from __future__ import annotations

import math

R_KM = 6371.0088


def vec(p: list) -> tuple:
    lon, lat = math.radians(p[0]), math.radians(p[1])
    return (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))


def lonlat(v: tuple) -> list:
    x, y, z = v
    return [math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.hypot(x, y)))]


def dot(a: tuple, b: tuple) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: tuple, b: tuple) -> tuple:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a: tuple) -> tuple:
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def angle(a: tuple, b: tuple) -> float:
    """The angle between two unit vectors, in radians, stable for tiny and near-antipodal angles."""
    return math.atan2(math.sqrt(dot(cross(a, b), cross(a, b))), dot(a, b))


def distance_km(p: list, q: list) -> float:
    return angle(vec(p), vec(q)) * R_KM


def slerp(a: tuple, b: tuple, t: float) -> tuple:
    w = angle(a, b)
    if w < 1e-12:
        return a
    s = math.sin(w)
    fa, fb = math.sin((1 - t) * w) / s, math.sin(t * w) / s
    return unit((fa * a[0] + fb * b[0], fa * a[1] + fb * b[1], fa * a[2] + fb * b[2]))


def bearing(p: list, q: list) -> float:
    """Initial bearing from p toward q, in degrees clockwise from north, in [0, 360)."""
    lon1, lat1, lon2, lat2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    dl = lon2 - lon1
    y = math.sin(dl) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360


def end_bearing(line: list) -> float:
    """The direction of travel at a line's last vertex."""
    return (bearing(line[-1], line[-2]) + 180) % 360


def densify_gc(coords: list, max_deg: float) -> list:
    """Adds great-circle vertices so no segment spans more than max_deg of arc."""
    out = [list(coords[0])]
    for p, q in zip(coords, coords[1:]):
        a, b = vec(p), vec(q)
        n = max(1, math.ceil(math.degrees(angle(a, b)) / max_deg))
        out.extend(lonlat(slerp(a, b, i / n)) for i in range(1, n))
        out.append(list(q))
    return out


def densify_planar(coords: list, max_km: float) -> list:
    """Adds vertices along each edge as drawn in longitude and latitude, as boundary data means it, every max_km at most."""
    out = [list(coords[0])]
    for p, q in zip(coords, coords[1:]):
        if abs(q[0] - p[0]) <= 180:
            n = max(1, math.ceil(distance_km(p, q) / max_km))
            out.extend([p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n] for i in range(1, n))
        out.append(list(q))
    return out


def _crossing_lat(p: list, q: list) -> float:
    """Where the great circle through p and q meets the 180th meridian."""
    n = cross(vec(p), vec(q))
    d = unit((-n[2], 0.0, n[0]))
    if d[0] > 0:
        d = (-d[0], 0.0, -d[2])
    return math.degrees(math.asin(max(-1.0, min(1.0, d[2]))))


def split_antimeridian(coords: list) -> list:
    """Cuts a line into parts at +/-180, each crossing ending and starting on a vertex at exactly +/-180."""
    parts, cur = [], [list(coords[0])]
    for p, q in zip(coords, coords[1:]):
        if abs(q[0] - p[0]) > 180:
            side = 180.0 if p[0] > 0 else -180.0
            lat = _crossing_lat(p, q)
            cur.append([side, lat])
            parts.append(cur)
            cur = [[-side, lat]]
        cur.append(list(q))
    parts.append(cur)
    return [part for part in parts if len(part) > 1]


def line_geometry(coords: list) -> dict:
    parts = split_antimeridian(coords)
    if len(parts) == 1:
        return {"type": "LineString", "coordinates": parts[0]}
    return {"type": "MultiLineString", "coordinates": parts}


def point_segment_angle(p: tuple, a: tuple, b: tuple) -> float:
    """The angle from point p to the great-circle segment a-b."""
    n = cross(a, b)
    if dot(n, n) < 1e-24:
        return angle(p, a)
    n = unit(n)
    foot = (p[0] - dot(p, n) * n[0], p[1] - dot(p, n) * n[1], p[2] - dot(p, n) * n[2])
    if dot(foot, foot) > 1e-24:
        foot = unit(foot)
        if abs(angle(a, foot) + angle(foot, b) - angle(a, b)) < 1e-9:
            return abs(math.asin(max(-1.0, min(1.0, dot(p, n)))))
    return min(angle(p, a), angle(p, b))


def point_polyline_angle(v: tuple, vs: list) -> float:
    return min(point_segment_angle(v, a, b) for a, b in zip(vs, vs[1:]))


def point_line_km(p: list, line: list) -> float:
    return point_polyline_angle(vec(p), [vec(c) for c in line]) * R_KM


def line_km(line: list) -> float:
    return sum(distance_km(p, q) for p, q in zip(line, line[1:]))


def walk_back(line: list, km: float) -> list:
    """The point km before a line's end, measured along it."""
    left = km
    for i in range(len(line) - 1, 0, -1):
        seg = distance_km(line[i - 1], line[i])
        if seg >= left:
            return lonlat(slerp(vec(line[i]), vec(line[i - 1]), left / seg if seg else 0))
        left -= seg
    return list(line[0])


def graticule(step: float, densify_deg: float = 1.0, lon0: float = 0.0) -> list:
    """Meridians and parallels every step degrees, as LineString features with string ids, between the map's
    edges at lon0 - 180 and lon0 + 180."""
    west = lon0 - 180
    feats = []
    lon = math.ceil(round(west / step, 9)) * step
    while lon < lon0 + 180:
        line = [[lon, -90 + i * densify_deg] for i in range(int(round(180 / densify_deg)) + 1)]
        feats.append({"type": "Feature", "id": f"meridian-{lon:g}", "properties": {"dm_label": f"{lon:g}"},
                      "geometry": {"type": "LineString", "coordinates": line}})
        lon += step
    lat = -90 + step
    while lat < 90:
        line = [[west + i * densify_deg, lat] for i in range(int(round(360 / densify_deg)) + 1)]
        feats.append({"type": "Feature", "id": f"parallel-{lat:g}", "properties": {"dm_label": f"{lat:g}"},
                      "geometry": {"type": "LineString", "coordinates": line}})
        lat += step
    return feats


def sphere(densify_deg: float = 1.0, lon0: float = 0.0) -> dict:
    """The whole world as one polygon, densified along its edges at lon0 +/- 180 and the poles, for an ocean fill
    under a CRS."""
    west = lon0 - 180
    n_lon, n_lat = int(round(360 / densify_deg)), int(round(180 / densify_deg))
    ring = [[west + i * densify_deg, -90.0] for i in range(n_lon)]
    ring += [[west + 360, -90 + i * densify_deg] for i in range(n_lat)]
    ring += [[west + 360 - i * densify_deg, 90.0] for i in range(n_lon)]
    ring += [[west, 90 - i * densify_deg] for i in range(n_lat)]
    ring.append(ring[0])
    return {"type": "Feature", "id": "sphere", "properties": {"dm_label": "sphere"},
            "geometry": {"type": "Polygon", "coordinates": [ring]}}


def recenter(geom: dict, lon0: float) -> dict:
    """Cuts a geometry along the map's edge, the meridian opposite lon0, and moves each piece by 360 where it must,
    so every longitude falls within lon0 +/- 180 and nothing draws from one edge of the map to the other.

    Boundary files hold each ring within -180 to 180, with land that crosses 180 already cut there, so every
    ring is a plain polygon in longitude and latitude, and a straight cut along one meridian splits it.
    """
    west = lon0 - 180
    if west == -180:
        return geom
    edge = west if west > -180 else west + 360
    shift = (0, 360) if west > -180 else (-360, 0)
    t, c = geom["type"], geom["coordinates"]
    if t == "Point":
        return {"type": t, "coordinates": [c[0] + shift[c[0] < edge], c[1]]}
    if t in ("LineString", "MultiLineString"):
        lines = [c] if t == "LineString" else c
        parts = [part for line in lines for part in cut_line(line, edge, shift)]
        return {"type": "LineString", "coordinates": parts[0]} if len(parts) == 1 else {"type": "MultiLineString", "coordinates": parts}
    if t in ("Polygon", "MultiPolygon"):
        polys = [c] if t == "Polygon" else c
        out = [piece for poly in polys for piece in cut_polygon(poly, edge, shift)]
        return {"type": "Polygon", "coordinates": out[0]} if len(out) == 1 else {"type": "MultiPolygon", "coordinates": out}
    return geom


def cut_polygon(rings: list, edge: float, shift: tuple) -> list:
    """A polygon's parts east and west of the edge, each with its holes, moved by shift[0] and shift[1]."""
    out = []
    for keep, dx in ((lambda x: x >= edge, shift[0]), (lambda x: x <= edge, shift[1])):
        cut = [clip_ring(r, edge, keep) for r in rings]
        if cut[0]:
            out.append([[[x + dx, y] for x, y in r] for r in cut if r])
    return out


def clip_ring(ring: list, edge: float, keep) -> list:
    """Sutherland-Hodgman against the half-plane keep(lon), with a vertex on the edge wherever the ring crosses it."""
    pts = ring[:-1] if ring[0] == ring[-1] else ring
    out = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        if keep(p[0]):
            out.append(list(p))
        if keep(p[0]) != keep(q[0]) and edge not in (p[0], q[0]):
            out.append([edge, p[1] + (edge - p[0]) / (q[0] - p[0]) * (q[1] - p[1])])
    if len(out) < 3 or all(x == edge for x, _ in out):
        return []
    return out + [list(out[0])]


def cut_line(line: list, edge: float, shift: tuple) -> list:
    """A line's runs east and west of the edge, each ending on it where it crosses, moved by shift[0] and shift[1]."""
    parts, cur = [], [list(line[0])]
    for p, q in zip(line, line[1:]):
        if (p[0] < edge) != (q[0] < edge) and edge not in (p[0], q[0]):
            y = p[1] + (edge - p[0]) / (q[0] - p[0]) * (q[1] - p[1])
            parts.append(cur + [[edge, y]])
            cur = [[edge, y]]
        cur.append(list(q))
    parts.append(cur)
    out = []
    for part in parts:
        if len(part) > 1:
            dx = shift[sum(x for x, _ in part) / len(part) < edge]
            out.append([[x + dx, y] for x, y in part])
    return out


def map_coords(geom: dict, fn) -> dict:
    """Applies fn to every line and ring of a geometry."""
    t, c = geom["type"], geom["coordinates"]
    if t in ("LineString",):
        return {"type": t, "coordinates": fn(c)}
    if t in ("Polygon", "MultiLineString"):
        return {"type": t, "coordinates": [fn(r) for r in c]}
    if t == "MultiPolygon":
        return {"type": t, "coordinates": [[fn(r) for r in poly] for poly in c]}
    return geom


def ring_area_centroid(ring: list) -> tuple:
    """Signed planar area and centroid of a lon/lat ring."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        f = x0 * y1 - x1 * y0
        a += f
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    if abs(a) < 1e-12:
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        return 0.0, [sum(xs) / len(xs), sum(ys) / len(ys)]
    return a / 2, [cx / (3 * a), cy / (3 * a)]


def representative_point(geom: dict) -> list:
    """A point for a symbol: the point itself, or the centroid of the largest polygon's outer ring."""
    t, c = geom["type"], geom["coordinates"]
    if t == "Point":
        return list(c)
    if t == "MultiPoint":
        return list(c[0])
    polys = [c] if t == "Polygon" else c if t == "MultiPolygon" else []
    if not polys:
        line = c if t == "LineString" else c[0]
        return list(line[len(line) // 2])
    best = max((ring_area_centroid(p[0]) for p in polys), key=lambda ac: abs(ac[0]))
    return best[1]


def extent_lons(lons: list) -> tuple:
    """The west and east limits of the narrowest longitude band holding every value; west > east when it crosses 180."""
    xs = sorted(set(((x + 180) % 360) - 180 for x in lons))
    if len(xs) == 1:
        return xs[0], xs[0]
    n = len(xs)
    gaps = [(xs[(i + 1) % n] - xs[i]) % 360 for i in range(n)]
    i = max(range(n), key=lambda j: (gaps[j], j == n - 1))
    return (xs[0], xs[-1]) if i == n - 1 else (xs[i + 1], xs[i])


def all_positions(geom: dict) -> list:
    t, c = geom["type"], geom["coordinates"]
    if t == "Point":
        return [c]
    if t in ("MultiPoint", "LineString"):
        return list(c)
    if t in ("MultiLineString", "Polygon"):
        return [p for part in c for p in part]
    if t == "MultiPolygon":
        return [p for poly in c for ring in poly for p in ring]
    return []
