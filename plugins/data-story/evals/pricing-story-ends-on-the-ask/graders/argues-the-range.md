---
type: llm
focus: { source: file, path: pricing-story.md }
weight: 2
---
The file is a storyboard for a five-minute live presentation to a VP of Product who will set the launch price of a new product. The data is the average retail price by year of five competing products. A and B launched in 2008 at $395 and $360, peaked in 2010 at $425 and $410, and fell to $260 and $250 by 2014. C launched in 2010 at $100, D in 2011 at $160, and E in 2013 at $100, each far below A and B, and each rose after launch: C to $240 in 2013 before coming down to $180, D to $260 in 2012 before coming down to $215, E to $210 in 2014. In 2014 the five prices run from $180 to $260 and average $223. The presenter wants to recommend a launch price of $150 to $200. A draft slide in the workspace claimed that price has declined for all products since Product C launched in 2010, which is false for C, D, and E.

PASS if the storyboard gives a reason, drawn from the data, for the $150 to $200 range against at least one other price the VP might weigh: pricing at or above the market (the $223 average, or the $250 and more of A and B), or launching as low as the $100 that C and E started at. Reasons such as "the entrants that launched low all had to raise within a year" or "every product has ended up between $180 and $260 whatever it launched at" count.

FAIL if the range is only asserted or positioned ("below the average", "Finance is comfortable with it") with no reason from the data for why below the market, or why no lower.
