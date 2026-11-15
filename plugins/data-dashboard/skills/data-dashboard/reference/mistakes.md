# The thirteen mistakes

Step 7 walks this list after the check passes, and a review cites it by number, as in "mistake 7". The thirteen are Few's, in his order, from chapter 3, "Thirteen Common Mistakes in Dashboard Design". The 2026 forms are this skill's, since the vendor styles Few critiqued are gone and their descendants fill today's dashboards. Each entry gives what the mistake looks like now, why it fails, and the fix.

## 1. Exceeding the boundaries of a single screen

- **Looks like.** A page that scrolls; tabs, a dropdown, or radio buttons that show one region, product, or quarter at a time; a carousel of KPI cards; a panel with its own scrollbar.
- **Why it fails.** What can't be seen together can't be compared, and viewers treat whatever lies off screen as less important or never look at it.
- **Fix.** Fit everything at the design viewport by the row budget in `design.md`. Summarize or cut a measure rather than scroll, and put details one click away.

## 2. Supplying inadequate context for the data

- **Looks like.** A KPI card with a big bare number and perhaps a colored arrow; a gauge with tick marks but no numbers; a status color with no scale behind it.
- **Why it fails.** A number alone prompts "Compared to what? Is this good or bad?" and gives no answer.
- **Fix.** Give every measure a comparison (target, prior period, norm, or forecast) and its good and bad ranges, as a bullet graph or a graphical table row with a sparkline. Keep the value prominent and the context quieter.

## 3. Displaying excessive detail or precision

- **Looks like.** $3,848,305.93 where $3.8M would do; four or more decimal places; "updated 14:32:07"; transaction-level rows.
- **Why it fails.** Every digit the viewer doesn't need is one more to filter out before reading the rest.
- **Fix.** Round to the precision the viewer acts on, with one scale per column named in the header. Give the as-of time to the minute or the day, with its zone.

## 4. Choosing a deficient measure

- **Looks like.** Actual and budget as two lines or two numbers, leaving the viewer to subtract; a raw count where a rate or a share is the point.
- **Why it fails.** The measure is accurate but isn't the one that carries the message, so the viewer has to do the arithmetic.
- **Fix.** Show the variance itself, as a percentage of target (-9%) or a deviation line around 0%, with the amounts beside it when they matter too.

## 5. Choosing inappropriate display media

- **Looks like.** Donuts and pies, including pies of values that aren't parts of a whole; bubbles sized by value; a radar chart of regions; a map of four sales regions; a chart where a table of three numbers would do.
- **Why it fails.** People misjudge angles and areas and read circular scales slowly, and a map adds nothing when location carries no meaning.
- **Fix.** Pick from `media.md`, such as sorted bars for shares, a text table for lookup, and a map only when location is the message.

## 6. Introducing meaningless variety

- **Looks like.** A gauge, a donut, a bar chart, and a line chart for four measures of the same kind, chosen so the page looks varied.
- **Why it fails.** Each new form makes the viewer switch how they read, while one form throughout lets them read everything the same way, faster.
- **Fix.** Use the best medium for each kind of data, even if every key measure ends up a bullet graph.

## 7. Using poorly designed display media

- **Looks like.** Charting-library defaults, such as a legend beside every chart, unsorted bars each in its own color, heavy grid lines, 3D or glossy bars, numbers without thousands separators, compared bars drawn far apart.
- **Why it fails.** Each flaw makes the eye work before it reaches the data, bouncing to a legend or hunting for the meaning of a color that has none.
- **Fix.** Label data directly, sort bars by size, keep one color unless color means something, drop the grid and the 3D, separate thousands in every number, and put compared bars side by side.

## 8. Encoding quantitative data inaccurately

- **Looks like.** Bars on an axis that starts above zero, which makes small differences look large.
- **Why it fails.** A bar's length is its value; on Few's cut axis, revenue less than double the costs looks four times as large.
- **Fix.** Start every bar at zero, which the library enforces. On a narrow scale, draw the value as a dot instead of a bar; the library's bullet graph does this itself when its scale starts above zero.

## 9. Arranging the data poorly

- **Looks like.** A logo, a greeting, filters, or a date picker in the top left; the key measures low on the page; two trend charts to be compared set side by side and far apart; a bright header bar over every card.
- **Why it fails.** Placement should follow importance and the order of reading, and the top left is the most prominent spot on the screen.
- **Fix.** Put the always-important group top left, stack compared graphs one above the other, and set section titles in muted text over a hairline, never on a colored band.

## 10. Highlighting important data ineffectively or not at all

- **Looks like.** Every chart equally saturated; a status color on every row, green included; a large logo and bordered buttons.
- **Why it fails.** "Everything that deserves space on a dashboard is important, but not equally so," and when everything stands out, nothing does.
- **Fix.** Draw everything in gray, put the alert dot only on exceptions, use at most two intensities of one red, and set the alerting value in bold as a second cue.

## 11. Cluttering the display with useless decoration

- **Looks like.** Glassy or gradient cards, drop shadows, rounded bordered panels, an icon on every KPI card, background images or faded maps behind charts, numbers that count up on load, a hero banner.
- **Why it fails.** The viewer has to process decoration to reach the data, and its charm wears off within days.
- **Fix.** Remove it. "Blank space is better than meaningless decoration." A logo, if one is required, goes small and muted, out of the way.

## 12. Misusing or overusing color

- **Looks like.** A different hue for each series or bar; neon on a dark background; red, yellow, and green status; one color that means "good" in one chart and a product line in another.
- **Why it fails.** Viewers read any contrast as meaningful and link matching colors, and red against green fails color-blind viewers.
- **Fix.** Use grays, one muted accent for section titles, and saturated red only for alerts, in two intensities with a second cue. Give each color one meaning across the screen.

## 13. Designing an unattractive visual display

- **Looks like.** Dark gray panels with black grid lines, charts stretched to fill leftover space, clashing fills, a cramped default font, a decorative image beside the title.
- **Why it fails.** An ugly screen puts the viewer in a frame of mind that works against using it.
- **Fix.** Make the data itself attractive, with an off-white background, gray data, one accent, legible type, and graphs at their natural size, and add nothing that distracts from it.
