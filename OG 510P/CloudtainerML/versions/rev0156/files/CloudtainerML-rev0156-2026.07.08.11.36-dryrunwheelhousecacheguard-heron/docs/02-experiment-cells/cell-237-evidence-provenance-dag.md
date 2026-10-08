# CELL-237 — Evidence Provenance DAG

Priority: **P0**  
Status: **implemented-native-rev0020**  
Idea: `IDEA-0236`  
Sources: SRC-0261, SRC-0236, SRC-0248

## Cheap first run

Run experiments/evidence_provenance_dag/evidence_provenance_dag_probe.cpp; inspect stale/contaminated evidence tails.

## Metrics

- mean_support_score
- stale_invalidation_miss_rate
- contamination_read_rate
- catastrophic_evidence_failure_rate
- mean_utility

## Required baselines

- relevance_only
- source_weighted
- revision_aware
- provenance_dag
- flowtrace_support
- oracle_evidence

## Stop condition

If provenance DAG does not improve stale/contaminated regimes, treat as audit schema only.
