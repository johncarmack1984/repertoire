---
type: llm
focus: { source: file, path: pr-numbers.md }
weight: 2
---
The data was one before/after pair: `cargo test --lib` wall time, medians of ten alternated runs, 1.84 s on main (range 1.80 to 1.90) and 1.21 s on the branch (range 1.18 to 1.25), on one aarch64 macOS machine with rustc 1.91.

PASS if every figure in the note is one of those, or is computed from them: the difference (about 0.63 s), the percent change (about 34%, or about a third), or the ratio (about 1.5 times). Attributing the change to the branch's fixture-loader change is fine, since that is what the PR does.

FAIL only if the note gives a figure that is not in the data and cannot be computed from it, such as CPU time, memory, or throughput.
