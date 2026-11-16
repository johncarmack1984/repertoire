---
name: data-story
description: Use before making, redrawing, or fixing any chart, graph, plot, table, or slide. Use before putting results, metrics, benchmarks, survey data, or a before/after comparison into a report, README, PR description, issue, email, newsletter, status update, or chat reply. Use when asked to visualize, summarize, present, or explain data, to improve or restyle an existing chart, or for the takeaway. Turns numbers into a point a reader gets in seconds and can act on, by working through the questions Cole Nussbaumer Knaflic's Storytelling with Data asks. Who the reader is, what they should do, and the one-sentence point are decided before anything is drawn. Then come the form (a sentence, a table, a line, bars, a slopegraph), the clutter cut, the emphasis on the point, the conclusion in words, and the ask at the end. Not for a dashboard, a screen of measures monitored at a glance, which data-dashboard covers.
---

# Data story

A reader gives a page of numbers a few seconds before deciding whether to keep reading. Spend those seconds on purpose: the conclusion in words where the eye goes first, one visual that shows it at a glance, and what to do about it. The method is Cole Nussbaumer Knaflic's *Storytelling with Data*, with her lessons run in the order her eighth chapter runs them on one piece of work. Each step names the file that holds its detail. Read that file when the step starts and not before: each step builds on what the one before it wrote down, and which visual you will build isn't known until step 2.

The steps scale with the piece. A sentence or a table takes steps 1, 2, 7 and 8. One chart takes 1 to 5, 7 and 8. A deck, a talk or a long report takes all eight, with 2 to 5 for each visual in it. For two numbers in a reply the whole flow takes a moment; for a chart a decision depends on, it is most of the job.

## The brief

Write the answers down as you go, before building anything. The brief is working notes and never part of the deliverable:

```
Reader:    who decides, what they know, what they will doubt
Ask:       what they should know or do
Medium:    read alone or presented, and where it will be seen
Big Idea:  one sentence
Evidence:  the numbers for it, and the numbers against it
Visual:    the chooser's row, and why not the row above it
```

## 1. Context

Chapter 1. Read `chapters/context.md`. When the numbers are runs someone measured (benchmarks, timings, latency), read `reference/measurements.md` as well. When the piece will hold more than one visual, or is a deck, a talk or a long report, read `chapters/story.md` too and storyboard it now: its headings come before any visual.

Done when `chapters/context.md` is read, the brief's first five lines are written, "after reading this, the reader will ..." completes with a named reader and a verb, and a piece with a story has its headings written as sentences.

## 2. Choose a visual

Chapter 2. Find the row for what this reader needs to see, never for how much data there is or what the tool draws first. The rows run from the simplest to the most specialized, and when two fit, take the higher one: a form nobody has to learn to read is read fastest. Write the row in the brief's Visual line with the reason the row above it doesn't serve ("a line graph, not a table: the point is the trend across the year, not any one month"). Then read that row's file and no other in `visuals/`.

| The reader needs to see | Visual | Read |
| :-- | :-- | :-- |
| one or two numbers, or one before and after | a sentence with the numbers in it, or one number set large | `visuals/simple-text.md` |
| their own row, exact values, or several units at once | a table, or a heatmap when the pattern across the cells matters | `visuals/table.md` |
| how something changed over time | a line graph | `visuals/line.md` |
| what changed between two points in time, or two conditions, across several categories | a slopegraph | `visuals/slopegraph.md` |
| how categories compare | bars | `visuals/bars.md` |
| a total and its parts, parts of a whole across a few groups, or answers on a scale | stacked bars, or 100% stacked bars | `visuals/stacked-bars.md` |
| where a value started, what was added and taken away, and where it ended | a waterfall | `visuals/waterfall.md` |
| how two measures relate across many items | a scatterplot | `visuals/scatterplot.md` |
| numbers so different in size that a bar would hide the small one | square areas | `visuals/square-area.md` |

- A pie or a donut, anything in 3D, or a second y-axis makes the reader work harder for less. Take the row for what the reader needs instead: one or two shares go in a sentence, the shares of one whole in sorted bars, the same whole in a few groups in 100% stacked bars, a share that moved across categories in a slopegraph. Say in the reply what you replaced and why.
- The medium limits the rows. Plain text (a commit message, a terminal, a chat reply) takes the sentence. Markdown (a PR, an issue, a README) takes a sentence, a table, or a chart committed or attached as an image. A rendered chart or a slide takes any row.
- What should the reader compare? Those values go side by side on one baseline. Everything else is ordered by size unless it has an order of its own (age bands, a satisfaction scale, time), and whatever the point doesn't need is dropped or kept as grey context.
- If the file you read says the data breaks its form (lines that tangle, a slopegraph whose lines pile up), come back, change the Visual line, and read the new row's file.

