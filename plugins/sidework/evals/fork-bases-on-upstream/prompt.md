---
description: In a fork whose origin/main is stale, the worktree should start from upstream's default branch, which carries a commit the fork lacks, on a branch named with the repo's configured sidework.branchPrefix (dev/).
tags: [behavior, fork]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---

/sidework typo: ./app is my fork of a Rust project: origin is my fork and upstream is the original. In a separate worktree, fix the spelling of "recieve" in src/lib.rs and commit it, so I can open a pull request upstream later.
