# Story

Steps 1 and 6 of the flow in `SKILL.md`, from chapter 7 of *Storytelling with Data*, "lessons in storytelling", for a piece with more than one visual: a report, a deck, a talk, a long PR description, a README. Read it at step 1 and storyboard before choosing any visual; at step 6, run the checks at the end on what you built. A list of findings invites the reader to argue with each one. A story gives them a stake in how it ends, and it is what they repeat to someone else afterwards.

## What the reader wants

A story has a reader who wants something, something in the way, and a way through. Start with the reader and answer each of these in a line:

- Where and when is this?
- Who is it about? Make it the reader: their team, their budget, their users.
- What do they want, in their terms: the price they have to set, the release they have to approve?
- What changed, or what is in the way?
- What should be true instead, and how do we get there?

The gap between what is and what should be is the tension, and without it nobody has a reason to keep reading. If everything looks fine, look again for what the reader stands to lose or gain. Then say what moves this reader: money, time, risk, a competitor, a promise they made.

## Three sentences

Write the story in three sentences before any heading or slide: the situation the reader is in, what the data shows that changes it, and what to do. If the three don't follow from each other, more slides will not fix it. Keep them. When the piece is finished, they should still describe it.

## The middle convinces

Use what this reader needs and leave the rest out:

- the background they are missing
- a comparison: last year, the target, a competitor
- one example that makes the problem concrete
- the data that shows it
- what happens if nothing is done
- the alternatives, and what the data says about each
- why the one you recommend
- why this reader is the one who can act

The alternatives and the objection get skipped, and a skeptical reader looks for both. A recommendation needs a reason the other choices lack, so list the choices the reader will weigh and say what the numbers say about each. Then find the number that cuts against you, put it where the reader would raise it, and answer it there. A reader who finds it alone stops believing the rest.

## The end is the ask

Say exactly what you want done and by when, and tie it to the problem the piece opened with. State it as the action the reader takes: "End XML export on 30 September", "Approve two hires". "We recommend" leaves the reader asking who "we" is.

## Order

Going through events in the order they happened is the natural way to tell it and often the wrong one. Choose by the reader:

- Lead with the ask when they are busy, trust you, or want the answer more than the method. It also tells them what to listen for.
- Go in order (the problem, what was examined, what was found, what is recommended) when they have to be convinced, don't know you, or care how it was done.

Either way, say which one you are doing: "the recommendation first, then how we got there".

## Headings

- Write the headings first, as full sentences. Read alone and in order, they are the argument. A heading that is a topic ("Results", "Background") says nothing, so make it the sentence that section proves. The piece's own title follows the same rule: a storyboard, a report, or a deck is named for its ask and its reason ("Launch at $150 to $200, with the newer products"), never for what kind of document it is ("Pricing review storyboard").
- Under each heading, write the figures it rests on. A heading that speaks for several series or years has to be true of every one of them: "every service got faster" fails if one got slower, and "under 200 ms all year" fails if March was 240.
- A pair of headings can set up and pay off. "XML is under 4% of exports" makes the room expect a small problem, and "It is 38% of the export tickets" is the turn.
- Everything under a heading supports that heading. Anything else moves or goes.

## Repetition

Say what the piece will show, show it, then say what it showed, with the ask. To the writer this feels like saying it three times. To a reader seeing it for the first time, it is what makes the point stay.

A short phrase the reader can repeat to someone else does more than a paragraph. "Storage doubled since June" travels, and a table doesn't.

## Presented live or read alone

The same material needs two versions (chapter 9's case on animating what you present).

- Presented, the speaker controls what is seen and when. Slides stay sparse and the detail is spoken. Plan each step three ways: what is on the screen, what changed from the step before, and the sentence said aloud that leads to the next. Write that sentence even when only the slides were asked for, because the slides are the smaller part of a talk. Build one graph up in steps: the empty axes first, so the room learns how to read it, then one series or one highlight at a time. Keep the same graph and the same order of categories all the way through, and change only what is emphasized. A new chart on each slide makes the room learn to read again.
- Read alone, the reader controls the pace and nobody is there to explain. Use one version of the graph, annotated with what a speaker would have said, and words that say what each section means for the reader.

One document doing both jobs does neither well. When there is time for one version only, make the one that will be read alone.

## A talk, worked through

Five minutes at a live roadmap review, where the head of product decides what the next two quarters drop. The data is a year of exports by format, the support tickets about exports, and which accounts use XML. The first draft was six charts with titles such as "Exports by format" and "Tickets by category". The story notes:

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

1. End XML export on 30 September, with a converter first. This is the ask, and it says what the five minutes will cover.
2. Export problems are the largest category in support: 412 of 1,960 tickets last year.
3. XML is under 4% of exports: 3,600 of 101,000 a month.
4. It is 38% of the export tickets: 157 of 412.
5. Three accounts make 91% of the XML exports, and they pay $410k a year.
6. A converter for those three takes three engineer-weeks once, against two every quarter to keep XML alive.
7. Decision today: end XML on 30 September, converter first.

Each step of the talk, planned three ways:

| Step | On the screen | What changed | Said aloud |
| --: | :-- | :-- | :-- |
| 1 | The ask as one sentence | | "I'm asking you to end XML export on 30 September, with a converter first. Here is why, and what it costs." |
| 2 | Support tickets by category, as bars, with exports in the accent color | | "Exports are our largest support category: 412 tickets last year." |
| 3 | Monthly exports by format, as three bars, with XML in the accent color | a new chart | "XML is 3,600 of 101,000 exports a month. Under 4%." |
| 4 | The same three bars, now counting export tickets | the bars change; the order and the colors stay | "The same three formats, counted by tickets. XML is 157 of 412." |
| 5 | The 19 accounts that use XML, as bars, with three in the accent color | a new chart | "Three accounts make 91% of those exports, and they pay us $410k a year. So we can't switch it off today." |
| 6 | Two numbers: three weeks once, two weeks every quarter | | "A converter for those three takes three engineer-weeks. Keeping XML alive takes two every quarter." |
| 7 | The ask again, with the date | | "So: end XML on 30 September, converter first. Can it go on the Q2 roadmap?" |

Step 1 says what is coming. Steps 3 and 4 are one bar chart shown twice, the setup and the turn, with XML in the accent color both times. Step 5 raises the objection before the room does, and step 6 answers it with the cost of each alternative, so the recommendation has a reason the alternatives lack. Step 7 is the ask from step 1, now with its reasons behind it.

## Checks (step 6)

- Read the headings alone, in order. They should tell the story.
- Read each section against its heading.
- Find the alternatives the reader will weigh. Each is on the page with what the data says about it, and the recommendation has a reason they lack.
- Find the number that cuts against the recommendation. It is on the page where the reader would raise it, with its answer beside it. A weak spot named and left unanswered is the objection the room will raise.
- Read the three sentences again. If the finished piece has become a different story, one of the two is wrong.
- Write down the point of each section and compare the list with the outline you started from.
- Give it to someone who doesn't know the subject and ask what they think it says and where they got lost.

## The appendix

The detail a skeptic will ask for goes at the back: the full table, the method, the cases that were checked and came to nothing. It is there when someone wants it and out of the way otherwise.

A recurring report can be improved without rebuilding it. Put a short page in front that tells this period's story, and let the old report become the appendix behind it.
