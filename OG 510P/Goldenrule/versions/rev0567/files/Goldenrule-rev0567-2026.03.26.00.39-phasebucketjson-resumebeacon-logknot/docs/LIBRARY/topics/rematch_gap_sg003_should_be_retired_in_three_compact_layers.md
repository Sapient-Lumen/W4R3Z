# SG-003 should be retired in three compact layers

The rematch gap (`SG-003`) now dominates the open ledger. It carries `23` open assumptions and `24` open questions, while the two other gaps carry only one assumption and one question each.

That asymmetry is useful: it means the next implementor should treat `SG-003` as the backlog-collapse target rather than as one more research thread among many.

The clean order is:

1. **Canonicalization contract first** (`SQ-003` through `SQ-011`).
   - Decide what behavioral equivalence means in rematch-enabled worlds.
   - Specify cache invalidation, minimal cache keys, exact horizons, and the planner-manifest surface.
   - Keep the serialized planner compact enough to vendor into engine-facing artifacts.
2. **World telemetry and comparability contract second** (`SQ-012` through `SQ-016`).
   - Make role assignment explicit.
   - Require matched-vs-searching accounting, turnover tempo, and paired raw/in-match rankings.
   - This prevents future rematch claims from confusing occupancy artifacts with true strategic gains.
3. **Compact decision contract third** (`SQ-017` through `SQ-026`).
   - Delay robustness, live contenders, winner certification, budget-aware triage, materiality, delta frontiers, hazard bands, admissibility bands, and topology-stable anchors all belong here.
   - These questions are already phrased as minimal machine-checkable artifact contracts, so they should be retired with compact report/schema fields rather than bulky rerun tables.

The archive-size implication is the main reason to follow this order. The archive already knows how to generate large rematch tables; what it still lacks is the contract surface that tells inheritors which tiny summary fields are sufficient.

So the next tranche should not be “run more sweeps first.” It should be “freeze the smallest contract that makes future sweeps interpretable and compact.”
