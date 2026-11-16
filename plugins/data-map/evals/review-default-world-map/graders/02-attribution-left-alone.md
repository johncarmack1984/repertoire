---
type: llm
focus: trace
weight: 2
---
The user asked for a review of `ev-map/index.html`, a world map of new electric-car registrations. Its attribution is already correct: the footer reads "Source: Global Charge Monitor, Electric Car Registrations 2026 edition. Boundaries: Natural Earth (public domain).", and the map's attribution control credits the same two sources. The page's other faults are real.

Read the final reply to the user.

PASS if the reply proposes no change to the source line or the attribution. Leaving it unmentioned passes, and so does naming it as correct or as something to keep.

FAIL if the reply lists a change to the source line or the attribution, or counts either among the faults. Quote the change it proposed.
