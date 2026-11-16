# Color and classes

Step 4 reads this file before running `classes`. It picks the scheme type from the data's logic and the classing method and class count from the distribution, and it sets the legend's wording. `classes` does the arithmetic and prints PASS, WARN, and FAIL lines that cite these rules by pitfall number.

## The data's logic picks the scheme type

| The data | Scheme | Lightness | `--scheme` |
| :-- | :-- | :-- | :-- |
| ordered, with no meaningful midpoint, such as a rate, a density, or a share | sequential | light for low, dark for high | `seq` |
| ordered on both sides of a meaningful value, such as change around 0, a ratio around 1, or a gap from a national rate | diverging | light or neutral at the midpoint, darkening toward both ends | `div:MID` |
| categories with no order, such as land use | qualitative | about equal; hue carries the difference | `qual` |

Before choosing, name the wrong reading each other type would invite (Muehlenhaus ch. 10). A diverging scheme on unipolar data invents a critical value, and a sequential one hides the midpoint that bipolar data turns on (Slocum §14.4.1). Light-to-dark or rainbow order on categories reads as quantity, so "qualitative categories of data should be symbolized using unordered hues." (Slocum §10.5.3).

Write into the brief the judgment the palette must not make, such as *color must not suggest that more is worse*. In Muehlenhaus's test the unguided model chose alarm reds, and one such sentence moved it to a neutral ColorBrewer scheme (ch. 10).

Never use a rainbow for ordered data. It has no lightness order, its steps are unequal, and red against green fails color-blind readers (Slocum §14.4.1; Munzner §10.3.2).

`div:MID` takes the midpoint, and `classes` fails it when the midpoint lies outside the data's range (P7).

## Palettes and the diverging pairs

`classes` draws palettes only from ColorBrewer's schemes in `assets/palettes.json`, each flagged for color-vision-deficiency (CVD) safety at every class count. Pass `--palette NAME` to choose within the type.

Give a diverging scheme end hues a reader can name, so the side a unit falls on is plain. Brewer's tests found red-blue, orange-blue, orange-purple, brown-blue, yellow-blue, and yellow-purple easy to name and CVD-safe (Slocum §14.4.2, §14.4.3). Of those, red-blue, orange-blue, orange-purple, and yellow-purple also resist simultaneous contrast (Slocum §14.4.4). ColorBrewer's RdBu, PuOr, and BrBG are such pairs.

## Color vision and simultaneous contrast

About 8% of men and 0.5% of women confuse red and green (Munzner §10.3.4). Never let red against green carry a difference. Keep adjacent classes apart in lightness, so the map still reads in grayscale (Munzner §6.9). `classes` fails a palette that isn't CVD-safe at the class count (P8), and `--allow-unsafe-palette` overrides that only for a reason recorded in the brief.

A color shifts toward the opponent of its surround. A light class ringed by dark ones looks lighter, and a legend chip on a white panel won't match the same class on the map (Slocum §10.3.4, §14.4.4). Judge the classes on the rendered PNG, not on the legend.

## Lightness carries the order

Darker means more, on a light background and on a dark one (Slocum §14.4.1, §14.4.11). On a dark basemap, start the ramp light enough to stand apart from the background rather than flipping it. Keep the lightest class visible too, since a white low end vanishes into a white page (Slocum §14.5.1.1).

Let lightness carry the order, and let hue and saturation only assist (Slocum §14.4.1). A multi-hue ramp passes when its lightness changes in one direction from end to end, as viridis's does. Flip viridis so its dark end is high (Slocum §5.12).

ColorBrewer's classed colors come already spaced by eye. When you build stops yourself, as for an unclassed ramp, interpolate in CIELAB, never RGB or HSV, so equal steps look equal (Slocum §10.4.6; Munzner §10.2.2). In MapLibre that is `interpolate-lab`.

Keep large fills pastel and low in saturation, and save saturated color for small marks such as points and thin lines (Munzner §10.3.1). Keep blue off small features, because the eye resolves it worst (Slocum §10.3.2).

