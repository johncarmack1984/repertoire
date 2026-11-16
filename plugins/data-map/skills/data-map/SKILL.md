---
name: data-map
description: Design, build, and check maps of data the way the cartography canon teaches, from Slocum's Thematic Cartography and Geovisualization, Munzner's Visualization Analysis and Design, Muehlenhaus's Prompt Cartography, and the flow and network studies of Jenny, Yang, and Schöttler. Use when asked to map data or show it by place, region, or route, including choropleths, proportional symbols, dot and density maps, contours, origin-destination flows, networks between places, cartograms, bivariate maps, globes, and change over time, in MapLibre GL JS, deck.gl, or a native MapLibre app. Use also when asked to critique, fix, or restyle an existing map. Picks the idiom from the data and the reader's task, or a chart when location adds nothing. Then sets the projection, normalization, classes, color, symbol sizes, flow geometry, legend, and title, computes the encoding with bundled scripts, renders the map, and has a cold reader check it. Not for a chart with no geography, or GIS analysis with no map.
argument-hint: "[build | refine | review] <data, a map, or the question to map>"
---

# Data map

A thematic map makes an argument about where. It works when the reader gets that argument from the map in a few seconds, and it fails in ways that look fine. A choropleth of raw counts shows where people live. A Mercator world map makes the far north look important. Circles sized by radius exaggerate the large values. Flow lines drawn straight bury each other. An agent asked for a map draws the first idiom it thinks of, in the default look its training favors, and then praises its own work. This skill runs a cartographer's decisions in order instead, computes the encoding with code, renders the map, and has a reader with no context check it against answers the code computed.

The method comes from Terry Slocum and colleagues' *Thematic Cartography and Geovisualization* (5th edition), Tamara Munzner's *Visualization Analysis and Design*, Ian Muehlenhaus's *Prompt Cartography*, and three studies of flow and network maps by Jenny and colleagues, Yang and colleagues, and Schöttler and colleagues. `reference/sources.md` maps each step to its sources.

`<skill>` below is the directory that holds this file. Each step names the file that holds its detail. Read that file when the step starts, and not before.

## Steps

### 1. Mode

- **Build** turns data, or a question to map, into a new map. It is the default and runs steps 2 to 8.
- **Refine** improves an existing map and keeps its data. See "Refining" below.
- **Review** reports an existing map's faults and changes nothing. See "Reviewing" below.

With no data and no map to work from, ask what the reader needs to see and where the data lives.

### 2. Brief

Write the brief before touching the data or the design. It is working notes, never part of the map, and every later step and every subagent reads it:

```
Reader:      who reads it, and what they decide with it
Task:        one action and one target, such as "compare rates between regions" or "find the largest flows"
Question:    the one sentence the map answers; it becomes the title
Data:        geometry (areas, points, OD pairs, field samples, network); kind (count, rate, ratio, ordinal, category); unit; denominator; n; period; source
Supports:    the claims this data can carry, and the ones it can't
Location:    why where matters; if you can't say, the first chooser row applies
Candidates:  up to three idioms, each with its default lie
Idiom:       the chosen row, and why not the row above it
Companions:  the views beside the map
Visual plan: what dominates, what recedes, what is left out; the tone
Interface:   static or interactive; device; time spent on it; guided or exploratory; controls refused
Projection:  name, and why
Stack:       maplibre, deck-gl, mln-rs, or the project's own, and why
Sensitive:   locations or small counts to mask before they reach the page
Answer key:  three questions a reader should answer from the map, with the answers computed by code
Departures:  where this map breaks a rule from the sources, and why
```

Profile the data first, with code:

```sh
python3 <skill>/scripts/datamap.py inspect visits.csv counties.geojson --join visits.csv:fips=counties.geojson:GEOID
```

`inspect` reports each column's range and skew, guesses which columns are counts and which are rates, checks the coordinates, and lists join keys that match nothing. Take the rest from the request and its files. Ask only when a wrong guess would change the map, and state the guesses in the report.

Done when every line is filled, the task is one action and one target, and the answer key comes from code.

