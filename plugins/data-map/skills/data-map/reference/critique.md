# Critique

Step 7 follows this file once `check` passes and the screenshot has been opened. A reader with no context looks at the PNG and answers three questions whose answers code computed. Then the agent grades those answers, walks the idiom's default lies and `pitfalls.md` with located evidence, and fixes what fails, for two rounds at most.

## Why a cold reader

Asked to judge its own map, a model praises it. Muehlenhaus calls this validation bias (ch. 15) and warns that "it will almost always say it looks great, even when it doesn't." (ch. 16). A design also needs a tester who isn't its designer (Munzner §4.6.3). So the judge is a fresh subagent that never sees the brief's claim, the code, or the answer key. Its answers are graded against numbers that code computed, which makes a wrong answer a defect in the map rather than a matter of taste.

Slocum reports that GPT-4o, shown rendered maps with planted flaws and asked whether a named method was applied correctly, found the flaws and proposed fixes, while its answers to vague prompts varied from run to run (§28.5.6.2). Ask the image pointed questions, and check every claim against a rule before acting on it.

## Before the critic runs

1. Open the PNG yourself. A blank or half-drawn frame isn't the map (P33), so fix the readiness wait before going on.
2. Take the three questions from the brief's answer key, which step 2 computed with code. They are in the reader's words, and the map must answer them.
3. Check each answer against the `answers` block of `legend.json`, which the levers wrote at step 4. It holds the highest and lowest units, the low-n and no-data units, the largest flows, the top origins and destinations, and the asymmetric pairs. Where the block and the key disagree, find out why before the critic runs. For a map of homes heated with wood, one question could be *Which county heats the largest share of its homes with wood?*
4. Keep the answers, the brief's Question and Supports lines, and every file path except the PNG out of the critic's prompt.

## The critic's prompt

Spawn one subagent per round with no other context. Give it only this prompt, with the five placeholders in braces filled, and the same wording every round.

```
You are a skeptical, tactless cartography professor reviewing a map handed in for critique. Give no praise.

Open the image at {png} with your Read tool and study it before reading on. The map is for {reader}.

Answer in five numbered sections. Whenever you refer to something, say where it is in the image (top left, the legend's third swatch, the large circle on the east coast) so it can be found.

1. Description. What the map shows: the data, the symbols, the legend's claims, the title, and what is labeled.
2. Analysis. Where your eye lands first, second, and third, and what draws it to each.
3. Questions. Answer each from the image alone. If the image can't answer one, write "can't tell" and say what is missing or ambiguous.
   a. {question 1}
   b. {question 2}
   c. {question 3}
4. Interpretation. The one-sentence story a reader takes away in ten seconds.
5. Evaluation. At least three faults, worst first. For each, say where it is, what is wrong, and how it misleads or slows the reader.

Don't guess values you can't read from the image. Don't propose other data or another topic.
```

The reader line is the brief's Reader line, such as *county energy planners choosing where to fund stove replacements*.

## Grading the critic

- Compare each answer with the key. A wrong answer or a "can't tell" is a defect in the map. Find what misled the critic, such as the classes, the legend, a hidden symbol, or the draw order, and fix it. Never reword a question so the map passes.
- The first thing the critic noticed should be the subject of the questions. When its eye lands first on the basemap, a control, or a decoration, the hierarchy is wrong (`design.md`).
- Compare the critic's story with the brief's Question line. A different story is a defect when the data supports the brief, and a finding for the report when it doesn't.
- Check each fault the critic names against the PNG and a rule. Act on a fault you can locate and tie to a pitfall number, an idiom's default lie, or a rule in `design.md` or `color-and-classes.md`. List the rest in the report without acting on them.

## The walk

Walk two lists yourself, and give every item one line with located evidence. Evidence is a place in the PNG, a line of `check` output, or a value in `legend.json`.

1. The idiom file's default lies, each with its guardrail held or not.
2. Every number in `pitfalls.md` that bears on this idiom and stack, as held, failed, or not applicable.

```
P13 held. Legend circles of 100, 500, and 2,000 match dm_r in legend.json, lower right of the PNG.
P19 failed. The thickest coastal flow covers two thin flows, center right of the PNG.
P26 not applicable. dm-spec.animation is null and check reports moving: false.
```

Then name three ways the map could still mislead a reader with every check passing, and give each a guardrail or say why none fits (Muehlenhaus ch. 13). Common guardrails are a tooltip with the raw count beside the rate, a note on what a cut left out, and a companion view.

## Drift checks

After each round's fixes, answer Muehlenhaus's three drift checks (ch. 6):

- **Aesthetic drift.** Is there still a visual hierarchy? Do the strongest signals fall on the most important data? Was clarity traded for decoration?
- **Data drift.** Does the map still answer the brief's question? Does any default steer the reading? Would a reader reach the conclusion the data supports?
- **Ethical drift.** Is uncertainty visible where it matters? Can the reader reach the sources and the limits? Does the tone fit the subject?

## The QA list

Before the report, confirm Muehlenhaus's ten points (ch. 6):

1. The map at load carries the message.
2. Each interaction serves the map's goal.
3. No round of fixes added anything that competes with that goal.
4. The map reads without explanation.
5. Interactions behave as a reader expects.
6. A reader can get back to the overview after clicking, filtering, or exploring.
7. Sources, uncertainty, and limits show where they matter.
8. The tone fits the subject.
9. Every choice can be defended to a critical audience.
10. The brief records the decisions and the departures.

## Rounds

A round is the critic, the grading, the walk, the fixes, and a fresh `check`. Run a second round only when the first found defects, with a fresh subagent and the new PNG. Stop after two rounds. Report what still fails as open, with its pitfall number and its place in the PNG.

## Without subagents

Where no subagent can be spawned, run the same prompt in context. Open the PNG and answer the three questions before reopening the brief or `legend.json`, then grade as above. Say in the report that the critique ran in context and is weaker, because the reader already knew the intended answers.
