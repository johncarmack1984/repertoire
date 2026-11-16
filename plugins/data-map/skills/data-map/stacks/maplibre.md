# maplibre-gl

Step 5 reads this file when the brief's Stack line says maplibre. The template in `assets/templates/maplibre/` is one HTML page on maplibre-gl 6.18.0 that draws whatever the levers wrote to `data/`, with its legend, companions, title block, and source line, and opens from a file once `sync` has run.

## What it can draw

| Preset | Projection | Use it for |
| :-- | :-- | :-- |
| `equal-earth`, the default | a CRS registered with proj4, Equal Earth unless you change it | any areal idiom at world or continental extent, and any static world figure |
| `globe` | the MapLibre globe | flows and points at world extent |
| `mercator` | Web Mercator | a city or a region, where area barely varies |
| `chart` | no map | the no-map row of the chooser |

A choropleth, dots, or a bivariate map at world or continental extent in Web Mercator or on the globe fails `check` (P10). For a continent or a country, run `datamap.py crs` and put its `name` and `definition` in `dm-spec`; it recommends Lambert azimuthal equal-area for a continent and Albers for a mid-latitude country (Slocum, ch. 9).

## The project

```sh
python3 <skill>/scripts/datamap.py new maplibre map --preset equal-earth
python3 <skill>/scripts/datamap.py geo --sphere --graticule 30 --out map/data/frame.geojson
python3 <skill>/scripts/datamap.py classes rates.csv --field visits --per population --geo countries --key iso=id --out-dir map/data
python3 <skill>/scripts/datamap.py sync map
python3 <skill>/scripts/datamap.py check map --scale 2
```

- `index.html` holds the `dm-spec` block, the title block, the map cell, the side panel, and the source line. `sync` inlines the page library from `assets/templates/lib/` and every JSON and GeoJSON file in `data/`.
- `brief.md` is the brief to fill in before anything is drawn.
- Every color, size, and width comes from `legend.json` and the `dm_*` properties the levers wrote. Edit the page's text and its `dm-spec`, not the library region; `check` fails a library edited by hand.

## The slots

- `#dm-title` states the point, and `#dm-subtitle` says what, where, and when (Slocum, ch. 11). `check` fails a bracketed placeholder and warns on the word map.
- `#dm-source` names who published the data and when. `#dm-credits` holds the projection and the boundary or basemap credit.
- `dm-spec` records every decision the brief made. `check` judges the page against it.

| Key | Holds |
| :-- | :-- |
| `idiom` | the chooser row, such as `["choropleth"]` or `["flows"]` |
| `extent` | `world`, `hemisphere`, `continent`, `region`, or `[W, S, E, N]` |
| `projection` | the preset's, or a CRS's `name`, `definition`, and `property` |
| `zoom` | `{"min": "fit", "max": "fit+3"}`, where fit is the zoom that fits the data |
| `controls` | each control the brief asked for; an empty list means compact attribution only |
| `tiles` | each tile source with the grid it was cut in |
| `companions` | the small charts beside the map |
| `decisions` | each departure, with the pitfall it touches and why |
| `center` | the globe's center as `[lon, lat]`, when the data's mean position is the wrong one |

## What the page draws from data

The page reads the legend's layers and draws each by its kind. A `classes` layer becomes fills with white boundaries, hatching for `dm_low_n`, and an outline on hover. A `sizes` layer becomes circles in `dm_order`, largest first, with labels. A `flows` layer becomes lines in `dm_order`, nodes sized by `dm_r`, labels, and an arrowhead at each destination.

Base layers come from file names. `frame.geojson` from `geo --sphere --graticule` gives the ocean, the graticule, and the world's outline under a CRS, and only the graticule elsewhere. `land.geojson` from `geo --countries` is the base under flows and symbols. Any file named `base-<name>.geojson` is base information that needs no legend entry.

The side panel draws each legend layer. Classes get their limits, a separate no-data box, and the method. Sizes get nested circles with leaders. Flows get three or four reference widths with their arrowheads, the omitted note, and the node sizes.

## Companions

Each entry in `dm-spec.companions` draws a small SVG chart in the side panel, from a layer or from a JSON file in `data/`.

| `type` | Draws | Reads |
| :-- | :-- | :-- |
| `bars` | sorted bars, `top` of them, `order` asc or desc | `layer`, or `data` holding `{"rows": [[label, value]]}` |
| `table` | a table with numbers right-aligned | `layer`, or `data` with `columns` and `rows` |
| `matrix` | origins by destinations, darker for more | a flows `layer` |
| `series` | lines with their names at the ends | `data` holding `{"x": [...], "series": [{"name", "values"}]}` |

## The chart preset

`new maplibre map --preset chart` writes the same page with no map at all, for an answer from the no-map row. It holds the title block, the companions in one column, and the source line, and `dm-spec` says `"idiom": ["no-map"]` and `"projection": null`. Put the bars or the table in `companions`, with the values in a JSON file in `data/`. `check` skips the map rules and still judges the text, the fonts, the type scale, errors, and the blank frame.

