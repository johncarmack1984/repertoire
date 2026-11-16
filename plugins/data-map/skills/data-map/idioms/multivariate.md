# Multivariate maps

The chooser's row in `SKILL.md` for two measures per area. A 3×3 bivariate choropleth colors each unit by the pair of classes it falls in, so the reader finds where both measures are high, both low, or one high and one low. The row also covers a choropleth with symbols, small multiples, and the restraint that keeps a map to what a reader can decode. This file applies from step 3 to step 7.

## When it fits

Combine two measures on one map only when the reader must see them together, as when the question is where they coincide or diverge (Muehlenhaus ch. 13; Slocum §21.3.2). Otherwise pick the lighter form:

- The measures are to be compared, not combined. Use small multiples or linked views (Muehlenhaus ch. 13).
- One measure is a count and the other its rate. Size a symbol by the total and fill it, or the unit under it, by the rate (Slocum §21.3.1.2, §21.3.2.2).
- Three parts sum to 100 percent, such as a three-way vote. A ternary choropleth fits (Slocum §21.4.2.1).
- Three or more unrelated measures. Use small multiples, or map clusters of similar places as one qualitative layer (Slocum §21.4.1, §21.5).
- There is one measure after all. Take the choropleth row.

## Default lies

1. **The False Axiom** (Muehlenhaus ch. 13). More information looks better, but readers take in about three things at once (Muehlenhaus ch. 13). The guardrail is two measures per map and a 3×3 grid at most (P32).
2. **Jenks on both measures.** "The optimal method fails to reflect the high correlations between the attributes" (Slocum §21.3.1.1), so two closely related measures look unrelated. The guardrail is quantile classes on both (P5).
3. **A nominal palette.** Nine unrelated hues, as in the old Census scheme, make every unit a legend lookup (Slocum §21.3.2.1). The guardrail is a scheme whose diagonal reads as an ordered progression (P7).
4. **Channels the eye fuses.** A red axis against a green axis reads as four hues, and width against height reads as area (Munzner §5.5.3). The guardrail is separable channels, such as size with lightness, and no red-green axes (P8, P32).
5. **A bivariate map alone.** Without its legend, its two single-measure maps, and a note on reading it, readers misread it (Slocum §21.3.2.1). The guardrail is all three on the page.
6. **False coherence.** Two layers on one map read as related, and an overlay implies a cause (Muehlenhaus ch. 18, ch. 20). The guardrail is the brief's Supports line, which says whether the relation is defensible.
7. **The overloaded glyph.** Stars, faces, or rays carrying many measures overwhelm the reader (Slocum §21.4.2.3) (P32).

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**Combine or compare.** Combine only when joint reading is the task. Otherwise draw small multiples that share one projection, one extent, and one classing (Slocum §24.5.5; Munzner §12.3.2).

**The 3×3 grid.** Class each measure into tertiles by quantiles, which keep correlated measures looking alike, as Brewer and Pickle recommended (Slocum §21.3.1.1). Three classes per measure make nine cells, and more cells exceed what a reader can decode (Slocum §21.3.2.1). Run `classes` once per measure, then join the two layers by feature id and combine their `dm_class` values into one cell code, such as `2-3`, for a 9-color `match` expression. A unit missing either value takes the no-data color (P9).

```sh
python3 <skill>/scripts/datamap.py classes tracts.geojson --field canopy_pct --method quantile --k 3 --layer canopy --out-dir map/data
python3 <skill>/scripts/datamap.py classes tracts.geojson --field surface_temp_c --method quantile --k 3 --layer heat --out-dir map/data
```

**The bivariate dispute.** Munzner warns that some readers can't interpret a grid of 3×3 or more, and suggests one binary measure or two juxtaposed maps instead (Munzner §10.3.3). Olson found that readers do find regions of matching combinations when the map comes with a clear legend, its component maps, and a note (Slocum §21.3.2.1). The skill's default is the 3×3 grid with all three supports. Use a 2×3 grid when one measure is a threshold the reader cares about (above or below a standard), and juxtaposed maps when readers will spend only seconds on the page.

**Palette by polarity.** Two unipolar measures take complementary hues with a gray diagonal, or two subtractive primaries. A unipolar and a bipolar measure take a sequential scheme on one axis and a diverging one on the other. Two bipolar measures take two diverging schemes with a neutral center cell (Slocum §21.3.2.1). Keep red and green off opposite axes (Munzner §10.3.4). The sources give no CVD-safe bivariate palette, so simulate color-vision deficiency on all nine cells before publishing.

**A choropleth with symbols.** Size proportional symbols by the total with `sizes`, and class the rate with `classes`, either as the fill of the units or of the symbols (Slocum §21.3.2.2). Size and lightness are separable, so both read (Munzner §5.5.3). Fill symbols semi-transparent with an opaque stroke. When tiny units hold large totals, their circles hide the fill beneath, so use graduated circles or the cartogram row (Slocum §19.6.1).

**Small multiples.** One map per measure, sharing projection, extent, and scale. Pool the classes when the panels share a measure or related measures, and never pool unrelated ones, since the wider range would set every break (Slocum §24.5.5). Order panels by a meaningful value, not alphabetically (Munzner §12.4.3). Small units vanish in small panels, so enlarge the panels or link them (Slocum §21.4.1).

**Clusters for many measures.** Standardize each measure as a z score, cluster, and check the clustering before mapping it, since "it is possible to cluster any dataset, even a set of random numbers" (Slocum §21.5.1). Accept a cophenetic correlation of 0.80 or more, color clusters with qualitative hues, and name them from their mean z scores (Slocum §21.5.1). No `datamap.py` command clusters, so keep the script with the project.

## Legend and labels

- Draw the 3×3 legend as a square grid. Title each axis with its measure, unit, and tertile breaks, and set the no-data swatch apart (Slocum §21.3.2.1).
- Name the corners in words, such as both high and both low, so the off-diagonal cells read at a glance.
- Put a one-line reading note under the legend (Slocum §21.3.2.1).
- The title states the finding about the two measures together (P24).

## Interaction

- Hover shows both values and both classes.
- Selecting a unit on the bivariate map marks it on the component maps too (Slocum §24.4.5).
- Layer toggles show each measure alone (Muehlenhaus ch. 13).

## Companions

- The two single-measure maps, smaller, beside the bivariate map. They are required.
- A scatterplot of the two measures, with the tertile breaks drawn and points colored by cell, linked to the map (Munzner §12.3.2).

## What to look for in the render

- All nine colors appear, and the off-diagonal corners stand apart at a glance.
- The diagonal runs light to dark.
- In a CVD simulation, the nine cells stay distinct.
- The component maps share the bivariate map's projection and extent.
- No unit shows a cell color when one of its values is missing.
