# deck.gl

Step 5 reads this file when the brief's Stack line says deck-gl, for raised arcs or for more features than MapLibre draws smoothly. The template in `assets/templates/deck-gl/` is the maplibre page with deck.gl 9.4.1 over it. Read `stacks/maplibre.md` too, since everything there holds here except where this file says otherwise.

## What it can draw

| Projection | Notes |
| :-- | :-- |
| the globe, the default | flows and points at world extent |
| Web Mercator | a region or a city |

deck.gl can't draw a registered CRS, so an areal idiom at world or continental extent belongs on the maplibre page with Equal Earth (P10). Keep it here only as a departure recorded in `dm-spec.decisions`.

## The project

```sh
python3 <skill>/scripts/datamap.py new deck-gl map
python3 <skill>/scripts/datamap.py geo --countries --out map/data/land.geojson
python3 <skill>/scripts/datamap.py flows od.csv --nodes nodes.csv --geometry great-circle --top 30 --out-dir map/data
python3 <skill>/scripts/datamap.py sync map
python3 <skill>/scripts/datamap.py check map --scale 2
```

The page draws each flow as a deck.gl arc and everything else as MapLibre layers, the same as the maplibre page. That covers the land, the nodes and their labels, the arrowheads, and any classes or sizes layer. The legend, the companions, the title block, the source line, and the readiness hook are the same too.

## Raised arcs

Raised arcs are 3D, and an unjustified third dimension is a pitfall (P22). Munzner rules out 3D that the task doesn't need (ch. 6). Yang et al. found, in VR, that flows raised in proportion to distance read well on a globe. The template takes Yang's case and holds it to four conditions.

- The extent is global, and the arcs are great circles on the globe.
- Height follows each flow's length and nothing else, never its value.
- The arcs stay close to the surface. The longest flow's apex is `dm-spec.arcs.apex` of the Earth's radius, 0.08 by default, and every other apex is in proportion to its flow's length.
- `dm-spec.decisions` holds a pitfall 22 entry whose `why` says what the height buys this reader. The template ships that entry with an empty `why`, and `check` fails the page until it is filled.

Set `arcs.apex` to 0 for flat great circles, which need no decision. While the arcs are raised, the flows legend says "Arc height shows distance, not" and the unit, so no reader takes a tall arc for a large flow.

deck.gl's arc peaks at its height times the flow's length over two, so the page sets the height to twice the apex share over the longest flow's angle. Measured in profile at the globe's edge, the longest of a test's arcs rose 8.2% of the radius past the surface at the default of 8%. Each arc's length comes from the lever's `dm_km`, and nothing else sets its height.

Near the globe's edge an arc's height shows in profile, so arcs that land there curl over the horizon. That is the height drawn truthfully. The globe opens on the center that keeps the largest destinations in view, as `stacks/maplibre.md` says; if the arcs the title is about still curl at the rim, set `center` in `dm-spec`, and mark a place the title names on the far side with a note in `annotations`.

## Direction

Each flow ends in an arrowhead, because arrowheads beat tapered lines for direction in Jenny et al.'s user study. The heads are the maplibre page's own symbol layer, set back from each node and turned to their line on screen, and the arcs draw under them. Source and target share one color and the flow's `dm_opacity`, so the arcs fade by value as the maplibre page's lines do. A color gradient along the arc is the weaker cue, and a red-to-green one fails readers with color-vision deficiency (Slocum, ch. 20).

The arc lands on the surface almost vertically, so the head sits at the landing point and points along the ground track, which is the arc's direction as the reader sees it from above.

The two directions of a pair share one great circle and one height, so A to B and B to A draw as one arc with a head at each end. ArcLayer's `getTilt` would lean them apart, but 9.4.1 ignores it on great-circle arcs, and a render with a tilt of 15 degrees was byte-identical to one without. When the pair matters, run the lever with `--net`, or draw flat flows on the maplibre globe, where each direction moves `dm_offset` pixels to the right of travel.

The `focus` control works here too, and rebuilds the arcs in the two focus colors; a pair's two directions still share one arc. The reveal slider works here too. When the lever ran with `--reveal` and `controls` lists `reveal`, the slider rebuilds the arc layer with the flows up to its value, and the heads and nodes follow. The names and the notes keep clear of the arcs where the reader sees them: the page lifts each great circle as deck.gl does, by the square root of t(1 - t) times its length and height, and projects it to the screen. The arcs leave the ground, so `check` leaves them out when it looks for flows over unconnected nodes. The overlay picks within 6 px of the pointer, 12 on a touch screen, so a thin arc still answers a hover or a tap.

## Large layers

Past about 50,000 points or lines, draw that layer with a deck.gl layer instead of MapLibre's. Pass a function as the second argument of `DataMap.start` in the page's module. It gets `{map, overlay, layers, data, spec, legend, libs}`, where `layers` holds the overlay's arc layers, so it can add a layer with `overlay.setProps({layers: [...layers, layer]})`. Don't read `overlay.props.layers`: 9.4.1 keeps the layers elsewhere, and that read throws. Take every color and size from the `dm_*` properties and `legend.json`, so the legend still matches, and let `check` find the legend's colors in the render.

## The readiness hook

`dataMap.ready` waits for the map's first `idle` and for deck.gl's first frame, since the overlay draws in the map's render loop and the two can finish in either order. The report lists each arc layer as `deck:arc`, with its apex, its longest flow, and the height it set.

## Traps

- `MapboxOverlay` crashes on maplibre-gl 6, because it reads `map.transform`, which 6 removed. The page uses `deck.MapLibreOverlay`.
- The overlay must be interleaved on the globe, as the prototypes found.
- The globe culls back faces, and 9.4.1's arc strips wind clockwise, so the arc layer sets `parameters: {cullMode: 'none'}` or every arc vanishes (deck.gl issue 10670).
- deck.gl layers draw above every MapLibre layer unless they name a `beforeId`. The arcs name the nodes layer, so they draw under the nodes, the names, and the arrowheads, as the maplibre page's lines do.
- deck.gl loads from `vendor/` as a classic script before the page's module and defines `window.deck`. The template's vendor marker, `<!-- data-map:vendor deck.gl -->`, asks `sync` for it whatever the projection.
- The flows lever also writes `<layer>-arcs.json`. The page builds its arcs from the lines and the nodes instead, so that file only travels along.

## Updating the pins

deck.gl's pin sits in `LIBS` in `scripts/dm/vendor.py`, with the hash of `dist.min.js`. Move it together with maplibre-gl, since `MapLibreOverlay` follows maplibre-gl's map API. After a change, rebuild the test pages with `tests/pages/make.py`, run `tests/test_check.py`, and open the deck page's PNG and its offline PNG to see that the arcs still draw and still hug the globe.
