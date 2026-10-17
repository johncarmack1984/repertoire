#!/usr/bin/env bash
# shellcheck source=../_fixtures/lib.sh
source "$(dirname "$0")/../_fixtures/lib.sh"
# origin carries a feature branch under review; the checkout has only its
# remote-tracking ref.
write_shared "$WORKSPACE/shared"
seed="$WORKSPACE/.seed"
write_app "$seed"
g init -q "$seed"
commit_all "$seed" "Initial commit"
g -C "$seed" switch -q -c feature/retry
cat > "$seed/src/retry.rs" <<'RS'
/// Runs `op` until it succeeds, at most `max_tries` times.
pub fn retry<T, E>(max_tries: u32, mut op: impl FnMut() -> Result<T, E>) -> Result<T, E> {
    let mut attempt = 1;
    loop {
        match op() {
            Ok(value) => return Ok(value),
            Err(err) if attempt >= max_tries => return Err(err),
            Err(_) => attempt += 1,
        }
    }
}
RS
printf '\npub mod retry;\n' >> "$seed/src/lib.rs"
commit_all "$seed" "Add a retry helper"
g -C "$seed" switch -q main
g clone -q --bare "$seed" "$WORKSPACE/origin.git"
rm -rf "$seed"
g clone -q "$WORKSPACE/origin.git" "$WORKSPACE/app"
agent_identity "$WORKSPACE/app"
user_state "$WORKSPACE/app"
