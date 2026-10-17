#!/usr/bin/env bash
# Shows what goes wrong in a worktree nested inside its repository, next to
# the same checks in a sibling worktree. Builds everything in a temp folder and
# removes it afterward. Uses cargo, just, and node when they're installed.
set -euo pipefail

lab="$(cd "$(mktemp -d)" && pwd -P)"
trap 'rm -rf "$lab"' EXIT
cd "$lab"

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=lab GIT_AUTHOR_EMAIL=lab@example.invalid
export GIT_COMMITTER_NAME=lab GIT_COMMITTER_EMAIL=lab@example.invalid
g() { git -c init.defaultBranch=main "$@"; }

# A crate the app depends on by relative path, as a second checkout often is.
mkdir -p shared/src
printf '[package]\nname = "shared"\nversion = "0.1.0"\nedition = "2021"\n' > shared/Cargo.toml
printf 'pub fn hi() -> &%sstatic str { "hi" }\n' "'" > shared/src/lib.rs

# The app, on main: a path dependency, a rustflag in .cargo/config.toml, a
# justfile with fallback on and an old recipe, and an installed node package.
mkdir -p app/src app/.cargo app/node_modules/some-dep
cd app
g init -q
printf '[package]\nname = "app"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\nshared = { path = "../shared" }\n' > Cargo.toml
printf 'fn main() { println!("{}", shared::hi()); }\n' > src/main.rs
printf '[build]\nrustflags = ["--cfg", "from_main"]\n' > .cargo/config.toml
cat > justfile <<'EOF'
set fallback := true

old-recipe:
    @echo "ran in $(pwd)"
EOF
printf '/target\n/node_modules\n/.claude\n' > .gitignore
printf 'module.exports = "the main checkout'"'"'s copy"\n' > node_modules/some-dep/index.js
g add -A && g commit -qm main

# The branch under work: it drops the rustflag and the old recipe.
g worktree add -q -b nested .claude/worktrees/nested main
g worktree add -q -b sibling ../app-sibling main
for wt in .claude/worktrees/nested ../app-sibling; do
  printf '[build]\nrustflags = ["--cfg", "from_branch"]\n' > "$wt/.cargo/config.toml"
  printf 'set fallback := true\n' > "$wt/justfile"
  printf 'try { console.log(require("some-dep")) } catch { console.log("not installed") }\n' > "$wt/probe.js"
done

row() { printf '%-36s %-34s %s\n' "$1" "$2" "$3"; }

path_dep() {
  if (cd "$1" && cargo metadata -q --offline --format-version 1 >/dev/null 2>&1); then
    echo "resolves"
  else
    echo "fails: ../shared not found"
  fi
}
rustflags() {
  local log flags
  log="$(cd "$1" && cargo build -v --offline 2>&1)" || true
  flags="$(grep -o -- '--cfg from_[a-z]*' <<<"$log" | sort -u | sed 's/--cfg //' | paste -sd, - || true)"
  echo "${flags:-build failed}"
}
fallback() {
  local out
  out="$(cd "$1" && just old-recipe 2>&1 | tail -1)" || true
  case "$out" in
    "ran in $lab/app") echo "runs, in the main checkout" ;;
    "ran in "*) echo "runs in ${out#ran in }" ;;
    *) echo "errors: no such recipe" ;;
  esac
}
node_dep() { (cd "$1" && node probe.js 2>&1 | tail -1); }

# Prints a row, and flags any outcome that differs from what the README says.
unexpected=0
check() { # <label> <nested> <sibling> <expected nested> <expected sibling>
  local note=""
  if [ "$2" != "$4" ] || [ "$3" != "$5" ]; then
    note="   (expected: $4 / $5)"
    unexpected=1
  fi
  row "$1" "$2" "$3$note"
}

nested=.claude/worktrees/nested sibling=../app-sibling
echo
row "" "nested (.claude/worktrees/nested)" "sibling (../app-sibling)"
row "" "---------------------------------" "------------------------"
if command -v cargo >/dev/null; then
  check "path dependency ../shared" "$(path_dep $nested)" "$(path_dep $sibling)" \
    "fails: ../shared not found" "resolves"
  # cargo can't build the nested copy past the missing dependency, so check its
  # config in a copy that has none.
  for wt in $nested $sibling; do
    printf '[package]\nname = "app"\nversion = "0.1.0"\nedition = "2021"\n' > "$wt/Cargo.toml"
    printf 'fn main() {}\n' > "$wt/src/main.rs"
  done
  check "rustflags passed to rustc" "$(rustflags $nested)" "$(rustflags $sibling)" \
    "from_branch,from_main" "from_branch"
fi
if command -v just >/dev/null; then
  check "just old-recipe (removed on branch)" "$(fallback $nested)" "$(fallback $sibling)" \
    "runs, in the main checkout" "errors: no such recipe"
fi
if command -v node >/dev/null; then
  check "require(\"some-dep\") without install" "$(node_dep $nested)" "$(node_dep $sibling)" \
    "the main checkout's copy" "not installed"
fi
echo
exit "$unexpected"
