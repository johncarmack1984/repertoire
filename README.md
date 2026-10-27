# repertoire

Skills for coding agents, published as Claude Code plugins. Each is also a plain skill directory with a `SKILL.md`, scripts, and references, so any runner that follows the open agent skill standard can load it.

| Plugin | What it does |
|---|---|
| [`sidework`](plugins/sidework/) | Runs a task on its own branch in a git worktree beside your checkout. Leaves your checkout untouched. |
| [`build-review-lens`](plugins/build-review-lens/) | Reads a repository's PR history to find who reviews and what passes, then writes a lens skill for each reviewer to review your branch as that maintainer would. |
| [`data-story`](plugins/data-story/) | Puts measured numbers in front of a reader: the takeaway sentence first, then a sentence, a table or a chart, and a line on how it was measured. |

## Install

As Claude Code plugins:

```
/plugin marketplace add johncarmack1984/repertoire
/plugin install sidework@repertoire
/plugin install build-review-lens@repertoire
/plugin install data-story@repertoire
```

For any agent that reads skills, with the skills CLI:

```
npx skills add johncarmack1984/repertoire
```

Or as personal skills, from a clone:

```sh
git clone https://github.com/johncarmack1984/repertoire
ln -s "$PWD/repertoire/plugins/sidework/skills/sidework" ~/.claude/skills/sidework
ln -s "$PWD/repertoire/plugins/build-review-lens/skills/build-review-lens" ~/.claude/skills/build-review-lens
ln -s "$PWD/repertoire/plugins/data-story/skills/data-story" ~/.claude/skills/data-story
```

## sidework

Claude Code's own worktrees go in `.claude/worktrees/`, inside the repository, where Cargo, just and Node all see the checkout's config on top of the branch's. sidework puts each task's worktree beside the checkout instead. The table of what breaks nested, and the lab script that reproduces it, are in [its README](plugins/sidework/README.md).

## Review lenses

A review lens turns evidence of a maintainer's reviews into a review you can run before theirs. `build-review-lens` reads a repo's PR history, giving more weight to the last six months, to find who actually reviews and what passes. It writes a `<name>-lens` skill that reviews your branch as that maintainer will, leaving them nothing to flag when the PR opens.

The evidence comes from review habits. CONTRIBUTING.md describes the project maintainers want; merged PRs and their comments show the project they run. Once one repo's lens was tuned, PRs started merging on sight. A neighboring repo with a different maintainer kept sending the same comments back.

The mining script ranks reviewers by activity, weighted toward recent reviews. It shows who merges and how long outside contributors wait by PR size, then collects every word from each top reviewer, grouped by PR. A few merged PRs are held back to test the finished lens against comments it hasn't seen. The lens is one file: steps, rules backed by verbatim evidence and PR numbers, and pitfalls the repo's CI never spells out. The lens template, the evidence template and the refinement loop are in [`reference/`](plugins/build-review-lens/skills/build-review-lens/reference/).

## data-story

Numbers in front of a person are an argument, and a table that makes the reader do the arithmetic loses it. `data-story` loads when an agent is about to put measured numbers in a PR description, an issue, a README, a report or a reply: benchmark results, a before/after comparison, a performance claim. It picks the form first. One or two numbers go in a sentence. Values the reader will look up or compare, or more than one measure of the same thing, go in a table. A trend or a distribution goes in a chart, which the skill hands to a charting skill rather than carry chart rules of its own.

The method comes from three books. From Cole Nussbaumer Knaflic's *Storytelling with Data*: audience and context first, the one-sentence takeaway, and the choice between simple text, a table and a graph. From Stephen Few's *Show Me the Numbers*: the table design, with the values being compared side by side, the difference computed for the reader, numbers right-aligned with one precision per column, units in the headers, repeated labels left blank to show the grouping, and nothing in the table that is not data. From Martin Kleppmann's *Designing Data-Intensive Applications*: a measurement is a distribution, so the median and the tail get reported rather than a mean, and response time is a different measure from throughput. The skill's [`reference/sources.md`](plugins/data-story/skills/data-story/reference/sources.md) says which rule came from where.

What the skill produces: the takeaway sentence above the table, including what limits the result; one row per configuration in a meaningful order, with the two variants and their change side by side and time next to cost; and the method below the table, with the statistic, the run count, the spread and the machine. Its evals hand the agent raw benchmark runs and grade the PR section it writes: six configurations with wall and CPU time that belong in one table, one before/after pair that must stay a sentence, and a run set with two slow outliers where a mean would mislead.

## Development

`just validate` checks the marketplace and every plugin with `claude plugin validate --strict`. `just lint` runs shellcheck over sidework's scripts and the eval scaffolds, and compiles the lens miner. `just eval sidework` and `just eval data-story` run those plugins' eval suites, and `just lab` reproduces the nested-worktree failures. CI runs the same checks on every push and pull request; the evals workflow runs on demand and needs an `ANTHROPIC_API_KEY` secret.
