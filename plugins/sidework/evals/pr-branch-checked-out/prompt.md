---
description: Review feedback on an existing branch. The worktree should check out that branch rather than cut a new one, and commit there without pushing.
tags: [behavior, pr]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Bash, Read, Edit, Write, Glob, Grep, Skill]
---

/sidework retry-feedback: review feedback on the feature/retry branch in ./app. In a separate worktree, rename `max_tries` to `max_attempts` in src/retry.rs and commit it.
