# CELL-093 — Cross-Layer Shared Routing Probe

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0093`  
Sources: SRC-0133, SRC-0133

## Cheap first run

Route once across layers under support drift.

## Baselines

- per-layer score
- layer0 once
- mid once
- consensus shared
- two-anchor shared
- random

## Metrics

- support_recall
- worst_layer_recall
- routing_cost_fraction
- bad_layer_fraction

## Stop condition

If no shared route can avoid bad-layer cliffs, require layer deltas.
