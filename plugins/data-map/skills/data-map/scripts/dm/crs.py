"""Projection choice from the data's extent and idiom (Slocum ch. 9), as proj4 definitions MapLibre can register."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

# proj4 2.22.0 projects aea, laea, cea, stere, lcc, and tmerc to NaN when the false origin is left out.
TAIL = "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
WORLD_SPAN = 270
GLOBE_SPAN = 180
# A world map's central meridian. Its edge, the meridian opposite, runs through the Bering Strait at -168.4, between
# St. Lawrence Island (-171.79 to -168.69 in world-110m.json) and Alaska's Seward Peninsula (-168.11), so it cuts
# no country but Antarctica. At 0, Chukotka draws beside Alaska; at 10, a sliver east of -170 still does, since
# Cape Dezhnev lies at -169.9; at 11, the edge cuts St. Lawrence Island. Every center from 11.31 to 11.89 works.
WORLD_LON0 = 11.6
# Web Mercator's area scale is sec² of the latitude. Slocum's conformal and equidistant conics keep Kansas within about
# 1.6% of true area (§9.4.4), a small area "equally well represented by most projections" (§9.1), while Web Mercator's
# scale grows 9% across Kansas. An extent over which it grows by no more than the conics' 1.6% keeps Web Mercator.
MERCATOR_SPREAD = 0.016
MERCATOR_LAT = 85.0511
KM_PER_DEG = math.pi * 6371.0088 / 180


@dataclass(frozen=True)
class Extent:
    west: float
    south: float
    east: float
    north: float

    @property
    def lon_span(self) -> float:
        span = (self.east - self.west) % 360
        return 360.0 if span == 0 and self.east != self.west else span

    @property
    def lat_span(self) -> float:
        return self.north - self.south

    @property
    def center_lon(self) -> float:
        return ((self.west + self.lon_span / 2 + 180) % 360) - 180

    @property
    def center_lat(self) -> float:
        return (self.south + self.north) / 2

    @property
    def crosses_antimeridian(self) -> bool:
        return self.west > self.east

    @property
    def east_west(self) -> bool:
        """Wider than tall on the ground, measured at the middle latitude."""
        return self.lon_span * math.cos(math.radians(self.center_lat)) >= self.lat_span


WORLD = Extent(-180.0, -90.0, 180.0, 90.0)


@dataclass
class Recommendation:
    type: str
    name: str
    definition: str
    property: str
    reason: str
    alternatives: list = field(default_factory=list)


def _d(x: float) -> str:
    return f"{round(x, 2):g}"


def deg(x: float) -> str:
    return f"{round(x, 4):g}"


def edge_of(lon0: float) -> float:
    """The meridian opposite lon0, where a map centered on it is cut, from -180 up to 180."""
    return (lon0 + 360) % 360 - 180


def one_sixth(ext: Extent) -> tuple:
    """Standard parallels one-sixth of the latitude range in from each limit (Slocum §9.4.2)."""
    sixth = ext.lat_span / 6
    return ext.south + sixth, ext.north - sixth


def equal_earth(lon0: float = 0) -> str:
    return f"+proj=eqearth +lon_0={_d(lon0)} {TAIL}"


def world_alternatives(lon0: float = WORLD_LON0) -> list:
    return [
        {"name": "custom:mollweide", "definition": f"+proj=moll +lon_0={_d(lon0)} {TAIL}", "why": "equal-area with pointed poles; high latitudes compressed"},
        {"name": "custom:behrmann", "definition": f"+proj=cea +lon_0={_d(lon0)} +lat_ts=30 {TAIL}", "why": "equal-area with flat poles; keeps high latitudes wide, at a cost in shape"},
    ]


def polar(ext: Extent) -> bool:
    """Poleward of 45 degrees and holding the pole or half the longitudes."""
    if ext.south >= 45:
        return ext.north >= 85 or ext.lon_span >= 180
    if ext.north <= -45:
        return ext.south <= -85 or ext.lon_span >= 180
    return False


def area_spread(lat_a: float, lat_b: float) -> float:
    """How much Web Mercator's area scale, sec² of the latitude, grows from one latitude to another, Equator between them or not."""
    near = 0.0 if lat_a * lat_b < 0 else min(abs(lat_a), abs(lat_b))
    far = max(abs(lat_a), abs(lat_b))
    return (math.cos(math.radians(near)) / math.cos(math.radians(far))) ** 2 - 1


