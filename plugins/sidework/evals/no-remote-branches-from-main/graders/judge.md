---
type: llm
focus: trace
---
PASS only if all of these hold in the trace:

1. The agent created the worktree beside ./app, on a new branch that starts from `main`, not from `wip` or HEAD.
2. It made and committed the justfile change in that worktree.
3. ./app stayed on `wip` with its uncommitted changes: the agent never ran checkout, switch, stash, reset, add, or commit in ./app.

Otherwise FAIL, and name the first rule that was broken.
