# CELL-330 — Routing Family Report Refactor

Priority: **P0**  
Status: `audit-refactor-added`  
Idea: `IDEA-0328`  
Sources: SRC-0341, SRC-0342, SRC-0343, SRC-0345

This audit/refactor cell adds a routing-family report so the cube stops mixing token gates, operator routers, self-routing, expert routing, and value-geometry guards into one bucket.

## Cheap first run

Run tools/routing_family_report.py and inspect current routing probes plus missing guard fields.

## Metrics

- `routing_artifacts`
- `guard_ready`
- `missing_absorption_fields`
- `missing_coordination_fields`

## Stop condition

Keep only if it changes promotion decisions.
