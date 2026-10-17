#!/usr/bin/env bash
# shellcheck source=../_fixtures/lib.sh
source "$(dirname "$0")/../_fixtures/lib.sh"
standard_layout
# Another session is already working on the same task, with uncommitted edits.
g -C "$WORKSPACE/app" worktree add -q -b sidework/lint-recipe "$WORKSPACE/app-sidework-lint-recipe" origin/main
printf '\n# lint: WIP from another session\nlint:\n    cargo clippy\n' >> "$WORKSPACE/app-sidework-lint-recipe/justfile"
