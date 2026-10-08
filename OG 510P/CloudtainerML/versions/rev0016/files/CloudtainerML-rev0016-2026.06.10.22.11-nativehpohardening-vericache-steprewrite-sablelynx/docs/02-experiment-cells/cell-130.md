# CELL-130 — Primary Metric Patch Refactor

Priority: **P0**  
Status: **active-refactor**  
Idea: `IDEA-0129`  
Sources: SRC-0001

## Cheap first run

Run primary_metric_patcher.py then metric index and graph specs.

## Metrics

- patched count
- schema-ready count
- no-mapping count

## Required baselines

- metric index only
- patch-in-place
- sidecar patch

## Stop condition

If patching hides uncertainty, switch to sidecar-only.
