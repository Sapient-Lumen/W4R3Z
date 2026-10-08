# 61 — Replay-transparency validator scope refactor

rev0088 refactors the replay-transparency validation path so aggregate-local checks and mixed-layer composition checks are separated.

New helpers:

```text
check_scope_composition_guard(...)
check_scope_composition_decision_matrix(...)
```

The replay-transparency aggregate path now validates `scope_composition_guard` when present, after aggregate artifact timestamp semantics are available and before aggregate privacy, lineage, lifecycle, compromise-era, and recovery-rollup checks complete.

This keeps local lifecycle semantics local while still preventing consumers from composing downgrade, digest, profile-drift, transparency-policy, and lifecycle metadata into a cross-layer upgrade.
