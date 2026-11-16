# Networks

The chooser's row in `SKILL.md` for connectivity where the structure is the point. A geospatial network map shows located nodes and the links between them so the reader finds hubs, clusters, and paths, and it usually needs a matrix or a relaxed layout beside the map to show what geography hides. This file applies from step 3 to step 7.

## When it fits

The row fits when the brief's question is about structure, such as which places connect, which nodes are hubs, where clusters form, or how a path runs (Munzner ch. 9; Schöttler §3). Go back to the chooser when one of these holds:

- The task is the largest flows between pairs and their direction. Take the flows row.
- The task is each node's total. Take the proportional-symbols row.

A network that changes over time also reads the time row's file. Animation suits change from one year to the next, and small multiples suit longer periods (Schöttler §10.4).

## Schöttler's design space

Schöttler and colleagues sort geospatial network techniques on five dimensions (Schöttler §4). The skill uses them as vocabulary for the brief, not as rules, since by the authors' own account "our design space is descriptive, rather than prescriptive." (Schöttler §11.2). Record one choice per dimension on the brief's Idiom line.

| Dimension | Choices |
| :-- | :-- |
| GEO | mapped, distorted, abstract |
| NODE | explicit, aggregated, abstract |
| LINK | explicit, aggregated, abstract |
| COMP | juxtaposed, superimposed, nested, integrated |
| INTERACT | not required, required, interaction only |

Mapped geography with explicit nodes, superimposed on the map, covers 53 percent of the techniques surveyed (Schöttler §11.2). It is the starting point, and the decisions below say when to leave it.

## Default lies

1. **Geography hides the structure.** Drawn only on the map, a network shows where nodes sit, not how they connect, because one node position can't serve geography and topology at once (Schöttler §4.3, §11.4). The guardrail is a matrix or an abstract view linked to the map (P21).
2. **The hairball.** A node-link drawing stops being legible past about 3 to 4 links per node, or a few hundred nodes (Munzner §9.2, §9.4). The guardrail is aggregation, a cut, or the matrix (P18).
3. **Long links dominate.** "A connection across continents is not necessarily more important than a local link" (Schöttler §5.1), yet it takes the most ink. The guardrail is width from weight alone, and aggregation or a local view for the long links.
4. **Co-located nodes.** Nodes at one point hide each other and their links (Schöttler §10.2). The guardrail is one node symbol sized by the count it holds, or the matrix.
5. **Bundles that hide paths.** Tight edge bundling makes single links impossible to follow (Schöttler §9.1, §10.3). The guardrail is bundling only for overview tasks (Yang §2.2).
6. **Links that seem to stop.** A link passing under a node it doesn't connect reads as a stop there (P16).
7. **The long way round and the third dimension.** A link across ±180 drawn round the far side (P20), and arcs raised without a recorded reason (P22).

## Decisions

Make these in order at step 4, and copy each choice and its reason into the brief.

**Geography's fidelity.** Keep GEO mapped when the task needs where nodes are, how dense they are, or how far apart; distort or abstract it when the task doesn't, as when counting links per region (Schöttler §5.3). Abstract only what a task needs abstracted, or what the task can do without (Schöttler §11.3).

**The trade between fidelity and legibility.** When both geography and structure matter, Schöttler names four ways through it (Schöttler §11.4):

- morph between the geographic layout and a force-directed one;
- keep geography only around a focus node;
- distort positions toward a force-directed layout;
- draw a metro-map hybrid.

A static map shows one layout only, so it must cut clutter hard in the data (Schöttler §11.3).

**Juxtapose and link.** Pair the map with an adjacency matrix when the network is large or dense, or the task is counting links, finding the most connected node, or finding a direct link; node-link drawings stay better for following paths (Munzner §9.4). Matrices linked to maps (MapTrix) scaled better than bundled node-link maps (Schöttler §10.3). Juxtaposed views make the reader do the linking, so tie them with shared colors, brushing, and leader lines (Schöttler §8.1). Keep the geography on one map, never two, since two linked flat maps took readers about 51 seconds per answer against 21 (Yang §5.3).

**Aggregate and thin.** Aggregate nodes into predefined areas, clusters, or grid cells for patterns and summaries (Schöttler §6.2). Thin links by a derived importance such as weight or degree, never at random, which loses the skeleton (Munzner §3.7.2). `flows --top` keeps the heaviest links and prints what it dropped. For a question about structure, keep enough links that the hubs still connect, and say how many.

```sh
python3 <skill>/scripts/datamap.py flows lines.csv --nodes substations.csv --origin from --dest to --value capacity_mw --id substation --lon lon --lat lat --top 200 --geometry curved --layer grid --out-dir map/data
```

`flows` writes node sizes true to area from each node's gross total, link widths linear in weight, and arrows. Leave the arrows layer off for an undirected network.

**The data's traits.** Before choosing a technique, mark which of Schöttler's traits the data have, among them directed, weighted, dense, varying in density, co-located, dynamic, and uncertain in location (Schöttler §10). Each one rules techniques in or out.

## Interaction

- A network needs interaction when part of it is hidden, as on a globe's far side, or when overview and detail differ (Schöttler §9.1).
- Hover a node to show its one-hop neighborhood in saturated color over a desaturated rest (Munzner §12.5.2).
- Brushing carries a selection between the map and the matrix in both directions (Slocum §24.4.5).
- For neighbors off screen, Bring & Go pulls them into view, and link sliding follows a link to its far end (Schöttler §9.3).
- For local clutter, a lens that pushes links away from the cursor keeps the global view still (Schöttler §9.3).

## Legend and labels

- Show the node-size and link-width legends from `legend.json`, and the kept-and-omitted line when links were cut (P18).
- When positions are distorted or abstract, the subtitle says so.
- Label the hubs. The matrix carries every other name.
- The title states the structural finding, not the dataset's name (P24).

## Companions

- The adjacency matrix, with rows and columns grouped by region and ordered by degree, never alphabetically (Munzner §12.4.3).
- Sorted bars of node degree or strength.
- For a network over time, small multiples of the matrix or the map (Schöttler §10.4).

## What to look for in the render

- Answer the brief's structural question from the render alone. Name the top hub, and follow one path from end to end.
- No link passes under a node it doesn't connect.
- Co-located nodes can be told apart.
- The matrix order shows blocks and hubs, not noise.
- If positions moved, a reader can still find three named places.
