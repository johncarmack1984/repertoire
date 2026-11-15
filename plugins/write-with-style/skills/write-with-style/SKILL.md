---
name: write-with-style
description: Write and edit prose by the rules of William Strunk Jr.'s The Elements of Style (1918). Use before writing a PR description, commit message, issue or review comment, README or docs page, release notes, email, report, or post, and when asked to tighten, edit, proofread, or review a draft. Opens each paragraph on its topic sentence, makes definite assertions in the active voice, keeps co-ordinate ideas parallel, ends each sentence on its emphatic word, omits needless words, and brings the 1918 usage that has since changed up to date.
---

# Write with style

A reader gets each paragraph's point from its first sentence. Each sentence asserts something definite, in the active voice, and ends on its news, and every word tells. These are the composition rules of William Strunk Jr.'s *The Elements of Style* (1918), applied here to the prose an agent writes: PR descriptions, commit messages, READMEs and docs, issues, review comments, and email. The rule numbers below are the book's.

## Steps

1. **Point.** Say who the reader is and what they will do with the text: review and merge, install, decide, or reply. Write the point as one sentence. A caller that already states the reader, the ask, and the point (as `data-story` does) has done this step; use them. Done when that sentence could stand in for the text.
2. **Paragraphs.** List the topics before writing, and give each its own paragraph (Rule 9). A text is a single paragraph only when it has one topic, as a commit body or a short reply often does; an email that reports a delay and asks for a review has two. A fact too small to be a topic joins the topic it belongs to, since a single sentence stands as a paragraph only to mark a transition. In docs, where readers scan, a paragraph of more than three sentences usually holds two topics: split it. Open each paragraph with its topic sentence and develop it with the facts. In docs, develop it with an illustration too (Rule 10's "illustrations or specific instances"): the example a reader can copy, such as a sample config or command, often teaches more than a sentence. End the paragraph on the consequence or the strongest point, never on a digression or a recap (Rule 10). Use a list for parallel items the reader will scan or follow in order, a table for many like values (Rule 15), and a heading only where a reader will jump. Done when each paragraph holds one topic and the first sentences, read alone, give the topics in order.
3. **Sentences.** Read every sentence against Rules 11 to 18 as stated here. Open `reference/composition.md`, with Strunk's examples and the exceptions he allows, only when you can't tell whether a rule applies to a sentence or whether an exception covers it. The doer is the subject and the action an active verb, unless the sentence is about the receiver (Rule 11). The sentence makes a definite assertion in positive form, keeping *not* for denial and antithesis (Rule 12). A claim nobody has checked, such as a predicted speedup or a hoped-for drop in errors, is cut rather than hedged, and a default or a figure the sources don't give stays out, since Chapter V keeps *fact* for what can be verified. An illustration makes no such claim: a sample config or command that shows the syntax belongs (step 2). A condition or limit on a fact (*at -j1*, *in release builds*, *cause not found*) is part of the fact, not a hedge or a needless word. Related words sit together, each modifier beside the word it modifies (Rule 16). Co-ordinate ideas, list items included, share one grammatical form (Rule 15). The sentence ends on its news (Rule 18). A summary keeps one tense and says once that it is a summary (Rule 17). A run of two-clause sentences joined by *and*, *but*, or *which* is recast (Rule 14). Done when every sentence has been read against each rule.
4. **Words.** Omit needless words, so that every word tells (Rule 13). Cut the wordy forms: *the fact that* gives way to *because*, *though*, or a noun ("his failure"); *the question as to whether* to *whether*; *in a hasty manner* to *hastily*; a *who is* or *which was* clause that adds nothing to an apposition ("His brother, a member of the firm"); and *case*, *character*, *nature*, *factor*, and *feature* used as filler. Watch the words most often misused: *due to* belongs after a noun, and *because of* serves elsewhere; *fact* is for what can be verified; *less* is for amounts and *fewer* for counts; *very* and its kind give way to a word strong in itself. Open `reference/words.md`, Strunk's full list with each fix and the entries where usage has changed since 1918, only for a word you suspect is on it but isn't named here. Done when no word can go without losing meaning, and each intensifier has given way to a word strong in itself.
5. **Usage.** Check the punctuation against Rules 1 to 7: a singular possessive takes *'s* (*Charles's*); a series of three or more takes a comma before its *and* or *or*; a parenthetic expression takes a comma at each end; a comma goes before *and* or *but* when it joins two independent clauses; a comma alone never joins two independent clauses; a fragment doesn't stand as a sentence; and an opening participial phrase refers to the subject. Open `reference/usage.md` for quotations, numerals, titles, and references (Chapter IV), and for any case these lines don't settle. Done when each one follows the rules.

