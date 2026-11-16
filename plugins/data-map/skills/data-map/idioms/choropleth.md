# Choropleth

The chooser's row in `SKILL.md` for a rate, ratio, or density per area. A classed choropleth fills each enumeration unit with the color of its class, so the reader sees the pattern and compares regions. This file applies from step 3 to step 7.

## When it fits

A choropleth fits a standardized value (a rate, a ratio, a density, a median) for a phenomenon close to uniform inside each unit, or a message about the typical value per unit (Slocum §14.3, §4.6.5). Go back to the chooser when one of these holds:

- The data are counts. A count tracks unit size, so totals take the proportional-symbols row (Slocum §4.6.2).
- The phenomenon clusters inside units and a finer layer says where it can occur (land cover, zoning, buildings). Take the dots-and-density row's dasymetric map (Slocum §15.1).
- The phenomenon is a smooth field measured at stations, such as air temperature. Take the isarithmic row.
- A few small units hold most of the total, as cities do. Take the cartogram row, or put total symbols over the rates with the multivariate row (Slocum §19.1, §21.3.1.2).
- The reader looks up values for named places, or there are only a handful of places. Take the no-map row (Munzner §6.4).

## Default lies

1. **Raw Data Distortion** (Muehlenhaus ch. 13). Units filled by a count look highest because they are largest. The guardrail is a denominator in the brief and in the legend title; `classes` fails a count given without `--per` (P1).
2. **Internal Uniformity** (Muehlenhaus ch. 13). One flat color claims the value holds everywhere in the unit, and readers infer that change happens only at unit lines (Slocum §4.3.3). The guardrail is the brief's Location line saying why these units fit the phenomenon, and the dasymetric or dot row when they don't. No numbered pitfall covers it, so the critique names it.
3. **Projection Sensitivity** (Muehlenhaus ch. 13). A world or continental choropleth in Web Mercator inflates the high latitudes and the classes they hold. The guardrail is the equal-area CRS that `crs` names (P10), with no Web Mercator tiles under it (P11) and densified edges (P12).
4. **Classing as rhetoric.** Muehlenhaus calls the classing choice rhetorical (ch. 13). Equal intervals on skewed data put nearly every unit in one class, and a few outliers flatten the rest. The guardrail is the method `classes` picks from the skew and the fit, with its reason in the brief (P5, P6).
5. **A scheme against the data's logic.** A rainbow on ordered data, or a diverging scheme with no meaningful midpoint, implies differences the data lack (Slocum §14.4.1). Red against green fails color-vision-deficient readers. The guardrail is the scheme type in the brief and the CVD check in `classes` (P7, P8).
6. **The unit is the result.** Other boundaries, or another unit level, draw another pattern from the same data, which is the modifiable areal unit problem (Munzner §13.4.2). The guardrail is the unit level named in the subtitle, and a second level tried whenever the claim rests on the pattern.
7. **Small denominators read as certain.** A unit of 300 people with a handful of events tops the map with the confidence of a city. The guardrail is `--min-den`, which flags `dm_low_n` units for their own style and a legend note (P4).
8. **No data drawn as the lowest class.** A missing unit reads as low. The guardrail is the no-data class `classes` writes, with its own neutral color and swatch (P9).

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**Standardize.** Choose the denominator from the message, since each standardization of the same counts draws a different pattern (Slocum §14.3). A rate divides by the population at risk. A density divides by the area where the phenomenon can occur, so wheat yield is bushels per harvested acre, not per county acre (Slocum §14.3). The denominator has to grow with the unit, so a ten-year mean (divided by a constant ten) is still a total. Profile the join first, because a key that matches nothing drops a place silently (P3).

```sh
python3 <skill>/scripts/datamap.py inspect turnout.csv counties.geojson --join turnout.csv:geoid=counties.geojson:GEOID
python3 <skill>/scripts/datamap.py classes turnout.csv --field ballots --per eligible_voters --scale 100 --geo counties.geojson --key geoid --min-den 500 --layer turnout --out-dir map/data
```

**Classed or unclassed.** Classed by default. A reader matches a unit to a class far more reliably than to a shade on a ramp. As Slocum puts it, "The high accuracy of unclassed maps, however, is mathematical, not perceptual." (§14.6.3). Go unclassed only when the task is the overall pattern or the shape of the distribution, the data aren't heavily skewed, and hover gives each value (Slocum §14.6), and record it under Departures. Either way, look at an unclassed preview first to see where the values cluster (Muehlenhaus ch. 13).

**Method and class count.** Left to `auto`, `classes` takes quantiles for ordinal data and for maps that will be compared, Jenks when skewness exceeds 1, and equal intervals or standard deviations near normal. It picks the smallest k whose GADF reaches 0.80, from 3 to 7 and at most 6 on one hue (Slocum §5.8.3). Override it only for a reason the reader shares, such as round breaks at a meaningful value (the national rate) when the map is one of a set (Slocum §5.10), or head/tail breaks when the rare high values of a heavy tail are the story (Slocum §5.9). `classes` prints the fit of every candidate, so compare natural breaks, quantiles, and equal intervals before accepting one (Muehlenhaus ch. 13). Muehlenhaus prompts for 4 to 6 classes (ch. 13); the lever's 3 to 7 holds, and his range is a good default inside it.

