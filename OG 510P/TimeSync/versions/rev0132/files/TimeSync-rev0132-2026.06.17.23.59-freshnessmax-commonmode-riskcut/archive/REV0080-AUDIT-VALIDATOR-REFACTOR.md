# rev0081 validator audit/refactor note

The rev0080 aggregate validator had three nearby boundary-check patterns:

- aggregate monitor/witness cohort coverage,
- compromise-era suppression,
- recovery-audit rollup.

The rev0081 audit found the copy-paste risk was acceptable but growing. The validator now adds shared helpers:

- `boundary_false_errors(...)` for non-leakage and non-upgrade boolean boundaries,
- `non_negative_int(...)` for aggregate count normalization,
- `check_aggregate_privacy_controls(...)` for the new cadence / threshold / noise surface.

The refactor preserves the existing rev0080 compromise-era and recovery-rollup semantics while making the new privacy-control checks use the same non-upgrade vocabulary. It is intentionally not a full validator rewrite.
