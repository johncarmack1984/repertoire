# Proportional symbols

The chooser's row in `SKILL.md` for totals at points or per area. Each point, or each unit's center, gets one symbol whose area is proportional to its total, so the reader compares amounts across places. This file applies from step 3 to step 7.

## When it fits

Proportional symbols fit raw totals (visitors, megawatts, households) at points or per unit, where the reader compares amounts (Slocum §4.6.2). Go back to the chooser when one of these holds:

- The value is a rate or a density. Take the choropleth row.
- The data are many events, and density is the message. Take the dots-and-density row.
- The reader ranks places or reads exact values. Readers judge area with a Stevens exponent near 0.7, well below length (Munzner §5.5.1), so a sorted bar chart beside the map, or the no-map row, does that job.
- The totals mostly mirror population, as births mirror city size (Slocum §17.3). Map the rate instead, or pair the rate and the total with the multivariate row.
- The range is narrow, such as 3.3 to 22.7 percent, so true scaling draws near-equal circles (Slocum §17.3). Use a choropleth, or graduated symbols below.

## Default lies

1. **The Look-Right-Is-Wrong Error** (Muehlenhaus ch. 13). The radius grows with the value, so a value four times larger draws sixteen times the area, and "LLMs will cheerfully scale symbols by radius instead of area unless you explicitly prohibit this." The guardrail is `dm_r`, which `sizes` writes true to area; the page never computes a radius (P13).
2. **Exact magnitudes read from area** (Muehlenhaus ch. 13). Readers underestimate large symbols (Slocum §17.5.2), and nobody reads a quantity off a circle. The guardrail is a nested legend of three round values, a note that areas are proportional to the totals, and the value in the tooltip (P14).
3. **Collisions in small, dense units** (Muehlenhaus ch. 13). Big symbols bury small ones and the base beneath. The guardrail is largest-first order from `dm_order`, fills at 75 percent opacity, and a thin light outline (Slocum §17.7.2) (P14).
4. **A population map in disguise.** Totals that track population show where people live, and big units collect big totals (Slocum §4.6.2, §17.3). The guardrail is the brief's Supports line, which says whether totals or rates answer the question.
5. **Range grading that invents pattern.** Graded classes draw 10 and 11 percent far apart when they straddle a break, and readers skip the legend (Slocum §17.5.3). The guardrail is grading only ranges that mean something, with each class range labeled.
6. **Clamped ends.** A minimum radius, or software that rescales between a smallest and a largest size, breaks proportionality at the ends (Slocum §17.5.1). The guardrail is no `--rmin` unless the smallest symbols vanish, and a legend note when one is set (P13).

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**Proportional or graduated.** Proportional (unclassed) by default, so the symbols keep the ratios in the data (Slocum §17.5.3). Graduated symbols, 3 to 5 classes with clearly distinct sizes, fit a narrow range or a task that needs only the pattern (Slocum §17.5.3; Muehlenhaus ch. 13), and `--scaling graduated:4` gives four classes.

**Scaling.** Scale area to value, `r = rmax * sqrt(v / vmax)` (Slocum §17.5.1). The sources disagree on correcting for underestimation. Flannery's apparent-magnitude scaling (exponent 0.57) is in wide use (Slocum §17.5.2), but Slocum's own review leaves it unsettled (§17.5.2.2), Muehlenhaus calls it outdated (ch. 3), and three legend circles alone bring readers' estimates near true, at an exponent of 0.94 (Slocum §17.5.2.2). The skill scales by area and lets the legend do the correcting. `--scaling flannery` is a Departure with its reason. Muehlenhaus also offers log scaling when outliers dominate (ch. 13), but a log scale breaks the area relation, so send outliers to graduated symbols instead.

```sh
python3 <skill>/scripts/datamap.py sizes solar-plants.geojson --field megawatts --rmax 28 --scaling area --layer solar --out-dir map/data
```

**Symbol.** Circles by default, because they are compact, stable, and overlap least (Slocum §17.4). Squares when estimating area is the task, since readers judge them better, at an exponent of 0.93 (Slocum §17.5.2.1). No spheres, cubes, or extruded columns. Readers underestimate them badly (Slocum §17.5.2.1), and extrusion is unjustified 3D (P22). Pictographs only as graduated symbols (Slocum §17.5.3).

**Largest size.** Size for some overlap but no clutter. "Unfortunately, there are no rules regarding the appropriate amount of overlap." (Slocum §17.7.1). Set `--rmax` at the design zoom so the densest cluster overlaps a little while its smallest member stays visible. A map that argues for a concentration may accept more overlap (Slocum §17.7.1). Muehlenhaus prompts for 8 to 80 px (ch. 13); treat that as a starting range, not a rule.

**Draw order and opacity.** Draw the largest first, through `circle-sort-key` on `dm_order` in MapLibre or data order in deck.gl. Fill at 0.75 opacity with a thin light stroke (Slocum §17.7.2); Muehlenhaus's 0.7 is close enough (ch. 13). Never displace symbols on a zoomable map, which was the least effective fix tested (Slocum §17.7.2).

**Location and zoom.** Put each symbol at its point, or inside its unit at the centroid, moved inward when the unit's shape puts the centroid outside it. When large symbols belong to small units, a necklace map rings them around the region (Slocum §17.8). On a zoomable map, scale every radius by one zoom factor so the ratios hold at each zoom.

## Legend and labels

- Nest three circles from `legend.json` (`legend_values` and `legend_radii`), with a leader line to each value. The values are round, span the data, and include the largest (Slocum §17.6.2).
- The legend draws with the radii the map uses, never with a scale of its own.
- Add the note that circle areas are proportional to the totals (Slocum §17.5.2.2).
- Graduated symbols list each class range beside its size.
- The title states the point, and the subtitle names the total, its unit, and the year (P24). A clamp note goes under the legend.

## Interaction

- Hover shows `dm_tip`, the name and the total with its unit (Muehlenhaus ch. 13).
- At low zoom, aggregate rather than displace. A cluster's symbol is sized by its summed total, on the same scale.

## Companions

- Sorted bars of the largest totals, for exact comparison.
- A rate choropleth under the symbols when the totals track population (Slocum §21.3.1.2). That second layer reads the multivariate row's file.

## What to look for in the render

- Pick two symbols whose values differ fourfold. Their radii should differ twofold, and their areas fourfold.
- The smallest symbol in the densest cluster is visible on top.
- Each legend circle matches a map symbol of the same value.
- Every symbol's center can still be placed, and none covers a neighbor entirely.
- The base shows through overlaps, and outlines separate them.
- No symbol runs off the frame or under the legend.
