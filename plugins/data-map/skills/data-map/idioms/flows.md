# Flows

The chooser's row in `SKILL.md` for origin-destination pairs, regional or global. A flow map draws each pair as one line from origin to destination, with its width scaled to the volume and an arrowhead at the destination, so the reader finds the largest flows and their direction. This file applies from step 3 to step 7.

## When it fits

Flows fit origin-destination pairs whose route doesn't matter, where the task is the largest flows and their direction (Slocum §20.3). Go back to the chooser when one of these holds:

- The question is the network's structure, such as hubs, clusters, or paths. Take the networks row.
- The balance per place matters more than the pairs. Map each place's net flow, (in - out) / (in + out), on the choropleth row with a diverging scheme around zero (Slocum §20.7.2.2).
- Thousands of flows, where their overall density is the message. A density of flows answers it, not single lines (Muehlenhaus ch. 13).

Two adjustments keep the row. When origins differ greatly in size and the question is propensity, divide each flow by its origin's size first, or the largest origin wins by default (Slocum §20.3). When the route matters, as for the tracks of tagged animals, draw the tracks themselves, and this file's rules on width, order, and direction still hold (Slocum §20.3).

## Default lies

1. **The Flow Map's Default Lie** (Muehlenhaus ch. 13). Tidy lines imply that "clean channels exist where messy, multidirectional movement occurs." Every cut is editorial. The guardrail is the kept-and-omitted line that `flows` writes for `--top` or `--share`, printed in the legend (P18).
2. **The hairball.** Every pair drawn, crossing at shallow angles, so no single flow can be followed. The guardrail is the same cut; `flows` warns past 100 flows on a flat map and 300 on a globe (P18).
3. **Straight, stacked lines.** Straight flows share corridors, and reciprocal pairs draw on top of each other. On one of Jenny's test maps, curving the flows raised correct answers from 30 to 77 percent (Jenny §3.2.3). The guardrail is curved geometry with the two directions on opposite sides (P15).
4. **Flows that seem to stop.** A flow passing under a node it doesn't connect reads as a stop there, and acute crossings tangle (Jenny et al., principles 4 and 6). The guardrail is the side flip in `flows` and the render check (P16).
5. **No direction.** Missing arrowheads, or heads too small to see on thin flows (P17).
6. **Big flows on top.** Thick lines drawn last bury thin ones (Slocum §20.4) (P19).
7. **The long way round.** A line that jumps across ±180 draws round the far side of the world (P20). The guardrail is the split `flows` writes at the antimeridian.
8. **Unjustified raised arcs.** Arcs lifted off the map without a recorded reason (P22).

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**What to map.** Volume by default, a rate when the question is propensity (Slocum §20.3). Choose `--net` when only the balance between each pair matters. It draws one flow per pair in the net direction and puts both gross values in `dm_tip`, the case where Stephen and Jenny use full arrowheads (Slocum §20.7.2.1).

**The cut.** Keep the largest flows with `--top N` or `--share S`, so the map shows a few dozen readable flows instead of every pair. Top-N reduced clutter better than a cut at the mean (Slocum §20.7.1), and most flows are small, so a modest N keeps most of the volume (Slocum §20.6). N from 10 to 100 suits a static map (Slocum §20.7.1). The omitted count and share always print; that line is the skill's answer to completeness (P18).

**Geometry.** On a flat regional map, `--geometry curved` gives each flow one quadratic Bézier, which can't loop or S-bend (Slocum §20.7.1). Curvature grows with length (Jenny et al., principle 3), since one curvature for every flow did worse than straight lines in Xu's graph study (Jenny §2.2.1). Each curve bends to the right of travel, so A to B and B to A separate, and flips away from any node it would pass under (Jenny et al., principle 6). At world extent, use the globe and `--geometry great-circle`, densified and split at ±180 (P20). The globe suits flows because they encode no area; a layer that encodes area takes an equal-area CRS. For flows into one place on a flat map, center an azimuthal equidistant projection on the destination, since the units are not the symbol and equal area isn't needed (Slocum §9.4.3).

```sh
python3 <skill>/scripts/datamap.py crs --extent world --idiom flows --interactive
python3 <skill>/scripts/datamap.py flows routes.csv --nodes airports.csv --origin from --dest to --value passengers --id iata --lon lon --lat lat --top 40 --geometry great-circle --max-width 12 --min-width 1 --layer passengers --out-dir map/data
```

