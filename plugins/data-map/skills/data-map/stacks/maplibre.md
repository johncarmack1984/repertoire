# maplibre-gl

Step 5 reads this file when the brief's Stack line says maplibre. The template in `assets/templates/maplibre/` is one HTML page on maplibre-gl 6.18.0 that draws whatever the levers wrote to `data/`, with its legend, companions, title block, and source line, and opens from a file with no network once `sync` has run.

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
python3 <skill>/scripts/datamap.py geo --countries --lon0 11.6 --out countries.geojson
python3 <skill>/scripts/datamap.py classes rates.csv --field visits --per population --geo countries.geojson --key iso=id --out-dir map/data
python3 <skill>/scripts/datamap.py sync map
python3 <skill>/scripts/datamap.py check map --scale 2
```

- `index.html` holds the `dm-spec` block, the title block, the map cell, the side panel, and the source line. `sync` inlines the page library from `assets/templates/lib/` and every JSON and GeoJSON file in `data/`.
- `vendor/` holds the pinned libraries the page draws with, which `sync` copies in: MapLibre GL JS 6.18.0 with its stylesheet for any map, proj4 2.22.0 under a CRS, and pmtiles 4.5.0 with @protomaps/basemaps 5.7.2 for a `.pmtiles` basemap, each with its license where the package ships one. `sync` fetches each file once from jsDelivr into `~/.cache/data-map/` (or `$DM_CACHE`), checks it against its sha256, and copies it from there, so a second project needs no network. It removes a library the page no longer draws with. Ship `vendor/` with `index.html`.
- `.dm/` holds the working files, which never ship with the map: `brief.md`, the brief to fill in before anything is drawn, and the screenshots and `check.json` that `check` writes. `check` warns on a brief, a screenshot, `check.json`, or a notes file left beside `index.html`.
- Every color, size, and width comes from `legend.json` and the `dm_*` properties the levers wrote. Edit the page's text and its `dm-spec`, not the library region; `check` fails a library edited by hand.

## The slots

- `#dm-title` states the point, and `#dm-subtitle` says what, where, and when (Slocum, ch. 11). `<title>` names the tab, so it carries the same point, shortened to fit. `check` fails a bracketed placeholder in any of the three and warns on the word map.
- `#dm-source` names who published the data and when. `#dm-credits` holds the projection and the boundary or basemap credit.
- `dm-spec` records every decision the brief made. `check` judges the page against it.

| Key | Holds |
| :-- | :-- |
| `idiom` | the chooser row, such as `["choropleth"]` or `["flows"]` |
| `extent` | `world`, `hemisphere`, `continent`, `region`, or `[W, S, E, N]` |
| `projection` | the preset's, or a CRS's `name`, `definition`, and `property` |
| `zoom` | `{"min": "fit", "max": "fit+3"}`, where fit is the zoom that fits the data |
| `controls` | each control the brief asked for; an empty list means compact attribution only, `reveal` draws the flows slider, and `focus` the picker that shows one place's flows |
| `tiles` | each tile source with the grid it was cut in |
| `companions` | the small charts beside the map |
| `decisions` | each departure, with the pitfall it touches and why |
| `center` | the globe's center as `[lon, lat]`, when the default is the wrong one |
| `annotations` | notes that put the finding on the map, each `{"text": "...", "at": [lon, lat]}` or `"at": "node:<key>"` |
| `focus` | with `focus` in `controls`, the focused page's title and subtitle as templates, `by` (`out`, `in`, or `both`, the default), and the `layer` when there are two |
| `highlight` | the keys of the places the title names, such as `["IND", "BGD"]`: a flow node's `dm_key` or an area's or symbol's id. Their names draw bold, their circles get a dark ring, an area gets a dark outline on a white casing, and a bar or table row in a companion that names one draws bold, its bar dark. `check` warns on a key no node or area has |
| `frame` | under a CRS, `"none"` (the default) or `"sphere"`, which draws the ocean, the graticule, and the world's outline |
| `tooltips` | `false` to take the tooltips off; the page shows them on hover and on a tap unless told |
| `hint` | the line under an interactive map saying what a reader can do, which the page writes from `controls`, the zoom limits, and the projection, such as "Hover or tap for numbers; drag to turn the globe; scroll or pinch to zoom.", and adds "right-drag to tilt" when the map allows it. A string replaces it, and `false` leaves it off; a static figure has none |
| `figure` | a static figure's destination size, such as `{"size": "640x700", "scale": 2}`. The page lays itself out at that size in any window, in one column with the classes running across when it is 720 px wide or less, and the map keeps at least 55% of the height. `check` renders there unless `--size` or `--scale` says otherwise, and fails any text cut off or run off the figure |

