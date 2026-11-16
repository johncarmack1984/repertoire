# Design

Step 5 reads this file while filling the template's slots, after the stack file. It covers the hierarchy, the basemap, the map elements, type and labels, the defaults to refuse, interaction, motion, attribution, and privacy. Every element it allows goes into the page's `dm-spec` block, and `check` flags anything on the page that the block didn't ask for.

## Hierarchy

Rank what the map must show before drawing it, and write the ranking into the brief's Visual plan line (Slocum §13.3.1). The default order, most important first:

1. the thematic symbols and their labels;
2. the title, the subtitle, and the legend;
3. the base information;
4. a scale or orientation, when the map needs one;
5. the source and notes.

Make the visual hierarchy match that ranking through contrast in size, lightness, and line width (Slocum §13.3.2, §13.3.3). Muehlenhaus ranks an interactive map's parts in five levels, with the title, the thematic layer, and the legend on top and attribution and tooltips at the bottom (ch. 9). Spread the levels apart, since "Average hierarchy is almost always bad hierarchy." (Muehlenhaus ch. 9).

Squint at the PNG, or blur it. The data, the title, and the legend must still dominate (Slocum §13.3.2).

## Figure and ground

Screen the basemap back so the data comes forward (Slocum §13.3.4, §13.4.3.2):

- Draw boundaries in light gray, about 30%, never black.
- Tint land and water light and low in saturation. Saturated cyan water competes with the data (P27).
- Put the thematic layer under the basemap's labels, and mute the labels.
- Make points and lines darker than what lies under them. Make an area you want to stand out lighter than its surroundings, as land on water.

Give each layer its own band of lightness, and check that the bands stay apart in grayscale (Munzner §12.5.2). Warm hues come forward and cool ones recede, so keep the warm ones for the data (Slocum §10.5.1). Put no hillshade or shadow under a choropleth, because it reads as marks and shifts the class colors (Munzner §6.3.5).

The quietest basemap is none. A world choropleth needs only its own polygons, cropped to the latitudes they cover, which is the template's default under a CRS (`frame` none). Draw the sphere, its ocean, and a faint graticule only when the reader needs the globe's shape, and say why in `dm-spec.decisions`.

## Map elements

Each element answers a need of the reader, or it stays off (Slocum §11.4). Place them largest first, keep the mapped area as large as the frame allows, and avoid a top-heavy layout (Slocum §11.4.2, §13.3.5). The map is the largest element: on an interactive page it takes most of the window, and in a static figure it fills its column. A companion that pushes it under about two fifths of a figure's height, or a side panel that leaves it under about half the window's width, costs more than it adds, and `check` names the block that crowds it.

- **Title.** It states the point, in a sentence the data supports: *Homes heat with wood most in the northern hills* rather than *Wood heating by county*. A subtitle under it gives the theme, the unit, the region, and the date. Leave out the word *map* and any abbreviation (Muehlenhaus ch. 9; Slocum §11.4.4).
- **Legend.** It defines every thematic symbol at the map's own size and color, and it says how to read them, with the unit, the method and class count, what high and low mean, and no data (Muehlenhaus ch. 9; Slocum §11.4.5). It shows at load, and no heading reads Legend.
- **Source and date.** Set in the smallest type, after the word Source, under the legend. Name the thematic data and its date, and the projection when its distortion bears on the reading (Slocum §11.4.6).
- **Scale bar.** Only when distance helps the theme, and never on a world or continental map, where the scale changes across the map (Slocum §11.4.7).
- **North arrow.** Only when north isn't up or the map serves navigation (Slocum §11.4.8). "It is a common misconception that every map needs a north arrow." On a world map, label the graticule instead when latitude matters.
- **Frame and neat line.** None on screen, where the window frames the map (Slocum §11.4.1).
- **Inset.** Only for a question the main map can't answer, such as a crowded area or a detached territory (Slocum §11.4.3; Muehlenhaus ch. 9).
- **Notes.** Write the finding on the map, beside the place it is about, in a short note with a leader, through `dm-spec.annotations`: the six highest rates named where they sit, a new route named along its line. One to four notes; more turn the map into a caption. A place the title names that the opening view can't show gets a note too, which on a globe draws at the rim.

## Type and labels

Use at most two type families, and one on a simple map. On screen, set everything in a sans-serif system stack such as `system-ui` (Slocum §12.4, §12.3.1; Muehlenhaus ch. 11). No decorative or script faces. Use bold sparingly, and keep italic for water and for publication titles in the source line (Slocum §12.4).

Step type sizes at least 2 pt apart, about 2.7 CSS px; Slocum's rule is to "avoid differences of less than 2 points if possible" (§12.4). Set nothing smaller than about 9 px (Munzner §6.3.6). Set labels in title case and sentences in sentence case (Slocum §12.3.1).

Place point labels in Slocum's order of preference, which puts the symbol left and the label right, as in a legend. The order runs upper right, lower right, upper left, lower left, above, below, right, and left (§12.5.2). In MapLibre, `text-variable-anchor` names the corner of the label that touches the point, so that order is:

```json
"text-variable-anchor": ["bottom-left", "top-left", "bottom-right", "top-right", "bottom", "top", "left", "right"],
"text-radial-offset": 0.6
```

