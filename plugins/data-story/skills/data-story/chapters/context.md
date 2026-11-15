# Context

Step 1 of the flow in `SKILL.md`, from chapter 1 of *Storytelling with Data*, "the importance of context". Most of the result is decided here, before anything is drawn. The answers go in the brief.

## Who, what, how

- Who is the one reader? A person or a role with a decision to make: the maintainer who merges, the director who owns the budget, the committee that funds the program. "Stakeholders" and "anyone interested" are too many people to write for. When two audiences need different things, write for the one who decides, or make two pieces.
- What do they already know, what do they want, and what will they doubt? The answers set how much background and how much proof the page needs. A reader who trusts you needs less of both than one meeting you for the first time.
- What should they know or do when they finish? Start the answer with a verb they can act on: approve, merge, choose, fund, fix, stop, wait. You have been closer to the data than they have, so recommend something. Where the decision isn't yours to recommend, propose a next step, so they have something to react to. With no answer there is nothing to present yet.
- How will it reach them? Read alone (a PR, a README, a report, an email), the page has to answer what a presenter would have answered. Presented live, the page stays sparse and the detail is spoken. Decide the tone as well: a win, a warning, a routine update.

Take the answers from the request and what surrounds it: the thread, the repo, the file names, who asked. Ask only when the reader or the ask can't be inferred and a wrong guess would change the result. Otherwise go ahead, and state the assumption when you deliver. When you do ask, ask whoever wanted the work the questions a presenter would want answered: who will read it and what they care about, what decision it feeds, what the reader already believes, what could make them say no, and what a good outcome looks like.

## The point

- What does the data say? Find out first, any quick way. Look for what holds across every series, and for the one that breaks the pattern. For runs you measured, such as benchmarks and timings, `reference/measurements.md` says which statistic describes them and what to do with a slow run. That exploring is for you: of the hundred things you looked at, the reader gets the one or two that matter.
- With three minutes and no visuals, what would you say? Write that paragraph: what was going on, what changed or what you found, what it means for this reader, what you recommend.
- With one sentence? That sentence is the Big Idea. It states your point of view, says what is at stake, and is a complete sentence. "Cache latency results" is a topic. "The cache cuts p99 latency by a third at no memory cost, so it should ship in 4.2" is a Big Idea.
- Which two or three numbers make the sentence true, and which numbers cut against it? The second kind stays in: a reader who finds it alone stops believing the rest.
- What happens if nothing is done? That is what is at stake, and the reader should see it.

The brief stands in for the storyboard she sketches before building anything: an outline settled first, so everything after it has one direction.
