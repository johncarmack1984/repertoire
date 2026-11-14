---
name: data-story
description: Use before making, redrawing, or fixing any chart, graph, plot, table, slide, or dashboard. Use before putting results, metrics, benchmarks, survey data, or a before/after comparison into a report, README, PR description, issue, email, newsletter, status update, or chat reply. Use when asked to visualize, summarize, present, or explain data, to improve or restyle an existing chart, or for the takeaway. Turns numbers into a point a reader gets in seconds and can act on, by working through the questions Cole Nussbaumer Knaflic's Storytelling with Data asks. Who the reader is, what they should do, and the one-sentence point are decided before anything is drawn. Then come the form (a sentence, a table, a line, bars, a slopegraph), the clutter cut, the emphasis on the point, the conclusion in words, and the ask at the end.
---

# Data story

A reader gives a page of numbers a few seconds before deciding whether to keep reading. Spend those seconds on purpose: the conclusion in words where the eye goes first, one visual that shows it at a glance, and what to do about it. The method is Cole Nussbaumer Knaflic's *Storytelling with Data*, six lessons that are each a set of questions. Answer them in order and in writing, because most of the result is decided before anything is drawn.

The steps scale with what depends on the answer. For two numbers in a reply they take a moment and end in one sentence. For a chart a decision depends on, or a deck, they are most of the job.

## Before anything is drawn

### 1. Context: who, what, how

- Who is the one reader? A person or a role with a decision to make: the maintainer who merges, the director who owns the budget, the committee that funds the program. "Stakeholders" and "anyone interested" are too many people to write for. When two audiences need different things, write for the one who decides, or make two pieces.
- What do they already know, what do they want, and what will they doubt? The answers set how much background and how much proof the page needs.
- What should they know or do when they finish? Start the answer with a verb they can act on: approve, merge, choose, fund, fix, stop, wait. You have been closer to the data than they have, so recommend something. Where the decision isn't yours to recommend, propose a next step, so they have something to react to. With no answer there is nothing to present yet.
- How will it reach them? Read alone (a PR, a README, a report, an email), the page has to answer what a presenter would have answered. Presented live, the page stays sparse and the detail is spoken. Decide the tone as well: a win, a warning, a routine update.

Take the answers from the request and what surrounds it: the thread, the repo, the file names, who asked. Ask only when the reader or the ask can't be inferred and a wrong guess would change the result. Otherwise go ahead, and state the assumption when you deliver.

Done when you can complete "after reading this, the reader will ...", with a named reader and a verb.

### 2. The point

- What does the data say? Find out first, any quick way. Look for what holds across every series, and for the one that breaks the pattern. That exploring is for you: of the hundred things you looked at, the reader gets the one or two that matter.
- With three minutes and no visuals, what would you say? Write that paragraph: what was going on, what changed or what you found, what it means for this reader, what you recommend.
- With one sentence? That sentence is the Big Idea. It states your point of view, says what is at stake, and is a complete sentence. "Cache latency results" is a topic. "The cache cuts p99 latency by a third at no memory cost, so it should ship in 4.2" is a Big Idea.
- Which two or three numbers make the sentence true, and which numbers cut against it? The second kind stays in: a reader who finds it alone stops believing the rest.
- What happens if nothing is done? That is what is at stake, and the reader should see it.

Done when the reader could act on that sentence alone. Then write the answers down as a brief, before building anything. It is working notes and never part of the deliverable:

```
Reader:    who decides, what they know, what they will doubt
Ask:       what they should know or do
Medium:    read alone or presented, and where it will be seen
Big Idea:  one sentence
Evidence:  the numbers for it, and the numbers against it
```

## Building it

### 3. Form

Which form will this reader read most easily? Choose by what they need to see, never by how much data there is or what the tool draws first.

