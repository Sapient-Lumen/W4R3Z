# Experiment matrix — rev0071

| Experiment | Purpose | Status | Key output |
|---|---|---:|---|
| Pooled population power floor | Combine rev0069 and rev0070 seed-disjoint complete panels, recompute confidence intervals, and test whether precision still blocks the gate. | Complete, quarantined | `data/rev0071_population_power_floor_summary.json` |
| Population summary aggregation | Prevent duplicate rows from overwriting each other when pooling across size/life context axes. | Tested | `tests/test_rev0071_powerfloor_derivatives.py` |
| Outcome-only runner refactor | Separate game outcome evaluation from expensive per-transition C++ shadow construction. | Implemented | `src/muc5/cpp_rollout.py` |
| Evidence derivatives | Create compact profiles for the two rev0070 missing-derivative blockers. | Complete | `data/rev0071_evidence_derivatives_summary.json` |
| Evidence index refresh | Confirm missing-derivative blockers are zero and archive candidates rise to five. | Complete | `data/rev0071_evidence_index.json` |
