# Projection

Step 4 reads this file before `geo` writes any geometry. It picks the projection by the idiom and then the extent, following Slocum's chapter 9. It also says what each stack can draw and gives the proj4 definitions that `datamap.py crs` prints.

## The idiom sets the property

Use an equal-area projection whenever the symbols compare areas or densities, as a choropleth, a dot or density map, a bivariate map, and the standard map beside a cartogram do (Slocum §9.3). A conformal world map swells the high latitudes, so on a Mercator choropleth the darkest class seems to cover the north (Slocum §9.4.1). Slocum's verdict is that "conformal projections are generally discouraged for mapping the world" (§9.3).

Flows and point symbols don't fill enumeration units, so they don't need equal area (Slocum §9.4.3). Put flows and points at world extent on the globe. Draw flows that converge on one place in an azimuthal equidistant projection centered on that place, which keeps true distance from the center (Slocum §9.4.3).

Choose the extent first, then the property, then the aspect and the center, in the order Slocum takes from Snyder (§9.3.1). A measurement task starts from the property it needs instead.

## The extent picks the projection

| Extent | Projection | proj4 |
| :-- | :-- | :-- |
| the world | Equal Earth; Mollweide as the alternative | `eqearth`, `moll` |
| a hemisphere, or a continent about as tall as it is wide | Lambert azimuthal equal-area, centered on the extent | `laea` |
| the mid-latitudes, wider east to west | Albers equal-area conic | `aea` |
| along the Equator, wider east to west | cylindrical equal-area | `cea` |
| around a pole | polar Lambert azimuthal equal-area | `laea` at latitude 90 or -90 |
| a long north-south extent away from the poles | Lambert azimuthal equal-area, centered | `laea` |
| a city | the stack's default; the property barely matters | Web Mercator |

Slocum's chapter 9 also names Eckert IV and Goode's homolosine for the world and a transverse cylindrical equal-area projection for north-south extents. proj4 2.22.0, which maplibre-gl loads for a CRS, implements none of the three (`eck4`, `igh`, and `tcea` are missing), so the table uses the nearest projection it has. When `datamap.py crs` lists one of them as an alternative, pick another.

Center a world map on its area of interest by setting `+lon_0`; Slocum recenters a literacy map on 40° E (§9.4.1). Equal Earth's flat poles keep Russia and Canada legible. Mollweide's pointed poles compress high latitudes, which suits a map whose story lies nearer the Equator (Slocum §9.4.1).

Don't interrupt a world map for a general audience, because the breaks confuse readers who don't know the globe well (Slocum §9.4.1).

## The edge of a world map

A world map is cut along the meridian opposite its center, and whatever land that meridian crosses draws at both edges. At `+lon_0=0` the cut runs through Chukotka, and its tip draws beside Alaska, where readers take it for part of the United States. `crs` centers a world map on 11.6° E, which puts the cut through the Bering Strait at 168.4° W, between St. Lawrence Island and Alaska, so Russia stays whole and no country but Antarctica is cut. In the bundled 110m countries the cut must fall between 168.69° W and 168.11° W. At 10° E a sliver of Chukotka still crosses, since Cape Dezhnev lies at 169.9° W there; at 11° E the cut splits St. Lawrence Island.

Whatever the center, give it to `geo` as `--lon0`. It cuts every polygon and line at the opposite meridian and moves the far side by 360°, so each longitude lies within `lon0 ± 180`, and it draws the graticule and the outline between those edges. `crs` prints both runs for a world projection. Join the data to the file `geo` wrote, not to the bundled countries, which would draw Antarctica across the map.

```sh
python3 <skill>/scripts/datamap.py geo --countries --densify 100 --lon0 11.6 --out map/data/countries.geojson
python3 <skill>/scripts/datamap.py geo --sphere --graticule 30 --lon0 11.6 --out map/data/frame.geojson
```

## The conic rule

Set every conic's parameters from the data's extent (Slocum §9.4.2):

- Put each standard parallel one-sixth of the latitude range in from its limit, so `lat_1 = S + (N - S) / 6` and `lat_2 = N - (N - S) / 6`.
- The central meridian `lon_0` sits at the middle of the longitude range. Count that range across 180° when the extent crosses it.
- `lat_0` only moves the origin of the coordinates and changes nothing visible.

For the conterminous United States, 24.5° N to 49.4° N, the rule gives 28.7° and 45.2°, close to the USGS parallels of 29.5° and 45.5° (Slocum §9.4.2). Either serves.

Check every parameter a tool suggests. An automatic tool gave a 0° central meridian for a Fairbanks to Seoul map that needed 169.469° E, and Slocum's advice is that "users should always check the recommended results" (§9.5). Read the `lon_0` that `crs` prints against the data's extent before using it.

## Small areas

The property barely matters on a small area, since "small geographic areas are equally well represented by most projections." (Slocum §9.1). Over Kansas, the conformal and equidistant conics stay within about 1.6% of true area (Slocum §9.4.4).

Web Mercator is the exception at state size. Its area scale is sec² of the latitude, which grows about 9% from 37° N to 40° N. A state-wide dot or density map takes Albers. A city map can stay on Web Mercator and keep its standard tiles.

## Generalization

