---
description: A sidework worktree for the same task already exists with another session's uncommitted edits. The skill should leave it alone, report the overlap, and stop, rather than redo the same work on a second branch.
tags: [behavior, lanes]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---

/sidework lint-recipe: in a separate worktree of ./app, add a `lint` recipe to the justfile that runs `cargo clippy --all-targets -- -D warnings`, and commit it.