### 3. Idiom

Find the row that fits the data and the task. Write its candidates into the brief first, each with its default lie, the way the map would mislead if drawn carelessly, so the choice is between known risks. Then read the chosen row's file and no other. A map with two layers, such as a choropleth with symbols, reads both rows' files.

| The data is | The reader needs to | Idiom | Read |
| :-- | :-- | :-- | :-- |
| a few places, or location isn't the message | rank or compare | no map: sorted bars or a table | `idioms/no-map.md` |
| a rate, ratio, or density per area | see the pattern, compare regions | classed choropleth | `idioms/choropleth.md` |
| totals at points or per area | compare amounts | proportional symbols, sized by area | `idioms/proportional-symbols.md` |
| many events, or counts with a known spread inside each unit | see where things are dense | dots, bins, or a dasymetric map | `idioms/dots-and-density.md` |
| a continuous field sampled at points | read the surface | filled isolines with the samples shown | `idioms/isarithmic.md` |
| origin-destination pairs, regional or global | find the largest flows and their direction | curved flows, or great circles on a globe | `idioms/flows.md` |
| connectivity where the structure is the point | see hubs, clusters, and paths | a map linked to a matrix, or relaxed geography | `idioms/networks.md` |
| totals where land area misleads | compare people, not land | a cartogram with a way back | `idioms/cartogram.md` |
| two measures per area | find where both are high | a 3×3 bivariate map, or small multiples | `idioms/multivariate.md` |
| any of these, over time | see what changed | change maps or small multiples | `idioms/time.md` |

Done when the brief names the idiom, why not the row above it, its companions, and its default lie with the guardrail against it.

### 4. Encode

Compute every class break, color, symbol size, line width, and flow path with the bundled levers, never by hand. Each prints PASS, WARN, and FAIL lines that name the pitfall and the fix, and each writes prepared GeoJSON whose `dm_*` properties carry the encoding, plus one `legend.json` that both the map and its legend read.

```sh
python3 <skill>/scripts/datamap.py crs --extent data.geojson --idiom area
python3 <skill>/scripts/datamap.py geo --countries --sphere --graticule 30 --out map/data/base.geojson
python3 <skill>/scripts/datamap.py classes visits.csv --field visits --per population --scale 1000 --geo counties.geojson --key fips --out-dir map/data
python3 <skill>/scripts/datamap.py sizes reservoirs.geojson --field capacity --out-dir map/data
python3 <skill>/scripts/datamap.py flows movers.csv --nodes states.csv --top 50 --geometry curved --out-dir map/data
```

`classes` refuses raw counts on an areal idiom, picks the method and the number of classes from the distribution, and labels the legend from the same rounded breaks. `sizes` scales symbols by area. `flows` curves each flow by its length, sends it around nodes it doesn't connect, keeps the largest flows, and states what it cut. Read `reference/projection.md` for the projection and `reference/color-and-classes.md` for the scheme and the classes. Run any command with `--help` for its flags.

Done when every color, size, width, and line on the map comes from encode output, and every command exits 0.

### 5. Build

Pick the stack, unless the project already has one:

| The map is | Stack |
| :-- | :-- |
| a static figure, or an areal map of a large region | `maplibre` with a registered equal-area CRS, captured at device scale 2 |
| a zoomable web map | `maplibre`, Mercator or globe |
| flows or points at world scale, interactive | `maplibre` globe, or `deck-gl` when it needs more than about 50,000 features or raised arcs |
| a native app | `mln-rs` |

Start from the stack's template, which already holds the title block, the legend panel, the source line, a quiet basemap or none, and no controls:

```sh
python3 <skill>/scripts/datamap.py new maplibre map --preset equal-earth
```

Then read `stacks/<stack>.md` and `reference/design.md`, fill the page's marked slots, and inline the data so the page opens from a file:

```sh
python3 <skill>/scripts/datamap.py sync map
```

Every element on the page is a decision. The templates add nothing until the brief asks for it, and the page's `dm-spec` block records what was asked for. A map in an existing codebase keeps its stack and takes the same encoding, the same legend, and the same rules.

