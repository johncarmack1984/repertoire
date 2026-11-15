# List the recipes.
default:
    @just --list

# Validate the marketplace and every plugin's manifests and skills.
validate:
    claude plugin validate --strict .
    for plugin in plugins/*/; do claude plugin validate --strict "$plugin" && claude plugin validate --strict "$plugin.claude-plugin/plugin.json" && claude plugin validate --strict "${plugin}skills" || exit 1; done

# Lint the shell scripts and the eval scaffolds, and compile the lens miner.
lint:
    shellcheck -x plugins/sidework/scripts/*.sh plugins/sidework/evals/_fixtures/lib.sh plugins/*/evals/*/scaffold.sh
    python3 -m py_compile plugins/build-review-lens/skills/build-review-lens/scripts/mine_reviews.py

# Run a plugin's eval suite (sidework, data-story, and write-with-style have one). Each case's scaffold runs as you and the agent gets a shell. It runs from the repo root so that a case can load a plugin it depends on from beside it.
eval plugin *args:
    claude plugin eval . --eval-dir plugins/{{plugin}}/evals --scaffold --allow-tools Bash Edit Write {{args}}

# Reproduce the nested-worktree failures sidework's README lists.
lab:
    cd plugins/sidework && bash scripts/nesting-lab.sh
