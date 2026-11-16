# Sources

Every rule in this skill names its source in the file that holds it. The rules are paraphrased, the few quotations are short and verbatim, and no figure from any source is reproduced. Slocum and Munzner are cited by section number, Muehlenhaus by chapter, because his book numbers no sections, and the papers by section or by Jenny's numbered principles.

## The six sources

- Terry A. Slocum, Robert B. McMaster, Fritz C. Kessler, and Hugh H. Howard, *Thematic Cartography and Geovisualization*, 5th edition (CRC Press, 2027).
- Ian Muehlenhaus, *Prompt Cartography: Interactive Web Map Design with LLMs* (CRC Press, 2027).
- Tamara Munzner, *Visualization Analysis and Design* (A K Peters and CRC Press, 2014).
- Bernhard Jenny, Daniel M. Stephen, Ian Muehlenhaus, Brooke E. Marston, Ritesh Sharma, Eugene Zhang, and Helen Jenny, "Design principles for origin-destination flow maps", *Cartography and Geographic Information Science* 45 (2018).
- Yalong Yang, Tim Dwyer, Bernhard Jenny, Kim Marriott, Maxime Cordeil, and Haohui Chen, "Origin-Destination Flow Maps in Immersive Environments", *IEEE Transactions on Visualization and Computer Graphics* 25 (2019).
- Sarah Schöttler, Yalong Yang, Hanspeter Pfister, and Benjamin Bach, "Visualizing and Interacting with Geospatial Networks: A Survey and Design Space", *Computer Graphics Forum* 40 (2021).

## Where each part comes from

| Part of the skill | Sources |
| :-- | :-- |
| step 2, the brief | Munzner ch. 2 and 3, data and task abstraction; Muehlenhaus ch. 2, the CRAFT checklist, and ch. 4, the data brief, the visual plan, the interface plan, and specifications as contracts |
| step 3, the chooser | Slocum ch. 4, which matches each technique to its data, and ch. 14 to 21; Munzner ch. 5, the ranking of channels, and §8 and ch. 9; Muehlenhaus ch. 13, each idiom's default lie |
| step 4, `projection.md` | Slocum ch. 9, selecting a projection, and ch. 6, scale and generalization |
| step 4, `color-and-classes.md` | Slocum ch. 5, data classification, ch. 10, color, and §14.4 to §14.5; Munzner ch. 10; Muehlenhaus ch. 10 |
| the `classes` lever | Slocum ch. 5 and ch. 14, with the fit measures of §5.8 and the method criteria of §5.10 |
| the `sizes` lever | Slocum ch. 17, proportional symbol mapping |
| the `flows` lever | Jenny et al., principles 1 to 9 and §4; Slocum ch. 20, flow mapping; Yang et al. on height and the globe |
| the `crs` lever | Slocum ch. 9, including the one-sixth rule for a conic's standard parallels |
| step 5, `design.md` | Slocum ch. 11, map elements, ch. 12, typography, and ch. 13, cartographic design; Muehlenhaus ch. 8 and 9, style drift and the defaults, ch. 11, type, ch. 14, motion, and ch. 15, interaction; Munzner ch. 6, 11, and 12 |
| privacy in `design.md` | Muehlenhaus ch. 5 |
| step 7, `critique.md` | Muehlenhaus ch. 6, the critique pipeline, ch. 15, validation bias, and ch. 16, the walkthrough; Slocum §28.5, the LLM experiments; Munzner ch. 4, validation |
| `pitfalls.md` | all six; each entry cites its own |
| `idioms/choropleth.md` | Slocum ch. 14 and ch. 5; Muehlenhaus ch. 13 |
| `idioms/proportional-symbols.md` | Slocum ch. 17; Muehlenhaus ch. 12 and 13 |
| `idioms/dots-and-density.md` | Slocum ch. 15 and 18; Muehlenhaus ch. 5 and 13 |
| `idioms/isarithmic.md` | Slocum ch. 16; Muehlenhaus ch. 13 |
| `idioms/flows.md` | Jenny et al.; Slocum ch. 20; Yang et al.; Muehlenhaus ch. 13 |
| `idioms/networks.md` | Schöttler et al.; Munzner ch. 9 and 12 |
| `idioms/cartogram.md` | Slocum ch. 19; Muehlenhaus ch. 13 |
| `idioms/multivariate.md` | Slocum ch. 21; Munzner ch. 10 and 12 |
| `idioms/time.md` | Slocum ch. 23 and §24.4; Muehlenhaus ch. 14; Munzner ch. 6 |
| `idioms/no-map.md` | Munzner ch. 5, 6, and 12 |

