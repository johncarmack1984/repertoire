---
type: llm
focus: trace
weight: 3
---
The user asked for a review of `ev-map/index.html`, a MapLibre world map of new electric-car registrations by country from 2019 to 2025, before it goes on their homepage, and asked that the file not be changed. It has these faults:

1. It is a world choropleth in Web Mercator (`projection: { type: 'mercator' }`), which inflates the high latitudes, so Canada, Russia, and the Nordic countries look far bigger than they are. Fix: an equal-area projection such as Equal Earth.
2. It colors countries by raw registration counts, which mostly track the size of each car market. Fix: a rate, such as registrations per 1,000 people or electric cars' share of new car sales, or the totals drawn as symbols sized by area instead of filled countries, which suits the headline's claim about totals.
3. It uses a rainbow ramp (`#00007f` through `#7f0000`, the "jet" colors) for ordered data, which has no natural order of lightness and fails color-blind readers. Fix: a sequential ramp, light to dark.
4. It uses 9 equal-interval classes (`max / 9`) on counts that are heavily skewed by China's 11.3 million, so 41 of 43 countries fall in the lowest class in 2025. Fix: 5 or so classes, by quantiles or natural breaks.
5. It uses three font families: Montserrat for the title and year, Georgia for the body, and Courier New for the legend and north arrow. Fix: one family, two at most.
6. A `setInterval` advances the year every 1.5 seconds, in an endless loop with no pause and no regard for reduced-motion settings. Fix: show 2025 still, with small multiples or a year control the reader drives.
7. It adds a north arrow, zoom buttons (`NavigationControl`), and a scale bar (`ScaleControl`) to a world map, where none of them helps. Fix: remove them.

Read the final reply to the user.

PASS only if all of these hold:

1. The reply marks all seven faults. Faults 3 and 4 may share one finding, and so may the three elements in fault 7, as long as each is named. One change that removes several faults, such as symbols sized by total in place of filled countries (which ends the area distortion, the color ramp and the classes all at once), counts as the fix for each fault it names.
2. Each finding gives the rule it breaks, either as a pitfall number or in words (for example "Mercator distorts area, so a choropleth misleads").
3. Each finding gives a concrete fix in about a line, in terms the front-end team can act on. A fix of three short lines or fewer counts; a fix that runs to a paragraph or a list of steps for one finding does not.
4. The reply does not claim to have edited the file.

FAIL otherwise, and name the first fault that was missed or the first rule that was broken.
