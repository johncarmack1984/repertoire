# Isarithmic maps

The chooser's row in `SKILL.md` for a continuous field sampled at points. An isarithmic map interpolates a surface from the samples and draws it as filled bands between isolines (hypsometric tints), with the samples on top, so the reader reads the surface and sees where it is known. This file applies from step 3 to step 7.

## When it fits

The row fits a phenomenon that exists everywhere and changes gradually, such as air temperature, rainfall, air pollution, pressure, or elevation, measured at stations (Slocum §16.3; Muehlenhaus ch. 13). Areal data fit only when a smooth surface is plausible and the values are standardized, and then pycnophylactic interpolation keeps each unit's total (Slocum §16.6). Go back to the chooser when one of these holds:

- The values are counts or follow population, with sharp breaks. As Slocum says, "it makes no sense to create an isopleth map of the raw number of people" (§16.3). Take the dots-and-density row.
- The data are discrete events, such as sightings or incidents. A surface invents hot spots and voids between them (Muehlenhaus ch. 19). Take the dots-and-density row.
- The value changes at unit boundaries, as a tax rate does. Take the choropleth row.
- The field is a vector, such as wind or currents. Streamlines or a dense texture beat isolines and grid arrows (Munzner §8.5).

## Default lies

1. **The Beautiful Lie** (Muehlenhaus ch. 13). A polished surface over sparse samples looks accurate everywhere. The guardrail is the stations drawn on the map, and the surface faded or dashed beyond a distance from the nearest one (P28).
2. **A field that isn't one.** Interpolating counts, categories, or events treats discrete items as a field (Munzner §2.4.3). The guardrail is the brief's Data line, which says why the phenomenon is continuous (P28).
3. **Past the samples.** Values at the map's edge with no stations beyond it are guesses (Slocum §16.5). The guardrail is stations outside the mapped area, or a fade at the edge (P28).
4. **Method artifacts.** Inverse distance weighting rings each station in a bull's-eye, kriging can't exceed the input range and so misses a trend, and splines overshoot past the data (Slocum §16.5.5). The guardrail is cross-validation plus a look at the map.
5. **A rainbow ramp.** Spectral colors don't track value and fail color-vision-deficient readers (Slocum §16.7.1) (P7).
6. **A 3D surface.** A fishnet or an extruded surface hides low areas behind peaks (Slocum §16.7.1; Munzner §6.3) (P22).
7. **Terraced tints.** Few classes draw a smooth field as steps (Slocum §16.7.1). The guardrail is continuous tone with contours over it, or enough bands to read as gradual.

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**Field check.** Write on the brief's Data line why the phenomenon is continuous and smooth, and name any known discontinuity (a fault, a ridge, a coast) so the interpolation respects it (Slocum §16.3).

**Explore the samples.** Map the stations, and look at a histogram and any trend before interpolating (Slocum §16.5). Log-transform skewed values, as Slocum did for snowfall, which lowered every method's error (Slocum §16.5.5). Include stations outside the mapped area, so the edge has neighbors (Slocum §16.5).

```sh
python3 <skill>/scripts/datamap.py inspect stations.csv
```

**Interpolation.** No `datamap.py` command interpolates, so write a seeded script or use GDAL, and keep it with the project. Choose among these (Slocum §16.5):

- Delaunay triangulation with natural neighbors adapts to uneven station density and honors every sample (Slocum §16.5.1).
- Inverse distance weighting, power about 2, is fast and draws bull's-eyes (Slocum §16.5.2).
- Ordinary kriging, with a fitted semivariogram and never the default one, gives a standard error at every node, which is the certainty layer for free (Slocum §16.5.3).
- Splines draw the smoothest lines and can validate worst (Slocum §16.5.4).

Pick by leave-one-out cross-validation (mean absolute error, root mean square error, mean bias) and by looking at each map, since the lowest error can still lose the field's character (Slocum §16.5.5). Use great-circle distances at continental scale, and a search neighborhood split into sectors so a coast doesn't starve one side (Slocum §16.5.2). Name the method and its assumptions in the legend note (Muehlenhaus ch. 13).

**Contour interval.** Use one constant, round interval. Neither Slocum's chapter 16 nor Muehlenhaus gives a rule, so pick one that splits the range into 5 to 7 tint bands, the count `classes` allows, and add lines between them only where they stay apart at the map's size. Draw every 4th or 5th line as a thicker, labeled index line (Muehlenhaus ch. 13). Isolines bunch where the field changes fast and spread where it is flat, which is what lets many levels coexist (Munzner §8.4.1).

**Hypsometric tints.** Light for low and dark for high (Slocum §16.7.1), or a diverging scheme around a meaningful zero for anomalies (Muehlenhaus ch. 13). Elevation takes a hard break at sea level (Munzner §10.3.2). An isarithmic map tolerates more schemes than a choropleth, because like values sit next to each other (Slocum §16.7.1), but lightness still carries the order. `classes` on the stations with `--method equal` gives round, constant breaks and a lightness-ordered ramp for the bands.

```sh
python3 <skill>/scripts/datamap.py classes stations.geojson --field july_mean_c --already-normalized "air temperature at each station" --method equal --k 6 --layer temp --out-dir map/data
```

**Showing the samples.** Draw the stations on top as small neutral dots (Slocum §26.5.2). Fade or dash the surface beyond a distance from the nearest station; Muehlenhaus uses 5 km (ch. 13), but scale it to the network's spacing. With kriging, show the standard error as a pattern overlay or an adjacent map, labeled certainty (Slocum §26.6.2).

## Legend and labels

- The tint legend gives the interval, the unit, and the period. The title states the point (P24).
- A note names the interpolation method, the station count, and the fade distance.
- The station symbol and the fade or mask each get a legend entry.
- Label index lines along the line, and only those.

## Companions

- A map or table of the stations alone, when the network is dense enough that dots on the surface would clutter it.
- A map of cross-validation residuals, which shows where the surface is weakest.

## What to look for in the render

- Every station is visible, and the surface fades where they are sparse.
- No bull's-eye rings sit around single stations.
- No band holds values outside the stations' range, unless the method and a trend justify it.
- Contours are smooth, never jagged, and never cross.
- The surface stops or fades past the outermost stations.
- In grayscale, the bands still read in order (Munzner §6.9).
