# List the recipes.
default:
    @just --list

# Validate the marketplace and every plugin's manifests and skills.
validate:
    claude plugin validate --strict .
    for plugin in plugins/*/; do claude plugin validate --strict "$plugin" && claude plugin validate --strict "$plugin.claude-plugin/plugin.json" && claude plugin validate --strict "${plugin}skills" || exit 1; done

# Lint the shell scripts and the eval scaffolds, and compile the lens miner and the dashboard check.
lint:
    shellcheck -x plugins/sidework/scripts/*.sh plugins/sidework/evals/_fixtures/lib.sh plugins/*/evals/*/scaffold.sh
    python3 -m py_compile plugins/build-review-lens/skills/build-review-lens/scripts/mine_reviews.py
    python3 -m py_compile plugins/data-dashboard/skills/data-dashboard/scripts/dashboard.py plugins/data-dashboard/tests/palette.py plugins/data-dashboard/tests/build_components.py

# Check data-dashboard: the library's unit tests, the palette's contrast in both themes, each inlined library against assets/, and the test and example pages in headless Chrome.
dashboards:
    #!/usr/bin/env bash
    set -euo pipefail
    check=plugins/data-dashboard/skills/data-dashboard/scripts/dashboard.py
    node plugins/data-dashboard/tests/lib_test.mjs
    python3 plugins/data-dashboard/tests/palette.py
    python3 "$check" sync --check plugins/data-dashboard/skills/data-dashboard/assets/template.html
    for page in plugins/data-dashboard/tests/components.html plugins/data-dashboard/skills/data-dashboard/assets/example/blood-supply.html; do
        python3 "$check" sync --check "$page"
        python3 "$check" check "$page"
    done

# Run a plugin's eval suite (sidework, data-story, data-dashboard, and write-with-style have one). Each case's scaffold runs as you and the agent gets a shell. It runs from the repo root so that a case can load a plugin it depends on from beside it.
eval plugin *args:
    claude plugin eval . --eval-dir plugins/{{plugin}}/evals --scaffold --allow-tools Bash Edit Write {{args}}

# Reproduce the nested-worktree failures sidework's README lists.
lab:
    cd plugins/sidework && bash scripts/nesting-lab.sh
