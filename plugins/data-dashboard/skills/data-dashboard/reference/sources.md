# Sources

Every rule in this skill follows Stephen Few, *Information Dashboard Design* (O'Reilly, 2006). The rules are paraphrased, the quotations are short phrases from the book, each with its chapter named, and no figure from the book is reproduced. `exemplars.md` describes Few's dashboards in words, with proportions measured from his figures. Chapter and section titles below are given as the book prints them.

## Chapter map

| Part of the skill | Where it comes from |
| :-- | :-- |
| step 1, mode | chapter 1, "What Is a Dashboard?". A dashboard serves someone's objectives, so with no data and no dashboard the first question is what to monitor. |
| step 2, brief | chapter 2, "Classifying Dashboards by Role" (role is the classification that changes the design) and "Enrichment through comparison" (every measure against something); chapter 1, "What Is a Dashboard?" (tailored to a person, group, or function); chapter 8, "Sample Sales Dashboard" (the questions Few asked of each measure) |
| step 3, measures | chapter 5, "Condensing Information via Summarization and Exception"; chapter 3, "Displaying Excessive Detail or Precision" and "Choosing a Deficient Measure"; chapter 2, "Variations in timing" |
| step 4, media, and `media.md` | chapter 6, "Select the Best Display Medium" and "An Ideal Library of Dashboard Display Media"; the left-out list from "Final thoughts about graphs", "Alert icons", and the opening of "Bullet graphs"; chapter 1, "All That Glitters Is Not Gold"; chapter 3, "Choosing Inappropriate Display Media" |
| step 5, arrangement, and the layout in `design.md` | chapter 7, "Organize the Information to Support Its Meaning and Use" and "Maintain Consistency for Quick and Accurate Interpretation"; chapter 5, "Highlight the most important data pixels that remain" (the emphasis zones) and "Eliminate all unnecessary data pixels" (multi-foci time); chapter 3, "Arranging the Data Poorly" |
| perception in `design.md` | chapter 4, "Understanding the Limits of Short-Term Memory", "Visually Encoding Data for Rapid Perception", and "Gestalt Principles of Visual Perception" |
| simplicity in `design.md` | chapter 5, "Key Goals in the Visual Design Process", "Reduce the Non-Data Pixels", and "Enhance the Data Pixels" |
| step 6, build, and color and type in `design.md` | chapter 7, "Make the Viewing Experience Aesthetically Pleasing"; chapter 4, "Using Vivid and Subtle Colors Appropriately"; chapter 6, "Alert icons" |
| step 7, check, and `mistakes.md` | chapter 3, "Thirteen Common Mistakes in Dashboard Design", one section per mistake in Few's order |
| step 8, report | chapter 7, "Test Your Design for Usability", which says to present one design and to explain any display the viewer hasn't met |
| `exemplars.md` | chapter 8, "Putting It All Together", with its sales, CIO, telesales, and marketing analysis samples and its eight critiques |
| review and refine, and `refine.md` | chapter 3 for the numbered mistakes a review cites; chapter 8's critiques as the model of a review that names faults without redesigning |

## Departures from the 2006 book

- **The viewport.** Few assumed one fixed monitor and gave no size for it. The skill designs for a named viewport, 1440 by 800 CSS px by default, and sizes everything in `--u` so the whole page scales to any desktop screen without scrolling.
- **Contrast.** Sampled from his chapter 8 dashboards, Few's title accents reach 1.8 to 3.0:1 against his cream background and his light alert red 2.0:1. The skill keeps his hues, darkens them to 4.5:1 for text and 3:1 for marks that carry meaning, and adds a second cue beside every alert color, the value in bold and its percent of target as text. The light range bands of the bullet graph stay as he drew them, with each row's state in its screen-reader text.
- **Band polarity.** Few's chapter 6 bullet graphs and his sales dashboard put the darkest range at the bad end; his CIO and telesales dashboards put it at the good end. The skill takes chapter 6's rule, with ranges listed from bad to good and the darkest band bad, and mirrors the bands for a measure where lower is better.
- **Fonts and drawing.** Few drew his figures in Excel and Illustrator and judged fonts by name. The skill uses the system sans-serif stack and draws in SVG, so a page needs no network and stays crisp at any pixel density.
- **Phones.** Few's one screen was a desktop monitor. Below a floor width the skill's page becomes one scrolling column, with its groups in order of importance.
- **No blinking or sound.** Few's CIO and telesales alerts blink until clicked and may sound. The skill's alerts are added marks only, and the page honors the viewer's reduced-motion setting.
- **The as-of time.** Few's sales header gives a date and his CIO header a date and time, neither with a zone; only his marketing analysis header names its zone. The skill always shows the as-of time with its zone, at the precision the update cadence needs.
- **Number formats.** Few asks for thousands separators and rounding to the precision needed. The skill formats numbers for the viewer's locale, with one scale per column named in its header.
- **Today's forms of the mistakes.** Donuts, glassy cards, drop shadows, count-up numbers, and neon on dark aren't in the book. `mistakes.md` assigns each to the mistake whose reasoning covers it.
- **Short-term memory and color blindness.** Few's three to nine chunks and his 10% of men and 1% of women are the figures of his time. Nelson Cowan's work (2001) puts short-term capacity near four chunks, so the skill designs to the low end of Few's range. The commonly cited share of color-blind men today is about 8%, which leaves his color rules as they are.
- **Interaction.** Few describes hover and click with a mouse. The skill gives every hover a focus and a tap equivalent and keeps essential values out of tooltips.
- **Dark mode.** Few's book has none, and every palette in it assumes a light page. The skill's dark palette keeps his rules where they depend on the background. The worst range of a bullet graph has the most contrast with the background, so on a dark page it is the lightest band. The bar and the target stay the highest-contrast marks, and the alert stays two intensities of one red, the brighter one critical.
- **Small multiples and the treemap.** Few wished software would build small multiples; the library's are separate calls given one shared domain. The treemap colors on the alert hue by the same policy as every other medium, so Few's white-to-red ramp becomes neutral, then tints, then the full alert red.

## What is the skill's own

- The library, `assets/dashboard.js`, with its one rule for alert state, its refusal to draw a bar from a non-zero baseline, and its lack of any pie, donut, gauge, radar, or 3D function.
- The check, `scripts/dashboard.py`, and every number it enforces, such as the 9 px type floor and the warning outside three to nine groups.
- The unit `--u`, the row budget, and the token values in `assets/dashboard.css`. The size steps follow the ratios measured in Few's exemplars; the exact values are the skill's.
- The worked example, a regional blood supply center's morning dashboard, which is unlike any of Few's.
- The review format, which follows the review rule of this repository's `write-with-style` skill, and the mapping tables for Recharts, Chart.js, ECharts, Vega-Lite, and Grafana.
- The refine rules in `refine.md`, and smaller choices Few leaves open, such as a sparkline's end dot drawn only when its measure alerts and hairlines only under section titles and column headers.

## Credits Few gives

- **Edward Tufte.** The data-ink ratio, which Few adapts as non-data pixels; the sparkline, from *Beautiful Evidence* (2006); and the terms "small multiples" and "chartjunk".
- **Colin Ware.** The preattentive attributes, from *Information Visualization: Perception for Design* (2nd edition, 2004). Few reduces Ware's 17 attributes to 11.
- **John Tukey.** The box plot, in the 1970s.
- **Ben Shneiderman.** The treemap, in the 1990s at the University of Maryland.
- **Donald Norman.** The case, from *Emotional Design* (2004), that a pleasing display is a more usable one.

The accessibility targets come from WCAG 2.2, success criteria 1.4.1 (color is not the only cue), 1.4.3 (text contrast), 1.4.11 (contrast of graphics), and 2.3.1 (no more than three flashes a second).
