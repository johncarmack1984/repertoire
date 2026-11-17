# No map

The chooser's row in `SKILL.md` for a few places, or data whose location isn't the message. A sorted bar chart or a table wins there, because position on a common scale beats any map encoding for ranking and comparing. The file also says which companion views a map needs beside it. It applies from step 3 to step 7.

## When it fits

A map spends its most effective channel, position, on geography, so it earns its place only when the task is about spatial relationships (Munzner §8.2). Take this row when one of these holds:

- There are only a few places, and the reader ranks them or looks up their values. An ordered list shows more labels in less space and wins at lookup (Munzner §6.4).
- The task is a precise comparison. Aligned position is the most accurate channel for magnitude, while area and lightness, which a map would use, rank far below it (Munzner §5.4.2).
- The reader needs a unit's exact value. Matching one of many shades on a ramp is hard, and neighboring colors shift it (Slocum §14.6.3.1).
- The brief's Location line is empty. If the reader would reach the same conclusion with the places shuffled, the map adds nothing.

Go back to the chooser when the point is a cluster, a gradient, a neighbor, a distance, or a route. Muehlenhaus's method framework begins by asking "whether you have chosen the right method at all." (ch. 13), and this row is that check.

## Default lies

1. **A map where a chart wins.** The largest units dominate, values hide in a color ramp, and the ranking the reader wanted is nowhere on the page (P2). The guardrail is the brief's Location line, which has to say why where matters.
2. **Geography as decoration.** A map drawn because the data have place names, which adds weight and no information (P2). The guardrail is the shuffle test above.
3. **Places dropped by a join.** A table built from a failed join silently loses rows, just as a map does (P3). The guardrail is `inspect --join` before anything is drawn.

## Decisions

Make these in order, and copy each choice and its reason into the brief.

**Test location.** Write the brief's Location line before choosing. Profile the data, since the count of places and the join decide much of it.

```sh
python3 <skill>/scripts/datamap.py inspect visitors.csv parks.geojson --join visitors.csv:park_id=parks.geojson:id
```

**Sorted bars.** The default. Draw horizontal bars from zero, sorted by value, each labeled with its place's name and value, and put the place the point is about in the accent color. Position on a common scale makes the ranking exact (Munzner §5.4.2).

**A dot plot.** For two values per place, such as two years, or for values far from zero, a dot per value on one scale keeps the comparison aligned without bars that must start at zero.

**A table.** When the reader looks up exact values, or each place carries several measures, a table sorted by the measure that matters serves better than any chart (Munzner §6.4).

**Middle ground.** When ranking matters and rough location helps, linked micromaps put a small map beside each sorted group of rows, for up to about 100 units (Slocum §24.5.9). When every unit must show at an equal size, the cartogram row's tile map does it.

**Build.** Steps 4 to 6 still apply. Draw the chart with the template's SVG companion helper, render it, and check it as a map would be checked. Record the idiom as no map in `dm-spec`, and say in the report why location wasn't the message.

## Legend and labels

- The title states the point, and the subtitle gives the measure, its unit, and the period. A source line with its date closes the chart (P24).
- Label each bar at its end with its value, and drop the value axis when every bar carries its number.
- Spell out place names in full, and put them where they read left to right.

## Companions a map needs

When the map does earn its place, it rarely stands alone. Choose companions by what they share with the map (Munzner §12.3.2):

- **Different encoding, same data.** A sorted bar chart or list beside a choropleth, for ranking and lookup, linked so a selection in one marks the other (Munzner §12.3.2; Slocum §24.4.5).
- **Same encoding, part of the data.** An overview inset with the current view outlined, when the map zooms in (Munzner §12.3.2).
- **Same encoding, data split up.** Small multiples, by period or by category (Munzner §12.3.2).

The common ones by idiom are these:

- a histogram with class breaks, for a choropleth;
- a scatterplot of the two measures, for a bivariate map;
- an OD matrix, for flows and networks (Schöttler §10.3);
- a line chart of the total, for change over time.

A companion earns its place only when it answers a question in the brief that the map can't. Same data and same encoding is redundant, and views that share nothing aren't linked (Munzner §12.3.2). List each companion on the brief's Companions line and in `dm-spec`'s `companions`.

## What to look for in the render

- The chart answers the brief's question within seconds, and the top and bottom places are readable.
- The bars start at zero, and their order matches the values.
- The accent falls on the place the point is about, and nowhere else.
- Every place in the data appears, or the subtitle says which were left out and why.