## A registered CRS

maplibre-gl 6.15 added CRS support, which is still experimental, so the version is pinned. The page does three things for a `crs` projection.

- It loads proj4 2.22.0 in the page and in MapLibre's workers, where GeoJSON is reprojected, through `importScriptInWorkers` and `setProjectionHandler`.
- It registers the projection with `addProjection`, with a tile matrix sized to the projected world.
- It fits the view in the map's `load` event. Bounds passed to the constructor are fitted in Web Mercator before the style selects the CRS, which draws the world at half its size.

Under a CRS, Web Mercator tiles draw in the wrong place, so draw GeoJSON, or tiles cut in the CRS's own grid and listed in `tiles` with that grid (P11). Densify long edges with `geo --densify`, or a straight edge cuts a corner off a curved meridian (P12).

## Flows and arrowheads

Direction is shown with arrowheads, which beat tapered lines in Jenny et al.'s user study. Each head is drawn at a screen angle the page measures from two projected points along the arrow's bearing, for three reasons.

- A bearing is not a screen angle under a CRS that isn't conformal. In a test under Equal Earth they differed by about 30 degrees at high latitudes.
- MapLibre's map-aligned icons on the globe drift from local north away from the view's center. A pixel test measured 11 to 88 degrees of error at places 55 to 72 degrees from the center.
- On the globe, the page measures again whenever the view moves.

Each head is set back from its node by the node's radius and draws above the labels, so a label never hides a head and no node loses its name to one. `check` measures every head in view against the screen direction of its own line's last segment, and fails one more than 15 degrees off (P17).

## The view

The page fits the view to the data. Under a CRS it shows the whole world, in Mercator the data's bounds, and on the globe a disk that fills the map cell, centered on the data's mean position. Zoom then runs from the fitted zoom to three levels in, and Mercator stops panning about 4 degrees of longitude and 3 of latitude past the data (Muehlenhaus, ch. 9). A projection wider than its cell gets a map row of its own height, and the figure is centered on the page.

Nothing else is on the map. There are no zoom buttons, no compass, and no scale bar, pitch stays 0, and rotation is off. A control goes in `controls` with the question it answers, or `check` warns (P23).

## Offline basemaps

A globe or Mercator map can sit on a local Protomaps archive instead of `land.geojson`. Cut a small one once with `pmtiles extract`, from a Protomaps daily build into `data/basemap.pmtiles` with `--maxzoom=5`, and list it in `dm-spec`:

```json
"tiles": [{"source": "basemap", "grid": "web-mercator", "url": "data/basemap.pmtiles", "flavor": "white"}]
```

- The page then loads pmtiles 4.5.0 and @protomaps/basemaps 5.7.2 and draws the `white` flavor, land lighter than water.
- The `light` flavor's water is a saturated cyan, and `grayscale` draws the ocean darker than the land; both compete with the data (P27).
- Labels draw from local fonts in the page's own family, because the style names no glyphs.
- PMTiles needs a server that answers Range requests, such as the one `check` runs. A page opened from a file can't use the archive.
- The attribution control then credits Protomaps and OpenStreetMap, as the license asks.

## The readiness hook and the report

A classic script defines `window.dataMap` before the page's module runs, so a failed import rejects `dataMap.ready` at once. `ready` resolves after the map's first `idle` once the view is fitted, the arrowheads are turned, the legend and companions are drawn, and the fonts have loaded. `dataMap.report()` returns the facts `check` judges, namely the projection in use, pitch and zoom, the controls, the fonts and type sizes, the legend's swatches, whether the map moves, the layers and sources, the text boxes, the rendered features per layer, and the arrowheads' agreement with their lines.

To add a layer by hand, pass a function as the second argument of `DataMap.start` in the page's module. It gets `{map, overlay, data, spec, legend, libs}` and runs before the final idle, so the screenshot waits for it.

## Traps

- The page loads its libraries from jsDelivr at exact versions, so a render needs the network. Without it, or without Chrome, `check` runs its static pass and says the render was not measured.
- maplibre-gl's `glyphs`-free text uses `text-font` names as CSS families, and a generic such as `system-ui` can't carry a weight. The template handles basemap labels; a label layer of your own uses the page's font stack.
- The levers write string ids for areas, so hover outlines match the feature's id with a filter rather than feature-state.
- Class fills stay opaque. A `fill-opacity` below 1 blends each class with what lies under it, so the map no longer shows the legend's colors (P9), and `check` can't find them.
- `check` writes `index.<W>x<H>.png` and `check.json` beside the page; keep them out of version control.

## Updating the pins

The pins live in the page's URLs and in `PINS` in `scripts/dm/check.py`, which fails any other version. To move one, read the library's changelog first, since CRS is experimental and can change in a minor release. Then change the URLs in both templates and `PINS` together, rebuild the test pages with `tests/pages/make.py`, run `tests/test_check.py`, and open each PNG.
