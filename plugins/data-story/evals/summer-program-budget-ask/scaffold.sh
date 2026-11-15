#!/usr/bin/env bash
# The pilot summer science program from Storytelling with Data (chapters 1 and 9): a before and
# after survey of 100 students, a draft that shows it as two pies, and a budget committee that
# has to be asked for the money to run it again.
set -euo pipefail

mkdir -p program

cat > program/NOTES.md <<'EOF'
# Summer science pilot: notes for the budget committee page

I teach fourth-grade science. Every September the new class arrives already sure that science is hard and that they won't like it, and it takes weeks to get past that. Last summer a few of us in the department ran a four-week pilot to give younger kids an earlier look at the subject, hoping to change how they feel about it before they reach us.

- 100 students took part, mostly rising second and third graders.
- We asked each of them one question on the first day and again on the last: "How do you feel about doing science?" They picked one of five answers. All 100 answered both times.
- The counts are in `survey.csv`.
- Running it again next summer costs $12,000: two teachers for four weeks, plus materials. That money has to come from the budget committee, which votes on Thursday.
- Every program gets one page in the committee's packet. They read the packet before the meeting, and nobody presents.

`draft.md` is as far as I got.
EOF

cat > program/survey.csv <<'EOF'
feeling,before,after
Bored,11,12
Not great,5,6
OK,40,14
Kind of interested,25,30
Excited,19,38
EOF

cat > program/draft.md <<'EOF'
# Survey Results

## PRE: How do you feel about doing science?

```mermaid
pie
    "Bored" : 11
    "Not great" : 5
    "OK" : 40
    "Kind of interested" : 25
    "Excited" : 19
```

## POST: How do you feel about doing science?

```mermaid
pie
    "Bored" : 12
    "Not great" : 6
    "OK" : 14
    "Kind of interested" : 30
    "Excited" : 38
```

## Methodology

The survey was administered on paper on the first and last day of the program. Students circled one of five responses.
EOF
