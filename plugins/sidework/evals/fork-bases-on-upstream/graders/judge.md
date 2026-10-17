---
type: llm
focus: trace
---
PASS only if all of these hold in the trace:

1. The agent fetched and created the worktree from upstream's default branch (for example `upstream/main`), not from origin/main or the checkout's HEAD.
2. The worktree sits beside ./app in the same parent folder, on a new branch named `dev/typo` (the repo sets `sidework.branchPrefix` to `dev/`).
3. The fix was made and committed in that worktree, and ./app's files, branch, index, and stash were never changed.
4. Nothing was pushed to either remote.

Otherwise FAIL, and name the first rule that was broken.
