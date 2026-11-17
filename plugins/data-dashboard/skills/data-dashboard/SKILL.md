---
name: data-dashboard
description: Build, refine, or review an information dashboard the way Stephen Few's Information Dashboard Design teaches, as one screen that shows what someone must monitor and is read at a glance. Use when asked for a dashboard, a KPI or metrics page, a scorecard, an executive summary screen, or a status, operations, or monitoring screen, and when asked to critique, declutter, fix, or redesign an existing one (HTML, React, Grafana, or a screenshot). Gives every measure its comparison (a target, a prior period, a normal range), draws it with Few's display media (bullet graphs, sparklines, sorted bars, lines, box plots, alert dots) from bundled SVG components, keeps color for what needs attention, fits everything on one screen with no scrolling, and renders the page to check it. Not for a single chart, table, or number in a document.
argument-hint: "[build | refine | review] <data, a dashboard, or what to monitor>"
---

# Data dashboard

Stephen Few defines a dashboard as the most important information someone needs to meet their objectives, arranged on a single screen so it can be monitored at a glance. The viewer looks for a few seconds, sees whether anything needs action, and acts. Everything in this skill serves that glance. The method is Few's *Information Dashboard Design* (2006). The drawing is done by a small library this skill ships, which draws his display media in SVG, and a script renders the page and checks it.

`<skill>` below is the directory that holds this file.

## Steps

### 1. Mode

- **Build** turns data, or a description of what to monitor, into a new dashboard. It is the default and runs steps 2 to 8.
- **Refine** improves an existing dashboard and keeps its data. See "Refining" below.
- **Review** reports an existing dashboard's faults and changes nothing. See "Reviewing" below.

Read the mode from the request. With no data and no dashboard to work from, ask what the viewer needs to monitor and where the data lives.

### 2. Brief

- Who monitors this, and what do they do when something is wrong? Write for one person or role with objectives, never for "the team".
- Which role does the dashboard play? Role is the one choice that changes the whole design.

  | Role | Measures | Context | Alerts | Interaction |
  | :-- | :-- | :-- | :-- | :-- |
  | strategic | few, high level | targets and a brief history | simple good or bad | none, a daily or monthly snapshot |
  | analytical | more, with what explains them | rich comparisons, longer history | few or none | links to detail |
  | operational | specific and current | thresholds | immediate, the loudest thing on screen | detail on demand |

  A screen that serves two roles takes the design of the more urgent one, and the other's group goes where it gets the least emphasis, the bottom right.
- Which objectives does it serve? A measure that serves none doesn't go on the screen.
- Where is it read, and how often? Design for the default screen, a laptop browser at 1440 by 800 CSS px. The page scales whole to fill any desktop screen, so a 1920 by 1080 monitor or a wall display shows the same page with larger type. Pass a larger `--viewport` only when the measures need more room than the default holds, since its type then stays laptop-sized on the bigger screen. A phone gets the page's one-column reflow, not a design of its own.
- As of when? Give the time with its zone, at the precision the update cadence needs, never to the second.

Take the answers from the request, the files, and their notes. Ask only when a wrong guess would change the dashboard, and state the assumptions in the report. Write the brief down before touching the data, and fill its Medium and Group columns at steps 4 and 5. It is working notes, never part of the page:

```
Viewer:      the blood center's operations manager; moves stock, calls donors, and ships expiring units at the 7:00 huddle
Role:        operational, with a strategic group (last week against target) in the bottom right
Objectives:  never run short of any blood type; waste as little as possible; fill every hospital order
Screen:      1440x800 laptop browser
As of:       2026-11-16 06:00 EST, refreshed every morning

Measure              Period     Unit   Compared to                Better  Alert when                                Medium           Group
Days of supply x8    now        days   5-day target, 3-day floor  up      under 2 days critical, under 3 warning    table row        Red cells on hand
Red cells collected  last week  units  weekly target 2,150        up      under 85% critical, under 95% warning     table row        Last week
...
```

Done when every measure answers "compared to what", serves an objective, and has an alert rule or a note that it never alerts.

### 3. Measures

- Compute every value with code from the source, never by reading numbers off a file by eye. Write the computation as a script that prints the page's data block, in the format the "Data" section of `reference/api.md` gives, so a refresh is one command (step 6).
- Summarize to the level the viewer acts on. Totals and averages are the usual forms, distributions sometimes. Individual records belong only on an operational screen, and only the ones that need action.
- Choose the measure that carries the message. When the gap from target is the point, show the variance itself, as a percentage of target or a deviation from a baseline.
- Give every measure its comparison: a target, the same period last year, a normal range, a forecast, or a projection to the end of the period. Never invent one. When the data has none, use the prior period, or ask for the target.
- Write the alert rule into the data, with at most two levels. Use the page's `policy` when one ratio of the comparison serves every measure, and each measure's `ranges` when the thresholds differ. Some measures never alert, and an analytical screen may have no alerts at all.
- Round to the precision the viewer acts on, such as 3.8 million dollars rather than 3,848,305.93, with one scale per column named in its header.

