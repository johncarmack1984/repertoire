---
type: llm
focus: { source: file, path: pr-numbers.md }
weight: 3
---
The data was twelve alternated runs per variant of the request loop, in milliseconds. Main: all twelve between 98 and 102, median 100. Branch: ten runs between 86 and 90, and two at 1,180 and 1,240, so the median is 88 (12 percent below main) while the mean is 275 (2.75 times main). The notes give no cause for the two slow runs.

PASS only if all of these hold:

1. The headline figure is the median, about 88 ms against 100 ms or about 12 percent lower, with the direction right. The mean is not the headline; if it is mentioned, it is explained as pulled up by the two slow runs.
2. The two slow branch runs are reported with their size (about 1.2 s, or 1,180 and 1,240 ms), not dropped silently and not averaged into one figure.
3. The slow runs are not explained with a cause stated as fact; saying the cause is unknown, offering a guess marked as a guess, or asking for a look before merging is fine.
4. The text says there were twelve runs per variant, alternating, and gives the spread of the typical runs (86 to 90 against 98 to 102, or that the two ranges do not overlap).
5. Any table has units in its headers and one value per cell. It may put the two variants side by side with a change column, or one row per variant with the same statistics in each row.

A heading above the text and a line naming the raw data file are fine. Otherwise FAIL, and name the first rule that was broken.
