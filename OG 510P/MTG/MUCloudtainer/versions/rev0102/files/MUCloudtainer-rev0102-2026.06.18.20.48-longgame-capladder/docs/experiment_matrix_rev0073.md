# rev0073 experiment matrix

| Experiment | Question | Status | Primary artifact |
|---|---|---:|---|
| Exact maximin gate | Can the current 2x3 population security calculation avoid approximation noise? | Complete | `src/muc5/population_frontier.py` |
| Pool robustness | Does the low-floor quarantine survive source, size, life, and leave-one cuts? | Complete, quarantined | `data/rev0073_population_pool_robustness_summary.json` |
| Evidence-tier catalog discovery | Can the lean sidecar workflow survive revision renames without hardcoded rev0072 paths? | Complete | `data/rev0073_evidence_tiering_catalog.json` |

The rev0073 strategic result is deliberately conservative: all fifteen robustness cuts fail by low conservative floor, not by missing cells, underpowered cells, or solver approximation.
