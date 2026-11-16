# mln-rs

Step 5 reads this file when the brief's Stack line says mln-rs, a native app on louwers/mln-rs, the Rust port of MapLibre Native. The template in `assets/templates/mln-rs/` is a Rust project that draws `style.json` over the files the levers write to `data/`, in a window or offscreen to a PNG with a report beside it.

## What it can draw

| Draws | Doesn't draw yet |
| :-- | :-- |
| Web Mercator, the globe, or vertical-perspective, set by the style's `projection` | a registered CRS, so no equal-area world map |
| fills, lines, circles, and symbols from GeoJSON or `pmtiles://` vector tiles | raised arcs, because custom layers get no globe matrix |
| labels from a local font file named in `font-faces` | a backdrop color around the globe in a window |

An areal idiom at world or continental extent, such as a choropleth, dots, or a bivariate map, needs an equal-area projection that mln-rs can't draw (P10). Draw it in maplibre-gl with a registered CRS, or keep it here and record the departure in the brief's Departures line. Flows and points at world extent go on the globe, as `reference/projection.md` says.

Raised arcs wait for custom layers on the globe, which is upstream work, so flows stay flat (P22).

## The project

```sh
python3 <skill>/scripts/datamap.py new mln-rs map
python3 <skill>/scripts/datamap.py geo --countries --out map/data/countries.geojson
python3 <skill>/scripts/datamap.py flows od.csv --nodes nodes.csv --geometry great-circle --out-dir map/data
cd map && cargo build --release --locked && target/release/map --snapshot map.png --pixel-ratio 2
python3 <skill>/scripts/datamap.py check --png map.png --legend data/legend.json --report map.report.json
```

- `Cargo.toml` pins mln-rs to a commit on main and optimizes every dependency in dev builds.
- `Cargo.lock` ships with it. The commit pins mln-rs alone, and at the prototype 30 of its 411 crates resolved newer than mln-rs's own lock, so build with `--locked`.
- `src/main.rs` holds the map's code, which builds the style and the arrowhead, applies live values, and writes the snapshot and its report.
- `src/window.rs` holds the window.
- `style.json` is the style, with `{{DATA}}` where the data folder's path goes.
- `brief.md` is the brief to fill in.

`datamap.py new mln-rs OUT` names the package in `Cargo.toml` after the project folder and gives the copied files fresh times. Keep that name unique. The binary takes the name, as `target/release/map` above, under `$CARGO_TARGET_DIR` when that is set. Cargo hashes a root package's path relative to its own folder, so two projects with one package name in one target folder share a binary, and the binary reads the data folder it was built from. A fresh copy whose files keep their old times builds nothing and runs the other project's map.

A first release build took 38 s on an M2 Max in a target folder that had built mln-rs before, and the prototype's cold build took 57 s, 32 of them in `read-fonts`. A rebuild takes about 1.5 s, and a snapshot 0.4 to 0.8 s.

## The template's functions

- `style(data_dir)` reads `style.json`, puts the data folder's path in place of `{{DATA}}`, and leaves out any source whose file is missing, with its layers, printing one line for each. So one style serves `classes`, `sizes`, and `flows` and draws whichever files they wrote.
- `arrow()` draws the arrowhead as a signed distance field, so `icon-color` colors it. It is 16 px long with a 4 px margin. The style's `icon-size` divides `dm_arrow` by 16, and its `icon-offset` takes back the margin and sets the tip `dm_setback` + 1 px back from the node's center at any zoom. Change both files together.
- `update(&map, &Flows)` sets each flow's width from a live value through feature-state, scaled by the legend's `width`, so the legend stays true.
- `snapshot` renders offscreen until a frame shows everything loaded, then writes the PNG and `<name>.report.json` with the projection, pitch, bearing, zoom, zoom range, size, scale, the layers with their sources, and the sources with their URLs.
- `window::show` opens a winit window and draws the map until it closes.

