# Refining a lens

A lens is finished when the reviewer has nothing left to say that it did not say first. Until then every round of review is training data, and the lens, not a memory file, is where the lesson lands.

## When review comments arrive

1. **Read all of it.** List the reviews with their body lengths before reading anything, then read every non-empty review body and every inline thread, including the ones filed minutes apart: a one-line hunk comment and a review body with the larger ask often arrive as two events. Earlier rounds too, fork PRs included.
2. **Sort each comment.** Covered by an existing rule, or new?
   - Covered: the lens failed at application, not at knowledge. Sharpen the rule's wording so the next run cannot miss it (name the grep, the file pattern, the tell), and check whether a sibling sweep was skipped.
   - New: write the rule now, positive lead, verbatim quote, PR number, date. Two quotes make a rule; mark a single-quote rule as a candidate.
3. **Sweep siblings before they do.** When one instance of a pattern draws a comment, fix every instance in the diff and the series. Reviewers write "same" on the second one, and a re-made comment is the lens failing at its one job.
4. **Answer short, with the sha.** One line per thread, apply, resolve, re-request review. Push one round with everything; a trickle of small pushes reads as unsettled.
5. **Record the pace and the cycle facts** you observed (minutes to first comment, whether approval came with a suggestion commit, whether the body was edited by the maintainer) in the review-cycle rule and the Gotchas.
6. **Record a lesson about the environment** (a stale generated file, a flaky shard, a lint that lies) under Gotchas with the date and PR. Nothing else goes to memory; the lens is the one place, so a session that loads it gets everything.

## When the reviewer de-vibes your text

A maintainer who edits your PR body, deletes your comments or trims your doc prose before merging is teaching. Take note of exactly what they cut and why, and fold it in as a rule the same day: what they cut is what they never want to read again.

## Run it for real

Invoke the lens through the skill mechanism before every push and say which lenses ran. Applying its rules from memory does not count: the file changes between sessions, and the from-memory pass waves through what the current file catches. If a lens was not run, say so plainly.

A lens also briefs a fresh reviewer. For a large diff, hand a subagent the lens file path, the diff, and the body draft, read-only, and ask for one line per ruling in a fixed shape (`RULE <name> | <file>:<line> | HIT: <what> | <apply|owner> | FIX: <change>`) followed by the rules checked with no hit. Several lenses can review the same diff in parallel that way, and a round ships only when every one of them passes.

## Two reviewers, one repo

Their preferences will conflict somewhere (one wants deferred work stated in the body, the other calls a "not in this PR" section noise). Reconcile by design, not per round: decide which lens owns which surface (the body, the tests, the changelog), write the decision into both lenses, and state the order they run in. A single rule like "the second lens owns the body: under 300 words, nothing about what the PR does not do, deferred items become issues the thread can name" ends the oscillation.

## Reviewing their PRs

The lens also carries the register for commenting on the reviewer's own PRs. Lead with the one finding that unblocks them, verified, with a suggestion block they can batch; stop posting once they stop applying; anything non-breaking becomes a follow-on fix after merge, where it reads as observant instead of a pile-on. Functional findings only on someone else's PR; style opinions phrased as the maintainer's are presumptuous there.

## Template questions

Before a lens report or a PR body asks the author anything, check whether the repo's conventions or the reviewer's recorded preferences already answer it. A question whose answer is in the lens is a loop for no reason, and an "open questions for you" section is the tell that a template, not a review, produced the text.

## Re-mine on a schedule

Reviewers leave and arrive. Re-run `mine_reviews.py` when the lens is six months old or when a new name starts approving, compare the ranking and the arc with the lens's opening paragraph, and rewrite the cast if it moved.
