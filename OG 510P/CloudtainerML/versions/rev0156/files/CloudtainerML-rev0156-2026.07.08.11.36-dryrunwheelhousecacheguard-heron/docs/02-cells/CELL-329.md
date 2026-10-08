# CELL-329 — Routing Family Absorption-vs-Coordination Split

Priority: **P0**  
Status: `priority-reconsidered`  
Idea: `IDEA-0327`  
Sources: SRC-0341, SRC-0342, SRC-0343, SRC-0345

This priority cell separates routing-as-selection from routing-as-coordination. Routing absorption threatens token-selection gates; directional routing suggests coordination routers might remain useful. The split should guide trained-tiny escalation.

## Cheap first run

Use routing_family_report to compare selection gates, coordination routers, self-routing, and operator routers.

## Metrics

- `absorption_gap`
- `coordination_dependency`
- `rare_miss`
- `route_flip`
- `winner_diversity`

## Stop condition

Keep the split only if it predicts which routing ideas deserve trained escalation.
