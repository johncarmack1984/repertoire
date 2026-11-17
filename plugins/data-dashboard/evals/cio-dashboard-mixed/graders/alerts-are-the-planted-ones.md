---
type: llm
focus: last_message
weight: 3
---
What follows is the agent's final reply after building a dashboard for a CIO. By IT's rules exactly six things need an alert: the Data Warehouse, critical (down right now, and 93.2% available over 30 days against an acceptable 97.0%); Network, a warning (98.6% against 99.0%); ERP, a warning (97.9% against 98.5%); CPU, a warning (79% used); the Budgeting system milestone, critical (13 days past due); and the data warehouse upgrade's cutover rehearsal, a warning (3 days past due).

PASS if the reply says the page flags those six and nothing else, with the Data Warehouse and the Budgeting system milestone as critical and the other four as warnings. Naming the Data Warehouse in a "now" strip, in its availability row, or both is fine.

FAIL if the reply leaves one of the six out of what it says is flagged, says anything else is flagged, calls a warning critical or a critical item a warning, or doesn't say what is flagged.
