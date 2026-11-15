# Design

Step 5 of the flow in `SKILL.md`, from chapter 5 of *Storytelling with Data*, "think like a designer". Form follows function: decide what the reader should do with the visual, then make that easy to do.

## Make its use obvious

- Give it a clear order of importance: the title first and largest, then the data the point is about, then the context in grey, then the notes in small type. Step 4 brought the point forward and step 3 took out what distracts; this is the order those two leave.
- Don't make it harder to read than it needs to be. A form people already know beats a clever one, and one idea per visual beats two.

## Words

- If they read only the title, do they have the point? When the reader has something to decide or approve, the title is the ask with its reason, in one line where it fits: "Please approve a 14-day retention on debug logs, which doubled storage cost". A bare ask ("Approve a 14-day retention") leaves the reason for the reader to find. The line under it gives the evidence: "Storage cost went from $4.2k in May to $8.4k in October". With nothing to decide, the title is the Big Idea: "The cache cuts p99 latency by a third". The label for what is plotted ("Monthly cloud spend by service") goes under them, smaller.
- Say the conclusion in words. Two people looking at the same chart will not reach the same one on their own.
- Is everything labelled in the reader's words? Every chart gets a title, and every axis a title or values on the data. Plain words, units written out, acronyms spelled out once, and one name for one thing all the way through.
- Is the reason written next to the evidence? Put a short note on the data where the thing happened: one line, above or beside that point, where the eye passes on its way in: "debug logging turned on". The note says what happened; what followed belongs in the title or the line under it. A note beside the data also explains a caveat, or why this point is highlighted.
- Where did the numbers come from? A small line at the bottom: the source, the dates, how many, how it was measured, and what more is available. For numbers you measured, that line gives the statistic (medians, not means), how many runs and in what order, the spread, and the machine, as `reference/measurements.md` describes.

Step 7 hands these lines to `write-with-style` once the visual is ready, so write them to say the right thing here and leave the polish to that pass.

## Look finished

A visual that looks cared for is trusted more and read longer. Line things up on shared edges, leave the white space, use color sparingly and on purpose, and leave nothing that looks like a default nobody chose.

## When you change someone's chart

People resist a new look for a chart they know. Say what changed and why it reads faster, show the old and the new side by side when you can, and keep the conventions the reader's team relies on (its colors, its names for things) wherever they don't hide the point.
