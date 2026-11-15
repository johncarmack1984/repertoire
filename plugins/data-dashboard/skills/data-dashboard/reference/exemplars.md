# Few's dashboards, described

Chapter 8, "Putting It All Together", shows four dashboards Few designed and critiques eight others built to the same sales brief. Open this file at step 5 to see how an expert arranged a screen. Copy the structure and the reasoning, never the sections, because every dashboard's measures come from its own viewer. Proportions below were measured from the book's figures and are approximate. Widths are also given in u on the 72 by 40 canvas; that canvas is wider than Few's screen, so carry over his width shares, not his height shares.

## What all four share

- A cream background, one sans-serif family, and gray for everything that isn't a title or an alert.
- One muted accent hue on the dashboard title and section titles. The title is the largest text but light, so it doesn't compete with the data.
- Red alerts, the only saturated color among the data, in front of the rows that need attention. The marketing analysis dashboard has none.
- Graphical table rows that read sparkline, alert dot, label, graph, value, with one axis at the foot of each column instead of one per row.
- Groups separated by white space, with hairlines under section titles and column headers and few other rules. No gradients or shadows, and at most one boxed strip.
- A legend, when needed, as small gray text, usually on the section-title line and right-aligned.
- The always-important group in the top left.

## Sample sales dashboard

**Role and viewer.** Strategic, for a sales manager watching performance and opportunities, from a snapshot dated in the header.

**Grid.** Two columns, the left about 55% of the width (40 u) and the right about 39% (28 u), with a gutter between. A thin header strip holds the title, the as-of date in gray, and a Help button at the right.

**Left column, top to bottom.**

- **Key metrics, year to date.** Seven rows (revenue, profit, average order size, on-time delivery, new customers, customer satisfaction, market share), each with a 12-month sparkline, an alert column, the metric, a bullet graph on one shared % of target scale with the target fixed at 100%, and the actual value. The break points between bad, satisfactory, and good differ by measure.
- **Revenue year to date, by region.** Five regions with sparkline, alert, region, a bar against a target tick, the actual, and each region's % of the total.
- **Product sales year to date.** Five products, each with two thin bars, revenue on a top axis and units on a bottom axis, each against its own target tick.

**Right column, top to bottom.**

- **Market share.** Bars sorted largest first, "Our company" in a darker gray than the competitors, "All others" last.
- **Revenue quarter to date.** Stacked bars of actual plus pipeline against target. Its rows line up with the regions of the section to its left, so it needs no row labels, and its alert dots sit in the gutter between the two.
- **Top 10 customers in the pipeline.** A ranked text table with pipeline, quarter-to-date, and year-to-date revenue, numbers right-aligned.

**Alerts and comparisons.** Red dots mark profit, the one key metric ending in its bad range; the Middle East, well short of its target; the regions whose actual plus pipeline falls short of target this quarter; and Merlot, far below its revenue target. Nothing else is red. Every value sits against a target, its 12-month history, its share of a total, or its competitors.

**Why it works.** Few names the reasons. Color appears only on the light-brown headings and the red alerts, the key metrics hold the top left, sparklines and bullet graphs are small enough for a dense screen, some measures appear both as graphics and as text, and one Help button replaces all instructions. "White space alone has been used to delineate and group data."

## Sample CIO dashboard

**Role and viewer.** Strategic and operational together, for a chief information officer. The header gives the as-of time to the minute.

**Grid.** Two columns, the left about 46% (33 u) and the right about 50% (36 u). The top left holds a "Now" strip, the only near-real-time section and the only one in a thin box. It lists five systems and puts a red dot over any system failing at this moment. The title, in muted green, sits at the top right with the as-of time and Help.

**Left column.** System availability for the last 30 days, seven systems, each with a 12-month sparkline, an alert, and its availability as a dark mark on an 85 to 100% scale with its acceptable zone shaded; the scale doesn't start at zero, so no bar is drawn. Hardware use as a % of capacity, with sparklines and bullet graphs. Daily network traffic by hour as three gray lines, from light to black, for the 6-month daily mean, the 7-day daily mean, and yesterday. Response time per system as box plots over a gray band marking the acceptable range.

**Right column.** Key non-system metrics (expenses, customer satisfaction, severe problems) as a graphical table, with one continuous 100% line through all three bullet graphs. Major project milestones as a text table with a column of days until or past due, and alert dots on the milestones past due or nearly due. The top projects in the queue, sorted by priority, with an X for approved funding. Critical events for the next 14 days.

**Alerts and comparisons.** Two intensities of red, dark for critical and light for warning. Every system measure is set against its acceptable performance. In this dashboard the darkest band of a bullet graph means good, the reverse of the sales dashboard; this skill picks one rule, recorded in `sources.md`.