def side_km(ext: Extent) -> float:
    """The extent's longer side on the ground: north to south, or east to west at its middle latitude."""
    return max(ext.lat_span, ext.lon_span * math.cos(math.radians(ext.center_lat))) * KM_PER_DEG


def square_spread(lat: float, km: float) -> float:
    """Web Mercator's area spread over a square km on a side, centered on lat."""
    half = km / KM_PER_DEG / 2
    return area_spread(lat - half, lat + half)


def city_limit_km(lat: float) -> float:
    """The side of the largest square centered on lat that keeps Web Mercator's area spread within MERCATOR_SPREAD."""
    lo, hi = 0.0, 180 * KM_PER_DEG
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if square_spread(lat, mid) <= MERCATOR_SPREAD and abs(lat) + mid / KM_PER_DEG / 2 < MERCATOR_LAT else (lo, mid)
    return lo


def recommend(ext: Extent, idiom: str = "area", interactive: bool = False) -> Recommendation:
    """Web Mercator for a city or a small region, where its area scale barely changes and street tiles line up; otherwise
    the projection the extent and idiom call for."""
    km, limit = side_km(ext), city_limit_km(ext.center_lat)
    if km > limit:
        return by_extent(ext, idiom, interactive)
    alt = by_extent(ext, idiom, interactive)
    return Recommendation(
        "mercator", "mercator", "", f"conformal; area scale within {MERCATOR_SPREAD:.1%} across the extent",
        f"a city or small region, {km:,.1f} km on its longer side: Web Mercator's area scale (sec² of the latitude) changes by "
        f"{square_spread(ext.center_lat, km):.2%} across it, within the {MERCATOR_SPREAD:.1%} Slocum's conics keep over Kansas "
        f"(§9.4.4), and street tiles line up under it; at latitude {_d(ext.center_lat)} that holds up to {limit:,.0f} km",
        [{"name": alt.name, "definition": alt.definition, "why": "equal-area, for a static map that compares areas and draws no tiles"}],
    )


