# Evidence corpus template

The lens cites; this file holds what it cites. Every quote verbatim with PR number and date, so a rule can be re-checked without re-mining. Lives beside the lens (`lens-evidence/<repo>.md`), never inside it.

```markdown
# <repo> lens: evidence corpus

Mined <YYYY-MM-DD> with `mine_reviews.py` from <owner>/<repo>: <N> PRs created <from> → <to> (<merged>/<closed>/<open>), the <M> newest inline review comments (<from> → <to>), <other sources: canonical forge, mailing list, Slack export, issue threads>. Quotes are verbatim; `…` marks a capture boundary, not the end of the comment.

## Who reviews

<The ranking table from summary.md, trimmed to the people who matter, with real names and roles from their profiles. The arc: who used to review and left, who arrived, when. Who presses merge and whether authors self-merge.>

## Cast

- **<login> (<Full Name>, <employer or role>)** — <what they review, how they review, what they ask first, their pace>. <Era: since when, how much of the recent weight.>
- …
- **Bots:** <which review bots run on every PR and whether the humans read them>.

## <login> — verbatim

1. "<quote>" (#<PR>, <YYYY-MM-DD>)
2. …

> Ten to thirty quotes per reviewer, newest first, grouped by theme if the list runs long. Keep typos. Keep the ones that recur across PRs; a single-PR opinion is marked as such.

## What passes

- <Pattern> — <quote>, #<PR>.

## What gets declined

- <Pattern> — <quote>, #<PR>. <From raw/declined.md: the reason in the last comment.>

## Outside contributors: how it went

- **#<PR> <author>** (<what it was>): opened <date> → first maintainer reply <date> (<what was asked>) → <rounds> → merged/closed <date>. <Days, rounds.>
- …

## Process and climate

- Merge mode (squash → the body is the commit message), required checks, CLA, changelog, PR template, CODEOWNERS, commit style.
- AI policy or stated norms, with the date and where they were said.
- Release cadence and who cuts releases; freezes.

## Back-test

- <date>: lens v<N> against #<PR>, #<PR>, #<PR> (held out): <hits>/<reviewer comments> predicted; missed: <list, each now a rule>; over-called: <list, each cut>.
```
