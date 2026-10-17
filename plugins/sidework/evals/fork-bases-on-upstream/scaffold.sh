#!/usr/bin/env bash
# shellcheck source=../_fixtures/lib.sh
source "$(dirname "$0")/../_fixtures/lib.sh"
# upstream is the original project; origin is a fork taken before upstream's
# latest commit, so the fork's main is stale.
write_shared "$WORKSPACE/shared"
seed="$WORKSPACE/.seed"
write_app "$seed"
g init -q "$seed"
commit_all "$seed" "Initial commit"
g clone -q --bare "$seed" "$WORKSPACE/upstream.git"
g clone -q --bare "$seed" "$WORKSPACE/origin.git"
printf '# News\n\n- 0.1.1: greetings are cached.\n' > "$seed/NEWS.md"
commit_all "$seed" "Add release notes"
g -C "$seed" push -q "$WORKSPACE/upstream.git" main
rm -rf "$seed"
g clone -q "$WORKSPACE/origin.git" "$WORKSPACE/app"
g -C "$WORKSPACE/app" remote add upstream "$WORKSPACE/upstream.git"
agent_identity "$WORKSPACE/app"
# This contributor prefixes their branches.
g -C "$WORKSPACE/app" config sidework.branchPrefix dev/
user_state "$WORKSPACE/app"
