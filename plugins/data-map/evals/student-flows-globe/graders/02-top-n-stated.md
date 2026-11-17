---
type: llm
focus: trace
weight: 2
---
The user asked for an interactive globe of international student flows: 300 pairs, 3,549,110 students in all. The share of all students that the largest N flows carry, with the smallest flow kept at that N:

- top 10: 34.8% of students (smallest kept flow 37,480)
- top 20: 43.8% of students (smallest kept flow 26,400)
- top 25: 47.1% of students (smallest kept flow 22,160)
- top 30: 50.0% of students (smallest kept flow 19,440)
- top 40: 54.9% of students (smallest kept flow 16,190)
- top 50: 59.1% of students (smallest kept flow 14,070)
- top 60: 63.0% of students (smallest kept flow 13,440)
- top 75: 68.3% of students (smallest kept flow 11,380)
- top 100: 75.2% of students (smallest kept flow 8,070)
- top 150: 84.6% of students (smallest kept flow 5,670)

Read the page the agent wrote under `student-globe/`, any data files it prepared for the page, and its final reply.

PASS only if all of these hold:

1. The globe, as it first opens, draws only the largest flows, not all 300. A control that lets the reader show more is fine.
2. The page itself, not only the reply, states how many flows are drawn and what share of all students they carry (or how many are left out and their share).
3. The stated share is within one percentage point of the true share for the cut the page makes. When the cut is a threshold, use the smallest kept flow above to find N.

FAIL otherwise, and name the first rule that was broken.
