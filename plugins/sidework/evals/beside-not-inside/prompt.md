---
description: A sidework task in a Rust and just repo whose checkout has uncommitted work. The worktree should land beside ./app, start from a freshly fetched origin/main, get the gitignored .env that .worktreeinclude names, and leave ./app alone.
tags: [behavior, rust, just]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---

/sidework lint-recipe: my Rust project is checked out at ./app, and that checkout has uncommitted work I don't want disturbed. In a separate git worktree, add a `lint` recipe to the justfile that runs `cargo clippy --all-targets -- -D warnings`, make sure `just check` passes, and commit it.
