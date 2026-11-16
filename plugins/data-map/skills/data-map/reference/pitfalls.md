# Pitfalls

Step 7 walks this list after the cold reader, and review mode cites it by number, as in P13. `datamap.py` prints the same numbers in its PASS, WARN, and FAIL lines. The numbers never change, and a pitfall found later takes the next free number.

Each entry says what the pitfall looks like, why it fails, with its source, and the fix. **Held by** names what catches it. The lever is a `datamap.py` command that refuses it or computes it right. The template is the starting page, which says no to it. The check is `check`, which fails or warns on it. The cold reader is step 7's answer key. Prose means only these files hold it, so walk it by hand.

## Raw counts on an areal idiom (P1)
- **Looks like.** A choropleth or other area fill of totals, so the biggest or most populous units come out darkest.
- **Why it fails.** Totals grow with a unit's size or population, so the fill maps the denominator rather than the phenomenon (Slocum §14.3, §4.6.1).
- **Fix.** Divide by the denominator the message needs, such as people, households, or land area, or show the totals as proportional symbols.
- **Held by.** The lever and prose. `classes` fails a count without `--per` or `--already-normalized`, and the brief's Data line names the data's kind.

## A map where a chart wins (P2)
- **Looks like.** Four regions shaded on a map, or a handful of places the reader must rank or look up by name.
- **Why it fails.** Position is the strongest channel, and a map spends it on geography; a sorted list beats a map for lookup and ranking (Munzner §6.4, §8.2).
- **Fix.** Sorted bars or a table, with one line on why a map adds nothing.
- **Held by.** Prose. The chooser's first row and `idioms/no-map.md`.

## Joins that silently drop places (P3)
- **Looks like.** Countries missing from a world map because their keys didn't match, such as France and Norway under Natural Earth's ISO code -99, or a name spelled two ways.
- **Why it fails.** Unmatched units draw as no data or not at all, and the totals stop adding up (Muehlenhaus ch. 7; Slocum §15.6.3).
- **Fix.** Run `inspect --join`, fix every unmatched key, and report any left over.
- **Held by.** The lever. `inspect --join` lists the keys that match nothing on either side, and the bundled countries carry fixed ISO codes.

## Small denominators read as certain (P4)
- **Looks like.** A tiny unit in the darkest class because three events among 400 residents make a high rate.
- **Why it fails.** A rate on a small base swings with a single event, so it can't carry the confidence of a rate on a large one (Slocum §4.6.2, §26.6.1.1).
- **Fix.** Flag units under a minimum denominator, mark them on the map and in the tooltip, and show totals beside rates when the base varies widely (Slocum §21.3.1.2).
- **Held by.** The lever and the cold reader. `classes --min-den` writes `dm_low_n` and lists the units, and the answer key includes them.

## A classing method that doesn't fit the distribution (P5)
- **Looks like.** Equal intervals on skewed data, with nearly every unit in the lightest class, or breaks with no stated reason.
- **Why it fails.** The breaks ignore where the values lie, so classes sit empty and the pattern disappears (Slocum §5.4, §5.10).
- **Fix.** Choose the method by the distribution and the task, as `color-and-classes.md` sets out, and record the reason.
- **Held by.** The lever. `classes` reports skewness, GVF, and GADF, warns when equal intervals meet skewness above 1, and writes `method_reason`.

## Too many or too few classes (P6)
- **Looks like.** Nine shades of one hue, two classes, or a legend swatch no unit uses.
- **Why it fails.** Readers can't separate more than about six lightness steps of one hue, and too few classes hide the pattern (Slocum §5.8.3; Munzner §10.2.3).
- **Fix.** Between 3 and 7 classes, at most 6 for one hue, using the smallest count whose GADF reaches 0.80.
- **Held by.** The lever. `classes` clamps the count and warns outside 3 to 7 or on an empty class.

## A scheme that contradicts the data's logic (P7)
- **Looks like.** A rainbow on rates, a red-white-blue scheme on a share with no meaningful midpoint, or a one-hue ramp on change around zero.
- **Why it fails.** A rainbow has no lightness order, a diverging scheme asserts a critical value, and a sequential one hides the midpoint that exists (Slocum §14.4.1; Munzner §10.3.2).
- **Fix.** Sequential for one-sided data, diverging around a meaningful midpoint, and unordered hues for categories.
- **Held by.** The lever. `classes` offers palettes by type only and fails `div:MID` when the midpoint lies outside the data.

## Colors that color-blind readers can't tell apart (P8)
- **Looks like.** Red against green, a red-yellow-green scheme, or neighboring classes close in lightness.
- **Why it fails.** About 8% of men and 0.5% of women confuse red and green, and hue alone gives no order to anyone (Munzner §10.3.4; Slocum §14.4.3).
- **Fix.** A ColorBrewer scheme flagged safe at the class count, with neighboring classes apart in lightness, checked in grayscale.
- **Held by.** The lever. `classes` fails a palette that isn't safe at the class count.

