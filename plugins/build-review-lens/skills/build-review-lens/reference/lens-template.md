# Lens template

The skeleton every lens follows. Copy it, replace every `<…>`, delete every guidance line (they start with `>`). The shape is fixed because the lens is run by an agent under time pressure: Steps first, flat Rules second, Gotchas last. Keep it one file.

```markdown
---
name: <first>-lens
description: Review a <owner>/<repo> branch or PR the way <Full Name> (<login>, <role in one clause>) reviews, and apply the rulings before it opens. Use on "<First> lens", "would <First> take this", before opening or pushing any <repo> PR, and when <First>'s review comments arrive.
---

# <First> lens

<One paragraph. Who they are to the repo, with the number that proves it ("315 of ~600 reviews on the last 300 merged PRs"; "76% of recent review weight"). Their pace and register in a clause each: one-line inline comments, suggestion commits, approve-with-caveats, same-day squash merges, re-makes the same comment across rounds for people who don't internalize it. Then the sentence that names the job: "The lens is their review, run before they run it." Where people facts live (the folder's CLAUDE.md), where the verbatim evidence lives (`lens-evidence/<repo>.md`), and "this file is the review itself.">

## Steps

1. **Scope the diff.** `git diff <upstream>/<default-branch>...HEAD` (never the fork's own main) plus the PR title and body draft, every image and number in it, and every comment from every earlier round on the PR. Every hunk, test name, comment and body sentence is in scope.
2. **Strip before you review.** For every file in the diff ask whether the fix stops working without it. Tests, benches, helpers and doc prose that exist only to support the fix are candidates to cut, not polish. Review what survives.
3. **Apply every rule below to every hunk.** Each hit is a ruling: *apply* (mechanical, do it now) or *<owner>* (a design call, a claim only the author can make, or a message to the reviewer). A rule with no hit is stated as checked.
4. **Apply the mechanical rulings and re-verify** with the repo's own commands: <the exact lint, typecheck, unit, integration and snapshot commands this repo runs in CI, found in its CI config, justfile or package.json, never assumed; the narrowest build the change touches; the whole suite for anything that changes shared behaviour>. <Changelog entry rule if the repo has one.>
5. **Fact-check the PR body against the new tip** on every push, not just the first: every claim reproducible from the repo, every image captioned, every number re-measured. <Voice pass with the author's voice skill, if one exists.>
6. **Report**: one line per ruling naming the rule it came from, then what is left for <owner>. Done means every rule applied to the whole diff and body, every prior-round comment accounted for, and every *apply* ruling verified.

## Rules (evidence in parentheses)

> One paragraph per rule. Bold lead that states what PASSES, in the positive ("Doc comments state what in one line"), never only the ban. Then what the rule means in this repo, then the evidence: the reviewer's words verbatim (typos included), the PR number, the date. Two quotes make a rule; one quote is a candidate and says so. Order: the rules that cost whole rounds first (scope, size, body), then code shape, then tests, then docs and comments, then the review cycle.

**<Rule lead.>** <What passes and why they care.> ("<verbatim quote>", #<PR>, <YYYY-MM-DD>; "<second quote>", #<PR>).

**<Rule lead.>** …

**The review cycle is theirs.** <How they merge, how fast, what a self-close or a nudge reads as, whether suggestion commits should be accepted as-is, whether an approval closes the cycle, what "optional" means from them, how to answer a hunk comment (one line plus the sha), how to re-request review.>

**Reviewing their PRs.** <The register for commenting on the reviewer's own PRs: lead with the one finding that unblocks them, verified, with a suggestion block; stop when they stop applying; style items held back.>

## Who will review

> Only for a repo with more than one reviewer. Route by path: which directories pull which second reviewer in, and what each one asks first. Bots that review every PR and what the humans do with their output.

## Gotchas the environment does not confess

> Facts no config file states and CI only teaches by going red: stale generated files after a rebase, a flaky shard that is infra not you, a lint whose column points at the wrong cast, a docs job that checks in-page anchors, an API the fork cannot call. Start with what the evidence already shows; every lesson learned in use lands here with its date and PR.

- <gotcha, with the PR and date it was learned>

## <Owner>'s bar

> The author's own standing rules for this repo, dated and quoted, where they go beyond the reviewer's: body length, tables only where numbers change, no attribution trailers in commits, what waits for the author's click.
```

Naming: one gatekeeper (at or above half of recent review weight) gets a lens named for them and written as their review. Two strong reviewers get two lenses, run in a stated order, with one of them named as the owner of the PR body so their conflicting preferences are reconciled by design and not per round. A team gets a lens named for the repo with a block per reviewer and a routing section.
