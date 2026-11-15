#!/usr/bin/env bash
# The top ten design concerns from Storytelling with Data (chapter 4): ten categories with long
# names, three of which are the same complaint, and a reader who has to be shown which three.
set -euo pipefail

mkdir -p concerns

cat > concerns/NOTES.md <<'EOF'
# Design concerns, model year review

The ten most-reported design concerns for the sedan are in `top10.csv`, as concerns per 1,000 reported.

Reading the comments behind them, three of the ten are the same complaint: noise.

- Tire noise is reported mostly in the rain.
- Engine noise is reported mostly on starting the car after it has sat for a while.
- Wind noise is reported mostly on the freeway at high speed.

The chief engineer decides on Monday which concerns get engineering time for the next model year. She knows the car and has seen the raw list. I want her to put noise first. One chart goes in the review packet, and she will read it at her desk.
EOF

cat > concerns/top10.csv <<'EOF'
concern,per_1000
Bluetooth system has poor sound quality,10.0
Bluetooth system is difficult to use,8.6
Engine makes abnormal/excessive noise,11.6
Engine power is less than expected,12.9
Excessive wind noise,11.0
Front seat audio/entertainment/navigation controls,8.2
Hesitation or delay when shifting,10.3
Seat material concerns,11.6
Steering system/wheel has too much play,8.8
Tires make excessive noise while driving,12.3
EOF