| The reader needs to see | Use |
| :-- | :-- |
| one or two numbers, or one before and after | a sentence with the numbers in it and nothing beside it: no table, no chart; alone on a slide, the number set large with a few words under it |
| their own row, exact values, or several units at once | a table, its lines and shading faded so the values stand out |
| how something changed over time | a line graph, on even time intervals |
| two points in time, or two conditions, across several categories | a slopegraph |
| how categories compare | bars from a zero baseline, horizontal when the names are long |
| parts of a whole across a few groups, or answers on a scale | 100% stacked horizontal bars |
| a start, what was added and taken away, an end | a waterfall |
| how two measures relate | a scatterplot |

- What should they compare? Put those values side by side on one baseline. Order the rest by size, largest first, unless the categories have an order of their own (age bands, a satisfaction scale, time).
- Do they need every series, category, and year? Drop what the point doesn't need, or keep it as grey context.
- Trend or exact values? For a trend, keep a faint axis and label only the ends. For exact values, label the data and drop the axis.
- About to draw a pie, a donut, 3D, or a second y-axis? Draw sorted bars in place of the pie or donut, never 3D, and for two units label one series directly or stack two graphs on a shared x-axis.

Bars start at zero, always. A bar chart whose axis starts at 34 makes 35 against 39.6 look like a fivefold jump, and one reader who notices discards the argument along with the chart. A line may start above zero when the axis is labelled and the zoom doesn't turn a small change into a large one. `reference/visuals.md` has each form in detail, what to use where the medium is markdown or plain text, and what to do with a tangle of lines.

Done when the reader could say what they are looking at before reading a single value.

### 4. Clutter

Everything on the page costs the reader some attention. Go through it one element at a time.

- Would taking this out change what the reader understands? If not, take it out: borders, gridlines, data markers, tick marks, background shading, trailing zeros, decimals nobody needs, rotated text, and a legend. Take out a table or chart that repeats what a sentence already said, and a paragraph that repeats the table. What has to stay but isn't the message (axes, the other series, the source note) goes light grey.
- What here will feel like work? Do that work yourself. Label each line at its end so nobody matches colors to a legend. Compute the difference the reader would otherwise subtract. Spell out the abbreviation.
- Does it look ordered? Left-align text, line elements up on shared edges, and leave empty space empty. Data added because there was room is noise.
- Would they miss these words? Cut prose the same way: background the reader already knows, an account of the method, a caveat given a paragraph where a line would do. A page read before a decision is read in about a minute.

Keep what makes a number readable: its unit, the % or $ sign, the thousands separator.

Done when removing one more thing would lose information.

### 5. Focus

- Where should the eye go first? Turn everything grey, then bring forward what the Big Idea is about and nothing else: one accent color, a heavier line, value labels on only the data the argument uses.
- Where does it go? Look away, look back, and notice what you see first. If that isn't the point, change the emphasis.

Highlight about a tenth of the page at most; past that nothing stands out. A color means one thing and keeps meaning it. Never depend on red against green: use blue and orange, or add a sign or a word. The top left is read first, so the conclusion goes there. Without color (markdown, plain text) the tools are order, a heading, a line that stands alone, and one bold phrase. `reference/design.md` covers this step and the two on either side of it, with defaults for a chart.

Done when a glance goes to the point.

### 6. Words

- If they read only the title, do they have the point? The title is the Big Idea or the ask: "Please approve two hires", "The cache cuts p99 latency by a third". The label for what is plotted ("Ticket volume over time") goes under it, smaller.
- Is everything labelled in the reader's words? Every graph gets a title, and every axis a title or values on the data. Plain words, units written out, acronyms spelled out once.
- Is the reason written next to the evidence? Put a short note on the data where the thing happened: "two people left in May".
- Where did the numbers come from? A small line at the bottom: the source, the dates, how many, how it was measured, and what more is available.

Done when someone who sees only this could repeat the point and say where the numbers came from.

### 7. Story

For anything longer than one visual: a report, a deck, a talk, a long PR description, a README. A story has a reader who wants something, something in the way, and a way through. A list of findings has none of the three.

