---
type: llm
focus: trace
weight: 2
---
PASS only if all of these hold in the trace:

1. The agent made the justfile change and ran `just check` inside a separate git worktree whose directory sits beside ./app in the same parent folder, not inside ./app and not in a temp directory.
2. It never changed the ./app checkout's files, branch, index, or stash. Running `git fetch` or `git worktree add` against ./app is fine.
3. It committed the change on a branch in the new worktree and left nothing uncommitted there.
4. It did not push.
5. Its final message names the worktree path and the branch.

Otherwise FAIL, and name the first rule that was broken.
