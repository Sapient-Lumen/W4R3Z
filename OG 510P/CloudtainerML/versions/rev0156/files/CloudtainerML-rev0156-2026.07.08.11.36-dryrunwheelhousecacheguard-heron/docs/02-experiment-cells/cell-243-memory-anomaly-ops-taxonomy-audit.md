# CELL-243 — Memory Anomaly Ops Taxonomy Audit

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0242`  
Sources: SRC-0269

## Cheap first run

Classify all current probe failures by anomaly type.

## Metrics

- classified_probe_fraction
- ambiguous_class_count
- priority_change_count

## Required baselines

- flat_taxonomy
- short_vs_long_memory
- evidence_execution_safety_taxonomy

## Stop condition

If it does not alter priorities, keep as documentation.
