# repertoire

Skills for coding agents, published as Claude Code plugins. Each is also a plain skill directory with a `SKILL.md`, scripts, and references, so any runner that follows the open agent skill standard can load it.

| Plugin | What it does |
|---|---|
| [`sidework`](plugins/sidework/) | Runs a task on its own branch in a git worktree beside your checkout. Leaves your checkout untouched. |
| [`build-review-lens`](plugins/build-review-lens/) | Reads a repository's PR history to find who reviews and what passes, then writes a lens skill for each reviewer to review your branch as that maintainer would. |

## Install

As Claude Code plugins:

```
/plugin marketplace add johncarmack1984/repertoire
/plugin install sidework@repertoire
/plugin install build-review-lens@repertoire
```

Or as personal skills, from a clone:

```sh
git clone https://github.com/johncarmack1984/repertoire
ln -s "$PWD/repertoire/plugins/sidework/skills/sidework" ~/.claude/skills/sidework
ln -s "$PWD/repertoire/plugins/build-review-lens/skills/build-review-lens" ~/.claude/skills/build-review-lens
```

## sidework

Claude Code's own worktrees go in `.claude/worktrees/`, inside the repository, where Cargo, just and Node all see the checkout's config on top of the branch's. sidework puts each task's worktree beside the checkout instead. The table of what breaks nested, and the lab script that reproduces it, are in [its README](plugins/sidework/README.md).

## Review lenses

A review lens turns evidence of a maintainer's reviews into a review you can run before theirs. `build-review-lens` reads a repo's PR history, giving more weight to the last six months, to find who actually reviews and what passes. It writes a `<name>-lens` skill that reviews your branch as that maintainer will, leaving them nothing to flag when the PR opens.

The evidence comes from review habits. CONTRIBUTING.md describes the project maintainers want; merged PRs and their comments show the project they run. Once one repo's lens was tuned, PRs started merging on sight. A neighboring repo with a different maintainer kept sending the same comments back.

The mining script ranks reviewers by activity, weighted toward recent reviews. It shows who merges and how long outside contributors wait by PR size, then collects every word from each top reviewer, grouped by PR. A few merged PRs are held back to test the finished lens against comments it hasn't seen. The lens is one file: steps, rules backed by verbatim evidence and PR numbers, and pitfalls the repo's CI never spells out. The lens template, the evidence template and the refinement loop are in [`reference/`](plugins/build-review-lens/skills/build-review-lens/reference/).

## Development

`just validate` checks the marketplace and both plugins with `claude plugin validate --strict`. `just lint` runs shellcheck over sidework's scripts and compiles the lens miner. `just eval sidework` runs sidework's eval suite, and `just lab` reproduces the nested-worktree failures. CI runs the same checks on every push and pull request; the evals workflow runs on demand and needs an `ANTHROPIC_API_KEY` secret.
