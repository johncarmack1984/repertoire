---
type: llm
focus: { source: file, path: cio-dashboard.html }
weight: 2
---
You are reading the source of an HTML dashboard for a CIO. Seven systems' availability over the last 30 days runs from 93.2% to 99.7%, and each system has its own acceptable level from 94.0% to 99.5%. On a 0 to 100% scale those differences are a few pixels wide.

PASS if availability is drawn so that the gaps show: on a scale that starts well above zero (for example 85% to 100%) with each value as a marker or tick rather than a bar, or as each system's deviation from its acceptable level. Each system's acceptable level must appear on the same graphic (a shaded zone, a tick, or the zero line of a deviation). The 12-month history of each system may sit beside it as a sparkline.

FAIL if availability is drawn as bars on a scale that starts above zero, as bars on a 0 to 100% scale, as gauges, or as numbers alone with no acceptable level beside them. Say which.
