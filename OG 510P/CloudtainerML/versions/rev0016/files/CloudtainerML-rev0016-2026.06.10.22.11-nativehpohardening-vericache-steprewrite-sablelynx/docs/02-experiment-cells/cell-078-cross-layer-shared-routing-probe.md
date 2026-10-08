# CELL-078 — Cross-Layer Shared Routing Probe

Priority: **P1**
Status: **candidate**

## Cheap first run

Generate layer support sets with tunable agreement and compare one shared sparse index vs per-layer indexes.

## Sources

SRC-0133

## Baselines

- per-layer topk
- shared topk
- shared+delta
- oracle

## Metrics

- support recall
- routing cost
- output error
- layer conflict rate

## Stop condition

If shared index is safe only when all layers agree, demote.