## A legend that disagrees with the map (P9)
- **Looks like.** Legend colors or breaks that differ from the fills, or no-data units drawn as zero or in the lightest class.
- **Why it fails.** The reader decodes the map through the legend, so a mismatch misreports values, and missing data passes for low values (Slocum §11.4.5).
- **Fix.** Draw the fills and the legend from one `legend.json`, with a distinct, labeled no-data class.
- **Held by.** The lever and the check. The levers write one `legend.json` with a `nodata` entry, and `check` finds every legend color in the PNG.

## A projection that isn't equal-area for an area idiom (P10)
- **Looks like.** A world or continental choropleth or dot map in Web Mercator, with Russia, Canada, and Greenland swollen into the top class.
- **Why it fails.** Mercator inflates area toward the poles, so high-latitude units dominate and densities read wrong (Slocum §9.4.1; Muehlenhaus ch. 13).
- **Fix.** An equal-area CRS chosen by extent, as in `projection.md`, or a recorded departure on a stack without one.
- **Held by.** The template and the check. The static preset registers Equal Earth, and `check` fails Mercator under an area idiom at world extent.

## Tiles in the wrong grid (P11)
- **Looks like.** A Web Mercator basemap under a registered CRS, with coastlines that don't meet the data.
- **Why it fails.** maplibre-gl reprojects GeoJSON under a CRS but draws tiles in the grid they were cut in, so Mercator tiles land in the wrong place (maplibre-gl 6.15.0 CRS support).
- **Fix.** GeoJSON layers, or tiles cut in the CRS's own grid, each listed with its grid in `dm-spec.tiles`.
- **Held by.** The check. `check` fails a tile source whose grid isn't the CRS's.

## Long straight edges under a CRS or on a globe (P12)
- **Looks like.** A long border or a flow drawn as a straight chord across a curved projection, or a box with straight sides on the globe.
- **Why it fails.** The renderer joins vertices with straight segments, so a long edge skips the curve the projection gives a line on the Earth (Slocum §9.4.5).
- **Fix.** Densify lines and rings to about a degree with `geo --densify 100`.
- **Held by.** The lever. `geo --densify` and `flows` write densified geometry.

## Symbols scaled by radius (P13)
- **Looks like.** A value twice as large drawn with twice the radius, and so four times the area.
- **Why it fails.** Readers judge circles by area, so radius scaling inflates every difference, and "LLMs will cheerfully scale symbols by radius instead of area unless you explicitly prohibit this." (Muehlenhaus ch. 13; Slocum §17.5.1).
- **Fix.** Radius in proportion to the square root of the value, with a legend of at least three nested circles.
- **Held by.** The lever. `sizes` writes `dm_r` true to area and builds the legend from the same function.

## Big symbols hiding small ones (P14)
- **Looks like.** Small circles buried under a large one, or legend circles that don't match the map's sizes.
- **Why it fails.** Hidden symbols drop out of the reading, and a legend on another scale misreports every value (Slocum §17.7.2, §17.6).
- **Fix.** Draw the largest first, with fills at about 75% opacity and a thin outline, and build the nested legend from the map's scaling.
- **Held by.** The lever. `sizes` writes `dm_order` largest first and the nested legend values.

## Straight, overlapping, or stacked reciprocal flows (P15)
- **Looks like.** Straight lines sharing one corridor, or A to B drawn exactly over B to A.
- **Why it fails.** In Jenny's study straight flows hid each other where curved ones didn't, and a stacked pair hides one direction entirely (Jenny §3.2.3.1; Slocum §20.7.2.1).
- **Fix.** One quadratic curve per flow, bending more as it gets longer, offset to the right of travel so the two directions separate.
- **Held by.** The lever and the cold reader. `flows --geometry curved` draws them, and the answer key includes the asymmetric pairs.

## Flows under unconnected nodes, or crossing at sharp angles (P16)
- **Looks like.** A flow from A to D passing over node C, or two flows crossing nearly parallel.
- **Why it fails.** A reader takes a flow over a node to stop there, so "Flows must not pass under unconnected nodes" (Jenny §4.1), and reading time climbs steeply below a 30° crossing (Jenny §2.2.2).
- **Fix.** Flip the curve to the node's far side, then bend it more, and keep crossings near right angles.
- **Held by.** The lever and the cold reader. `flows` flips curves near unconnected nodes and reports any still too close.