Done when every value on the page comes from code and every alert follows a rule written in the brief.

### 4. Media

Pick each measure's medium by what the viewer needs to see. `reference/media.md` has the full table, each medium's specification, and the call that draws it.

| The viewer needs to see | Medium | Call |
| :-- | :-- | :-- |
| key measures, each against its target, with history | graphical table: sparkline, alert dot, label, bullet graph, value | `dd.table` |
| one measure against its target and its good and bad ranges | bullet graph | `dd.bullet` |
| a measure's recent history beside its value | sparkline | `dd.spark` |
| categories compared, or shares of a whole | bars from zero, sorted, one highlighted | `dd.bars` |
| wholes and their parts, or actual plus pipeline against target | stacked bars | `dd.stacked` |
| the shape of a series over time, or its deviation from a baseline | line, labeled at its end | `dd.line` |
| how values spread against an acceptable band | box plot | `dd.box` |
| a condition across too many items for a table, such as revenue by state against quota | treemap | `dd.treemap` |
| values to look up, ranked lists, schedules | text table | `dd.text` |

When a measure is a set of samples judged by the share within a limit, such as response times where a system is fine while 90% of today's samples beat its acceptable time, draw the samples as a box plot against the limit and give the group the rule's `state`. The share decides the alert dot, and the plot shows how far over the slow samples run, which a bullet graph of the share hides.

Never draw a pie, donut, gauge, meter, thermometer, traffic light, radar, area graph, or anything in 3D. The library has no function for any of them, and a call to one throws an error that names the medium to use instead. Use the same medium for the same kind of data everywhere, even if every key measure ends up a bullet graph.

Done when nothing on the left-out list is used and every difference between media reflects a difference in the data.

### 5. Arrangement

- Group by business function, entity, or use, in three to nine groups, closer to four.
- Put the always-important group in the top left, and keep the bottom right for what matters least. Never spend the top left on a logo or controls. A strategic or analytical screen keeps its title in a thin header strip, as Few's sales and marketing dashboards do; only an operational screen, watched all day for what needs action now, moves the title to the footer, as his telesales dashboard does.
- Put what is compared side by side on one scale, and line up the rows of sections that share categories.
- Separate groups with white space. Hairlines go under section titles and column headers only, never around a section.
- Where history matters, show recent time finely and older time coarsely, such as this month by day beside the last 12 months by month.
- Write the row budget before building. The page is 72 by 40 u. Padding and the title leave about 37 u for the grid, and with 2 u kept spare each column plans to 35 u. `reference/design.md` gives each element's height and the worked example's budget.

`reference/design.md` covers grouping, emphasis, color, and type. `reference/exemplars.md` describes how Few arranged four dashboards and what the eight he critiqued got wrong. When a column overflows, cut a measure or move a group, and say which in the report. Never shrink the unit or let the page scroll.

Done when every column's budget fits, with room to spare.

### 6. Build

With a shell, start from the template, which has the library and its styles inlined:

```sh
python3 <skill>/scripts/dashboard.py new dashboard.html --title "Blood supply" --viewport 1440x800
```

Then fill the page's marked regions with Edit, and never retype the library or its styles:

- `data-dashboard:page-style` holds the grid, as `grid-template-columns` and `grid-template-areas`, one area per section or per `.dd-stack` column of sections.
- `data-dashboard:page` holds the header, the sections, the footer, the data block, and the module script that draws.
- The data block, `<script type="application/json" id="dd-data">`, holds the computed values. Write it from the step 3 script with `python3 <skill>/scripts/dashboard.py sync dashboard.html --data data.json`, which is also how the page is refreshed. Each measure is a record in `measures`, keyed by name, with `value`, its comparison (`target`, `prior`, `forecast`, or `norm`), `better`, `ranges` when the bands aren't the policy's, `history`, and `format`. The `policy` sets the alert ratios for the whole page.

Every section follows one pattern, a title with its qualifier and legend, then the element a call draws into:

```html
<section class="dd-sec" style="grid-area: stock">
  <h2 class="dd-sec-title">Inventory <span class="dd-qual">(days of supply)</span><span class="dd-legend" id="stock-legend"></span></h2>
  <div id="stock"></div>
</section>
```

The template's module script already holds `const dd = DataDashboard` and `const d = dd.data()`. Add one call per section:

```js
dd.table('#stock', d.measures, {rows: ['oNeg', 'oPos', 'aNeg', 'aPos'], scale: 'shared'})
dd.legend('#stock-legend', [{mark: 'bar', label: 'On hand'}, {mark: 'target', label: 'Target'}])
```

A graphical table's `scale` is `'pctTarget'` by default, every row as a percent of its target on one axis, which suits measures in different units. Rows in one unit, such as days of supply, take `'shared'`, one axis in that unit. The template's header holds the title, the as-of line, and `p.dd-flags`, where `dd.flags('#dd-flags')` counts what the page flags, such as "2 critical · 4 warnings", so a glance says whether to act. On an operational screen, move all three into `footer.dd-foot`; the styles handle the rest.