- What does the reader want, and what is in the way? Say it in their terms: the price they have to set, the release they have to approve. The gap between what is and what could be is the tension, and it is the reason they keep listening.
- What is the story in three sentences? The situation the reader is in. What the data shows that changes it. What to do. Write them before any heading or slide.
- Why this, and why none of the alternatives? List the choices the reader will weigh, and say what the data says about each. A recommendation needs a reason the alternatives lack.
- What will they object to? Find the number that cuts against you, put it where the reader would raise it, and answer it there.
- What order? Open with the ask for a busy reader who trusts you. For a reader who has to be convinced, go in order: the problem, what you looked at, what you found, what you recommend. Either way, start by saying what is coming.
- Do the headings tell it on their own? Write them first, as full sentences, and under each write the figures it rests on. A heading that speaks for several series or years ("every service got faster", "under 200 ms all year") has to be true of every one of them.
- Is it presented live? Then plan each step three ways: what is on the screen, what changed from the step before, and the sentence said aloud that leads to the next. Write that sentence even when only the slides were asked for, because the slides are the smaller part of a talk. Build one graph up across the steps. A new chart on each slide makes the room learn to read again.
- Does it end on what to do? Close with the ask, tied to the problem the piece opened with. Saying the point at the start, showing it, and saying it again with the ask is repetition the reader needs.

`reference/story.md` has each of these in full, and plans the talk in the third worked example below step by step.

Done when the three sentences still describe the finished piece, the headings make the argument without the text under them, and the last heading is the ask. For a talk, every step also has the sentence that is said with it.

## Before it goes out

### 8. Check it as the reader

- Is it true to the data? Recompute every number the words claim, then read each claim against what the numbers can support. A change in totals doesn't show which individuals changed. A result measured once doesn't show that it lasts. Things that happened together don't show that one caused the other. Nothing is inflated or softened: bars start at zero, the time window wasn't chosen to flatter, the caveat is on the page, and the title claims no more than the numbers show.
- What does a reader who knows nothing see? Give the finished piece, with nothing else, to someone who hasn't seen the data (a subagent with no context will do) and ask where they looked first, what they think it says, what they would do, and what they aren't sure of. If the answer isn't the Big Idea, fix the piece and ask again. With nobody to ask, render it and look: for a chart, look at the picture and never only the code that draws it.
- Tell whoever asked, in two lines with the result: who it was written for, the point it makes, and what was left out. If a claim in what they gave you is wrong, say which one and what the data shows. A wrong assumption then takes one reply to fix.

## Worked examples

A build-script change in a PR, measured against main for two profiles at three `-j` values, with the change behind an opt-in variable. The first draft of the numbers:

| | -j16 | -j4 | -j1 |
| --- | --- | --- | --- |
| debug | 5.34 → 4.05 s | 6.75 → 4.73 s | 22.04 → 11.36 s |
| release | 13.64 → 12.10 s | 14.77 → 13.19 s | 38.35 → 22.60 s |

The brief:

```
Reader:    the crate's maintainer, who knows the build and hasn't seen the timings; will ask whether it helps at the -j people use
Ask:       merge it, as opt-in
Medium:    a PR description, read alone
Big Idea:  Running the probes once cuts the build script's CPU time about in half at every setting, so it is safe to take; the wall-time gain is smallest in release.
Evidence:  for: CPU time down 41% to 54% in all six configurations. Against: wall time down only 11% in release at -j4 and -j16, where one file takes 10 s on its own.
```

The draft answers none of it. Every cell has two values and an arrow, so the reader does the subtraction; `-j` runs backwards; CPU time, the measure the change is about, is missing; and no words say what to conclude. Rebuilt:

