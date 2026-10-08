# TimeSync rev0113 audit — scope-composition source binding

## Focus

rev0113 continues FT-0090 with a narrow executable cleanup in scope composition. The issue was not a new TimeState concept; it was that a mixed-layer current guard could cite one digest-bound artifact in `surface_decisions[*].source_digest` while its `temporal_coherence.input_observations[*].source_time_digest` qualified a different artifact class or digest value.

That mismatch is risky because the guard is supposed to coordinate already-separated surfaces without upgrading them. If freshness evidence can silently point at a different digest-bound object than the surface decision, the guard can appear fresh/current while the specific composed surface was not the object actually observed.

## What changed

- Added `tools/scope_composition_semantics.py`.
- Moved scope-composition decision-matrix and guard semantic checks out of `tools/validate_archive.py`.
- Added current-surface `source_digest` artifact-class checks for the mixed-layer surfaces already used by the guard.
- Added current temporal-observation alignment: for current surfaces, `source_time_digest` must match the corresponding `surface_decisions[*].source_digest` by algorithm, value, and `binds` target.
- Normalized the existing positive scope-composition fixtures so `aggregate_lifecycle_rollup` temporal evidence cites the same lifecycle-summary digest as the composed surface rather than a different decision-table artifact class.

## New negative coverage

- `examples/negative/scope-composition-surface-source-wrong-bind-invalid.json`
- `examples/negative/scope-composition-temporal-source-mismatch-invalid.json`
- `examples/negative/scope-composition-surface-temporal-digest-mismatch-invalid.json`

All three are derivation-checked from `examples/scope-composition-guard-rev0090.json`.

## Risk reduced

The guard can no longer pass a current-use composition decision by combining surface identity from one artifact with freshness from another. This is deliberately smaller than adding a scope-composition registry or a provenance graph; it just makes the existing digest boundary executable.

## Still open

FT-0090 remains open. The validator is smaller and more modular than it was, but remaining dense areas still include aggregate correction-authority semantics and trust-policy reference semantics. Future extraction should continue only where it either closes a concrete bypass or removes fragile inline logic.