## No direction, or arrowheads lost on thin flows (P17)
- **Looks like.** Plain lines on directed data, tapered lines, or arrowheads too small to see on the thinnest flows.
- **Why it fails.** The reader can't tell origin from destination; in Jenny's study arrowheads beat tapers, 51.4% against 14.2% correct on incoming flows (Jenny §3.2.3.2).
- **Fix.** An arrowhead at each destination, scaled with the width and enlarged on thin flows (Jenny §4.2).
- **Held by.** The lever. `flows` writes arrow points with `dm_arrow`, floored at a minimum size.

## A hairball, or a silent top-N cut (P18)
- **Looks like.** Every flow drawn, or the top 50 drawn with no word that 600 more exist.
- **Why it fails.** An all-pairs map can't be read, and an unstated cut implies, in Muehlenhaus's words, that "clean channels exist where messy, multidirectional movement occurs." (ch. 13; Slocum §20.7.1).
- **Fix.** Keep the top N or a share of the volume, and print what was kept and what was left out.
- **Held by.** The lever and prose. `flows --top` or `--share` writes the kept and omitted line into the legend and warns past 100 flows on a flat map or 300 on a globe, and the brief records the cut.

## Large flows drawn over small ones (P19)
- **Looks like.** A thick flow drawn last, covering the thin flows beneath it.
- **Why it fails.** The small flows vanish, and Slocum's rule is that "Smaller flow lines should appear on top of larger flow lines." (§20.4; Jenny §4.1).
- **Fix.** Sort the flows so the smallest draw last.
- **Held by.** The lever. `flows` writes `dm_order` rising as the value falls.