Done when the page's `dm-spec` matches the brief's projection, interface, and refused controls.

### 6. Check

```sh
python3 <skill>/scripts/datamap.py check map
```

The check renders the page in headless Chrome at its design size, saves a screenshot beside it, and prints a line per finding: the pitfall, the measured fact, and the fix. It fails a Mercator world map of an areal idiom, Web Mercator tiles under a registered CRS, a layer with no legend, a legend color missing from the render, a blank frame, controls or fonts the brief didn't ask for, and motion that starts by itself. For the mln-rs stack, run the app's `cargo run --release -- --snapshot map.png`, then `datamap.py check --png map.png --legend map/data/legend.json`.

- Fix every FAIL and read every WARN.
- Open the screenshot with Read and look at it as the reader would.
- Where Chrome or the network is missing, the check runs its static pass only and says the render was not measured. Say so in the report.

Done when the check exits 0 and the screenshot has been opened.

### 7. Critique

Follow `reference/critique.md`. A critic with no context gets the screenshot, the reader line, and the answer key's three questions, never the answers or the code. Compare its answers with the key: a wrong answer is a defect in the map, not a difference of opinion. Then walk the idiom file's default lies and `reference/pitfalls.md` against the screenshot, with a located piece of evidence for each, and name three ways the map could still mislead. Take at most two rounds of fixes.

Done when the critic's answers match the key, the first thing it noticed is the question's subject, and every default lie has located evidence that the map avoids it.

### 8. Report

Tell whoever asked, in a few lines:

- the absolute paths of the map and its screenshot;
- the idiom, why it fits the task, and the candidate it beat;
- what was cut or left out, such as "the 50 largest of 2,097 flows, carrying 23% of movers", and the controls refused;
- the claims the data can't support, and any departure from the sources;
- whether the render was measured.

If something in what they gave you is wrong, such as notes that call a region the highest when the rates say otherwise, say which and what the data shows.

## Refining

Refine an existing map by reviewing it first, then fixing what the review found.

- Keep every place and every value. Drop or replace one only when it can't be mapped honestly, and name it and the reason in the report.
- Fix in place when the user maintains the code. Keep their data plumbing and stack, and change the encoding and the presentation. Rebuild from a template only when the input is a screenshot or the user asks for a new file.
- Run the encode levers on their data, so the fixes come from code. Then check and critique as in steps 6 and 7.
- Report the faults fixed by pitfall number.

## Reviewing

A review changes nothing. Open with one line that names the map's idiom and says whether it serves the reader's task. Then list the faults, worst for the reader first. For each, quote or locate it, name the pitfall from `reference/pitfalls.md` by number, and give the fix in one line in the map's own stack. Put no mark on anything that keeps the rules, however differently you would have built it.

## Worked example

Movers between US states over one year, mapped for readers who want to know where people are moving. The data is counts of movers by origin and destination state, so the map is a flow map: totals between places, not rates per area. Its candidates were a choropleth of net migration rate, which hides where people go, and a flow map of every pair, which buries the pattern in 2,500 lines. The flow map keeps the largest flows and states the share it kept.

The projection is an equal-area Albers registered as a CRS in MapLibre, with standard parallels set from the data's latitude range, since the map compares regions of a large country. `flows` curves each flow to the right of its direction of travel, so the two directions between a pair of states separate. It also bends longer flows more, routes flows around states they don't connect, and draws small flows over large ones. Arrowheads show direction, widths are linear in movers, and the legend shows three reference widths. A sorted list of the largest flows sits beside the map, because a reader asked for exact values reads a list faster than a line width. `assets/example/` holds the page and its screenshot. Copy its structure, never its data.

## Sources

Every rule cites its source in the file that holds it. `reference/sources.md` maps each step to the chapters and papers behind it, and records where the sources disagree and the default this skill takes, for example Munzner's caution about 3D against Yang's evidence for raised arcs on a globe. It also says what is the skill's own.