## Classed by default

Class the map unless the task is the overall pattern or the shape of the distribution (Slocum §14.6). Classes win when a reader looks up one unit's value, and the studies found no difference for overall pattern. "The high accuracy of unclassed maps, however, is mathematical, not perceptual." (Slocum §14.6.3.1).

An unclassed ramp over skewed data paints one dark outlier and leaves the rest pale. Class it, or end the ramp below the outlier and give the outlier its own mark (Slocum §14.6.1, §24.5.4).

An animated choropleth is the exception, since change shows better unclassed (Slocum §23.5.2.3). `idioms/time.md` holds those rules.

## Methods

Slocum holds that "there is no single best method of classification" (§5.10). Pick by the distribution and the task.

| `--method` | Fits | Fails |
| :-- | :-- | :-- |
| `equal` | near-uniform data and round intervals a reader can follow, such as 0 to 100% | skewed data, where most units land in one class and another sits empty (P5) |
| `quantile` | ordinal data, maps to be compared, and wording like the top fifth | an outlier sharing the top class with values far below it |
| `jenks` | skewed data, skewness above 1, where like values should group; exact Fisher-Jenks | maps to be compared, because each map's breaks follow its own distribution |
| `stddev` | near-normal data whose mean is a meaningful divider, with a diverging scheme and an even class count | non-normal data, where classes fall outside the data or sit empty |
| `headtail` | heavy-tailed data where the rare high values matter; Jiang's split at the mean while the head holds under 40% | readers who take its limits, which are means, for data values |
| `geometric` | values of 0 or more whose positive values span two or more orders of magnitude, such as rates of a disease by country | negative values, or a range narrower than about one order of magnitude, where it has too few readable values to choose from |
| `manual` | breaks the domain fixes, such as a legal threshold | breaks chosen with no reason given (P5) |

Slocum notes that "quantiles is the only method that can be used for ordinal data" (§5.13). With `--method auto`, `classes` takes quantiles for ordinal data and for maps to be compared, Jenks when skewness exceeds 1, and equal intervals or standard deviations near normal (Slocum §5.10, ch. 21). When skewed positive values span two or more orders of magnitude, it builds Jenks and geometric breaks both, and takes geometric when Jenks's largest class holds more than 40% of the units and geometric's holds fewer. It writes its reason, with both shares, to `method_reason`.

## Geometric breaks

Slocum lists geometric breaks among the interval methods (§5.12), and Jiang names arithmetic and geometric series as the older answer to a heavy tail (Slocum ch. 5, note 6). Each break is a fixed ratio above the last, so each class covers the same span on a log scale. `classes` keeps every break readable. It climbs the ladder 1, 2, 5, 10, 20, 50 by one, two, or three rungs per class, a ratio of 2 to 2.5, 4 to 5, or 10, and uses 1, 2.5, 5 only when that ladder can't fill every class, because 2.5 adds a decimal to every label.

The ratio is the finest that covers the positive values' span in at most 7 classes (6 on one hue), and the class count follows from it. The first break centers the progression on the positive values. Of the placements that leave every class a unit, `classes` takes the one whose wider end class spans the fewest orders of magnitude, so neither the lowest class nor the highest swallows its end of the range. A first break of 1, 10, or 0.1 labels one decimal finer, so the lowest class reads `0 to 0.9`, never `0`.

## One class swallows the map

A class that holds most of the units spreads one color over most of the map. When that class is the lowest, its pale color reads as none. `classes` warns when one class holds more than 40% of the units, a share past the even third of the fewest classes, and names the class, its share, and the fix (P5). Where the positive values span two orders of magnitude, the fix is `--method geometric`, with the share its largest class would hold.

Rates per 100,000 for 172 countries, with skewness 4.7 and positive values from 0.044 to 117.7, show what each method does:

