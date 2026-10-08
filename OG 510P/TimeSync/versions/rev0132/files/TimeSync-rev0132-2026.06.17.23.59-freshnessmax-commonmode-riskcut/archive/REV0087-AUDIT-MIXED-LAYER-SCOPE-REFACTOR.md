# rev0087 audit — mixed-layer scope refactor

Audit finding: rev0087 made profile drift, downgrade proof, digest binding, and aggregate lifecycle decisions safe locally, but did not expose a single machine-checkable object for cross-layer composition.

Refactor:

- Added `check_scope_composition_guard(...)` for composed-surface decisions.
- Added `check_scope_composition_decision_matrix(...)` for attack-corpus completeness.
- Added discovery support for returning a guard object.
- Added replay-transparency aggregate support for validating a nested guard.
- Added render/profile-catalog propagation for `scope_composition_guard_summary`.

The refactor keeps the six-field TimeState core unchanged.