`reference/api.md` gives every call, option, and data field, and the library's errors name the fix when a call is wrong. Draw nothing by hand: no `<svg>` shapes, no `<canvas>`, no chart library, nothing loaded from the network. The page opens from a file with no connection.

Without a shell, read `<skill>/assets/template.html`, which holds the same template, and write the page from it with the regions filled. Keep the row budget by hand, and say in the report that the fit was not measured.

Done when the page opens from `file://` and every graphic on it comes from a library call.

### 7. Check

```sh
python3 <skill>/scripts/dashboard.py check dashboard.html
```

The check renders the page in headless Chrome at the design viewport, in the light and the dark scheme, and at phone width, saves a screenshot of each beside the page (`<page>.<W>x<H>.png`, `.dark.png`, and `.phone.png`), and prints a `PASS`, `WARN`, or `FAIL` line per finding, each naming the element, the numbers, the mistake it commits, and the fix. It fails a page that scrolls, clips or overlaps text, draws a shape by hand, loads anything from the network, or shows a measure with nothing to compare against.

- Fix every FAIL and read every WARN.
- Open both desktop screenshots with Read and look at each as the viewer would. Where does the eye land first? It should land on the alerts and the top-left group in both schemes. Notice what you see second and third. The page follows the viewer's dark mode on its own, so a page that reads well only in light isn't done; `--theme light` or `--theme dark` checks one scheme alone while you fix it.
- Walk `reference/mistakes.md` from 1 to 13 against the screenshot.
- Take at most two more rounds. If the page still doesn't fit, cut rather than shrink.

Done when the check exits 0 and the first glance lands on what needs attention.

### 8. Report

Tell whoever asked, in a few lines:

- the absolute paths of the page and its screenshot;
- the viewer, role, and screen it was designed for, and any assumption made about them;
- what is flagged and why, and the alert rule behind it;
- what was left out, and why.

If a claim in what they gave you is wrong, such as a notes file that calls a measure on track when the data says otherwise, say which and what the data shows.

## Refining

Refine an existing dashboard by reviewing it first, then fixing what the review found. `reference/refine.md` has the rules and the changes for Recharts, Chart.js, ECharts, Vega-Lite, and Grafana.

- Keep every measure and every value. Drop or replace one only when it is a deficient measure, and name it and the reason in the report.
- Fix in place when the user maintains the code, keeping their data plumbing and changing only the presentation. Rebuild as a page with the library when the input is a screenshot or a PDF, or when the user asks for a new file, and say which values were read off an image.
- Check the result as in step 7, and report the faults fixed by mistake number.

## Reviewing

A review changes nothing. Open with one line that names the dashboard's role and says whether a glance shows what needs action. Then list the faults, worst for the viewer first. For each, quote or locate it, name the mistake from `reference/mistakes.md` by number, and give the fix in one line in the dashboard's own stack. List every measure that has nothing to compare against. Put no mark on anything that keeps the rules, however differently you would have built it. Name it once as one to keep, and suggest nothing for it, not even an addition such as annotations, markers, or another series, since a suggestion on a correct panel reads as one more fault. When a fix to the arrangement moves it, say that it moves unchanged.

## Worked example

`<skill>/assets/example/blood-supply.html` is a regional blood center's morning dashboard, built only from library calls, and `blood-supply.png` is its screenshot at 1440 by 800. Read both before building a dashboard of your own, then copy the structure, never the sections.

Its viewer is the center's operations manager, who decides at the 7:00 huddle which blood types to move between hospitals, which donors to call, and which units to ship before they expire. The screen is operational, so the title sits in the footer, and the top left holds what matters most: days of supply for each of the eight blood types against a 5-day target. Hospital stock of the two short types sits beside it, as two graphical tables that share one set of hospital rows. The bottom band holds tomorrow's donors, booked with expected walk-ins as a lighter projection against each site's target; the units expiring within 72 hours, soonest first; and, in the bottom right, last week's collections, fill rate, and outdates, the one strategic group.

Six of its 44 rows alert, and all six tell one story: O-negative is short. The center holds 1.6 days of it, two hospitals hold less than their par, and tomorrow's O-negative bookings fall short of the goal. Everything else is gray, so a glance lands on the two red dots at the top left. Collections at 96% of target and a fill rate of 95.8% against 98% stay quiet, because neither crosses its rule. Donor wait times, platelets, and shipments against forecast were left out, since none of them serves a decision taken at the huddle.

## Sources

Every rule follows Stephen Few, *Information Dashboard Design* (O'Reilly, 2006). `reference/sources.md` maps each step to its chapter, lists where the skill departs from the 2006 book (the viewport, contrast, band polarity, phones, and the rest), and credits the people Few builds on: Edward Tufte, Colin Ware, John Tukey, and Ben Shneiderman.
