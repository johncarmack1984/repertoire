# Sources

Where each rule in this skill comes from, paraphrased, with the chapter it rests on. Quotations are short phrases from the books. Pages for Few are the second edition; Knaflic's chapter titles are printed in lowercase in the book.

## Cole Nussbaumer Knaflic, *Storytelling with Data* (Wiley, 2015)

- Context first (step 1): chapter 1, "the importance of context". Before building anything, answer who you are communicating to, what you need them to know or do, and how the data helps make the point.
- The takeaway sentence (step 1): chapter 1, the Big Idea, which Knaflic takes from Nancy Duarte's *Resonate* (2010) and credits to her. It "must articulate your unique point of view", "must convey what's at stake" and "must be a complete sentence".
- The takeaway in words, above the evidence (steps 1 and 5): chapter 5, "think like a designer": "If there is a conclusion you want your audience to reach, state it in words", as an action title rather than a descriptive one; chapter 7, "lessons in storytelling", repeats the action-title rule.
- A sentence for one or two numbers (step 2): chapter 2, "choosing an effective visual", the section on simple text: "When you have just a number or two to share, simple text" is the way to communicate them; a table or graph makes such numbers lose some of their force.
- When a table (step 2): chapter 2, section "Tables": "Tables interact with our verbal system, which means that we read them", and a table suits an audience whose members each look for their own row, or data with several units of measure. The framing, and the look-up test, are Stephen Few's; Knaflic points to his book for table design.
- Table decoration (`tables.md`, Width): chapter 2: "think of using light borders or simply white space", and "The data should be what stands out, not the borders."
- Declutter (step 5): chapter 3, "clutter is your enemy!": clutter is "visual elements that take up space but don't increase understanding". She credits Edward Tufte for the data-ink ratio and the Gestalt school for the perception principles.
- Focus (step 5): chapter 4, "focus your audience's attention": preattentive attributes (size, colour, position on the page), used sparingly, and the test "Where are your eyes drawn?". A markdown table gives almost nothing to vary, which is why this skill spends the reader's attention on the sentence and the change columns and nothing else.

## Stephen Few, *Show Me the Numbers* (Analytics Press, 2nd edition, 2012)

- Table or graph (step 2): chapter 3, "Differing Roles of Tables and Graphs" (pages 45 and 51). A table when "The display will be used to look up individual values", to compare individual values "but not entire series of values", when "Precise values are required", when the data "involves more than one unit of measure", or when summary and detail values appear together. A graph when "The message is contained in the shape of the values" (patterns, trends, exceptions) or it shows relationships among whole sets of values.
- A table is read (`tables.md`, opening): chapter 3 (page 44): a table's values are "encoded as text, which we can understand directly, without translation", where a graph's are visually encoded. His paper "Use-Based Types of Quantitative Display" (2012) says tables "communicate primarily through verbal channels (words and numbers that must be read)".
- Compared values side by side: chapter 8, "Table Design" (page 184): "Place columns containing data that should be compared close together."
- The difference computed: chapter 8 (page 168): derived values (a difference, a percentage) are a column of their own, placed "just to the right of the column from which they were derived". His paper "Displaying Change Between Two Points in Time" (2014) makes the graph-side case: showing the change itself lets a reader "compare amounts of change more easily and accurately", at the cost of losing sight of the actual values, which is why this skill keeps both the values and the Δ.
- Right-aligned numbers, left-aligned labels: chapter 8 (pages 171 to 173): quantitative values "should always be aligned to the right", with "both the decimal point and the final digit" lined up; text is "aligned to the left because we read from left to right"; a header is aligned the way its column is.
- One precision per column: chapter 8 (pages 171 and 175): express each value "using the same number of decimal digits", and "The level of precision should not exceed the level needed".
- Units in the header: chapter 8 (pages 174 and 175): a unit, a scale or a rounding is declared "in the title or header" ("U.S. dollars in thousands"), and his examples carry a currency sign on summary rows only. Keeping every unit out of the cells is this skill's reading of that practice, not a sentence of his.
- Repeated labels blank: chapter 8 (page 182): it "isn't necessary to repeat the name of the state on each row"; the blanks give "an obvious visual cue" that a new group starts.
- White space over rules: chapter 8 (pages 162, 163 and 183): "Use white space alone whenever space allows", "Avoid grids altogether", and whatever support remains is subdued "in relation to the data". The data-ink idea is Edward Tufte's (*The Visual Display of Quantitative Information*, 1983); Few credits him for it in "Elegance Through Simplicity" (2004).
- Meaningful order: chapter 8 (pages 170 and 184): "Whenever categorical subdivisions have a meaningful order, sort them in that order"; alphabetical order is for looking up items that have no natural order.
- Summary rows last: chapter 8 (pages 178 to 181): a column summary "appears in a separate row beneath the last row of detailed values", visually distinct from the detail.

## Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 2017; 2nd edition with Chris Riccomini, 2026)

The material is the section "Describing Performance": in the first edition under Scalability in chapter 1, "Reliable, Scalable, and Maintainable Applications"; in the second edition a section of chapter 2, "Defining Nonfunctional Requirements", with the subsections "Latency and Response Time", "Average, Median, and Percentiles" and "Use of Response Time Metrics".

- A measurement is a distribution (`measurements.md`, opening): think of response time "not as a single number, but as a distribution of values".
- Median over mean: the mean "doesn't tell you how many users actually experienced that delay", so "Usually it is better to use percentiles"; "The median is also known as the 50th percentile", and p95, p99 and p999 are "also known as tail latencies".
- Why the tail matters: the slowest requests often belong to "the most valuable customers", while past some percentile "the benefits are diminishing". The second edition adds that the mean still serves to estimate throughput limits.
- Percentiles do not average: averaging percentiles "is mathematically meaningless"; the way to aggregate is "to add the histograms" (the "Percentiles in Practice" sidebar in the first edition, "Computing Percentiles" in the second).
- Measure at the client: head-of-line blocking means "it is important to measure response times on the client side", and, in the first edition, a load generator should "keep sending requests independently of the response time".
- Throughput and response time are different measures: for a batch system "we usually care about throughput", for an online system "what's usually more important is the service's response time". That they are reported each on its own, never one implied from the other, is this skill's rule, not a sentence of his.
- Latency against response time: "Latency is the duration that a request is waiting to be handled", while response time adds "network delays and queueing delays" to the service time (the first edition's sidebar; the second edition words latency as time a request is not being actively processed).
- Cost: the second edition ties throughput to the resources needed "and hence the cost of serving a particular workload". Putting cost in a column next to the time it buys, with its own change, is this skill's rule.
- The book gives no rule about how many runs to make or how to report their spread; the rules under "The runs" come from the worked example's method, not from the book.

## The worked example's method

These rules come from rebuilding the table in the worked example, not from the books: the takeaway sentence carries what limits the result; one row per configuration, grouped and then ordered by the swept condition; the change in time next to the change in cost, each with its own Δ; the statistic, the run count, the spread and the machine in a line below the table; interleaved runs; an overlap statement as the spread; a difference inside the spread reported as no measurable difference; slow runs reported rather than dropped.