## Lines that wrap at ±180 or go the long way round (P20)
- **Looks like.** A Tokyo to Los Angeles route that crosses Asia, Europe, and the Atlantic, or a streak across the whole map.
- **Why it fails.** A line whose longitude jumps from about 179 to about -179 is drawn through 0, and both maplibre-gl and mln-rs render it the long way (seen in this skill's test renders).
- **Fix.** Densify along the great circle and split the line at ±180 into a MultiLineString.
- **Held by.** The lever. `geo` and `flows` densify and split at the antimeridian.

## A network drawn only on the map (P21)
- **Looks like.** A dense node-link map where the question is hubs, clusters, or which pairs connect.
- **Why it fails.** Node-link maps stop being legible past about 3 or 4 links per node or a few hundred nodes, and geography takes the position that topology needs (Munzner §9.4; Schöttler §11.4).
- **Fix.** A linked matrix or abstract view beside the map, or relaxed geography, as in `idioms/networks.md`.
- **Held by.** Prose. `idioms/networks.md`.

## Unjustified 3D (P22)
- **Looks like.** A pitched camera, extruded prisms, or raised arcs with no recorded reason, or arc height tied to the value.
- **Why it fails.** Perspective breaks comparisons of size and position, and occlusion hides data (Munzner §6.3); height by value was Yang's slowest condition and height by distance his best (Yang §4.3).
- **Fix.** Pitch 0 and flat layers, with raised arcs only at world extent, height from distance, and a recorded reason.
- **Held by.** The template, the check, and the lever. The template sets pitch 0, `check` fails pitch or extrusion without a recorded decision, and the deck.gl page sets each arc's height from `dm_km` alone.

## The LLM default look and elements nobody decided on (P23)
- **Looks like.** Gray fills with thin black outlines, light-blue water, and Roboto, or a north arrow, zoom buttons, or a scale bar on a world map, or three font families.
- **Why it fails.** Defaults flatten the hierarchy and add parts no reader needs, and scale and north change across a world map (Muehlenhaus ch. 8, ch. 9; Slocum §11.4.7, §11.4.8).
- **Fix.** Decide every element and font in `dm-spec`, as `design.md` sets out.
- **Held by.** The template and the check. The template draws none of them, and `check` compares the rendered fonts and controls with `dm-spec`.

## A missing title, legend, unit, or source (P24)
- **Looks like.** No title, a title that names the dataset instead of the point, swatches with no unit, or no source and date.
- **Why it fails.** The reader can't tell what is shown, in what unit, or on whose data (Slocum §11.4.4, §11.4.5, §11.4.6; Muehlenhaus ch. 9).
- **Fix.** A title that states the point, a legend with its unit and method, and a source line with its date.
- **Held by.** The template and the cold reader. The template has a slot for each, and a critic who can't find the unit fails the answer key.

## Infinite zoom (P25)
- **Looks like.** A county choropleth the reader can zoom to one street, or pan out over empty ocean.
- **Why it fails.** It claims precision the data lack and strands the reader away from the data; "Infinite panning suggests infinite relevance. Most maps do not deserve that claim." (Muehlenhaus ch. 9; Munzner §11.5.3).
- **Fix.** Minimum and maximum zoom and bounds set from the data, as `design.md` sets out.
- **Held by.** The template. It sets the limits from `dm-spec.zoom` and the data's extent.

## Autoplay or looping motion (P26)
- **Looks like.** A map that animates at load, loops, pulses, or ignores the reader's reduced-motion setting.
- **Why it fails.** Motion is nearly impossible to ignore and pulls the eye off the data, and readers retain little from passive animation (Munzner §10.4.5; Muehlenhaus ch. 14).
- **Fix.** No motion at load, and motion only on the reader's action, with pause and stop and instant changes under reduced motion.
- **Held by.** The template and the check. The template has no animation, and `check` fails a map that is still moving when it reports ready.

## A basemap that competes with the data (P27)
- **Looks like.** Saturated cyan water, black borders as heavy as the symbols, or busy labels over the fills.
- **Why it fails.** Nothing comes forward or recedes, so the eye lands on the base first (Slocum §13.3.4; Munzner §12.5.2).
- **Fix.** Screen the basemap to light, low-saturation tones, or drop it.
- **Held by.** The template and the cold reader. The template starts with a quiet basemap or none, and the critic's first glance must land on the data.

## Interpolating what isn't a continuous field (P28)
- **Looks like.** Smooth isolines drawn from county totals, or a polished surface reaching far past its samples.
- **Why it fails.** Interpolation assumes a value everywhere and gradual change, so the surface looks equally sure where no sample exists, which Muehlenhaus calls the beautiful lie (ch. 13; Slocum §16.3; Munzner §2.4.3).
- **Fix.** Isolines only for a sampled continuous field, with the samples drawn and sparse areas marked.
- **Held by.** Prose. `idioms/isarithmic.md`.

## Dots placed uniformly or at centroids (P29)
- **Looks like.** Dots spread evenly over each unit or piled at its center, lakes and empty land included.
- **Why it fails.** The dots claim to show where things are but only restate each unit's total (Slocum §18.3.1, §18.3.3; Muehlenhaus ch. 13).
- **Fix.** Place dots inside masks drawn from ancillary data, seeded and with a minimum spacing, and say whether the pattern may only mirror population.
- **Held by.** Prose. `idioms/dots-and-density.md`.

## A cartogram with no way back (P30)
- **Looks like.** Distorted units with no toggle, inset, or linked map that shows the true geography.
- **Why it fails.** Readers lose their bearings and can't find places (Slocum §19.3.2, §19.4.2; Muehlenhaus ch. 13).
- **Fix.** A toggle or linked view to the equal-area map, and a note that size shows the variable, not the land.
- **Held by.** Prose. `idioms/cartogram.md`.

## Animation where small multiples serve (P31)
- **Looks like.** A time slider over many years, or classes recomputed for each frame so a color changes its meaning.
- **Why it fails.** Readers compare frames from memory and miss changes, and shifting breaks make one color stand for different values (Slocum §23.8, §23.9; Munzner §6.5).
- **Fix.** Small multiples or a change map, with one set of breaks across every panel (Slocum §5.1).
- **Held by.** Prose and the template. `idioms/time.md` holds the rules, and the template has no animation.

## A bivariate scheme past 3×3 (P32)
- **Looks like.** A 4×4 color grid, or three variables packed into one symbol.
- **Why it fails.** It has more cells than a reader can decode, and some readers can't read even a 3×3 grid (Slocum §21.3.2.1; Munzner §10.3.3).
- **Fix.** Three classes per variable, a diagonal ordered by lightness, and both one-variable maps beside it.
- **Held by.** Prose. `idioms/multivariate.md`.

## A blank or unfinished frame judged as the map (P33)
- **Looks like.** A screenshot taken before the tiles, fonts, or data loaded, critiqued as if it were the map.
- **Why it fails.** Every later judgment rests on a picture of nothing (Muehlenhaus ch. 17).
- **Fix.** Capture after the page signals it is ready, then test the PNG for a blank frame and for the legend's colors.
- **Held by.** The check. `check` waits on `dataMap.ready` and runs the blank and legend-color tests.

## A self-critique that praises (P34)
- **Looks like.** The builder reports that the map is clear, effective, and follows best practice.
- **Why it fails.** A model asked about its own work finds it good, which is validation bias, and a designer is a poor tester of the design (Muehlenhaus ch. 15, ch. 16; Munzner §4.6.3).
- **Fix.** The cold reader in `critique.md`, graded against a key that code computed.
- **Held by.** The cold reader.

## Precise sensitive locations (P35)
- **Looks like.** Points at people's homes, at victims of crime, or at rare species' sites, or a count of two in a small unit.
- **Why it fails.** The map identifies people or exposes what needs protecting, and a smooth surface over raw points still ships the points (Muehlenhaus ch. 5; Slocum §26.3).
- **Fix.** Aggregate or mask in the data before it reaches the page, and strip names, as `design.md` sets out.
- **Held by.** Prose and the lever. The brief's Sensitive line records the masking, and `dm_low_n` flags small counts.
