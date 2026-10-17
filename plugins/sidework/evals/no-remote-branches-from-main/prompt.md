---
description: A repo with no remote whose checkout sits on a WIP branch. The new branch should start from the local default branch, not from the checkout's HEAD, and the checkout should stay on its branch with its changes.
tags: [behavior, no-remote]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---

/sidework fmt-recipe: ./app is a local-only repo with no remote, and I'm in the middle of something on its wip branch. In a separate worktree, add a `fmt` recipe to the justfile that runs `cargo fmt --all`, and commit it.
