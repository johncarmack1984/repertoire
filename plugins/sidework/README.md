# sidework

Run Claude Code tasks in git worktrees beside your checkout, not inside it.

Claude Code's own worktrees (`claude --worktree`, the `EnterWorktree` tool, subagents with `isolation: "worktree"`) go in `.claude/worktrees/<name>/`, inside the repository. sidework is a skill that puts each task's worktree next to the checkout instead, on its own branch, and leaves the checkout alone:

```
~/code/app/                          your checkout, untouched
~/code/app-sidework-lint-recipe/     one session
~/code/app-sidework-8412-feedback/   another
```

## Why not nested

A nested worktree sits two directories below the checkout, inside it. Anything that resolves a relative path or walks up parent directories sees a different project from there. In a Rust repo driven by just, that breaks four ways, and `scripts/nesting-lab.sh` reproduces each one:

| | nested in `.claude/worktrees/` | beside the checkout |
|---|---|---|
| `shared = { path = "../shared" }` | fails: `../shared` not found | resolves |
| a rustflag your branch removed from `.cargo/config.toml` | still passed to rustc | gone |
| `just old-recipe`, removed on your branch, with `set fallback` | runs, in the main checkout | errors |
| `require("some-dep")` before you install | loads the main checkout's copy | not installed |

Cargo merges every `.cargo/config.toml` from the working directory up to the root and joins arrays like `rustflags`, so a nested worktree builds with the checkout's config on top of its own. With `set fallback := true`, just looks in parent directories for a recipe it can't find and runs it there. Node searches every parent's `node_modules`. A sibling has the same parents as the checkout, so none of that reaches into it.

## Install

As a Claude Code plugin:

```
/plugin marketplace add johncarmack1984/sidework
/plugin install sidework@sidework
```

Or as a personal skill:

```sh
git clone https://github.com/johncarmack1984/sidework
ln -s "$PWD/sidework/skills/sidework" ~/.claude/skills/sidework
```

## Use

```
/sidework add a lint recipe to the justfile
/sidework 8412-feedback: address the review comments on #8412
```

A leading `<name>:` names the session; otherwise it's named for the task. sidework runs only when you type `/sidework`: Claude never loads it on its own, so installing it doesn't change how Claude handles any other request for a worktree.

Each session:

1. finds the main checkout and reads the repo's sidework notes, if it keeps any;
2. checks that no other session owns that worktree or branch, and stops to tell you if one does;
3. adds `../<repo>-sidework-<session>` on a new branch from the freshly fetched default branch (upstream's when origin is a fork, the local one when there's no remote), or on the existing branch for review feedback;
4. copies the gitignored files your `.worktreeinclude` names, initializes submodules, and installs dependencies with the tool your lockfile names;
5. does the work there, commits it, and reports the path, branch, tip SHA, and the checks it ran.

It never changes the checkout's files or branch, never stashes (the stash list is shared across worktrees), and doesn't push, open pull requests, or remove the worktree unless you ask.

## Configure

- **Branch prefix.** Branches are `sidework/<session>` by default. `git config --global sidework.branchPrefix me/` makes them `me/<session>`; drop `--global` to set it for one repo.
- **Repo notes.** Setup steps and traps for one repo go in `.claude/sidework.md` in its main checkout: an install command, files to copy, a different base branch, a branch convention. Every session reads the file first, and adds what it learns when the file is gitignored.
- **Permissions.** A sibling worktree is outside the directory you launched Claude in, so reads and edits there ask for approval by default. Launch Claude from the parent folder, or add that folder as a working directory (`claude --add-dir ..`, `/add-dir ..`, or `permissions.additionalDirectories`), and the worktree follows your permission mode the way the checkout does.

`EnterWorktree` could move the session into the worktree instead, but Claude Code asks for approval every time it enters one outside `.claude/worktrees/`, and the move swaps the session's `CLAUDE.md` and settings for the worktree's. sidework stays in the launch directory and works in the worktree by absolute path.

## Evals

`evals/` is a [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals) suite. Each case builds a fixture repo with a scaffold script, runs Claude on a task with and without the plugin, and grades what's left on disk.

- **Behavior** (with a shell): a task in a Rust and just repo with uncommitted work; a fork whose `origin/main` is stale, with a branch prefix set in its git config; a repo with no remote, checked out on a WIP branch; a worktree another session already owns; review feedback on an existing branch. Each prompt invokes `/sidework` and asks for a separate worktree, so the run without the plugin gets the same request. Graders check where the worktree landed, which base it started from, that the change was committed on the right branch, and that the checkout's files, branch, and stash are unchanged and nothing was pushed. An LLM judge reads the trace for the rest.
- **Invocation** (no shell): plain requests like "spin up a worktree" and "do this on the side" don't load the skill, and `/sidework` does.

```sh
just eval              # the whole suite; runs each case's scaffold as you
just eval-invocation   # the invocation cases only
```

Cases that grant a shell run under Claude Code's sandbox (macOS, or Linux with `bubblewrap` and `socat`), and the harness refuses them on a machine whose cloud credential config it can't wall off, an AWS `credential_process` for one. The `evals` workflow runs the suite in GitHub Actions on demand; it needs an `ANTHROPIC_API_KEY` repository secret.

## License

MIT
