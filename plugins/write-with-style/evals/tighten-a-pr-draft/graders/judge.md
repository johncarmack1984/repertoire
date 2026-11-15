---
type: llm
focus: { source: file, path: pr-body.md }
weight: 3
---
The draft was an agent-written PR description for a change to an HTTP client. Its facts: `Client::send` now retries failed requests; before, transient errors from upstream services reached callers directly; it retries only on 502, 503, and 504 responses; the backoff starts at 200 ms and doubles (200, 400, and 800 ms); a new `max_retries` option on `ClientConfig` defaults to 3; POST requests are never retried, to avoid duplicate side effects; there are 4 new tests; the PR closes #142. The draft also predicts, with no measurement, that users will see fewer failed requests ("should potentially reduce … quite significantly"); that prediction is not a fact, and a good revision cuts it.

PASS only if all of these hold:

1. Every fact above survives, and nothing is added that the draft did not say: no new numbers, behavior, options, or claims of impact.
2. The unmeasured prediction is gone: no sentence says or implies that users will see fewer failed requests, however it is hedged.
3. The text's first sentence states what the change does; a first sentence that announces the PR ("This PR introduces", "This PR adds improvements") fails. Later sentences may refer to the PR.
4. The statements are definite: no hedges such as "should potentially", "may", "might", or "quite significantly" about what the change does.
5. Where an actor exists, it is the subject: no passives such as "has been added", "were being surfaced", or "are performed" that hide who acts.
6. If there is a list, its items share one grammatical form.
7. The text ends on a fact or the issue reference, not on a sentence that sums up what came before.

Otherwise FAIL, and name the first rule that was broken.