def by_extent(ext: Extent, idiom: str, interactive: bool) -> Recommendation:
    if polar(ext):
        north = ext.south > 0
        lat0 = 90 if north else -90
        return Recommendation(
            "crs", f"custom:laea-{'north' if north else 'south'}-polar",
            f"+proj=laea +lat_0={lat0} +lon_0={_d(ext.center_lon)} {TAIL}", "equal-area",
            f"polar extent ({_d(ext.south)} to {_d(ext.north)} degrees): an azimuthal centered on the pole (Slocum §9.3.1.3)",
            [{"name": "custom:polar-stereographic", "definition": f"+proj=stere +lat_0={lat0} +lon_0={_d(ext.center_lon)} {TAIL}", "why": "conformal, when shape matters more than area"}],
        )
    world = ext.lon_span >= WORLD_SPAN
    if ext.lon_span >= GLOBE_SPAN and interactive and idiom in ("flows", "points"):
        return Recommendation(
            "globe", "globe", "", "none (a rotatable globe; true shape and direction near the center)",
            "flows or points across half the world or more, read interactively: a globe keeps great circles whole and has no edge to cut flows (Yang et al. 2019)",
            [{"name": "custom:equal-earth", "definition": equal_earth(WORLD_LON0), "why": "a static, equal-area world map"}],
        )
    if world:
        return Recommendation(
            "crs", "custom:equal-earth", equal_earth(WORLD_LON0), "equal-area",
            "world extent: an equal-area pseudocylindrical keeps every country's area true (Šavrič, Patterson and Jenny 2018; Slocum §9.4.1); "
            f"centered on {deg(WORLD_LON0)}, its edge runs through the Bering Strait and cuts no country but Antarctica",
            world_alternatives(),
        )
    if max(abs(ext.south), abs(ext.north)) <= 30 and ext.east_west:
        lat_ts = max(abs(ext.south), abs(ext.north)) / 2
        return Recommendation(
            "crs", "custom:cylindrical-equal-area",
            f"+proj=cea +lon_0={_d(ext.center_lon)} +lat_ts={_d(lat_ts)} {TAIL}", "equal-area",
            "an east-west extent near the Equator: a cylinder is tangent along it (Slocum §9.3.1.3, Table 9.3)",
            [{"name": "custom:laea", "definition": f"+proj=laea +lat_0={_d(ext.center_lat)} +lon_0={_d(ext.center_lon)} {TAIL}", "why": "if the extent is closer to square"}],
        )
    if (ext.south >= 0 or ext.north <= 0) and ext.east_west:
        lat1, lat2 = one_sixth(ext)
        return Recommendation(
            "crs", "custom:albers",
            f"+proj=aea +lat_1={_d(lat1)} +lat_2={_d(lat2)} +lat_0={_d(ext.center_lat)} +lon_0={_d(ext.center_lon)} {TAIL}",
            "equal-area",
            f"a mid-latitude, east-west extent: Albers with standard parallels one-sixth in from each limit ({_d(lat1)} and {_d(lat2)}) and the central meridian at {_d(ext.center_lon)} (Slocum §9.4.2)",
            [{"name": "custom:laea", "definition": f"+proj=laea +lat_0={_d(ext.center_lat)} +lon_0={_d(ext.center_lon)} {TAIL}", "why": "equal-area for a compact extent"}],
        )
    return Recommendation(
        "crs", "custom:laea",
        f"+proj=laea +lat_0={_d(ext.center_lat)} +lon_0={_d(ext.center_lon)} {TAIL}", "equal-area",
        f"a hemisphere, continent, or compact extent: Lambert azimuthal equal-area centered on {_d(ext.center_lat)}, {_d(ext.center_lon)} (Slocum §9.3.1.2)",
        [{"name": "custom:transverse-mercator", "definition": f"+proj=tmerc +lat_0={_d(ext.center_lat)} +lon_0={_d(ext.center_lon)} {TAIL}", "why": "conformal, for a long north-south extent where shape matters more than area"}],
    )


def lon0_of(definition: str) -> float:
    m = re.search(r"\+lon_0=([-\d.]+)", definition)
    return float(m.group(1)) if m else 0.0


def geo_commands(rec: Recommendation, script: str) -> list:
    """The geo runs whose boundaries and frame match a world CRS's center; none for a regional CRS or the globe."""
    if rec.type != "crs" or rec.name not in ("custom:equal-earth", "custom:mollweide", "custom:behrmann"):
        return []
    lon0 = deg(lon0_of(rec.definition))
    run = f"python3 {script} geo"
    return [f"{run} --countries --densify 100 --lon0 {lon0} --out OUT/data/countries.geojson (or IN in place of --countries; "
            "join to that file with --geo, not to the bundled countries)",
            f"{run} --sphere --graticule 30 --lon0 {lon0} --out OUT/data/frame.geojson"]


def snippet(rec: Recommendation) -> str:
    """The registration that the maplibre-gl 6.18.0 prototype rendered with, before the map is made."""
    if rec.type in ("globe", "mercator"):
        return f"style.projection = {{type: '{rec.type}'}};"
    return "\n".join([
        "const handler = new Blob([`import proj4 from 'https://esm.sh/proj4@2.22.0';",
        "  self.setProjectionHandler(definition => proj4(definition));`], {type: 'text/javascript'});",
        "await maplibregl.importScriptInWorkers(URL.createObjectURL(handler));",
        f"const definition = '{rec.definition}';",
        "const projection = proj4('EPSG:4326', definition);",
        f"const halfWidth = projection.forward([{deg(lon0_of(rec.definition) + 180)}, 0])[0] * 1.04;",
        f"maplibregl.addProjection({{name: '{rec.name}', definition, projection,",
        "  tileMatrixSet: {origin: [-halfWidth, halfWidth], extentAtZoom0: 2 * halfWidth}});",
        f"// in the style: projection: {{type: '{rec.name}'}}",
    ])