## What the page draws from data

The page reads the legend's layers and draws each by its kind. A `classes` layer becomes fills with white boundaries, hatching for `dm_low_n`, and an outline on hover. A `sizes` layer becomes circles in `dm_order`, largest first, with labels. A `flows` layer becomes lines in `dm_order`, each as opaque as its `dm_opacity`, nodes sized by `dm_r`, labels, and an arrowhead at each destination. Under each flow an unseen line at least 12 px wide, 24 on a touch screen, takes the pointer, because MapLibre hits a line only within half its width and a 1 px flow would be all but untappable; a pointer on a drawn line still takes that line first. One feature answers the pointer at a time: the topmost under it, outlined alone.

The `flows` lever draws every flow in one color, `#a63603` unless `--color` names another, and fades them by value, from `--fade-min` (0.45) at the smallest kept flow to fully opaque at the largest; `--no-fade` keeps them all opaque. Larger flows darker is Jenny et al.'s suggestion, and the fade follows magnitude, never length (Slocum, ch. 20), so long thin arcs don't out-ink short heavy ones.

Flow nodes take the fill the lever wrote. With `--node-value net`, the side panel keys the gain and loss colors under the node sizes, which it then draws as outlines. With `--reveal`, the page draws the flows up to `reveal.default` by `dm_rank`, and only the nodes those flows touch. When `controls` lists `reveal`, a slider under the flow widths draws the N largest flows, and the kept line under it says how many of how many and what share of the total as it moves. It moves nothing on its own, and the arrow keys move it. The arrowheads, the names, and the deck.gl arcs follow, and the names and notes find new places when it stops.

Base layers come from file names. `frame.geojson` from `geo --sphere --graticule` gives the ocean, the graticule, and the world's outline under a CRS when `frame` is `"sphere"`, and only the graticule elsewhere. `land.geojson` from `geo --countries` is the base under flows and symbols. Any file named `base-<name>.geojson` draws quietly under the data with no legend entry. Its polygons get a pale fill with white edges, and its lines are thin and gray.

The side panel draws each legend layer. Classes get their limits, a separate no-data box, and the method. Sizes get nested circles with leaders. Flows get three or four reference widths with their arrowheads at the opacities of those values, the omitted note, and the node sizes under a heading that says which flows they total.

## Focus on one place

