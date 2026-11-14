# Measurements

A measurement is a distribution of runs, not a number. A report the reader can trust names the statistic that describes the typical run, says how many runs there were and how much they varied, and keeps different kinds of measure apart.

## The statistic

- Report the **median** of the runs for each configuration. The mean is pulled by a few slow runs and does not say how many runs actually took that long; when the mean and the median disagree, the runs are skewed and the median is the typical one.
- When the tail matters to the reader (request latency, anything a user waits on), report a high percentile beside the median, p95 or p99, named as such and with the sample count.
- Percentiles do not average. To combine runs, pool the raw samples and take the percentile of the pool.
- Compute each change from the medians (or the percentile) as a percent of the baseline, and say which variant is the baseline.

## The runs

- Say how many runs per configuration and how they were ordered. Interleave the variants (main, change, main, change) so drift in the machine hits both, and say so.
- Give the spread. A range per cell is too much for a table, so give it in the method line: an overlap statement ("in every row the slowest run with the change beat the fastest without it"), the widest range, or the min and max for the headline figure. A result with no spread stated reads as a single run.
- A difference inside the spread is "no measurable difference", not "1% faster".
- Never drop a run silently. Report slow runs with their size and say what you know about the cause, which may be nothing: "two of twelve runs took 1.2 s against a median of 88 ms, cause not found" is a finding, and the reader may want it looked at before merging.
- Say what was measured (wall, CPU, allocations, bytes), with what (the tool, the command), on what (CPU, OS, compiler, flags, cache state), and what was held fixed.
- For a server, say that response times were measured at the client, and whether the load generator sent requests on a schedule or waited for each response: queueing delay is part of what the caller sees, and a generator that waits hides it.

## Kinds of measure

- Response time and throughput are different measures: a batch job is judged by how many records a second it gets through, a request by how long the caller waits, and one can improve while the other gets worse. Report each on its own, never one implied from the other.
- Cost (CPU time, memory, bytes, dollars) is a third kind. Put it next to the time it buys, with its own change, so the reader can see a wall-time win that is parallelism spending the same CPU, or a CPU win that parallelism hides.
- Latency is the time a request waits before it is handled; response time is what the caller sees, service time plus queueing plus the network. Name the one you measured.

## Claims

- Claim only what the runs show: the configurations measured, on the machine measured. A result that holds under a condition ("at -j1", "with the cache warm") carries the condition in the takeaway sentence.
- Say what limits the result before the reader finds it: the configuration where the win shrinks, the one not measured, the cold run.