**Scheme.** Sequential by default, light for low and dark for high, on a light background or a dark one (Slocum §14.4.1, §14.4.11). Lightness carries the order and hue only helps (Munzner §10.3). Diverging only around a midpoint the reader cares about, such as zero change, the national rate, or 50 percent, and inside the data's range (`--scheme div:MID`) (Slocum §14.4.1). Qualitative hues only for categories. Keep the lightest class visible against the page and apart from the no-data gray (Slocum §14.5.1.1), and keep large fills low in saturation (Munzner §10.3.1). Read `reference/color-and-classes.md` for the palettes.

**Projection.** At world or continental extent, register the equal-area CRS that `crs` names (Equal Earth for the world, Lambert azimuthal equal-area for a continent, Albers for a mid-latitude country), and draw GeoJSON or tiles cut in that grid (Slocum §9.3). At the extent of a city, Web Mercator's area error is negligible (Slocum §9.4.4), and `crs` names it. Across a state such as Kansas its area scale already changes by 9%, so a state takes Albers (`reference/projection.md`). deck.gl and mln-rs draw no CRS, so a world choropleth on either is a Departure. Read `reference/projection.md` for the definitions.

```sh
python3 <skill>/scripts/datamap.py crs --extent world --idiom area
python3 <skill>/scripts/datamap.py geo --countries --densify 100 --lon0 11.6 --out map/data/base-countries.geojson
```

**Small denominators and certainty.** Set `--min-den` to the smallest denominator whose rate the brief trusts, draw flagged units with a light hatch or a dashed outline, and print the count and denominator in the tooltip beside the rate (Muehlenhaus ch. 13). Flag only the units whose rate the reader could misread: a hatch over a large, thinly settled unit with an ordinary rate, such as Greenland at zero, becomes the loudest texture on the map and points at nothing. Keep a flagged unit on the map with its counts in an annotation, such as "1,177 per million, from 4 cases among 3,400 people", rather than dropping it; a dropped unit hides both the place and the reason to doubt it. For survey estimates, compute the coefficient of variation (the 90 percent margin of error over 1.645, divided by the estimate) and show it as a pattern overlay or an adjacent map, labeled certainty rather than uncertainty (Slocum §26.6.1.1, §26.6.2). The low estimates are usually the unstable ones (Slocum §26.6.1.1).

**Units.** Choose the finest units whose rates stay stable, and units of similar size where the data allow it, since the largest units carry the most visual weight and the largest error (Slocum §14.3). Name the unit level in the subtitle. If a claim holds at one level only, it is a finding about the units, because "changing the boundaries of the regions used to analyze data can yield dramatically different results" (Munzner §13.4.2).

## Legend and labels

- The title states the point. The subtitle names the measure, the denominator, the unit level, and the period, as in `Turnout, percent of eligible voters, by county, 2024` (P24).
- Draw the legend from `legend.json` only. Its labels round to the data's precision and put "to" between limits, which reads correctly with negatives (Slocum §5.3, §14.7).
- Run the swatches horizontally, low on the left, touching, with the numbers below them (Slocum §14.7).
- Set the no-data swatch apart from the ramp, and add a line for low-denominator units when any are flagged (P9, P4).
- Add a strip of unit values above equal-width boxes when the distribution is part of the message (Slocum §14.7).
- Label only the units the point names. The ramp carries the rest.

## Interaction

- Hover shows `dm_tip`, which holds the name, the rate with its unit, and the count over the denominator (Muehlenhaus ch. 13).
- Mark a hovered or selected unit with an outline, never a recolor, which hides its class (Munzner §11.4.2).
- Offer a classing or scheme toggle only on an exploratory map, and say so in the brief (Slocum §24.4.2).

## Companions

- A sorted bar chart or dot plot of every unit's value, for ranking and lookup (Munzner §12.3.2).
- A histogram with the class breaks drawn on it, which shows what the classing did.
- Total symbols over the rates, when the count matters as much as the rate (Slocum §21.3.1.2). That second layer reads the multivariate row's file.

## What to look for in the render

- If the largest units carry the pattern, the map may be showing unit size. Check them against their denominators.
- Every class appears on the map, and none is empty (P6).
- The lightest class stands apart from the page and from the no-data gray.
- Under a CRS, coastlines and long boundaries curve smoothly, and no tile basemap is drawn in Web Mercator (P11, P12).
- In grayscale, the classes still read in order (Munzner §6.9).
- Small units the point depends on (islands, city-states) are visible. If one is a speck, add an inset or a symbol.