Done when the Visual line names one row and why not the row above it, and that row's file is read.

## 3 to 5. Build the chart

Chapters 3 to 5, one pass each. These steps are for a chart: a sentence or a table carries its own versions of them in its file. In markdown and plain text, the tools for all three are position (the first line is the conclusion, and the ask goes first or last), a heading that is a sentence, one bold phrase that states the point, a blank line as white space, and a `<details>` block as the appendix.

3. **Declutter.** Read `chapters/declutter.md`. Done when removing one more element would lose information.
4. **Focus.** Read `chapters/focus.md`. Done when, looking away and back, the eye goes first to what the Big Idea is about.
5. **Design.** Read `chapters/design.md`, and `reference/chart-defaults.md` before drawing. Done when the title states the ask, or the Big Idea when the reader has nothing to decide, everything is labelled in the reader's words, and a note says where the numbers came from. The visual is ready.

## 6. Story

Chapter 7, for a piece with more than one visual, a deck, a talk or a long report. You storyboarded it in step 1; now run the checks at the end of `chapters/story.md` on what you built.

Done when the headings alone, read in order, make the argument; the recommendation has a reason the alternatives lack; the number that cuts against it is raised where the reader would raise it and answered there; everything under each heading supports it; and the last heading is the ask. For a talk, every step also has the sentence said with it.

## 7. Words

When the visual is ready, invoke the `write-with-style` skill on every line the reader will read: the prose around the visual, the headings, a chart's title, subtitle, annotations and note, and a talk's spoken lines. Table cells, axis labels and data labels stay as they are, and so does your reply to whoever asked. A chart with no prose around it still goes through the pass: its title and notes are the lines read first. If `write-with-style` is already loaded, apply it without loading it again.

Ask it to revise the lines rather than rewrite them, and give it:

- the brief's Reader, Ask and Big Idea, which answer its first step;
- the lines, each marked with where it sits and how much room it has. Each stays a separate line in its place: a note on a chart is revised where it is and never merged into a paragraph;
- what it must keep as it is: every number with its unit, sign and precision; the facts in the method line; each condition and limit ("for large images", "cause not found"); the number that cuts against the point, and its answer; the Big Idea and the ask, the Big Idea first and the ask last; a forecast or a cost of doing nothing that the data supports, with its basis ("at this rate the backlog passes 500 in March, on a straight line through the last five months"); every name that matches a chart label or a table header.

Put each revised line back where it came from, and render a chart again. If `write-with-style` isn't installed, go on to step 8: the earlier steps have already cut the prose.

Done when `write-with-style`, where it's installed, has revised every line, and every number in the draft is in the revision, unchanged.

## 8. Check it as the reader

- Is it true to the data? Recompute every number the words claim, then read each claim against what the numbers can support. A change in totals doesn't show which individuals changed. A result measured once doesn't show that it lasts. Things that happened together don't show that one caused the other. Nothing is inflated or softened: bars start at zero, the time window wasn't chosen to flatter, the number that cuts against the point is on the page with its caveat, and the title claims no more than the numbers show.
- What does a reader who knows nothing see? Give the finished piece, with nothing else, to someone who hasn't seen the data (a subagent with no context will do) and ask where they looked first, what they think it says, what they would do, and what they aren't sure of. If the answer isn't the Big Idea, fix the piece and ask again. With nobody to ask, render it and look: for a chart, look at the picture and never only the code that draws it.
- Tell whoever asked, in two lines with the result: who it was written for, the point it makes, and what was left out. If a claim in what they gave you is wrong, say which one and what the data shows. A wrong assumption then takes one reply to fix.

Done when every number the words claim is recomputed, the fresh reader's answer is the Big Idea, and the two lines are written.

## Sources

Every step follows a chapter of Cole Nussbaumer Knaflic's *Storytelling with Data* (Wiley, 2015). `reference/sources.md` maps each file to its chapter and credits the people she builds on: Nancy Duarte for the Big Idea, Stephen Few and Edward Tufte for tables and clutter, and Colin Ware for contrast. The table rules in `visuals/table.md` follow Stephen Few's *Show Me the Numbers*, and the measurement rules in `reference/measurements.md` follow Martin Kleppmann's *Designing Data-Intensive Applications*.
