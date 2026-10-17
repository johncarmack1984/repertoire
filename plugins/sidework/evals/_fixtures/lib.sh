# shellcheck shell=bash
# Shared setup for the eval cases. Each case's scaffold.sh sources this file.
#
# A scaffold runs in the run's empty workspace, which stands in for the folder
# that holds your checkouts: the repository goes in ./app, so a sibling worktree
# (./app-sidework-<session>) lands inside the workspace, where the eval sandbox
# allows writes.

set -euo pipefail

# Keep the operator's git config out of the fixtures (signing, hooks, templates)
# and fix identities and dates so fixture commits hash the same everywhere.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME="Fixture" GIT_AUTHOR_EMAIL="fixture@example.invalid"
export GIT_COMMITTER_NAME="Fixture" GIT_COMMITTER_EMAIL="fixture@example.invalid"
export GIT_AUTHOR_DATE="2026-01-01T12:00:00Z" GIT_COMMITTER_DATE="2026-01-01T12:00:00Z"

WORKSPACE="$(pwd)"

g() { git -c init.defaultBranch=main -c commit.gpgsign=false "$@"; }

commit_all() { # <repo> <message>
  g -C "$1" add -A
  g -C "$1" commit -q -m "$2"
}

# The crate the app depends on by relative path. A plain folder beside the app,
# as a second checkout often is.
write_shared() { # <dir>
  mkdir -p "$1/src"
  cat > "$1/Cargo.toml" <<'EOF'
[package]
name = "shared"
version = "0.1.0"
edition = "2021"
EOF
  cat > "$1/src/lib.rs" <<'EOF'
pub fn salutation() -> &'static str {
    "Hello"
}
EOF
}

# A small Rust crate driven by just, with a path dependency on ../shared, a
# gitignored .env, and a .worktreeinclude that names it.
write_app() { # <dir>
  mkdir -p "$1/src"
  cat > "$1/Cargo.toml" <<'EOF'
[package]
name = "app"
version = "0.1.0"
edition = "2021"

[dependencies]
shared = { path = "../shared" }
EOF
  cat > "$1/src/lib.rs" <<'EOF'
//! Greeting helpers.

/// Builds the greeting we send when we recieve a new user.
pub fn greet(name: &str) -> String {
    format!("{}, {name}!", shared::salutation())
}

#[cfg(test)]
mod tests {
    #[test]
    fn greets() {
        assert_eq!(super::greet("Ada"), "Hello, Ada!");
    }
}
EOF
  cat > "$1/justfile" <<'EOF'
# List the recipes.
default:
    @just --list

# Fast checks that need no toolchain: the path dependency resolves and the crate is in place.
check:
    test -f ../shared/Cargo.toml || { echo "error: path dependency ../shared not found" >&2; exit 1; }
    test -f src/lib.rs

# Run the tests.
test:
    cargo test
EOF
  cat > "$1/README.md" <<'EOF'
# app

Greeting helpers. Run `just check` before you commit.
EOF
  printf '/target\n.env\n' > "$1/.gitignore"
  printf '.env\n' > "$1/.worktreeinclude"
}

# Identity for the commits the agent makes: the run's home has no git config.
agent_identity() { # <repo>
  g -C "$1" config user.name "Eval User"
  g -C "$1" config user.email "eval@example.invalid"
}

# Local state a real checkout carries: an ignored .env and uncommitted work.
user_state() { # <repo>
  printf 'DATABASE_URL=postgres://localhost/app_dev\n' > "$1/.env"
  printf '\n// wip: trying a warmer greeting, not ready to commit\n' >> "$1/src/lib.rs"
}

# The standard layout: origin.git (the remote), app (a clone of it, with local
# state), and shared (the path dependency). origin gains one commit after the
# clone, so the checkout's origin/main is stale until someone fetches.
standard_layout() {
  write_shared "$WORKSPACE/shared"
  local seed="$WORKSPACE/.seed"
  write_app "$seed"
  g init -q "$seed"
  commit_all "$seed" "Initial commit"
  g clone -q --bare "$seed" "$WORKSPACE/origin.git"
  g clone -q "$WORKSPACE/origin.git" "$WORKSPACE/app"
  printf '# Changelog\n\n## 0.1.1\n\n- Document the check recipe.\n' > "$seed/CHANGELOG.md"
  commit_all "$seed" "Add a changelog"
  g -C "$seed" push -q "$WORKSPACE/origin.git" main
  rm -rf "$seed"
  agent_identity "$WORKSPACE/app"
  user_state "$WORKSPACE/app"
}
