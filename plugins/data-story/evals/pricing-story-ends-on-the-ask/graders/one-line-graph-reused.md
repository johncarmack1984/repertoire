---
type: llm
focus: { source: file, path: pricing-story.md }
weight: 1
---
The file is a storyboard for a five-minute live presentation to a VP of Product who will set the launch price of a new product. The data is the average retail price by year of five competing products. A and B launched in 2008 at $395 and $360, peaked in 2010 at $425 and $410, and fell to $260 and $250 by 2014. C launched in 2010 at $100, D in 2011 at $160, and E in 2013 at $100, each far below A and B, and each rose after launch: C to $240 in 2013 before coming down to $180, D to $260 in 2012 before coming down to $215, E to $210 in 2014. In 2014 the five prices run from $180 to $260 and average $223. The presenter wants to recommend a launch price of $150 to $200. A draft slide in the workspace claimed that price has declined for all products since Product C launched in 2010, which is false for C, D and E.

PASS if the graph described is a line graph of price over time with the five products on shared axes, used again from slide to slide with a different part emphasized each time. A table kept in an appendix for questions is fine.

FAIL if the main slides use clustered columns, a different chart type on each slide, or a table.
