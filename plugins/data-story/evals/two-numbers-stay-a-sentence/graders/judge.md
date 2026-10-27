---
type: llm
focus: { source: file, path: pr-numbers.md }
weight: 3
---
The data was one before/after pair: `cargo test --lib` wall time, medians of ten alternated runs, 1.84 s on main (range 1.80 to 1.90) and 1.21 s on the branch (range 1.18 to 1.25), on one aarch64 macOS machine with rustc 1.91.

PASS only if all of these hold:

1. The numbers are in prose: no table and no bullet list of values. A heading and more than one short paragraph are fine.
2. Both medians appear (1.84 s and 1.21 s) with the size of the change (about 34 percent, about a third, about 0.6 s, or about 1.5 times), and the direction is clear.
3. The text says the figures are medians, says there were ten runs per variant, and gives the spread: the two ranges, or that the ranges do not overlap.
4. No figure goes beyond the data: no CPU, memory or throughput numbers. Attributing the change to the branch's fixture-loader change is fine, since that is what the PR does.

Otherwise FAIL, and name the first rule that was broken.