## Writing, revising, reviewing

- **Writing:** run the steps on your draft before anyone reads it.
- **Revising someone's text:** run the same steps and keep every fact, figure, name, link, code span, and commitment. A prediction nobody has measured is not a fact, so it goes. A caller may pass a keep-list: numbers with their units, signs, and precision, the method's facts, conditions, limits, and caveats, names that must match a chart's labels or a table's headers, and any order it sets, such as the point first and the ask last. Everything on it stays exactly as given, whatever the rules would cut. The author's voice stays wherever it keeps the rules. Return the revision, without a list of changes unless one is asked for.
- **Reviewing without rewriting:** mark each fault the way Strunk meant his rule numbers to be used, "as references in correcting manuscript": quote the phrase, name the rule, give the fix. The review holds those marks and at most a line on what passes; optional suggestions and content questions stay out, a missing example or a missing fact among them. Mark only what a rule covers; a sentence that keeps every rule gets no mark, however differently you would have written it.

## Where the rules bend

- "The best writers sometimes disregard the rules of rhetoric," Strunk warns, and when they do, the sentence gains something in return. Break a rule only for a gain you can name.
- A voice or style guide loaded for the author or the project decides wherever it speaks; these rules fill its gaps.
- Code, commands, identifiers, error text, quotations, and names stay verbatim.
- Usage has changed since 1918. Write *they* for a person of unknown gender, and leave an opening *however* and a comma before *so* unmarked: Strunk objected to all three, and today all three are standard. `reference/words.md` marks each entry that has changed, and `reference/sources.md` lists every departure from the book.

## Worked example

A PR description as an agent might first write it:

> ## Summary
>
> This PR introduces a number of improvements to the way that the `sync` command handles interrupted uploads. It's worth noting that previously, uploads were being restarted from the beginning due to the fact that no record of progress was being kept.
>
> ## Changes
>
> - Added a progress file at `.sync/state.json`
> - Uploads now resume from the last confirmed chunk
> - Very minor cleanup of the retry code
> - Tests for resuming and for a corrupt state file
>
> ## Impact
>
> One of the most significant benefits of this change is that large uploads should potentially be much faster to recover. In testing, resuming a 2 GB upload interrupted at 90% took 14 s instead of 3 min 10 s.
>
> Overall, this change makes `sync` more robust and efficient.

Revised:

> Instead of starting over, an interrupted `sync` upload now picks up at its last confirmed chunk. `sync` records each confirmed chunk in `.sync/state.json`. In a test with a 2 GB upload cut off at 90%, starting over took 3 min 10 s; resuming took 14 s.
>
> The retry code is tidier, and new tests cover a resume and a corrupt state file.

The subject is of slight extent, so the three headings fold into two paragraphs (Rule 9). The first sentence states the change where the draft announced "a number of improvements" (Rules 10 and 12), and `sync` becomes the subject that "were being restarted" and "was being kept" left out (Rule 11). "It's worth noting that", "due to the fact that", and the closing recap go (Rules 13 and 10), and so do "one of the most" and "very" (Chapter V). The measurement replaces "should potentially be much faster", the hedge it settles (Rule 12), and its sentence ends on the 14 s (Rule 18). The four list items were a participle, a sentence, a noun phrase, and a bare noun (Rule 15); their facts now sit in the two paragraphs. The draft's 122 words are now 62, and every fact survived.

## Sources

William Strunk Jr., *The Elements of Style* (privately printed, Ithaca, New York, 1918), in the public domain. Its rule numbers differ from the 1920 edition's and from the later editions with E. B. White. `reference/sources.md` maps each rule to its chapter, lists every departure from 1918 usage with its reason, and marks the lines that are this skill's reading rather than Strunk's sentence.