- Never let a road, border, or flow come between a point and its label, and never letterspace a point label (Slocum §12.5.2).
- Set line labels just above the line, following its trend, and repeat them along a long line rather than spreading the letters. In MapLibre that is `symbol-placement: line`, a low `text-max-angle`, `symbol-spacing`, and `text-keep-upright` (Slocum §12.5.3).
- Set an area label in capitals, letterspaced with `text-letter-spacing`, only when it fits inside the area. A small area gets a point label outside it (Slocum §12.5.4).
- Keep halos thin, in the color of the fill beneath (Slocum §12.5.1).
- Place larger, more important labels first, with `symbol-sort-key` (Slocum §12.5.1).

## The default look and style drift

An agent's default map has gray fills with thin black outlines, light-blue water, Roboto, and zoom buttons, a north arrow, and a scale bar that nobody decided on (Muehlenhaus ch. 8, ch. 9; P23). Muehlenhaus sums it up, "Default is average. Average is rarely good." (ch. 9). The templates start with none of it, and every element is a decision in `dm-spec`.

Each edit can silently reset a font, a basemap, or a legend, which Muehlenhaus calls style drift (ch. 8). Apply his countermeasures:

1. Declare the style once and refer back to it. The `dm-spec` block is the declaration, so re-read it before each edit.
2. Start from a named template, `datamap.py new`, never from a page written from memory.
3. Change one thing per edit, in the order layout and basemap, color, type, symbols. Never restyle and restructure in one edit.
4. After each edit, run `check`, which compares the rendered fonts, controls, and colors with `dm-spec`.
5. Justify each choice against a rule, and give no weight to praise of your own output. Step 7's cold reader judges the map.

## Saying no to controls

Add a control only when the brief names the question it answers, because "every interface element should correspond to a real question the map is prepared to answer." (Muehlenhaus ch. 9). That rules out zoom buttons, fullscreen, geolocation, layer toggles, sliders, and search by default. An exploratory reader who must see more flows than a static cut shows is such a question, and `reveal` answers it with one slider that opens on the stated cut. Panning and zooming by gesture and keyboard stay. Turn rotation off on a north-up map. List every control in `dm-spec.controls`; `check` fails any control the list leaves out (P23).

Set the zoom and pan limits from the data (P25):

- `minZoom` shows the whole extent and little more (Munzner §11.5.3).
- `maxZoom` stops at the data's resolution. That is the zoom where the boundary file reaches its source scale (`projection.md`), or the zoom that shows the smallest unit clearly, whichever comes first (Muehlenhaus ch. 9; Munzner §11.5.3).
- `maxBounds` is the union of the data's extents plus 4° of longitude and 3° of latitude on each side (Muehlenhaus ch. 9).

## Interaction

Show the overview first, then zoom and filter, then details on demand (Munzner §6.7). The map opens on its whole extent, and the message reads at load, before any interaction (Muehlenhaus ch. 6).

- A hover is a glance. The tooltip shows the name and one value with its unit, and the raw count and denominator beside a rate. `dm_tip` holds that text (Muehlenhaus ch. 13, ch. 15).
- A click may open two or three more fields, never a panel that covers the map (Muehlenhaus ch. 15).
- Show a hovered feature by its outline, with a line layer driven by `feature-state`. A fill change hides the feature's class (Munzner §11.4.2).
- Every hover also works on tap and on keyboard focus, and nothing essential lives only in a tooltip.
- A selection in a companion chart lights the same features on the map, and the reverse (Slocum §24.4.5).
- Show which filters are on, and give the reader a way back to the overview (Munzner §13.2; Muehlenhaus ch. 15).

## Motion

Nothing moves at load, so the page has no autoplay, no loop, and no pulsing symbols (Muehlenhaus ch. 14; P26). Motion starts only on the reader's action, has pause and stop, and turns into instant changes under a reduced-motion setting. MapLibre's paint properties fade over 300 ms by default, so set `transition: {duration: 0}` where a value should cut. `idioms/time.md` holds the rules for change over time.

## Attribution

Credit every basemap and every data source with its license and date, in the attribution control and the source line (Muehlenhaus ch. 5). Left unasked, an agent omits credits or invents them. Check each credit against the source's own license or about page before it ships, and never write a credit you haven't seen. ColorBrewer's palettes carry their Apache-2.0 notice in `palettes.json`, and Natural Earth is in the public domain.

## Privacy is a data step

Aggregate or mask sensitive locations before the data reaches the page. A heat map or grid drawn over raw points still ships the points in its source (Muehlenhaus ch. 5; P35). Sensitive means people's homes, health records, victims of crime, rare species, and counts small enough to identify someone (Slocum §26.3).

Aggregate to grid cells or coarser units, or displace each point by a random offset within a stated distance, and strip names and identifiers from the properties. Muehlenhaus's examples are 100 m cells, masking within 1 km, and displacement within 500 m; none is a standard, so record the choice in the brief's Sensitive line. Call displacement masking. Muehlenhaus labels it differential privacy, but that term means noise calibrated to a privacy budget with a provable bound, and random displacement gives no such bound.
