# Cartograms

The chooser's row in `SKILL.md` for totals where land area misleads. A cartogram resizes each unit by its total, so the reader compares people or output instead of land, and it always comes with a way back to the standard map. This file applies from step 3 to step 7.

## When it fits

A cartogram fits raw totals per unit (people, votes, output) when small units hold large totals and the standard map's area bias misleads, as when a capital city is a speck on the map and a large share of the cartogram (Slocum §19.1, §19.3.2.1). Go back to the chooser when one of these holds:

- The value is a rate. A rate's range is too narrow to resize units clearly, so map it on the choropleth row (Slocum §19.1).
- The units are regular and similar in size. A choropleth with proportional symbols reads better there, 65 against 47 percent correct on complex questions (Slocum §19.6.1). Take the multivariate row.
- The reader needs exact values. Take the no-map row.

Muehlenhaus warns against reaching for a cartogram for analytical credibility; it is a rhetorical form, and its emphasis has to be the brief's point (ch. 13).

## Types

Pick the type from the task (Slocum §19.3 to §19.5):

| Type | Keeps | Choose it when |
| :-- | :-- | :-- |
| Contiguous | topology, shapes bent | most tasks; readers did best with it (Slocum §19.5.2) |
| Dorling circles | rough position | the big picture, with an inset map (Slocum §19.4.2) |
| Demers squares | rough topology | readers estimate ratios (Slocum §19.4.3) |
| Noncontiguous | shape and position | recognizing places matters more than adjacency (Slocum §19.5.2) |
| Tile or grid | one cell per unit | every unit must show, each labeled, used with caution (Slocum §19.4.4) |
| Mosaic | integer cells | readers count whole units, such as seats (Slocum §19.3.3) |
| Balanced | physical size, floored | sparse places must not vanish (Slocum §19.6.3) |

Never draw a rectangular cartogram for general reading. "Rectangular cartograms were clearly the least effective approach." (Slocum §19.5.2).

## Default lies

1. **A Cartogram's Lie** (Muehlenhaus ch. 13). The distortion is presented as the truth, when it is emphasis, possibly of a variable that doesn't matter, and readers lose their bearings. The guardrail is the toggle back and an inset of the standard map (P30).
2. **No way back.** A cartogram alone leaves readers unable to find places they know (Slocum §19.3.2). The guardrail is a toggle, a morph, or the standard map beside it (P30).
3. **Sparse places vanish.** A population cartogram reverses the problem it solves, because "the areas of lowest population density become the smallest on the map" (Slocum §19.6.3). The guardrail is a balanced cartogram with a minimum size, when the sparse places matter to the point.
4. **A rate as the size.** Units resized by a percentage barely change (Slocum §19.1). The guardrail is the brief's Data line, which names the total that sets the size.
5. **Shifting layouts.** Cartograms recomputed for each period move every unit, so change can't be seen (Slocum §19.4.3). The guardrail is one stable layout across periods.

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**Size and fill.** Size each unit by its total, unclassed, since the wide range of areas keeps sizes distinct (Slocum §19.3.1). Fill with a muted color, or with a rate on a classed scheme. With irregular units, a contiguous cartogram filled by a rate was nearly as good as a choropleth with symbols, at 67 percent correct against 71 (Slocum §19.6.1).

**Compute it offline.** No `datamap.py` command builds a cartogram. Make a contiguous one with go-cart.io, which implements the Gastner and Newman method (Slocum §19.3.2). For Dorling circles, `sizes` gives each unit an area-true radius, and a seeded force layout then separates the circles. Limit the attraction to a distance threshold so the overall geography holds (Slocum §19.4.2). Demers squares take a side proportional to the square root of the total.

```sh
python3 <skill>/scripts/datamap.py sizes countries.geojson --field population --scaling area --rmax 40 --layer dorling --out-dir map/data
```

**The way back.** It is required (P30). An interactive map gets a toggle or an animated morph to the standard map, with linked selection between the two (Slocum §19.3.2). Switching by animation more than halved readers' errors on overview questions (Slocum §19.3.2). A static map puts the standard map beside the cartogram, or as an inset that marks the selected unit (Muehlenhaus ch. 13).

**Labels.** Label the units the point names, and every unit on a tile map. A gridded cartogram distorts more, so label its key places (Slocum §19.3.2.1, §19.4.4).

**Over time.** Keep one layout for every period, and size every period on one scale (Slocum §19.4.3).

**Without distortion.** When bent shapes are unacceptable, a value-by-alpha map fades units by their totals on a black background. It spotlights where totals are large but gives no values (Slocum §19.6.2).

## Legend and labels

- State that size shows the total, not the land area, in the subtitle and the tooltip (Muehlenhaus ch. 13).
- A simple box legend with the total it stands for is enough. Grid lines and extra keys didn't raise accuracy (Slocum §19.3.2).
- The title states the point (P24).

## Interaction

- The toggle or morph back to the standard map, and a reset.
- Hover shows the name, the total, and the land area (Muehlenhaus ch. 13), and marks the same unit on the inset.

## Companions

- The standard map, always, as the inset, the toggle, or a panel beside the cartogram.
- Sorted bars of the totals, for exact comparison.

## What to look for in the render

- A reader can find three named units without the inset.
- The way back is on the page, and `dm-spec` lists it.
- Areas match totals. Measure two units whose totals differ fourfold.
- Sparse units the point needs are still visible.
- Dorling circles don't overlap, and neighbors stay roughly in place.
