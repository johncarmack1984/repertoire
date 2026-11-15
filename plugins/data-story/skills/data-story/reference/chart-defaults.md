# Chart defaults

Read before drawing any chart, at step 5 of the flow in `SKILL.md`. Use the destination's own style where it has one. Where nothing else decides:

- White background, painted as a rectangle so a dark-themed page can't turn grey text invisible, and no border.
- Text in dark grey, not black: #333 for the title, #555 for labels, #888 for axis text and notes.
- Context data in #b0b0b0 at 2px; the emphasized series in one accent (#1f6fb5 blue, with #d9731a orange as the second accent) at 3.5px.
- Title 18px bold, a sentence, top left. Subtitle 13px under it, saying plainly what is plotted and in what unit.
- Series labels 12 to 13px at the end of each line, in the line's color, with the last value when it helps.
- Annotations 12px next to the data they explain, the key phrase bold.
- Axis lines 1px in #c8c8c8, no tick marks, at most five or six axis labels.
- A note at the bottom left in 10 to 11px grey: source, period, sample size, how it was measured.
- All text horizontal, except a y-axis title when there is no room for it above the axis.

## A dark background

Chapter 9 of *Storytelling with Data* has a case where the client's template forced a dark background. White is the better default, because a dark background pulls the eye away from the data and light text on dark is harder to read. When the template wins, keep the method and invert the values: light grey for the context, one bright accent that holds its contrast on the dark, near-white for the title, slightly larger and heavier text, and fewer colors than on white.

## Another tool draws it

If a charting skill or a plotting library is already in use, let it draw, and apply these choices to it: the form, what is cut, what is emphasized, and the words. Either way, look at the rendered picture, never only the code that draws it.
