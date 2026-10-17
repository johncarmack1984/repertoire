---
name: sidework
description: Run a task in its own git worktree beside the main checkout (../<repo>-sidework-<session>), not nested inside the repository, and leave the main checkout untouched.
argument-hint: "[<name>:] <task>"
disable-model-invocation: true
---

# Sidework

Do the task in a dedicated git worktree that sits next to the main checkout:

```
<parent>/<repo>/                      main checkout: never modified
<parent>/<repo>-sidework-<session>/   this session's worktree
```

A sibling sits at the same depth as the main checkout, so relative paths (`path = "../shared"` in a Cargo.toml, `cd ../other-repo` in a justfile, `file:../pkg`) resolve the same way from both, and tools that walk up parent directories (Cargo's `.cargo/config.toml` merge, `just`'s fallback, Node's `node_modules` lookup) never reach into the main checkout. Never create the worktree inside the repository (for example under `.claude/worktrees/`), and don't put it in a temp directory.

## Start

1. **Find the main checkout.** In `git worktree list --porcelain`, the first `worktree` entry is the main checkout, even when the session starts inside another worktree. If the session starts outside any repository, use the repository the task names, and ask if it names none.
2. **Read the repo's sidework notes**, if it keeps any: `.claude/*sidework*.md` in the main checkout, and sidework entries in the project memory. Notes override the defaults below (base branch, branch prefix, install steps, files to copy).
3. **Name the session**: a short kebab-case slug for the task (`bench-index-fix`, `8412-feedback`), or the name the task gives when it starts with `<name>:`. The worktree path is `<parent>/<repo>-sidework-<session>`.
4. **Check for an existing lane.** Run `git worktree list` and `git branch -vv`, where a `+` marks a branch checked out in another worktree.
   - The path exists and is clean: reuse it when the task continues that work.
   - The path exists with uncommitted changes, or the task's branch is checked out in another worktree: another session owns it, so leave it alone. If the task is the same work (same PR, same branch), report the overlap and stop; otherwise choose another name.
   - The path exists but is not a worktree of this repository: choose another name.
5. **Choose the branch and base.**
   - Work on an existing branch or pull request: check out that branch in the worktree instead of creating one (for a GitHub PR, add the worktree with `--detach` and run `gh pr checkout <number>` inside it), then fast-forward it to its remote.
   - Anything else gets a new branch `<prefix><session>`. Read the prefix with `echo "prefix: $(git -C <main> config --get sidework.branchPrefix)"`; when that prints nothing after the colon, use the notes' convention, else `sidework/`. Run `git fetch`, then base the branch on the default branch of `upstream` when that remote exists (origin is then a fork), else of `origin`, else the local default branch when there is no remote. `git symbolic-ref --short refs/remotes/<remote>/HEAD` names a remote's default branch; run `git remote set-head <remote> --auto` if it's unset.
   - Never start from the main checkout's current HEAD or its uncommitted changes. If the task needs that work, say so and ask.
6. **Create the worktree**: `git -C <main> worktree add -b <branch> <path> <base>`, or `git -C <main> worktree add <path> <branch>` for an existing branch.
7. **Set it up.**
   - If `.gitmodules` exists: `git -C <path> submodule update --init --recursive`.
   - Copy the gitignored files the work needs from the main checkout: those matching its `.worktreeinclude`, plus any the notes name (`.env`, local config). Never overwrite tracked files.
   - Install dependencies with the tool the lockfile names: `bun.lock` or `bun.lockb` → `bun install --frozen-lockfile`, `pnpm-lock.yaml` → `pnpm install --frozen-lockfile`, `package-lock.json` → `npm ci`, `yarn.lock` → `yarn install --immutable` (`--frozen-lockfile` on Yarn 1), `uv.lock` → `uv sync --frozen`.
   - Rust needs no install, but the worktree's first build is cold, so start it in the background early. Keep the worktree's own `target/`: never point `CARGO_TARGET_DIR` at the main checkout's, where other sessions build.
8. **Announce**: `Sidework: <session> at <path> on <branch> (from <base>)`.

## While working

- The main checkout is read-only: don't edit its files, switch its branch, stage, stash, reset, or build in it. Other sessions' worktrees are off limits too.
- The shell can reset to the launch directory between commands, so begin each command with `cd <path> &&` or use `git -C <path>`, and give file tools absolute paths. Before every edit, check that the path starts with `<path>/`.
- Run the repo's own commands (`just`, `cargo`, package scripts) from inside the worktree.
- Don't call EnterWorktree: with a name it nests a new worktree under `.claude/worktrees/`, and entering this worktree by path asks the user for approval and swaps the session's CLAUDE.md and settings for the worktree's. Give subagents the worktree path rather than `isolation: "worktree"`.
- Parallel sessions share the machine: pick free ports for dev servers, and don't stop processes you didn't start.
- If every read or edit in the worktree asks for permission, tell the user once that `/add-dir <parent>` (or launching Claude from `<parent>`) stops it.

## Finish

- Commit each verified unit on the branch in the repo's commit style, staging files by path. Keep the repo's hooks and signing on.
- Leave the worktree clean. Commit unfinished work as a WIP commit instead of stashing it: the stash list is shared with the main checkout.
- Don't push, open pull requests, or post anything unless the task says to; when it does, push to `origin`, never `upstream`. Don't remove the worktree or the branch unless asked; when asked, use `git -C <main> worktree remove <path>`.
- If you learned something the next sidework session in this repo needs (a setup step, a trap), add it to the notes file from step 2 when that file is gitignored, else to the project memory, else list it in the recap.
- Recap: the session, path, branch and tip SHA, the checks you ran and their results, and anything left for the user, such as the push command.

## Task

$ARGUMENTS
