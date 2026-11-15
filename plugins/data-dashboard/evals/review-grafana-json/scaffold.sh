#!/usr/bin/env bash
# A Grafana service-health dashboard with the faults Few's chapter 3 names: a pie of requests by region,
# four gauges with green/yellow/red thresholds, a stat panel whose whole background turns red or green,
# and a table with red/green cells. One panel is done well: a single gray p95 latency line with a dashed
# SLO threshold and no legend. The review should mark the faults and leave that panel alone.
set -euo pipefail

mkdir -p grafana

cat > grafana/service-health.json <<'EOF'
{
  "title": "Service Health",
  "uid": "svc-health",
  "schemaVersion": 39,
  "version": 14,
  "editable": true,
  "refresh": "30s",
  "time": { "from": "now-6h", "to": "now" },
  "timepicker": {},
  "tags": ["checkout", "on-call"],
  "templating": { "list": [] },
  "annotations": { "list": [] },
  "panels": [
    {
      "id": 1,
      "type": "stat",
      "title": "Service status",
      "gridPos": { "h": 4, "w": 24, "x": 0, "y": 0 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "min(up{job=\"checkout\"})" }],
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "justifyMode": "center",
        "textMode": "value",
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false }
      },
      "fieldConfig": {
        "defaults": {
          "mappings": [
            { "type": "value", "options": { "0": { "text": "DOWN", "color": "red" }, "1": { "text": "UP", "color": "green" } } }
          ],
          "thresholds": { "mode": "absolute", "steps": [{ "color": "red", "value": null }, { "color": "green", "value": 1 }] }
        },
        "overrides": []
      }
    },
    {
      "id": 2,
      "type": "gauge",
      "title": "CPU usage",
      "gridPos": { "h": 7, "w": 6, "x": 0, "y": 4 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "avg(rate(container_cpu_usage_seconds_total{service=\"checkout\"}[5m])) * 100" }],
      "options": { "showThresholdLabels": false, "showThresholdMarkers": true, "reduceOptions": { "calcs": ["lastNotNull"] } },
      "fieldConfig": {
        "defaults": {
          "unit": "percent", "min": 0, "max": 100, "decimals": 2,
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }, { "color": "yellow", "value": 70 }, { "color": "red", "value": 85 }] }
        },
        "overrides": []
      }
    },
    {
      "id": 3,
      "type": "gauge",
      "title": "Memory usage",
      "gridPos": { "h": 7, "w": 6, "x": 6, "y": 4 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "avg(container_memory_working_set_bytes{service=\"checkout\"} / container_spec_memory_limit_bytes{service=\"checkout\"}) * 100" }],
      "options": { "showThresholdLabels": false, "showThresholdMarkers": true, "reduceOptions": { "calcs": ["lastNotNull"] } },
      "fieldConfig": {
        "defaults": {
          "unit": "percent", "min": 0, "max": 100, "decimals": 2,
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }, { "color": "yellow", "value": 75 }, { "color": "red", "value": 90 }] }
        },
        "overrides": []
      }
    },
    {
      "id": 4,
      "type": "gauge",
      "title": "Error rate",
      "gridPos": { "h": 7, "w": 6, "x": 12, "y": 4 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "sum(rate(http_requests_total{service=\"checkout\",code=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"checkout\"}[5m])) * 100" }],
      "options": { "showThresholdLabels": false, "showThresholdMarkers": true, "reduceOptions": { "calcs": ["lastNotNull"] } },
      "fieldConfig": {
        "defaults": {
          "unit": "percent", "min": 0, "max": 10, "decimals": 3,
          "thresholds": { "mode": "absolute", "steps": [{ "color": "green", "value": null }, { "color": "yellow", "value": 1 }, { "color": "red", "value": 5 }] }
        },
        "overrides": []
      }
    },
    {
      "id": 5,
      "type": "gauge",
      "title": "Apdex",
      "gridPos": { "h": 7, "w": 6, "x": 18, "y": 4 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "(sum(rate(http_request_duration_seconds_bucket{service=\"checkout\",le=\"0.3\"}[5m])) + sum(rate(http_request_duration_seconds_bucket{service=\"checkout\",le=\"1.2\"}[5m]))) / 2 / sum(rate(http_request_duration_seconds_count{service=\"checkout\"}[5m]))" }],
      "options": { "showThresholdLabels": false, "showThresholdMarkers": true, "reduceOptions": { "calcs": ["lastNotNull"] } },
      "fieldConfig": {
        "defaults": {
          "unit": "none", "min": 0, "max": 1, "decimals": 4,
          "thresholds": { "mode": "absolute", "steps": [{ "color": "red", "value": null }, { "color": "yellow", "value": 0.85 }, { "color": "green", "value": 0.94 }] }
        },
        "overrides": []
      }
    },
    {
      "id": 6,
      "type": "piechart",
      "title": "Requests by region",
      "gridPos": { "h": 9, "w": 8, "x": 0, "y": 11 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "sum by (region) (rate(http_requests_total{service=\"checkout\"}[5m]))", "legendFormat": "{{region}}" }],
      "options": {
        "pieType": "pie",
        "displayLabels": [],
        "legend": { "showLegend": true, "displayMode": "table", "placement": "right", "values": ["percent"] },
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false },
        "tooltip": { "mode": "single" }
      },
      "fieldConfig": { "defaults": { "color": { "mode": "palette-classic" }, "unit": "reqps" }, "overrides": [] }
    },
    {
      "id": 7,
      "type": "timeseries",
      "title": "p95 latency (ms), dashed line is the 300 ms SLO",
      "gridPos": { "h": 9, "w": 16, "x": 8, "y": 11 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [{ "refId": "A", "expr": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{service=\"checkout\"}[5m]))) * 1000", "legendFormat": "p95" }],
      "options": {
        "legend": { "showLegend": false, "displayMode": "hidden", "placement": "bottom", "calcs": [] },
        "tooltip": { "mode": "single", "sort": "none" }
      },
      "fieldConfig": {
        "defaults": {
          "unit": "ms",
          "decimals": 0,
          "min": 0,
          "color": { "mode": "fixed", "fixedColor": "#4d4d4d" },
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "fillOpacity": 0,
            "gradientMode": "none",
            "showPoints": "never",
            "axisPlacement": "auto",
            "axisLabel": "",
            "axisGridShow": false,
            "thresholdsStyle": { "mode": "dashed" }
          },
          "thresholds": { "mode": "absolute", "steps": [{ "color": "transparent", "value": null }, { "color": "#8c8c8c", "value": 300 }] }
        },
        "overrides": []
      }
    },
    {
      "id": 8,
      "type": "table",
      "title": "Endpoints",
      "gridPos": { "h": 9, "w": 24, "x": 0, "y": 20 },
      "datasource": { "type": "prometheus", "uid": "prom" },
      "targets": [
        { "refId": "A", "expr": "sum by (route) (rate(http_requests_total{service=\"checkout\"}[5m]))", "format": "table", "instant": true },
        { "refId": "B", "expr": "sum by (route) (rate(http_requests_total{service=\"checkout\",code=~\"5..\"}[5m])) / sum by (route) (rate(http_requests_total{service=\"checkout\"}[5m])) * 100", "format": "table", "instant": true }
      ],
      "transformations": [
        { "id": "merge", "options": {} },
        { "id": "organize", "options": { "excludeByName": { "Time": true }, "renameByName": { "route": "Endpoint", "Value #A": "Requests/s", "Value #B": "Error %" } } }
      ],
      "options": { "showHeader": true, "cellHeight": "md", "footer": { "show": false } },
      "fieldConfig": {
        "defaults": { "custom": { "align": "center", "cellOptions": { "type": "auto" } }, "decimals": 4 },
        "overrides": [
          {
            "matcher": { "id": "byName", "options": "Error %" },
            "properties": [
              { "id": "custom.cellOptions", "value": { "type": "color-background", "mode": "basic" } },
              { "id": "thresholds", "value": { "mode": "absolute", "steps": [{ "color": "green", "value": null }, { "color": "red", "value": 1 }] } }
            ]
          }
        ]
      }
    }
  ]
}
EOF
