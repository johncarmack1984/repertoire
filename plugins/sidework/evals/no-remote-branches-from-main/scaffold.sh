#!/usr/bin/env bash
# shellcheck source=../_fixtures/lib.sh
source "$(dirname "$0")/../_fixtures/lib.sh"
# A local-only repo whose checkout is on a work-in-progress branch with a
# commit main doesn't have, plus uncommitted changes.
write_shared "$WORKSPACE/shared"
write_app "$WORKSPACE/app"
g init -q "$WORKSPACE/app"
commit_all "$WORKSPACE/app" "Initial commit"
g -C "$WORKSPACE/app" switch -q -c wip
printf '# Notes\n\nHalf-finished refactor of the greeting API.\n' > "$WORKSPACE/app/WIP_NOTES.md"
commit_all "$WORKSPACE/app" "WIP: refactor notes"
agent_identity "$WORKSPACE/app"
user_state "$WORKSPACE/app"