## Where the sources disagree

- **Raised arcs.** Munzner allows 3D only for a task about 3D shape (§6.3). Yang found raised arcs on a globe the most accurate for global flows. The skill draws flows flat by default, and raises arcs only at world extent, with height from distance and a recorded reason, since Yang's readers wore VR headsets.
- **Arrowheads or tapers.** Graph-drawing studies favored tapered links; Jenny's study of maps found arrowheads better. The skill uses arrowheads.
- **Symbol scaling.** Slocum presents Flannery's apparent-value scaling as a live option; Muehlenhaus lists it among outdated defaults. The skill scales by area and lets the legend correct the eye, with Flannery as a recorded departure.
- **Classed or unclassed.** Slocum weighs both. The skill classes by default and goes unclassed for an overall-pattern task or an animated choropleth on a fixed domain.
- **How many classes.** Munzner, Muehlenhaus, and Slocum each give a different upper limit. The skill clamps to 3 to 7, at most 6 for one hue, and prefers 4 to 6.
- **The title.** Slocum's title names the theme; Muehlenhaus's states the point. The skill's title states the point, and the subtitle carries the theme, unit, place, and period.
- **Globe or equal-area.** Slocum's guideline asks for equal-area at world extent. The skill uses a registered equal-area projection for anything that encodes area, and the globe for flows and points.
- **Animation.** Slocum gives guidelines for animated maps; Muehlenhaus bars motion on load and looping. The skill prefers small multiples and change maps, and animates only on the reader's command, with his constraints.
- **Completeness.** Muehlenhaus calls every cut of flows editorial. The skill cuts to the largest flows and always prints what the cut left out.
- **Point-label positions.** Slocum and Muehlenhaus order the positions around a point differently. The skill follows Slocum's revised order.

## Departures and updates

- **Equal Earth.** Slocum recommends Mollweide and Eckert IV for the world. The skill defaults to Equal Earth (2018), which is also equal-area, and offers Mollweide; the proj4 version the templates pin has no Eckert IV.
- **One renderer.** The books describe many tools. The skill draws with MapLibre, including its experimental registered projections, with deck.gl for raised arcs and large data and a native MapLibre app for desktop use.
- **The GADF formula.** Slocum's printed formula for the goodness of absolute deviation fit inverts its own definition. The lever uses one minus the ratio, the form the text describes.
- **Masking.** Muehlenhaus describes displacing points as differential privacy. Displacement gives no such guarantee, so the skill calls it masking.
- **Evidence.** Jenny observed, but didn't test, that longer flows curve more. Yang's results come from headsets. The skill uses both, and says so where it does.

## What is the skill's own

- The levers in `scripts/` and the numbers they use, such as the curvature range, the clearance of 2 px on screen, the bend cap of 6% of the view, the arrowhead size of 2.5 times the line, and the warnings past 100 flows on a flat map and 300 on a globe.
- The templates, the page check and its thresholds, and the `dm-spec` contract.
- The cold reader graded against answers that code computed, which turns Muehlenhaus's critique into a test.
- The pitfall numbering, and a contour interval of 5 to 7 tint bands, for which the sources give no rule.
- The worked example of movers between states.

## Credits

- **Color.** The palettes are Cynthia Brewer and Mark Harrower's ColorBrewer schemes, under the Apache License 2.0.
- **Boundaries.** The world countries come from Natural Earth's 1:110m Admin 0 file, which is in the public domain.
- **The worked example.** Its data is the US Census Bureau's, in the public domain. The flows are the 2024 American Community Survey's state-to-state migration table, the nodes the 2020 centers of population, and the boundaries the 2023 cartographic boundary files.
- **Libraries.** The templates load MapLibre GL JS, proj4js, PMTiles, and deck.gl, each under its own license.
