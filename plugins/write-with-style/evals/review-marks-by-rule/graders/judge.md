---
type: llm
focus: { source: file, path: review.md }
weight: 3
---
The page under review, `docs/overview.md`, had five planted faults:

- a dangling participle: "Having installed the binary, the config file must be created…" (the phrase does not refer to the subject);
- a comma splice: "`tidy` reads the config once per run, it never caches it between runs.";
- *due to* used as an adverb: "Due to the size of a large workspace, `tidy` checks files in parallel." (*because of* fits);
- *less* for *fewer*: "It checks less files…";
- a wordy *the fact that*: "The fact that the run is limited this way makes…".

It also had two sentences that are correct today and must not be marked as faults: the sentence that opens with "However," and the comma before "so" in "…after an upgrade, so clear it beforehand with `tidy clean`.".

PASS only if all of these hold:

1. Each of the five faults is marked, with the phrase quoted or clearly identified, the fault named (a rule number, or a name such as "dangling participle" or "comma splice"), and a fix given.
2. Neither the opening "However," nor the comma before "so" is marked as a fault. Noting that either is acceptable is fine.
3. Any other mark rests on a rule of usage or style, such as the passive "must be created" hiding who creates the file. A mark that is only a matter of taste fails.

Otherwise FAIL, and name the first rule that was broken.