The flags are `--snapshot PNG`, `--size WxH` in logical pixels (1200x800 by default), `--pixel-ratio N` (the window takes the display's own), and `--live JSON`, an object of flow `id` to value that `update` applies before the first frame.

## The style

| Layer | Source file | Reads |
| :-- | :-- | :-- |
| `ocean` | none | a `background`, which on the globe paints only the sphere |
| `land`, `borders` | `countries.geojson` | nothing; land is `#d3d0c9` and borders take the ocean's color |
| `classes` | `classes.geojson` | `dm_fill` |
| `sizes` | `sizes.geojson` | `dm_r`, `dm_fill`, `dm_order` |
| `flows` | `flows.geojson` | `dm_width`, `dm_fill`, `dm_order` |
| `nodes` | `flows-nodes.geojson` | `dm_r`, `dm_fill`, `dm_order` |
| `arrows` | `flows-arrows.geojson` | `dm_arrow`, `dm_bearing`, `dm_setback`, `dm_value`, `dm_fill` |

The file names are the levers' defaults. A lever run with `--layer` writes another name, so rename the source's file to match. The sort keys draw small flows over large ones (P19) and small circles over large ones (P14). The arrows align to the map in rotation and pitch, so they lie on the sphere and point along the flow at its destination, as Jenny et al. advise (§4.2).

The camera is the style's `center` and `zoom`, with pitch 0 (P22). At zoom 2.5 and a center at latitude 10, the globe measured 702 px across in an 800 px frame. The globe grows with the center's latitude. At zoom 2.3 it measured 628 px at latitude 10 and 767 px at latitude 40. After moving the camera, open the PNG and keep the whole globe inside the frame.

Land at 30% gray (`#b3b3b3`) outweighed the flows in a test render, and the nodes lost their contrast against it, so the template keeps the lighter warm gray (P27). On this globe, `geo --countries` drew the same with and without `--densify 100`: 0 pixels differed at zoom 3.6. Flows still need the lever's densified great circles.

The template draws no labels. They render offline from a TTF in `data/`, named in the style's root, with no `glyphs` URL:

```json
"font-faces": {"Label": "file://{{DATA}}/label.ttf"}
```

A `symbol` layer then sets `"text-font": ["Label"]` and `"text-field": ["get", "dm_label"]`. Collision drops labels that overlap, as Seoul's did beside Tokyo's in the test. Ship only a font whose license allows it.

## Live values

Feature-state changes a paint property without reloading or re-tiling the GeoJSON, and the next frame draws it. The `flows` layer reads `["coalesce", ["feature-state", "dm_width"], ["get", "dm_width"]]`, and in the test `--live` changed two flows' widths in the same frame that drew the rest. The style spec allows feature-state in any data-driven paint property, such as line opacity or circle radius; the prototype also tested circle color.

- Feature-state needs the top-level integer `id` that the levers write, since mln-rs has no `promoteId`. An arrow has its flow's `id`.
- Layout properties can't read feature-state, `icon-size` and the sort keys among them. An arrowhead keeps the size the lever gave it while its line's width changes. When that misleads, replace the arrows source's data with `map.set_geojson_source_data`, which parses GeoJSON again but only one point per flow. This path is untested here.
- A threshold is one value for every feature. Declare it in the style's root as `"state": {"min_value": {"default": 0}}`, read it with `["global-state", "min_value"]` in a filter, and change it with `map.set_global_state_property("min_value", "2500")`. Put the same filter on the flows and the arrows layers. Each arrow point carries its flow's `dm_value`, so an arrow leaves the map with its line.

## An offline basemap

The bundled countries are enough for a world flow map. For more detail, cut a Protomaps archive once with `pmtiles extract` and a `--maxzoom`, put it in `data/`, and name it as a vector source:

```json
"basemap": {"type": "vector", "url": "pmtiles://file://{{DATA}}/basemap.pmtiles"}
```

Draw its `earth`, `water`, and `boundaries` source layers yourself, with boundaries filtered to `["==", ["get", "kind"], "country"]`, in the land and ocean colors above. The Protomaps light flavor has saturated water that competes with the data (P27). `style()` leaves the source out when the archive is missing.

## Moving the pin

```sh
git ls-remote https://github.com/louwers/mln-rs main
```

Put that commit in `Cargo.toml`'s `rev`, with its date and pull request in the comment above it. Build once without `--locked` so Cargo moves the lock, then take a snapshot, run `check --png`, and compare the PNG with the one from before the move. If the render changed, find out why before keeping the new pin.

## Traps

- **Frames.** Poll `drain_frame_results` for the token you demanded and check that its `disposition` is `Rendered`. A snapshot waits for a frame whose `mode` is `Full` with no `needs_repaint`. Symbols fade in, so that takes about 200 frames.
- **Release order.** Release the session, then the map, then the runtime.
- **Images.** Call `set_style_image` again after every `set_style_json`, because a new style drops its images.
- **The antimeridian.** A line that jumps from 179 to -179 goes the long way round the globe (P20). Split it at 180, as `flows` does.
- **Sky.** Leave it out. It draws a white crescent on the globe's rim, and a flat sky didn't color the space around the globe either.
- **The window's thread.** The session's work runs on the window's thread (`Driver::CallerThread`), where macOS makes the surface. Never wait on a session's completion there, since nothing else runs its work. The first frames finish as `TargetNotReady` until macOS shows the window, so the window redraws on `Occluded(false)`.
- **Black around the globe.** On the globe the renderer clears to transparent black, and the pinned runtime has no clear color, so a window shows black there. A snapshot keeps those pixels transparent, and `check --png` composites them onto the page color. A clear color for the globe is upstream work.
- **No gestures.** The window holds the camera still. When the brief's Interface line lets the reader turn the globe, `examples/desktop` in the mln-rs repository shows the gestures to copy.

## Companion views

The style draws only the map, with no title, legend, source line, or companion. The host app draws them in its own UI from `data/legend.json`. That covers the title that states the point, the width legend from `legend_values` and `legend_widths`, the nested node legend, the `omitted_note`, and the source and date (P24). Ranked flows, an origin-destination matrix, or a second globe for the far side sit beside the map, as the brief's Companions line says. A snapshot for a report goes on a page that holds them around the PNG.
