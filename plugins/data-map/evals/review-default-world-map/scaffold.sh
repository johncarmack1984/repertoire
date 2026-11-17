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
  CHN: [625200, 845600, 1810200, 2660600, 4121500, 6160300, 11296400],
  USA: [447300, 507400, 758300, 835800, 965700, 1273200, 1567700],
  DEU: [181900, 237600, 279400, 300700, 383400, 466400, 552800],
  GBR: [56600, 65900, 116800, 143800, 216100, 329200, 457100],
  FRA: [75600, 94200, 134000, 165000, 227400, 284500, 396300],
  NOR: [14400, 17800, 32100, 47200, 63600, 85000, 129300],
  SWE: [25800, 34300, 50900, 64700, 97300, 109900, 163500],
  NLD: [34300, 46900, 56800, 89100, 120200, 127700, 183500],
  BEL: [23200, 28500, 39200, 67900, 80300, 121500, 163000],
  ITA: [8600, 12000, 19600, 29300, 46300, 75600, 114000],
  ESP: [14500, 18100, 32300, 46500, 53200, 84800, 121400],
  CAN: [36900, 45300, 70300, 95500, 116400, 191000, 242900],
  KOR: [24000, 33200, 43600, 67900, 100100, 130500, 172900],
  JPN: [23600, 26100, 35000, 56600, 71200, 89100, 109700],
  AUS: [42500, 55500, 53500, 71500, 84700, 105500, 122100],
  NZL: [2400, 3600, 4900, 7900, 10900, 15000, 22700],
  IND: [19400, 21400, 41200, 45900, 74300, 109400, 136200],
  BRA: [8000, 9400, 17300, 27200, 40500, 56900, 95400],
  MEX: [12500, 15200, 20600, 23000, 30000, 39900, 46700],
  TUR: [28700, 35500, 43800, 61800, 72800, 84800, 108400],
  THA: [28200, 31000, 40100, 49300, 61400, 76200, 96300],
  IDN: [5100, 7800, 10800, 18100, 23400, 35600, 59600],
  VNM: [11700, 14700, 25800, 29600, 43300, 69400, 88000],
  ISR: [4800, 6500, 10600, 16500, 20200, 34600, 43300],
  CHE: [6700, 9800, 14400, 20700, 31900, 50200, 68100],
  AUT: [8200, 10200, 15800, 19600, 34400, 42100, 61200],
  DNK: [39500, 45200, 59900, 63600, 92200, 95400, 120500],
  FIN: [14700, 16700, 18600, 23500, 27900, 30500, 41400],
  POL: [5600, 7300, 10300, 17200, 21500, 34900, 44500],
  PRT: [7200, 10900, 14300, 21100, 24800, 35900, 53200],
  IRL: [7200, 8700, 12200, 13100, 16600, 18900, 24500],
  CZE: [4700, 5900, 6900, 8600, 11500, 14300, 18200],
  GRC: [1300, 1700, 2700, 4200, 5600, 8700, 13700],
  HUN: [1700, 2400, 3600, 5600, 6500, 10000, 15000],
  ZAF: [2900, 3100, 4300, 5000, 5100, 5900, 7700],
  CHL: [3100, 3400, 5300, 6800, 6800, 10000, 11900],
  COL: [1800, 2800, 3200, 4600, 7600, 9900, 14400],
  ARE: [8100, 11100, 11300, 15400, 17600, 26900, 29800],
  SAU: [1000, 1300, 2200, 3100, 4400, 7000, 9100],
  MYS: [3500, 4500, 6600, 9300, 13400, 19500, 30200],
  PHL: [2000, 2000, 3100, 3500, 4100, 5400, 6000],
  TWN: [3400, 4900, 7100, 10700, 18600, 29600, 41000],
  ISL: [800, 1300, 2000, 2800, 4500, 6800, 9100]
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