| `--method` | k | Countries per class, low to high | Largest |
| :-- | :-- | :-- | :-- |
| `jenks` | 7 | 95, 43, 21, 6, 5, 1, 1 | 55% |
| `geometric`, and `auto` | 5 | 18, 48, 56, 37, 13, at 0.2, 1, 5, 20 | 33% |
| `quantile` | 7 | 25, 25, 25, 25, 24, 24, 24, at limits like 0.215 to 0.523 | 15% |
| `headtail` | 4 | 130, 33, 6, 3 | 76% |
| `equal` | 7 | 154, 11, 3, 2, 0, 1, 1 | 90% |
| `manual` at 0.5, 2.5, 10, 40 | 5 | 47, 42, 50, 26, 7 | 29% |

Jenks fits the raw values best and still leaves 55% of the countries in its palest class. Geometric breaks and the round hand breaks in the last row keep every class under a third.

## The class count

Take the smallest k whose goodness of absolute deviation fit reaches 0.80 (Slocum §5.8.3). It is `GADF = 1 - ADCM / ADAM`, where ADCM sums the absolute deviations about each class's median and ADAM those about the median of all the values. The book prints the ratio without the `1 -`, which contradicts its own definition, so `classes` uses the corrected form. Geometric breaks are the exception. Their count follows from the span and the ratio, since GADF measures fit on the raw values and would ask for finer classes at the top.

Keep k between 3 and 7, and at most 6 for a single hue, whose lightness steps blur past six (Slocum §5.8.3). Too many classes also make a simple trend look complex (Slocum §14.6.3.2). `classes` reports GVF, GADF, and the largest class's share for each candidate, clamps k, and warns outside 3 to 7 or on an empty class (P6).

## Maps that will be compared

Class maps that will be compared, side by side or as a bivariate pair, by quantiles. Jenks per map hides correlation, and "The optimal method fails to reflect the high correlations between the attributes" (Slocum §21.3.1.1).

A series of one attribute, such as years in small multiples, takes one set of rounded, meaningful breaks across every panel (Slocum §5.10, §24.5.5). Never pool unrelated attributes into one break set, because the one with the larger range then sets every break (Slocum §24.5.5).

## Breaks and legend labels

Round the breaks to meaningful values at the data's precision, then assign classes by the rounded breaks, so the legend and the fills always agree (Slocum §5.3, §5.4). `classes` does both.

Label the legend by these rules (Slocum §11.4.5, §14.7):

- Write `to` between limits, which reads right with negatives, as in `-89.2 to -45.4`.
- Leave no gaps and no overlaps. Every value falls in exactly one labeled class.
- Separate thousands, keep the leading zero in 0.4, use integers for whole things such as people, and use the fewest decimals that keep a rate's meaning.
- Put the unit and the denominator in the legend's heading once, not in each label.
- Order the swatches as a number line, touching, with each value after its swatch. A horizontal legend ascends left to right.
- Under the swatches, say how the classes were cut, with the method and the class count, and what high and low mean (Muehlenhaus ch. 9).
- Never title it Legend.

## No data and small denominators

Give missing values a class of their own, a neutral well apart in lightness from the lightest class. It gets its own legend entry and a note such as "Data unavailable for areas shown in white." (Slocum §11.4.5). Never draw no data as zero or as the lowest class (P9). `classes` writes these features with `dm_class` set to -1 and fills the `nodata` entry in `legend.json`.

A rate on a small denominator swings with one event (Slocum §4.6.2). Pass `--min-den N`, and `classes` marks those features `dm_low_n` and lists them in `legend.json` (P4). Draw them with a pattern overlay, which beat every color cue for showing reliability (Slocum §26.6.2), and put the count and the denominator in the tooltip.

## The command

```sh
python3 <skill>/scripts/datamap.py classes data/counties.geojson --field wood_heated \
  --per households --scale 100 --min-den 500 --scheme seq --layer wood --out-dir map/data
```

Read every WARN and FAIL before going on. FAIL P1 means the field looks like a count. Standardize it with `--per`, or pass `--already-normalized REASON` when it is a rate already. Copy the layer's `method_reason`, `gvf`, and `gadf` into the brief.