> It cuts the build script's CPU time about in half at every setting measured. Wall time drops less as -j rises, least in release, where `bcm.c` alone takes about 10 s at -O3:
>
> | profile | -j | wall, main (s) | wall, opt-in (s) | Δ wall | Δ CPU |
> | :-- | --: | --: | --: | --: | --: |
> | debug | 1 | 22.04 | 11.36 | −48% | −48% |
> | | 4 | 6.75 | 4.73 | −30% | −49% |
> | | 16 | 5.34 | 4.05 | −24% | −54% |
> | release | 1 | 38.35 | 22.60 | −41% | −41% |
> | | 4 | 14.77 | 13.19 | −11% | −43% |
> | | 16 | 13.64 | 12.10 | −11% | −49% |
>
> Medians of 4 to 8 interleaved runs per row (x86_64 Linux, gcc 15.2, `default-features = false`). In every row, the slowest run with the variable beat the fastest without it.

The first sentence is the Big Idea. The second gives the number that cuts against it before the reader finds it. A table is the form because the maintainer will look up their own configuration and there are two measures; the change is computed, and wall time is next to CPU time so the reader sees that parallelism, and not the change, is what shrinks the gain. The last line says where the numbers came from.

The same questions with a chart as the answer. Monthly cloud spend by service, for the platform lead who sets log retention and has seen the bill rise without knowing why. The first draft was the plotting library's default: clustered columns in three colors, a legend, gridlines, the title "Monthly cloud spend".

```
Reader:    the platform lead, who decides retention; knows the total went up, not which service
Ask:       approve a 14-day retention on debug logs
Medium:    one chart in the monthly cost review, read alone
Big Idea:  Storage cost has doubled since debug logging went on in June while compute and network stayed flat, so a retention limit is the fix.
Evidence:  for: storage $4.2k in May, $8.4k in October. Against: compute is still the largest line, at $12.7k.
```

Rebuilt as `assets/storage-cost.svg`: a line graph, because it is change over time. Compute and network are grey, storage is the one accent color, and each line is labelled at its end with its October value in place of a legend. A note at June says what happened. The title is the ask, with the plain label under it, and the source and period are in small type at the bottom. Read that file before drawing a line graph and `assets/flaky-tests.svg` before drawing bars: keep the structure, replace the data.

A story, for five minutes at a live roadmap review where the head of product decides what the next two quarters drop. The data is a year of exports by format, the support tickets about exports, and which accounts use XML. The first draft was six charts with titles such as "Exports by format" and "Tickets by category". The story notes:

```
Reader wants:  fewer support tickets without losing accounts
In the way:    XML export, which three large accounts depend on
Three sentences:
  We keep three export formats alive, and export problems are the largest category in support.
  XML is under 4% of exports and 38% of those tickets, and three accounts make 91% of the XML exports.
  End XML export on 30 September, after building those three accounts a converter.
Alternatives:  keep it: 157 tickets a year and two engineer-weeks a quarter go on.
               end it now: $410k a year of renewals is at risk.
Objection:     "those three accounts pay $410k a year". The converter ships first and takes three engineer-weeks, once.
```

The headings, each with the figures it rests on:

1. We recommend ending XML export on 30 September, with a converter first. This is the ask, and it says what the five minutes will cover.
2. Export problems are the largest category in support: 412 of 1,960 tickets last year.
3. XML is under 4% of exports: 3,600 of 101,000 a month.
4. It is 38% of the export tickets: 157 of 412.
5. Three accounts make 91% of the XML exports, and they pay $410k a year.
6. A converter for those three takes three engineer-weeks once, against two every quarter to keep XML alive.
7. Decision today: end XML on 30 September, converter first.

Headings 3 and 4 are one bar chart shown twice, by exports and then by tickets, with XML in the accent color both times. Heading 5 is the objection, raised before the room raises it, and heading 6 answers it. Keeping XML and ending it now are both on the screen with what each costs, so the recommendation has a reason the alternatives lack.

## Sources

Every step follows a chapter of Cole Nussbaumer Knaflic's *Storytelling with Data* (Wiley, 2015). `reference/sources.md` maps each question to its chapter and credits the people she builds on: Nancy Duarte for the Big Idea, Stephen Few and Edward Tufte for tables and clutter, and Colin Ware for contrast.