**Width.** Linear in value, `w = max_px * v / vmax`, floored at `--min-width` (Slocum §20.4). Readers judge constant-width lines about linearly, so width needs no perceptual correction (Slocum §20.4). The floor keeps thin flows visible but breaks proportionality at the bottom, so say so under the width legend (Slocum §20.7.2.2). Set `--max-width` so the largest flow doesn't cover its neighbors.

**Direction.** Arrowheads at the destination end, scaled with the flow's width, enlarged on thin flows, and set back from the node symbol (Jenny §4.2). `flows` writes them as points with `dm_bearing` and `dm_arrow`. "Direction is best indicated with arrowheads." (Jenny §4.2), and in Jenny's study they beat tapered lines on every question, 51 against 14 percent correct for incoming flows (Jenny §3.2.3.2). Tapers suit only links of equal length and width, the case where graph-drawing studies favored them (Jenny §2.2.3). For dense two-way flows, Koylu and Guo's half arrowhead with biased curvature did best overall (Slocum §20.7.2.1); record it as a Departure.

**Draw order.** Small flows on top of large ones (Slocum §20.4; Jenny §4.1). `dm_order` rises as the value falls. MapLibre reads it through `line-sort-key`, and deck.gl draws in data order.

**Color.** One hue for every flow. If anything varies, make larger flows darker or more opaque, which Jenny offers as a hypothesis (Jenny §4.2). Fade by magnitude, never by length (Slocum §20.7.2.1). Never show direction with red and green (Slocum §20.7.3). Broad, swooping red arrows read as an army's advance, which is wrong for people forced from their homes (Slocum §20.4). A moderate gray casing separates overlapping flows (Slocum §20.7.2.2).

**Raised arcs.** Flat by default, because Munzner allows 3D only for a task about 3D shape (Munzner §6.3). Yang found raised arcs on a globe the most accurate, but in VR headsets, with 12 to 20 participants and one comparison task (Yang §4 to §6). Raise arcs only when the extent is the world, the stack is deck.gl or a custom layer, the height comes from the flow's length and never its volume (the deck.gl page sets it from `dm_km`), and Departures records the reason. Height by distance scored 0.98 where height by quantity scored 0.87 (Yang §4.3). Readers of raised arcs tilted and moved the view more (Yang §4.3), so the page allows pitch and rotation, and `dm-spec` records both. On mln-rs, raised arcs wait for custom layers on the globe.

**How each stack draws them.** Read `stacks/<stack>.md` for the layer code.

- MapLibre draws the flows file as a `line` layer with `line-width` from `dm_width`, and an arrowhead at each destination turned to a screen angle the page measures from the projected line, which stays true on the globe and under a CRS where a map-aligned icon drifts.
- deck.gl draws `<layer>-arcs.json` with an `ArcLayer`, which has no arrowheads, so the arrows file goes on as a second layer.
- mln-rs draws the same line and symbol layers from its style JSON, and the split at ±180 renders correctly on its globe.

## Legend and labels

- The title states the point. The subtitle names what flows, its unit, the period, and the kept line, as in `The 40 largest of 1,212 routes, 78% of passengers` (P24).
- Show three or four reference widths from `legend_widths`, each with its value and unit (Jenny §3.2.2).
- Label only the top origins and destinations. Node circles take area-true sizes from their gross totals.
- With raised arcs, the legend says that height shows distance (Yang §4.1).

## Interaction

- Hover a flow for its origin, destination, and volume, with both directions when `--net` is set (Muehlenhaus ch. 13).
- Hover a node to bring its flows forward and dim the rest (Munzner §12.5.2).
- A control for N, from 10 to 100, keeps the kept line in step (Slocum §20.7.1).
- On the globe, let the reader rotate it. Re-centering helped readers of flat maps too (Yang §5.3).

## Companions

- The OD matrix, with origins as rows and destinations as columns, ordered by total and shaded by volume. It shows every pair, the cut ones included, and every asymmetry (Schöttler §10.3; Munzner §9.4).
- Sorted bars of the largest flows, or of each node's totals in and out.
- A net-flow choropleth, when the balance per place is part of the question (Slocum §20.7.2.2).

## What to look for in the render

Walk Jenny's principles as a checklist:

- No flow passes under a node it doesn't connect (Jenny et al., principle 6).
- Crossings are near right angles, none sharper than about 30 degrees (Jenny et al., principle 4).
- Each reciprocal pair separates, and flows fan out around busy nodes (Jenny et al., principle 7).
- Thin flows show on top of thick ones, each with a visible arrowhead.
- No line goes the long way round or breaks at ±180.
- The kept line is in the legend, and its share matches `legend.json`.
