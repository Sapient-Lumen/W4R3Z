# Experiment matrix — rev0069

| Experiment | Scope | Rows/games | Status | Artifact |
|---|---:|---:|---|---|
| Population frontier pilot | 2 counter policies × 3 threat policies × 3 size cells × 2 life totals | 144 games | Operationally clean; pilot only | `data/rev0069_population_frontier_summary.json` |
| Population security table | One security row per size/life cell | 6 rows | Complete matrix | `data/rev0069_population_frontier_security.csv` |
| Inherited completeness audit | rev0065 + rev0067 summaries normalized into 2×3 population shape | 6 rows | Incomplete before rev0069 | `data/rev0069_population_frontier_inherited_completeness.csv` |
| Evidence migration audit | Bulk evidence >1 MiB | 78 records | 75 blocked by live references | `data/rev0069_evidence_index.json` |
| Matrix-safety regression tests | Comparison helpers and population/evidence utilities | 6 tests | Passing | `tests/test_rev0069_population_frontier.py` |
