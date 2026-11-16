# Dots, bins, and density

The chooser's row in `SKILL.md` for many events, or counts with a known spread inside each unit. Dot maps, dasymetric maps, hex bins, and heat maps show where things are dense, not how units compare. This file applies from step 3 to step 7.

## When it fits

The row fits raw totals whose spread inside units matters, and individual events whose density is the message (Slocum §18.1, §4.6.4). Pick the form from the data and the reader's need:

| Form | Fits | The reader gets |
| :-- | :-- | :-- |
| Dot map | unit totals with a layer saying where they can occur, or events | the pattern, and counts with a density legend |
| Dasymetric map | unit totals and a finer layer of where they can occur | density inside units, drawn as a choropleth |
| Hex or grid bins | many points, past about 40 percent overlap | a count per equal-area cell |
| Heat map | many points, where an impression of density is enough | a smooth surface with its bandwidth stated |

Go back to the chooser when the phenomenon is uniform inside units (the choropleth row), when the reader compares totals per place (the proportional-symbols row), or when a smooth field is sampled at stations (the isarithmic row). Dots scattered through large units with no layer to place them show no real pattern, and proportional symbols say the same thing honestly (Muehlenhaus ch. 13).

## Default lies

1. **The Dot Map's Default Lie** (Muehlenhaus ch. 13). Dots claim the phenomenon is where they are, when they often show where people live or where someone looked, so a map of sightings is a map of observers. The guardrail is one sentence on the map saying whether the pattern may mirror population or reporting effort (Muehlenhaus ch. 13).
2. **Even or centroid placement.** Dots spread evenly through each unit, or stacked at its centroid, make density jump at unit lines (Slocum §18.3.3.1). The guardrail is placement from masks and weights (P29).
3. **Clumps and holes.** "Pure randomness is also not desirable" (Slocum §18.3.3.1), since chance alone clusters dots, and an unseeded run moves every dot (Slocum §18.3.3.2). The guardrail is a minimum spacing and a fixed seed (P29).
4. **How Heat Maps Lie** (Muehlenhaus ch. 13). A smooth gradient implies precise locations where the bandwidth decides the shape, and halos run past the edge of the data. The guardrail is the bandwidth stated in meters, or bins instead (P28).
5. **The bin is the result.** Bin size and placement change the pattern, as unit boundaries do (Munzner §13.4.2). The guardrail is the bin size in the legend, with one size up and one size down tried before any claim.
6. **Hidden dasymetric assumptions.** Land cover read as population, forests zeroed though people live in them, units dropped because no zone admits them (Slocum §15.4, §15.6.3). The guardrail is every ancillary source and exclusion named on the map (Slocum §15.6.1).
7. **Precise sensitive points.** Exact homes, nests, or one event alone in a sparse cell (P35).
8. **A palette that alarms.** A rainbow ramp (P7), or a red end on data that carries blame (Muehlenhaus ch. 13).

## Decisions

Make these in order at steps 4 and 5, and copy each choice and its reason into the brief.

**Dot value and size.** Choose them so the "dots in the densest area should just begin to coalesce" (Slocum §18.3.2), tuning on the densest unit. A small unit value implies false precision, and a large one loses the pattern (Slocum §18.3.2). Draw dots of 3 to 5 px (Muehlenhaus ch. 13), and round the unit value (25, 50, 100, 200, 500), changing both with zoom on the web (Slocum §18.5). If readers must estimate counts, keep dots from coalescing and add a three-density legend (Slocum §18.3.4).

**Dot placement.** Limiting layers (water, parks, steep slopes) forbid places, related layers weight the odds, and a few dots stay in near-miss classes because land cover is often misclassified (Slocum §18.3.1). With no ancillary layer, weight dots toward denser neighbors so density doesn't step at unit lines (Slocum §18.3.3.1). Place dots evenly with a random component, rejecting any closer than a minimum spacing, from a fixed seed (Slocum §18.3.3.2). For several categories, shuffle the draw order so no group hides another (Slocum §15.7). No `datamap.py` command places dots, so write a seeded script and keep it with the project.

**Dasymetric method.** Start from raw totals, move them into the zones where they can occur, and finish with the density over the inhabited area (Slocum §15.3). The limiting-variable method was the most accurate in Eicher and Brewer's test. It caps the density of low classes (15 per km² in forest, 50 in farmland) and moves the excess into urban zones (Slocum §15.5). Decide what happens to a unit with no inhabited zone, and record it (Slocum §15.6.3). Then class the density as the choropleth row does.

**Bins.** Use hexagons or squares of equal area in an equal-area CRS, or H3 cells, which are close to equal area. Each cell has the same area, so its count is a density, and `classes` accepts it with `--already-normalized`. State the cell size. Muehlenhaus's 100 m hexagons for a city's trees are a starting value for that scale, not a rule (ch. 13).

```sh
python3 <skill>/scripts/datamap.py classes hex500.geojson --field trees --already-normalized "equal-area 500 m hexagons" --layer trees --out-dir map/data
```

**Heat maps.** Use one only for an impression of density, never for counts, since bins can report the count in each cell (Muehlenhaus ch. 13). State the bandwidth in meters and hold it in ground units across zooms; MapLibre's `heatmap-radius` is in pixels, so it has to grow with zoom. Use a sequential ramp, light to dark, and a single hue or yellow-green-blue for data that carries blame, such as crime (Muehlenhaus ch. 13).

**Privacy.** Mask or aggregate before the data reach the page, because a heat or bin layer drawn from raw points still ships every point to the reader. Aggregate to cells, displace each point within a stated radius (Muehlenhaus gives 500 m and 1 km as examples, ch. 5), and strip names and identifiers. Call displacement masking, not differential privacy, which bounds what one record reveals and needs a privacy budget. Suppress cells whose count would identify someone, at a threshold the data's owner sets, and write it on the brief's Sensitive line (P35).

## Legend and labels

- State the dot value and size, as in `1 dot = 50 trees`, and add a three-density legend when counts matter (Slocum §18.3.4).
- State the bin size or the bandwidth with its unit.
- Name the ancillary sources and the exclusions of a dasymetric map (Slocum §15.6.1).
- Put the sentence on what the pattern may mirror, and the masking note, under the legend.

## Interaction

- Change dot size and value with zoom (Slocum §18.5), and cap the zoom where masking would stop protecting anyone.
- Bins show their count on hover, which a heat map can't (Muehlenhaus ch. 13).
- A multi-category dot map gets a toggle per category (Slocum §15.7, §21.4.2.2).

## Companions

- A table or sorted bars of the unit totals, the numbers the dots stand for.
- For several categories, small multiples with one category in each (Slocum §15.7).

## What to look for in the render

- In the densest area, dots just touch. Elsewhere the pattern reads as a pattern, not sparse noise.
- No dots fall in water or masked zones, and density doesn't step at unit lines.
- Two renders give identical dots.
- No heat halo spreads past the last point.
- At the deepest zoom, no point lands on a findable home.
