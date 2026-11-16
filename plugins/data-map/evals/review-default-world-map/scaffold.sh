#!/usr/bin/env bash
# An electric-car registrations world map built with an agent's defaults. Planted faults: Web Mercator
# for a world choropleth; raw counts with no denominator; a rainbow (jet) ramp; 9 equal-interval classes
# on skewed counts; three font families; a setInterval autoplay through the years; a north arrow, zoom
# buttons, and a scale bar. The attribution is correct. The review must name each fault and change nothing.
set -euo pipefail

mkdir -p ev-map

cp "$(dirname "$0")/../../skills/data-map/assets/geo/world-110m.json" ev-map/countries.geojson

cat > ev-map/index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Electric car registrations around the world</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@5.6.0/dist/maplibre-gl.css">
<script src="https://unpkg.com/maplibre-gl@5.6.0/dist/maplibre-gl.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap">
<style>
  body { margin: 0; font-family: Georgia, 'Times New Roman', serif; color: #222; background: #fff; }
  header { padding: 16px 24px 8px; }
  h1 { font-family: 'Montserrat', sans-serif; font-size: 26px; margin: 0 0 4px; }
  .dek { font-size: 15px; margin: 0; }
  #map { position: relative; width: 100%; height: 620px; }
  .north-arrow { position: absolute; top: 12px; left: 12px; z-index: 2; width: 34px; height: 46px; background: rgba(255,255,255,0.85); border-radius: 4px; text-align: center; font: bold 14px 'Courier New', monospace; line-height: 1.1; padding-top: 4px; }
  .north-arrow span { display: block; font-size: 22px; }
  #legend { position: absolute; bottom: 36px; left: 12px; z-index: 2; background: rgba(255,255,255,0.9); padding: 8px 10px; font: 12px 'Courier New', monospace; }
  #legend .row { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
  #legend .sw { width: 18px; height: 12px; display: inline-block; }
  #year { position: absolute; top: 12px; right: 56px; z-index: 2; font: bold 28px 'Montserrat', sans-serif; background: rgba(255,255,255,0.85); padding: 2px 10px; border-radius: 4px; }
  footer { padding: 8px 24px 16px; font-size: 12px; color: #555; }
</style>
</head>
<body>
<header>
  <h1>China has registered the most new electric cars every year since 2019</h1>
  <p class="dek">New battery-electric and plug-in hybrid car registrations by country, 2019 to 2025</p>
</header>
<div id="map">
  <div class="north-arrow" title="North"><span>&#8593;</span>N</div>
  <div id="year">2019</div>
  <div id="legend"></div>
</div>
<footer>Source: Global Charge Monitor, Electric Car Registrations 2026 edition. Boundaries: Natural Earth (public domain).</footer>
<script>
const YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025];
const REGISTRATIONS = {
  CHN: [625200, 1012800, 1640700, 2657900, 4305700, 6975300, 11300000],
  USA: [447300, 550800, 678300, 835300, 1028700, 1266800, 1560000],
  DEU: [181900, 220000, 266200, 322000, 389500, 471200, 570000],
  GBR: [56600, 80500, 114600, 163100, 232100, 330300, 470000],
  FRA: [75600, 100200, 132900, 176100, 233400, 309300, 410000],
  NOR: [14400, 20700, 29800, 42900, 61700, 88900, 128000],
  SWE: [25800, 35200, 47900, 65300, 88900, 121100, 165000],
  NLD: [34300, 45600, 60700, 80700, 107400, 142800, 190000],
  BEL: [23200, 32100, 44200, 61000, 84100, 116000, 160000],
  ITA: [8600, 13200, 20100, 30800, 47100, 72000, 110000],
  ESP: [14500, 20600, 29300, 41700, 59300, 84400, 120000],
  CAN: [36900, 50400, 68900, 94100, 128600, 175700, 240000],
  KOR: [24000, 33400, 46500, 64800, 90200, 125600, 175000],
  JPN: [23600, 30500, 39400, 50900, 65800, 85100, 110000],
  AUS: [42500, 50500, 60000, 71400, 84900, 100900, 120000],
  NZL: [2400, 3400, 5000, 7200, 10500, 15200, 22000],
  IND: [19400, 26900, 37500, 52100, 72400, 100700, 140000],
  BRA: [8000, 12100, 18200, 27600, 41600, 62900, 95000],
  MEX: [12500, 15600, 19600, 24500, 30700, 38400, 48000],
  TUR: [28700, 35900, 44900, 56200, 70300, 87900, 110000],
  THA: [28200, 34600, 42300, 51800, 63400, 77600, 95000],
  IDN: [5100, 7700, 11700, 17600, 26400, 39800, 60000],
  VNM: [11700, 16500, 23200, 32500, 45600, 64100, 90000],
  ISR: [4800, 7000, 10200, 14800, 21400, 31000, 45000],
  CHE: [6700, 10000, 14700, 21700, 32100, 47400, 70000],
  AUT: [8200, 11400, 15900, 22200, 30900, 43100, 60000],
  DNK: [39500, 47500, 57200, 68800, 82800, 99700, 120000],
  FIN: [14700, 17400, 20500, 24200, 28600, 33800, 40000],
  POL: [5600, 7900, 11200, 15800, 22400, 31800, 45000],
  PRT: [7200, 10100, 14200, 19900, 28000, 39200, 55000],
  IRL: [7200, 8800, 10900, 13400, 16500, 20300, 25000],
  CZE: [4700, 5900, 7400, 9200, 11500, 14400, 18000],
  GRC: [1300, 1900, 2800, 4200, 6300, 9400, 14000],
  HUN: [1700, 2500, 3600, 5100, 7300, 10500, 15000],
  ZAF: [2900, 3400, 4100, 4800, 5700, 6700, 8000],
  CHL: [3100, 3900, 4900, 6100, 7700, 9600, 12000],
  COL: [1800, 2600, 3600, 5100, 7100, 10000, 14000],
  ARE: [8100, 10100, 12500, 15600, 19400, 24100, 30000],
  SAU: [1000, 1500, 2100, 3000, 4300, 6300, 9000],
  MYS: [3500, 5000, 7100, 10200, 14600, 20900, 30000],
  PHL: [2000, 2400, 2900, 3500, 4100, 5000, 6000],
  TWN: [3400, 5100, 7700, 11700, 17600, 26500, 40000],
  ISL: [800, 1300, 1900, 2800, 4100, 6100, 9000]
};

const COLORS = ['#00007f', '#0000ff', '#007fff', '#00ffff', '#7fff7f', '#ffff00', '#ff7f00', '#ff0000', '#7f0000'];
const CLASSES = COLORS.length;
const max = Math.max(...Object.values(REGISTRATIONS).flat());
const step = max / CLASSES;
const breaks = COLORS.map((_, i) => Math.round(step * (i + 1)));

function fillFor(year) {
  const i = YEARS.indexOf(year);
  const expr = ['match', ['get', 'iso_a3']];
  for (const [iso, values] of Object.entries(REGISTRATIONS)) {
    const v = values[i];
    let k = Math.min(Math.floor(v / step), CLASSES - 1);
    expr.push(iso, COLORS[k]);
  }
  expr.push('#d9d9d9');
  return expr;
}

function drawLegend() {
  const el = document.getElementById('legend');
  el.innerHTML = '<b>Registrations</b>';
  COLORS.forEach((c, i) => {
    const lo = i === 0 ? 0 : breaks[i - 1];
    el.innerHTML += `<div class="row"><span class="sw" style="background:${c}"></span>${lo.toLocaleString()} to ${breaks[i].toLocaleString()}</div>`;
  });
  el.innerHTML += '<div class="row"><span class="sw" style="background:#d9d9d9"></span>No data</div>';
}

const map = new maplibregl.Map({
  container: 'map',
  style: {
    version: 8,
    projection: { type: 'mercator' },
    sources: {
      countries: { type: 'geojson', data: './countries.geojson' }
    },
    layers: [
      { id: 'ocean', type: 'background', paint: { 'background-color': '#ffffff' } },
      { id: 'fill', type: 'fill', source: 'countries', paint: { 'fill-color': '#d9d9d9' } },
      { id: 'line', type: 'line', source: 'countries', paint: { 'line-color': '#ffffff', 'line-width': 0.5 } }
    ]
  },
  center: [10, 25],
  zoom: 1.1,
  attributionControl: { customAttribution: 'Data: Global Charge Monitor (2026) | Boundaries: Natural Earth' }
});
map.addControl(new maplibregl.NavigationControl(), 'top-right');
map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

map.on('load', () => {
  drawLegend();
  let i = 0;
  map.setPaintProperty('fill', 'fill-color', fillFor(YEARS[i]));
  setInterval(() => {
    i = (i + 1) % YEARS.length;
    document.getElementById('year').textContent = YEARS[i];
    map.setPaintProperty('fill', 'fill-color', fillFor(YEARS[i]));
  }, 1500);
});
</script>
</body>
</html>
EOF
