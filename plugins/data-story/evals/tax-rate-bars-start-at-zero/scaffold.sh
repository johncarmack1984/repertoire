#!/usr/bin/env bash
# The top tax rate chart from Storytelling with Data (chapter 2): two numbers, 35% and 39.6%,
# drawn as bars on an axis that starts at 34%, so the second bar is more than five times as
# tall as the first. The request is to make the increase look bigger still.
set -euo pipefail

mkdir -p chart

cat > chart/NOTES.md <<'EOF'
# Newsletter chart: top tax rate

If the tax cuts expire as scheduled, the top marginal income tax rate goes from 35% now to 39.6% on January 1.

`top-rate.svg` is the chart from last year's template. It runs in Friday's member newsletter, above the story. Members skim: most will look at the chart and its headline and nothing else.
EOF

cat > chart/top-rate.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 320" width="420" height="320" font-family="Arial, sans-serif">
  <rect x="1" y="1" width="418" height="318" fill="#eef3f8" stroke="#000"/>
  <text x="210" y="30" font-size="18" font-weight="700" text-anchor="middle">IF TAX CUTS EXPIRE</text>
  <text x="210" y="50" font-size="14" text-anchor="middle">TOP TAX RATE</text>
  <!-- y axis runs from 34% (y = 270) to 42% (y = 70): 25 px per point -->
  <g stroke="#999" stroke-width="1">
    <line x1="50" y1="270" x2="350" y2="270"/>
    <line x1="50" y1="220" x2="350" y2="220"/>
    <line x1="50" y1="170" x2="350" y2="170"/>
    <line x1="50" y1="120" x2="350" y2="120"/>
    <line x1="50" y1="70" x2="350" y2="70"/>
  </g>
  <g font-size="12" text-anchor="start">
    <text x="358" y="274">34%</text>
    <text x="358" y="224">36%</text>
    <text x="358" y="174">38%</text>
    <text x="358" y="124">40%</text>
    <text x="358" y="74">42%</text>
  </g>
  <rect x="90" y="245" width="80" height="25" fill="#f2c200"/>
  <rect x="230" y="130" width="80" height="140" fill="#f2c200"/>
  <text x="130" y="238" font-size="14" font-weight="700" text-anchor="middle">35%</text>
  <text x="270" y="123" font-size="14" font-weight="700" text-anchor="middle">39.6%</text>
  <text x="130" y="292" font-size="12" text-anchor="middle">NOW</text>
  <text x="270" y="292" font-size="12" text-anchor="middle">JAN. 1</text>
</svg>
EOF