**Why it works.** Besides grays, the only hues are a muted green for section names and two reds for alerts, so "the red alert objects are unique, visually unlike anything else." Milestones and coming events sit beside system performance, so the CIO can ask whether a system is ready for what's next.

## Sample telesales dashboard

**Role and viewer.** Operational and real time, for a supervisor of about 25 phone sales reps who keeps it open all day. Few limits it to six measures, because more would overwhelm a viewer who must respond fast.

**Grid.** The left about 56% (40 u) and the right about 43% (31 u), split by a light vertical rule. The title moves to a footer at the bottom left with the controls and the legend, which leaves the top left to the data.

**Left column.** Overall performance comes first. Hold time, call duration, and abandoned calls share one banded background on a 0 to 250% of target scale, one target line at 100% through all three rows, dark bars, the values as text, and today's sparkline beside each. Below it, utilization as a single marker on a 75 to 100% scale with the counts of reps on duty and online, then call and order volume for this hour, today, and this month, with two histograms of calls and orders per rep.

**Right column.** Every rep, ranked worst first by orders per hour, with calls per hour and a box plot of call durations. A thin red outline surrounds the four reps outside the acceptable range, and an X marks reps who are offline.

**Why it works.** It shows few measures, puts the three that matter most in the top left, and ranks the reps so the supervisor sees whom to help first. This skill replaces Few's blinking alerts, sounds, and freeze button with the 2026 updates in `design.md`.

## Sample marketing analysis dashboard

**Role and viewer.** Analytical, for a web marketing analyst looking for problems and opportunities. The header gives the as-of time with its zone.

**Grid.** Three bands. A header band holds bullet graphs of month-to-date visitors and orders against target at the top left, the title centered, and the shares of registered and repeat visitors at the top right. A full-width visitors band holds three line graphs. The lower band splits about 55% (40 u) and 44% (32 u).

**Sections.** The visitors band is multi-foci time, each panel a deviation line around 0% with the region below zero tinted gray. The panels show the last 12 months against the same months a year earlier, this month by day against a 13-week average for the same weekday, and today by hour against a 13-week average for the same hour. Lower left, the top 10 products by revenue, each a revenue-share bar with a tick for its share of views, so a product viewed often but rarely bought stands out; below it, the top referring sites as a text table with sparklines and the change since a year ago. Lower right, two ranked text lists of products bought together but not shown together, and shown together but rarely bought together.

**Alerts and comparisons.** None, by design. An item's place on a ranked list already says it matters, so an alert would add nothing.

**Why it works.** The deviation lines show the variance itself, the time panels give detail where it is recent, and ranked text serves an analyst who reads each entry before deciding to dig in.

## The eight critiqued entries

Few judged a DM Review competition whose entrants built a sales dashboard with the same measures as his, given no design guidance. Each line names the mistakes from `mistakes.md` the entry shows.

1. A text table of quarterly actuals, forecast, and target with cells shaded green, light red, or vivid red. Mistakes 2 and 5 (comparison to target needs mental math, and text is read serially), 7 (centered numbers), 10 (every quarter weighted alike), and 12 (the light red and green may look alike to the color-blind, and the worst numbers are hardest to read on dark red). Pipeline and the top 10 customers are missing.
2. Boxed panels with heavy table grids, gridded graphs, drop shadows, a pie, and too many bright colors, all in percentages. Mistakes 7 (grids that "imprison the numbers"), 11 (shadows), 5 (the pie), 10 and 12 (nothing stands out), and 2 (no amounts, and no trends by region or product).
3. Photos, a logo, and radio buttons that show one quarter at a time. Mistakes 1 (no comparison over time), 11 (the photos), 9 (photos and logo in the top left), 2 (targets only as printed numbers), and 5 (a line joining targets across unrelated categories).
4. Quadrants on white, navy, black, and gray-pink. Mistakes 12 and 13 (dark backgrounds where one off-white would do) and 9 (small tables lost in white space instead of enlarged).
5. Radio buttons and sliders beside every graph, glossy 3D pies, and shaded bars and buttons. Mistakes 1 (one measure per graph, so regions can't be compared), 5 and 7 (the pies and their 3D), 10 (the candy-bright pies dominate), and 11 (the shading).
6. Circular rings of status by year, quarter, and month, with gradient-filled bars. Few credits its looks and its color-blind-safe hues. Mistakes 5 (rings show history less clearly than a line), 2 (states only, no amounts or distance to target), 10 (every period weighted alike), and 8 and 11 (gradient fills add nothing and shift how bar lengths are read).
7. Bars whose height and width both encode values. Mistakes 5 and 8, since the eye compares their areas slowly and inaccurately.
8. A globe and bubbles holding rectangles coded by symbol and color, explained only by a separate key of nine states. Mistakes 5 and 7 (confusing at first glance and after, positions and codes to memorize, trend shown far worse than a line would show it) and 2 (never more than a rough sense of how a measure compares to its target).