With `focus` in `controls`, a picker under the subtitle lists every node of the flows layer by name, and clicking or tapping a node's circle does the same. The page then draws only that place's flows, every one the file holds, those leaving it in vermilion and those arriving in blue (Okabe and Ito's pair, apart under every color-vision deficiency), rings its circle, and shows only its partners' circles and names. The side panel puts a key to the two colors and a table of its partners in place of the companions, ranked by `by`. The notes step aside, and the kept line under the slider says how many flows it draws. Escape, a second click, the Show all button, or "every place" in the picker returns to the overview. Nothing moves on its own: the map turns or pans only to bring a focused place into view, at once under a reduced-motion setting.

The title and subtitle are rewritten from `dm-spec.focus`, with `{name}`, `{top}` (the largest partner by `by`), `{top_value}`, `{share}` (of `{total}`), `{total}`, `{out}`, `{in}`, `{partners}`, and `{unit}` computed from the flows:

```json
"controls": ["reveal", "focus"],
"focus": {"by": "out", "title": "Students from {name} most often study in {top}", "subtitle": "{top_value} of its {total} students abroad, {share}"}
```

The figures are true only when the page holds every flow, so run the lever with `--reveal` and a `--reveal-max` at least the number of flows. `check` warns when the layer holds fewer, fails a template field the page doesn't fill, and warns on a missing title template. It judges the overview; the page's own `dataMap.focus(key)` focuses a place for a test.

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

maplibre-gl 6.15 added CRS support, which is still experimental, so the version is pinned. For a `crs` projection the page runs proj4 2.22.0's self-contained UMD build in the page and inlines the same build into the data: URL it passes to `importScriptInWorkers`, where `setProjectionHandler` reprojects GeoJSON in MapLibre's workers. It registers the projection with `addProjection`, with a tile matrix sized to the projected world. It first projects the definition's own center. proj4 2.22.0 projects Albers, Lambert azimuthal, cylindrical equal-area, stereographic, Lambert conformal conic, and transverse Mercator definitions to NaN without `+x_0=0 +y_0=0`, so the page throws with the definition and that fix, and `check` reports it. `datamap.py crs` prints both. It fits the view in the map's `load` event. Bounds passed to the constructor are fitted in Web Mercator before the style selects the CRS, which draws the world at half its size.

Under a CRS, Web Mercator tiles draw in the wrong place, so draw GeoJSON, or tiles cut in the CRS's own grid and listed in `tiles` with that grid (P11). Densify long edges with `geo --densify`, or a straight edge cuts a corner off a curved meridian (P12).

## Flows and arrowheads

Direction is shown with arrowheads, which beat tapered lines in Jenny et al.'s user study. Each head is drawn at a screen angle the page measures from two projected points along the arrow's bearing, for three reasons. A bearing is not a screen angle under a CRS that isn't conformal. In a test under Equal Earth they differed by about 30 degrees at high latitudes. MapLibre's map-aligned icons on the globe drift from local north away from the view's center. A pixel test measured 11 to 88 degrees of error at places 55 to 72 degrees from the center. And on the globe, the page measures again whenever the view moves.

Each head is set back from its node by the node's radius and draws above the labels. `check` measures every head in view against the screen direction of its own line's last segment, and fails one more than 15 degrees off (P17).

## Labels

The page places every point label itself, for flow nodes and for symbols. A name longer than 10 ems breaks at the space that leaves its two lines most even, with MapLibre's own wrapping off, so each name's box is known before it is placed. The page tries each name's corners in Slocum's order, at the node's edge and again about twice as far out, and scores each against the flows, the arrowheads, the other nodes, the map's frame, and the names already placed, largest node first; a corner that leaves the name nearer another circle than its own costs nearly as much as covering that circle (Slocum §12.5.2). It sets `text-anchor` and `text-offset` per name, then asks MapLibre which names it drew and moves each hidden one to its next corner. `check` warns on a name that didn't render, an arrowhead over a name, a name nearer another circle than its own, and a name that runs past the map's edge, and names each.

## Notes on the map

Each entry in `dm-spec.annotations` writes the finding on the map, beside the place it is about, so the reader doesn't hunt for it in a footer. The note is quiet type at the label size, wrapped at 180 or 120 px, with a short leader to its place, and a dot where no node marks it. The page tries six leader lengths, out to 140 px, in each of Slocum's corners and takes the one that covers least of the flows, the arrowheads, the circles, the names, other notes, and land. Land is every polygon the page draws, class areas, `land.geojson`, and base polygons, and a note over it reads as a place there, so the page would rather run a long leader out to sea, to the bare page, or off the globe. `"at": "node:<key>"` points at a flow node or symbol by its key, so the leader starts at the circle's edge.

On a globe, a note whose place is on the far side draws at the rim in the place's direction, with "(far side)" added. Clicking it, or Enter on it, turns the globe there, at once under a reduced-motion setting. `check` warns on a note that didn't render, with the reason, on one that covers a name, and when the title names a place that is hidden at load, on the far side or outside the view, and no note marks it (P24).

## The view

The page fits the view to the data. In Mercator it shows the data's bounds. Under a CRS at world extent it shows the world between the cuts at the definition's `+lon_0` plus and minus 180, so a map centered on 11.6 E keeps Russia whole, and `check` fails a world whose edge runs past the frame. With no frame drawn, it crops to the latitudes the data covers and runs the full width, so no band of empty ocean sits below the southernmost country when Antarctica is left off. A projection wider than its cell gets a map row of its own height, and the figure is centered on the page. A static figure's map row hugs the map, and `check` warns when the figure's height leaves empty page below the source line, with the size that fits. The map leads the page (Slocum §11.4.2). `check` warns when an interactive map takes under 55% of the window's width or height, or a figure's map draws narrower than its column or under 40% of the figure's height, but only where other blocks take that room, and it names them with their sizes, such as a side panel widened to 700 px or a bar chart under a world figure. A world map's own shape leaves bands above and below it in a tall window, and those don't count.

`frame` is `"none"` by default because the world fixture rendered both ways said so. In a 640 px figure the same 608 px wide map took 278 px of height with no frame and 311 with the sphere, and at 1200x800 380 against 426. The sphere spends that height on empty polar ocean, and its graticule and outline carry no data; the bare map gives the figure that room back. With no ocean, class edges turn light gray so the palest class keeps its coast.

On the globe the disk fills the map cell. It opens on the center, within 45 degrees of the equator, that keeps the most inflow within 64 degrees of the middle, so the largest destinations show at load, unless `center` says otherwise. Circles keep their legend size out to the rim (`circle-pitch-scale` is `viewport`; MapLibre's default shrinks them by about a fifth there). MapLibre keeps the globe one size as it turns by changing the zoom, so the page holds the zoom between the fitted zoom at the center's latitude plus the `dm-spec.zoom` offsets, and a globe turned toward the equator neither shrinks nor stops zooming in. On a phone the globe fills most of the screen, so a one-finger swipe that starts vertical scrolls the page past it and one that starts sideways turns it, and two fingers still zoom; a test swiping a 390 px page with Chrome's touch input scrolled about 400 px and left the globe where it was.

Zoom runs from the fitted zoom to three levels in, and Mercator stops panning about 4 degrees of longitude and 3 of latitude past the data (Muehlenhaus, ch. 9). Nothing else is on the map. There are no zoom buttons, no compass, and no scale bar, pitch stays 0, and rotation is off. A control goes in `controls` with the question it answers, or `check` warns (P23).

## Offline basemaps

A globe or Mercator map can sit on a local Protomaps archive instead of `land.geojson`. Cut a small one once with `pmtiles extract`, from a Protomaps daily build into `data/basemap.pmtiles` with `--maxzoom=5`, and list it in `dm-spec`:

```json
"tiles": [{"source": "basemap", "grid": "web-mercator", "url": "data/basemap.pmtiles", "flavor": "white"}]
```

The page then loads pmtiles 4.5.0 and @protomaps/basemaps 5.7.2 and draws the `white` flavor, land lighter than water. The `light` flavor's water is a saturated cyan, and `grayscale` draws the ocean darker than the land; both compete with the data (P27). Labels draw from local fonts in the page's own family, because the style names no glyphs. PMTiles needs a server that answers Range requests, such as the one `check` runs. A page opened from a file draws without the archive and logs a warning, which the offline pass reports. The attribution control then credits Protomaps and OpenStreetMap, as the license asks.

## The readiness hook and the report

A classic script defines `window.dataMap` before the page's module runs, so a failed import rejects `dataMap.ready` at once. `ready` resolves after the map's first `idle` once the view is fitted, the arrowheads are turned, the labels are placed, the legend and companions are drawn, and the fonts have loaded. `dataMap.report()` returns the facts `check` judges, namely the projection in use, the center, pitch and zoom with the limits at the current latitude, the globe's radius, the controls, the fonts and type sizes, the legend's swatches, whether the map moves, the layers and sources, the text boxes, the rendered features per layer, the arrowheads' agreement with their lines, each label layer's names (rendered, hidden, covered, stray, and out of view), the notes, each flow line over the circle of a node it doesn't connect with the overlap in px, the reveal control's state, the figure's empty height, how far a world's edge runs past the frame, and whether the tooltips are on. `check` warns on a flow over an unconnected node, naming the flow, the node, and the overlap (P16).

To add a layer by hand, pass a function as the second argument of `DataMap.start` in the page's module. It gets `{map, overlay, data, spec, legend, libs}` and runs after the labels are placed and before the final idle, so the screenshot waits for it.

## Traps

- The page loads nothing from the network. Chrome loads no ES module from a file, and MapLibre 6 ships only ES modules, so `vendor/` carries MapLibre, its worker, and proj4 as text in classic scripts (`*.text.js`), and the page runs them from blob URLs. `check` renders the page, then opens it again from disk with every host name failing to resolve, and fails it if it doesn't draw. It warns on any URL the page loads from a CDN. Without Chrome, `check` runs its static pass and says the render was not measured.
- maplibre-gl's `glyphs`-free text uses `text-font` names as CSS families, and a generic such as `system-ui` can't carry a weight. The template handles basemap labels; a label layer of your own uses the page's font stack.
- The levers write string ids for areas, so hover outlines match the feature's id with a filter rather than feature-state.
- Class fills stay opaque. A `fill-opacity` below 1 blends each class with what lies under it, so the map no longer shows the legend's colors (P9), and `check` can't find them.
- `check` writes `.dm/index.<W>x<H>.png` and `.dm/check.json`; keep `.dm/` out of version control.
- A synced page holds every data file it draws, so it can travel without `data/`, though never without `vendor/`, and `check` then judges it from its inlined blocks. `sync` refuses such a page, since it would drop them.

## Updating the pins

The pins live in one place, `LIBS` in `scripts/dm/vendor.py`: each library's version and each file the page loads with its sha256. `sync` copies only those files, and `check` fails a file in `vendor/` that isn't one of them, has another version, or has another hash. To move one, read the library's changelog first, since CRS is experimental and can change in a minor release. Then change the version and every file's hash in `LIBS`, rebuild the test pages with `tests/pages/make.py`, run `tests/test_check.py`, and open each PNG and each offline PNG.
