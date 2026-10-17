---
type: llm
focus: trace
---
PASS only if all of these hold in the trace:

1. The agent created a worktree beside ./app with the existing `feature/retry` branch checked out, rather than a new branch.
2. It made the rename in that worktree and committed it on `feature/retry`.
3. It did not push, and it never changed ./app's files, branch, index, or stash.

Otherwise FAIL, and name the first rule that was broken.
