---
type: llm
focus: { source: file, path: README-watch.md }
weight: 3
---
The notes described `tidy --watch`, a new flag of `tidy`, a tool that formats and lints a Rust workspace. Its facts: it re-runs `tidy` whenever a file under the workspace changes; it waits 300 ms after the last change before re-running, so a burst of saves makes one run; it always ignores `.git/` and `target/`, and more ignores go in `watch.ignore`, a list of globs in `tidy.toml`; after each run it prints a one-line summary with pass or fail and the duration; Ctrl-C stops it, and its exit code is the last run's status; it works on macOS and Linux, and Windows support is tracked in #88. Naming FSEvents and inotify is optional.

PASS only if all of these hold:

1. The first sentence of the section's text says what `--watch` does.
2. Every fact above is present, and nothing is invented: no other platforms, flags, defaults, config keys, or behavior. Sample globs in an example are illustration, not invention.
3. Each paragraph holds one topic and opens with its topic sentence. The topics are what `--watch` does and when it re-runs, what each run prints and how watching stops, what it ignores and how to add ignores, and where it runs; a paragraph that mixes two of them fails. A list, if there is one, has parallel items in one grammatical form, and no paragraph is a lone sentence unless it marks a transition.
4. The statements are definite: no "should", "may", or "might" about behavior the notes state as fact.
5. Where an actor exists (`tidy`, the watcher, the reader), it is the subject; no passive hides it.
6. No needless words: no sentence repeats another, and the section does not end on a recap.
7. An example shows the `watch.ignore` syntax, such as a short `tidy.toml` block.

Otherwise FAIL, and name the first rule that was broken.
