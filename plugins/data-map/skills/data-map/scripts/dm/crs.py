"""Projection choice from the data's extent and idiom (Slocum ch. 9), as proj4 definitions MapLibre can register."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

TAIL = "+datum=WGS84 +units=m +no_defs"
WORLD_SPAN = 270
GLOBE_SPAN = 180


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


def one_sixth(ext: Extent) -> tuple:
    """Standard parallels one-sixth of the latitude range in from each limit (Slocum §9.4.2)."""
    sixth = ext.lat_span / 6
    return ext.south + sixth, ext.north - sixth


def equal_earth(lon0: float = 0) -> str:
    return f"+proj=eqearth +lon_0={_d(lon0)} {TAIL}"


def world_alternatives() -> list:
    return [
        {"name": "custom:mollweide", "definition": f"+proj=moll +lon_0=0 {TAIL}", "why": "equal-area with pointed poles; high latitudes compressed"},
        {"name": "custom:behrmann", "definition": f"+proj=cea +lon_0=0 +lat_ts=30 {TAIL}", "why": "equal-area with flat poles; keeps high latitudes wide, at a cost in shape"},
    ]


def polar(ext: Extent) -> bool:
    """Poleward of 45 degrees and holding the pole or half the longitudes."""
    if ext.south >= 45:
        return ext.north >= 85 or ext.lon_span >= 180
    if ext.north <= -45:
        return ext.south <= -85 or ext.lon_span >= 180
    return False


def recommend(ext: Extent, idiom: str = "area", interactive: bool = False) -> Recommendation:
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
            [{"name": "custom:equal-earth", "definition": equal_earth(), "why": "a static, equal-area world map"}],
        )
    if world:
        return Recommendation(
            "crs", "custom:equal-earth", equal_earth(), "equal-area",
            "world extent: an equal-area pseudocylindrical keeps every country's area true (Šavrič, Patterson and Jenny 2018; Slocum §9.4.1)",
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


def snippet(rec: Recommendation) -> str:
    """The registration that the maplibre-gl 6.18.0 prototype rendered with, before the map is made."""
    if rec.type == "globe":
        return "style.projection = {type: 'globe'};"
    return "\n".join([
        "const handler = new Blob([`import proj4 from 'https://esm.sh/proj4@2.22.0';",
        "  self.setProjectionHandler(definition => proj4(definition));`], {type: 'text/javascript'});",
        "await maplibregl.importScriptInWorkers(URL.createObjectURL(handler));",
        f"const definition = '{rec.definition}';",
        "const projection = proj4('EPSG:4326', definition);",
        "const halfWidth = projection.forward([180, 0])[0] * 1.04;",
        f"maplibregl.addProjection({{name: '{rec.name}', definition, projection,",
        "  tileMatrixSet: {origin: [-halfWidth, halfWidth], extentAtZoom0: 2 * halfWidth}});",
        f"// in the style: projection: {{type: '{rec.name}'}}",
    ])
