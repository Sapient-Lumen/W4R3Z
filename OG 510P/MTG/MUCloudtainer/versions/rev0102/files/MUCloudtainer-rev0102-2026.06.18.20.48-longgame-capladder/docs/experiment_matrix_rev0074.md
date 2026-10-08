# rev0074 experiment matrix

| Experiment | Question | Status | Primary artifact |
|---|---|---:|---|
| Raw population lineage | Do rev0069/rev0070 raw games exactly reproduce the inherited arm summaries? | Complete, 0 mismatches | `data/rev0074_population_raw_recomputed_arm_summary.csv` |
| Source-qualified game ids | Are local C++ shadow ids safe as archive-global keys? | Complete, local collision found and qualified | `data/rev0074_population_lineage_index.csv` |
| Fine raw strata guard | Do source × size × life strata promote when recomputed from raw games? | Complete, 0 promoted / 12 underpowered | `data/rev0074_population_raw_fine_gate.csv` |
| Evidence-tier carry-forward | Does the lean cold-sidecar workflow remain revision-local? | Complete | `data/rev0074_evidence_tiering_catalog.json` |

The rev0074 result is a lineage-and-stratification guard: the inherited summaries are correct, but the small high-point fine strata are not promotion evidence.
