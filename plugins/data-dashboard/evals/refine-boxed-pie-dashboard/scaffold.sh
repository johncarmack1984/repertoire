#!/usr/bin/env bash
# A sales dashboard built the way Few's chapter 3 warns against: a logo in the top left, boxed panels
# with gradient title bars and drop shadows, four gauges, a pie of revenue by region, a heavy-ruled
# table with red and green fills, unsorted rainbow bars with a legend and gridlines, values to the
# cent, a refresh time to the second, and a page about 1,960 px tall.
set -euo pipefail

mkdir -p dashboard

cat > dashboard/index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sales Performance Dashboard</title>
<style>
  body { margin: 0; background: #e9eef3; font-family: Verdana, Geneva, sans-serif; color: #222; }
  .topbar { display: flex; align-items: center; gap: 24px; padding: 16px 24px; background: #fff; border-bottom: 4px solid #1f5fb3; }
  .logo { width: 220px; height: 90px; background: linear-gradient(135deg, #1f5fb3, #0b2f66); color: #fff; font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center; border-radius: 8px; letter-spacing: 2px; }
  .topbar h1 { font-size: 30px; margin: 0; }
  .refreshed { font-size: 13px; color: #666; }
  .panel { background: #fff; margin: 24px; border: 1px solid #9ab; border-radius: 6px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35); min-height: 420px; }
  .panel h2 { margin: 0; padding: 12px 16px; font-size: 18px; color: #fff; background: linear-gradient(#3b7dd8, #1f5fb3); border-radius: 6px 6px 0 0; }
  .panel .body { padding: 20px; }
  .gauges { display: flex; gap: 20px; flex-wrap: wrap; }
  .gauge { text-align: center; }
  .gauge-name { font-weight: bold; margin-top: 6px; }
  .gauge-target { font-size: 12px; color: #666; }
  .pie-wrap { display: flex; gap: 40px; align-items: center; }
  ul.legend { list-style: none; padding: 0; margin: 0; line-height: 2; }
  .swatch { display: inline-block; width: 14px; height: 14px; margin-right: 8px; vertical-align: middle; }
  table.grid { border-collapse: collapse; width: 100%; font-size: 15px; }
  table.grid th, table.grid td { border: 2px solid #333; padding: 10px 14px; text-align: center; }
  table.grid th { background: #1f5fb3; color: #fff; }
</style>
</head>
<body>
  <div class="topbar">
    <div class="logo">BRIGHTLINE</div>
    <div>
      <h1>Sales Performance Dashboard</h1>
      <div class="refreshed">Last refreshed: 11/13/2026 08:02:17</div>
    </div>
  </div>

  <div class="panel">
    <h2>Key Performance Indicators</h2>
    <div class="body gauges">
      <div class="gauge">
        <svg width="260" height="170" viewBox="0 0 260 170">
          <path d="M 30.00 130.00 A 100 100 0 0 1 160.90 34.89" fill="none" stroke="#e74c3c" stroke-width="22"/>
          <path d="M 160.90 34.89 A 100 100 0 0 1 219.10 84.60" fill="none" stroke="#f1c40f" stroke-width="22"/>
          <path d="M 219.10 84.60 A 100 100 0 0 1 230.00 130.00" fill="none" stroke="#2ecc71" stroke-width="22"/>
          <line x1="130" y1="130" x2="185.77" y2="61.93" stroke="#222" stroke-width="4"/>
          <circle cx="130" cy="130" r="9" fill="#222"/>
          <text x="130" y="162" text-anchor="middle" font-size="20" font-weight="bold">94.37%</text>
        </svg>
        <div class="gauge-name">On-Time Delivery</div>
        <div class="gauge-target">Target: 95.00%</div>
      </div>
      <div class="gauge">
        <svg width="260" height="170" viewBox="0 0 260 170">
          <path d="M 30.00 130.00 A 100 100 0 0 1 160.90 34.89" fill="none" stroke="#e74c3c" stroke-width="22"/>
          <path d="M 160.90 34.89 A 100 100 0 0 1 219.10 84.60" fill="none" stroke="#f1c40f" stroke-width="22"/>
          <path d="M 219.10 84.60 A 100 100 0 0 1 230.00 130.00" fill="none" stroke="#2ecc71" stroke-width="22"/>
          <line x1="130" y1="130" x2="158.50" y2="46.74" stroke="#222" stroke-width="4"/>
          <circle cx="130" cy="130" r="9" fill="#222"/>
          <text x="130" y="162" text-anchor="middle" font-size="20" font-weight="bold">4.21 / 5</text>
        </svg>
        <div class="gauge-name">Customer Satisfaction</div>
        <div class="gauge-target">Target: 4.30 / 5</div>
      </div>
      <div class="gauge">
        <svg width="260" height="170" viewBox="0 0 260 170">
          <path d="M 30.00 130.00 A 100 100 0 0 1 160.90 34.89" fill="none" stroke="#e74c3c" stroke-width="22"/>
          <path d="M 160.90 34.89 A 100 100 0 0 1 219.10 84.60" fill="none" stroke="#f1c40f" stroke-width="22"/>
          <path d="M 219.10 84.60 A 100 100 0 0 1 230.00 130.00" fill="none" stroke="#2ecc71" stroke-width="22"/>
          <line x1="130" y1="130" x2="155.08" y2="45.65" stroke="#222" stroke-width="4"/>
          <circle cx="130" cy="130" r="9" fill="#222"/>
          <text x="130" y="162" text-anchor="middle" font-size="20" font-weight="bold">31.84%</text>
        </svg>
        <div class="gauge-name">Gross Margin</div>
        <div class="gauge-target">Target: 33.00%</div>
      </div>
      <div class="gauge">
        <svg width="260" height="170" viewBox="0 0 260 170">
          <path d="M 30.00 130.00 A 100 100 0 0 1 160.90 34.89" fill="none" stroke="#e74c3c" stroke-width="22"/>
          <path d="M 160.90 34.89 A 100 100 0 0 1 219.10 84.60" fill="none" stroke="#f1c40f" stroke-width="22"/>
          <path d="M 219.10 84.60 A 100 100 0 0 1 230.00 130.00" fill="none" stroke="#2ecc71" stroke-width="22"/>
          <line x1="130" y1="130" x2="184.37" y2="60.81" stroke="#222" stroke-width="4"/>
          <circle cx="130" cy="130" r="9" fill="#222"/>
          <text x="130" y="162" text-anchor="middle" font-size="20" font-weight="bold">97.12%</text>
        </svg>
        <div class="gauge-name">Order Fill Rate</div>
        <div class="gauge-target">Target: 98.00%</div>
      </div>
    </div>
  </div>

  <div class="panel">
    <h2>Revenue by Region (QTD)</h2>
    <div class="body pie-wrap">
      <svg width="320" height="320" viewBox="0 0 320 320">
        <path d="M 160 160 L 160.00 20.00 A 140 140 0 0 1 237.05 276.89 Z" fill="#e74c3c" stroke="#fff" stroke-width="2"/>
        <path d="M 160 160 L 237.05 276.89 A 140 140 0 0 1 28.54 208.15 Z" fill="#3498db" stroke="#fff" stroke-width="2"/>
        <path d="M 160 160 L 28.54 208.15 A 140 140 0 0 1 61.98 60.04 Z" fill="#2ecc71" stroke="#fff" stroke-width="2"/>
        <path d="M 160 160 L 61.98 60.04 A 140 140 0 0 1 121.51 25.39 Z" fill="#f1c40f" stroke="#fff" stroke-width="2"/>
        <path d="M 160 160 L 121.51 25.39 A 140 140 0 0 1 160.00 20.00 Z" fill="#9b59b6" stroke="#fff" stroke-width="2"/>
      </svg>
      <ul class="legend">
        <li><span class="swatch" style="background:#e74c3c"></span>North America: $4,182,377.45</li>
        <li><span class="swatch" style="background:#3498db"></span>Europe: $2,946,105.18</li>
        <li><span class="swatch" style="background:#2ecc71"></span>Asia Pacific: $1,873,662.90</li>
        <li><span class="swatch" style="background:#f1c40f"></span>Latin America: $812,419.37</li>
        <li><span class="swatch" style="background:#9b59b6"></span>Middle East &amp; Africa: $455,231.64</li>
      </ul>
    </div>
  </div>

  <div class="panel">
    <h2>Regional Performance vs Target (QTD)</h2>
    <div class="body">
      <table class="grid">
        <tr><th>Region</th><th>QTD Revenue</th><th>QTD Target</th><th>% of Target</th></tr>
        <tr><td>North America</td><td>$4,182,377.45</td><td>$4,050,000.00</td><td style="background:#2ecc71;color:#fff">103.27%</td></tr>
        <tr><td>Europe</td><td>$2,946,105.18</td><td>$3,100,000.00</td><td style="background:#e74c3c;color:#fff">95.04%</td></tr>
        <tr><td>Asia Pacific</td><td>$1,873,662.90</td><td>$1,950,000.00</td><td style="background:#e74c3c;color:#fff">96.09%</td></tr>
        <tr><td>Latin America</td><td>$812,419.37</td><td>$780,000.00</td><td style="background:#2ecc71;color:#fff">104.16%</td></tr>
        <tr><td>Middle East &amp; Africa</td><td>$455,231.64</td><td>$560,000.00</td><td style="background:#e74c3c;color:#fff">81.29%</td></tr>
        <tr><td><b>Total</b></td><td><b>$10,269,796.54</b></td><td><b>$10,440,000.00</b></td><td><b>98.37%</b></td></tr>
      </table>
    </div>
  </div>

  <div class="panel">
    <h2>Revenue by Product Line (QTD)</h2>
    <div class="body pie-wrap">
      <svg width="660" height="380" viewBox="0 0 660 380">
        <line x1="70" y1="340.00" x2="640" y2="340.00" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="344.00" text-anchor="end" font-size="11">$0K</text>
        <line x1="70" y1="297.14" x2="640" y2="297.14" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="301.14" text-anchor="end" font-size="11">$500K</text>
        <line x1="70" y1="254.29" x2="640" y2="254.29" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="258.29" text-anchor="end" font-size="11">$1,000K</text>
        <line x1="70" y1="211.43" x2="640" y2="211.43" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="215.43" text-anchor="end" font-size="11">$1,500K</text>
        <line x1="70" y1="168.57" x2="640" y2="168.57" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="172.57" text-anchor="end" font-size="11">$2,000K</text>
        <line x1="70" y1="125.71" x2="640" y2="125.71" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="129.71" text-anchor="end" font-size="11">$2,500K</text>
        <line x1="70" y1="82.86" x2="640" y2="82.86" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="86.86" text-anchor="end" font-size="11">$3,000K</text>
        <line x1="70" y1="40.00" x2="640" y2="40.00" stroke="#bbb" stroke-dasharray="4 3"/>
        <text x="62" y="44.00" text-anchor="end" font-size="11">$3,500K</text>
        <rect x="80" y="212.43" width="70" height="127.57" fill="#9b59b6"/>
        <text x="115" y="204.43" text-anchor="middle" font-size="12">$1,488,320.05</text>
        <rect x="190" y="73.87" width="70" height="266.13" fill="#3498db"/>
        <text x="225" y="65.87" text-anchor="middle" font-size="12">$3,104,882.12</text>
        <rect x="300" y="302.20" width="70" height="37.80" fill="#f1c40f"/>
        <text x="335" y="294.20" text-anchor="middle" font-size="12">$441,000.00</text>
        <rect x="410" y="81.17" width="70" height="258.83" fill="#e67e22"/>
        <text x="445" y="73.17" text-anchor="middle" font-size="12">$3,019,690.60</text>
        <rect x="520" y="150.07" width="70" height="189.93" fill="#1abc9c"/>
        <text x="555" y="142.07" text-anchor="middle" font-size="12">$2,215,903.77</text>
        <line x1="70" y1="340" x2="640" y2="340" stroke="#333" stroke-width="2"/>
      </svg>
      <ul class="legend">
        <li><span class="swatch" style="background:#9b59b6"></span>Services</li>
        <li><span class="swatch" style="background:#3498db"></span>Hardware</li>
        <li><span class="swatch" style="background:#f1c40f"></span>Training</li>
        <li><span class="swatch" style="background:#e67e22"></span>Support</li>
        <li><span class="swatch" style="background:#1abc9c"></span>Software</li>
      </ul>
    </div>
  </div>
</body>
</html>
EOF
