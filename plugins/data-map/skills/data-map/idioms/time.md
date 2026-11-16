# Time and change

The chooser's row in `SKILL.md` for any of the other rows, over time. Change over time is shown first with a change map or small multiples, and with animation only for movement and under motion rules, with one set of classes across every frame. Read the base idiom's file as well, since this file adds time to it. This file applies from step 3 to step 7.

## When it fits

The row fits when time is a key in the data and the task is what changed (Munzner §2.6.2). Choose the form by the task:

- Two times, where the reader needs to see what changed. A change map wins. An animation of city populations hid which cities lost people, and a percent-change map showed it at once (Slocum §23.9.1).
- Several steps. A small multiple of change maps beat both the animation and a small multiple of raw values in Slocum's study (Slocum §23.9.2).
- Each place's own trajectory. A sparkline per place shows it on one static map (Slocum §23.9.3).
- Movement, such as storms or tracked animals. Animation fits by congruence, since moving things are best shown moving (Slocum §23.5.1).
- A sequence that isn't time, such as classing methods or attributes. Use small multiples, never animation (Slocum §23.6.1).

## Default lies

1. **Animation where small multiples serve.** The reader compares frames from memory, and change blindness hides most of what changed, because "we are blind to our own change blindness" (Slocum §23.8; Munzner §6.5). The guardrail is the change map or small multiples first (P31).
2. **Classes recomputed per frame.** Each frame's colors mean something else, so a unit can change color without changing value. The guardrail is one set of breaks for every frame (P31).
3. **Motion nobody asked for.** Autoplay, looping, motion without pause and stop, or motion that ignores reduced-motion settings. Muehlenhaus warns that "LLMs love to animate unless you prohibit it" (ch. 14). The guardrail is the template's static start and `check`, which fails a map that moves at ready (P26).
4. **Two raw maps for a change task.** The reader subtracts by eye. "Don't just draw what you're given; decide what the right thing to show is," (Munzner §3.4.2.3), so map the derived change.
5. **Smooth tweens between snapshots.** Tweening between census years implies change happened continuously between them (Muehlenhaus ch. 14). The guardrail is the transition rule below.
6. **A midpoint that means nothing.** A diverging change map whose neutral color isn't at zero, or at another meaningful value, misplaces gains and losses (Slocum §23.5.2.1) (P7).
7. **Change read as level.** Large circles of gains read as places doing well overall (Slocum §23.5.3). The guardrail is a legend that says it shows change, not the level.

## Decisions

Make these in order at steps 4 and 5, and copy each choice and its reason into the brief.

**Form, in this order.** First a change map for two times; then small multiples, of change or of states, for up to a few dozen steps (Munzner §6.5.2); and only then animation, for movement or as a second view beside a static one (Slocum §24.4.7). Every period uses the same units. Redraw any changed boundaries to one set before comparing.

**The change map.** Derive the change, as an absolute difference or a percent change, and class it on a diverging scheme around zero (Munzner §3.4.2.3; Slocum §4.4).

```sh
python3 <skill>/scripts/datamap.py classes counties.geojson --field jobs_pct_change --scheme div:0 --layer change --out-dir map/data
```

**One set of classes.** Class every period together, so one set of breaks serves every panel and frame (Slocum §5.1, §24.5.5). Run `classes` once on a file with one feature per place and period, then draw every panel from that one `legend.json`. Quantiles are a sound default across panels (Slocum §24.5.5). Symbols over time take one scale too. Run `sizes` once over every period's values, and add fixed symbols for the period's minimum and maximum as benchmarks (Slocum §23.7.1, §23.7.2).

```sh
python3 <skill>/scripts/datamap.py classes county-years.geojson --field unemployment_rate --method quantile --k 5 --layer unemployment --out-dir map/data
```

**Small multiples.** Every panel shares the projection, the extent, the scale, and the legend. Order panels by time, with each date large. Link hover and zoom across panels on an interactive map (Slocum §24.4.7). Keep units few and large enough to see in a small panel (Slocum §21.4.1).

**Animation, when it earns a place.** Follow Muehlenhaus's non-negotiables (ch. 14). Never loop by default, never start on page load, animate only on an explicit change of state, move one map element at a time, and give pause and stop. Replace transitions with instant changes when the reader's system asks for reduced motion (Muehlenhaus ch. 14). Then add Slocum's guidelines (§23.10). Give play, stop, step, and speed controls, put a temporal legend that matches the nature of time (a bar for linear time, a clock for cyclic) next to the area of change, and test the pace on a few readers. `dm-spec` records the trigger, the controls, and reduced-motion support.

**The two animation disputes.** On length, Muehlenhaus gives 20 to 45 seconds (ch. 14) and Slocum's older guideline 30 to 60 (§23.10). The skill keeps a run under 45 seconds, with longer runs only under narration that directs the eye. On transitions, Muehlenhaus cuts between discrete snapshots and tweens continuous processes (ch. 14), while Fish found that a two-second transition, or a one-second hold and a one-second transition, beat an abrupt change for detecting change (Slocum §23.8). The skill cuts between snapshots by default and uses a one-second transition with a one-second hold when detecting change is the task, with the date changing at the cut.

**Classed or unclassed when animating.** Harrower's readers detected change better on unclassed animated choropleths, because a unit near a break flickers between classes while large changes inside one class stay invisible (Slocum §23.5.2.3). So an animated choropleth takes an unclassed ramp over a domain fixed to the whole period, recorded under Departures, while small multiples stay classed. Smooth a noisy series over a window, such as 30 days, before animating it (Slocum §23.7.2).

## Legend and labels

- The temporal legend sits near the area of change, with the date large (Slocum §23.10).
- A change legend says it shows change, gives the unit and the two dates, and centers its neutral color on zero.
- A note under the legend says the breaks are fixed across the period.
- The title states what changed (P24).

## Interaction

- Play, pause, step, and a scrubber, with speeds of 0.5×, 1×, and 2× (Slocum §23.5.1).
- Hover gives values while paused, and a reset returns to the first frame.
- Nothing plays until the reader asks (P26).

## Companions

- A line chart of the total, or of selected places, with the current frame marked.
- The static small multiple, as the alternative to any animation (Slocum §24.4.7).

## What to look for in the render

- The first frame is still at ready.
- Every panel uses one legend, and a color means the same value in all of them.
- The change map's neutral color sits at zero, and gains and losses stay distinct in a CVD simulation.
- Panels run in time order, and each date is readable.