Draw boundaries from a file made at the map's scale or at most 10 times more detailed. A 1:25,000 file serves maps down to 1:250,000, and past that cap its coastlines and borders crowd into dark smears (Slocum §6.5.2.1, §6.7). Shown at a larger scale than its own, a file passes off its coarse lines as precise (P25).

At zoom z, maplibre-gl draws the world 512 × 2^z CSS pixels wide, about 1:296,000,000 / 2^z at the Equator on a 96 dpi screen. By that arithmetic Natural Earth's 1:110m file, the bundled `--countries`, holds to about zoom 1.4, the 1:50m file to about 2.6, and the 1:10m file to about 4.9. A continent past zoom 2.6 needs the 1:10m file, and `design.md` caps `maxZoom` the same way.

Simplify shared borders topologically, so neighboring units neither gap nor overlap (Slocum §6.7).

## What each stack can draw

| Stack | Projections |
| :-- | :-- |
| maplibre-gl 6.18.0 | Web Mercator, the globe, or a CRS registered with `maplibregl.addProjection` and proj4 (experimental since 6.15.0) |
| deck.gl over MapLibre | Web Mercator or the globe only |
| mln-rs | Web Mercator, the globe, or vertical-perspective, set by the style's `projection`; no CRS yet |

Under a registered CRS in maplibre-gl:

- GeoJSON sources are reprojected in the workers once proj4 is loaded there, through `importScriptInWorkers` and `setProjectionHandler`. `stacks/maplibre.md` has the code.
- Web Mercator tiles draw in the wrong place. Use GeoJSON layers, or tiles cut in the CRS's own grid, such as martin's `tile_grids`. List every tile source with its grid in `dm-spec.tiles`; `check` fails a mismatch (P11).
- A world map draws no frame by default (`dm-spec.frame: "none"`): land on the page color, cropped to the data's latitudes, which reads larger at a newsletter's width. For the sphere's outline, ocean, and graticule, set `"frame": "sphere"` and write them with `geo --sphere --graticule 30`, with the definition's `+lon_0` as `--lon0`.
- Densify long edges with `geo --densify 100`, because the renderer joins vertices with straight segments and a long one skips the curve the projection gives it (P12). `flows` writes densified lines already.
- Clip the data to the hemisphere a view shows, in the prep script. The renderer doesn't clip it.
- Call `fitBounds` in the map's `load` event. Bounds given to the constructor are fitted in Web Mercator and draw the world at half size.

On deck.gl and mln-rs, an areal idiom at world or continental extent has no equal-area option. Move the map to maplibre-gl, or record it in the brief's Departures line.

## The globe

Choose the globe for flows and points at world extent. Great circles draw whole, with no edge to cut a flow, and Yang's study found the globe the most accurate and fastest view of global flows, though with raised arcs in VR (Yang §5.3). `idioms/flows.md` holds the flow rules.

A globe shows at most one hemisphere and foreshortens everything near its edge, as the orthographic projection does, so it can't carry an area comparison (Slocum §9.3.1.2). Whatever lies on the far side needs a companion view, such as a second globe turned 180°, a flat equal-area inset, or a ranked list. Name it in the brief's Companions line.

## The command

```sh
python3 <skill>/scripts/datamap.py crs --extent data/lakes.geojson --idiom area
python3 <skill>/scripts/datamap.py crs --extent -125,24.5,-66.9,49.4 --idiom area --json
python3 <skill>/scripts/datamap.py crs --extent world --idiom flows --interactive
```

`crs` prints the name (`custom:<slug>`), the proj4 definition, the property, the reason, the alternatives, and a JS snippet. With an areal idiom it repeats that Web Mercator tiles can't sit under the CRS. Copy the name and definition into `dm-spec.projection`.

## proj4 definitions

```
# World, equal-area, centered so the edge runs through the Bering Strait. Set +lon_0 to the center of interest.
custom:equal-earth    +proj=eqearth +lon_0=11.6 +datum=WGS84 +units=m +no_defs     (EPSG:8857 at +lon_0=0)
custom:mollweide      +proj=moll +lon_0=11.6 +datum=WGS84 +units=m +no_defs        (ESRI:54009 at +lon_0=0)

# Lambert azimuthal equal-area, centered on a hemisphere or a compact continent.
custom:laea           +proj=laea +lat_0=<lat> +lon_0=<lon> +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs
custom:laea-europe    +proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs   (EPSG:3035)

# Albers equal-area conic, mid-latitudes.
custom:albers-us      +proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs   (EPSG:5070 parameters)
custom:albers-europe  +proj=aea +lat_0=30 +lon_0=10 +lat_1=43 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs      (ESRI:102013 parameters)

# Polar Lambert azimuthal equal-area.
custom:laea-north-polar  +proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs    (EPSG:6931)
custom:laea-south-polar  +proj=laea +lat_0=-90 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs   (EPSG:6932)

# Equatorial band; lat_ts near half the band's highest latitude.
custom:cylindrical-equal-area  +proj=cea +lat_ts=<lat> +lon_0=<lon> +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs

# Flows into one place, centered on it.
custom:aeqd           +proj=aeqd +lat_0=<lat> +lon_0=<lon> +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs
```
