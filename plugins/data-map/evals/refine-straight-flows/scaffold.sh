#!/usr/bin/env bash
# A MapLibre page of weekly pallets between 8 Midwest distribution centers: 12 flows drawn as straight
# two-point lines, so the three reciprocal pairs lie on top of each other, with no direction cue, and
# centers sized by radius (pallets / 250 px). The refine must keep every flow and value and fix the faults.
set -euo pipefail

mkdir -p freight-map

cat > freight-map/index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Weekly freight flows</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@5.6.0/dist/maplibre-gl.css">
<script src="https://unpkg.com/maplibre-gl@5.6.0/dist/maplibre-gl.js"></script>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; color: #222; }
  h1 { font-size: 22px; margin: 16px 24px 4px; }
  p.note { margin: 0 24px 10px; font-size: 14px; color: #555; }
  #map { width: 100%; height: 600px; }
  footer { margin: 8px 24px 16px; font-size: 12px; color: #666; }
</style>
</head>
<body>
<h1>Weekly freight flows between distribution centers</h1>
<p class="note">Line width is pallets moved per week. Circle size is pallets handled per week at each center. Average week, July to September 2026.</p>
<div id="map"></div>
<footer>Source: Lakeshore Supply warehouse management system, Q3 2026.</footer>
<script>
const centers = {
  "type": "FeatureCollection",
  "features": [
    {"type": "Feature", "properties": {"id": "CHI", "name": "Chicago", "pallets": 9400}, "geometry": {"type": "Point", "coordinates": [-87.65, 41.85]}},
    {"type": "Feature", "properties": {"id": "MKE", "name": "Milwaukee", "pallets": 2300}, "geometry": {"type": "Point", "coordinates": [-87.9065, 43.0389]}},
    {"type": "Feature", "properties": {"id": "IND", "name": "Indianapolis", "pallets": 4100}, "geometry": {"type": "Point", "coordinates": [-86.1581, 39.7684]}},
    {"type": "Feature", "properties": {"id": "CMH", "name": "Columbus", "pallets": 3200}, "geometry": {"type": "Point", "coordinates": [-82.9988, 39.9612]}},
    {"type": "Feature", "properties": {"id": "DTW", "name": "Detroit", "pallets": 3600}, "geometry": {"type": "Point", "coordinates": [-83.0458, 42.3314]}},
    {"type": "Feature", "properties": {"id": "STL", "name": "St. Louis", "pallets": 3900}, "geometry": {"type": "Point", "coordinates": [-90.1994, 38.627]}},
    {"type": "Feature", "properties": {"id": "MCI", "name": "Kansas City", "pallets": 2700}, "geometry": {"type": "Point", "coordinates": [-94.5786, 39.0997]}},
    {"type": "Feature", "properties": {"id": "DSM", "name": "Des Moines", "pallets": 1150}, "geometry": {"type": "Point", "coordinates": [-93.625, 41.5868]}}
  ]
};

const flows = {
  "type": "FeatureCollection",
  "features": [
    {"type": "Feature", "properties": {"from": "CHI", "to": "IND", "from_name": "Chicago", "to_name": "Indianapolis", "pallets": 2140}, "geometry": {"type": "LineString", "coordinates": [[-87.65, 41.85], [-86.1581, 39.7684]]}},
    {"type": "Feature", "properties": {"from": "IND", "to": "CHI", "from_name": "Indianapolis", "to_name": "Chicago", "pallets": 610}, "geometry": {"type": "LineString", "coordinates": [[-86.1581, 39.7684], [-87.65, 41.85]]}},
    {"type": "Feature", "properties": {"from": "CHI", "to": "DTW", "from_name": "Chicago", "to_name": "Detroit", "pallets": 1580}, "geometry": {"type": "LineString", "coordinates": [[-87.65, 41.85], [-83.0458, 42.3314]]}},
    {"type": "Feature", "properties": {"from": "DTW", "to": "CHI", "from_name": "Detroit", "to_name": "Chicago", "pallets": 1420}, "geometry": {"type": "LineString", "coordinates": [[-83.0458, 42.3314], [-87.65, 41.85]]}},
    {"type": "Feature", "properties": {"from": "CHI", "to": "STL", "from_name": "Chicago", "to_name": "St. Louis", "pallets": 1760}, "geometry": {"type": "LineString", "coordinates": [[-87.65, 41.85], [-90.1994, 38.627]]}},
    {"type": "Feature", "properties": {"from": "STL", "to": "CHI", "from_name": "St. Louis", "to_name": "Chicago", "pallets": 390}, "geometry": {"type": "LineString", "coordinates": [[-90.1994, 38.627], [-87.65, 41.85]]}},
    {"type": "Feature", "properties": {"from": "MKE", "to": "CHI", "from_name": "Milwaukee", "to_name": "Chicago", "pallets": 980}, "geometry": {"type": "LineString", "coordinates": [[-87.9065, 43.0389], [-87.65, 41.85]]}},
    {"type": "Feature", "properties": {"from": "IND", "to": "CMH", "from_name": "Indianapolis", "to_name": "Columbus", "pallets": 870}, "geometry": {"type": "LineString", "coordinates": [[-86.1581, 39.7684], [-82.9988, 39.9612]]}},
    {"type": "Feature", "properties": {"from": "DTW", "to": "CMH", "from_name": "Detroit", "to_name": "Columbus", "pallets": 1130}, "geometry": {"type": "LineString", "coordinates": [[-83.0458, 42.3314], [-82.9988, 39.9612]]}},
    {"type": "Feature", "properties": {"from": "STL", "to": "MCI", "from_name": "St. Louis", "to_name": "Kansas City", "pallets": 1290}, "geometry": {"type": "LineString", "coordinates": [[-90.1994, 38.627], [-94.5786, 39.0997]]}},
    {"type": "Feature", "properties": {"from": "MCI", "to": "DSM", "from_name": "Kansas City", "to_name": "Des Moines", "pallets": 640}, "geometry": {"type": "LineString", "coordinates": [[-94.5786, 39.0997], [-93.625, 41.5868]]}},
    {"type": "Feature", "properties": {"from": "DSM", "to": "CHI", "from_name": "Des Moines", "to_name": "Chicago", "pallets": 450}, "geometry": {"type": "LineString", "coordinates": [[-93.625, 41.5868], [-87.65, 41.85]]}}
  ]
};

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://demotiles.maplibre.org/style.json',
  center: [-88.6, 41.0],
  zoom: 5.2
});

map.on('load', () => {
  map.addSource('flows', { type: 'geojson', data: flows });
  map.addSource('centers', { type: 'geojson', data: centers });
  map.addLayer({
    id: 'flow-lines', type: 'line', source: 'flows',
    paint: { 'line-color': '#e4572e', 'line-opacity': 0.8, 'line-width': ['/', ['get', 'pallets'], 150] }
  });
  map.addLayer({
    id: 'center-circles', type: 'circle', source: 'centers',
    paint: { 'circle-color': '#2e86ab', 'circle-opacity': 0.85, 'circle-radius': ['/', ['get', 'pallets'], 250],
             'circle-stroke-color': '#ffffff', 'circle-stroke-width': 1 }
  });
  map.addLayer({
    id: 'center-labels', type: 'symbol', source: 'centers',
    layout: { 'text-field': ['get', 'name'], 'text-size': 12, 'text-offset': [0, 1.6] }
  });
  map.on('click', 'flow-lines', (e) => {
    const p = e.features[0].properties;
    new maplibregl.Popup().setLngLat(e.lngLat).setHTML(`${p.from_name} and ${p.to_name}: ${p.pallets} pallets/week`).addTo(map);
  });
});
</script>
</body>
</html>
EOF
