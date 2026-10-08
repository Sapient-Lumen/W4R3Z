# REV0112 to REV0113 migration map

## Summary

rev0113 extracts scope-composition guard and decision-matrix semantics into `tools/scope_composition_semantics.py` and tightens current-surface digest binding between `surface_decisions` and temporal freshness observations.

## Added

- `tools/scope_composition_semantics.py`
- `AUDIT-2026.06.13-rev0113.md`
- `archive/REV0113-AUDIT-SCOPE-COMPOSITION-REFACTOR.md`
- `examples/negative/scope-composition-surface-source-wrong-bind-invalid.json`
- `examples/negative/scope-composition-temporal-source-mismatch-invalid.json`
- `examples/negative/scope-composition-surface-temporal-digest-mismatch-invalid.json`
- semantic vectors `TV-N308` through `TV-N310`
- fixture derivations `DF-0113-001` through `DF-0113-003`

## Changed

- `tools/validate_archive.py` delegates scope-composition semantic checks to the new helper.
- Existing scope-composition fixtures now align `aggregate_lifecycle_rollup` temporal `source_time_digest` with the surface `source_digest` artifact class.
- `tests/semantic-test-vectors.yaml` now covers the three source-binding failure modes.
- `tests/fixture-derivations.yaml` now proves the new negative fixtures are base-plus-patch derivations.

## Compatibility note

The schema shape is unchanged. The behavioral change is fail-closed validation: current scope-composition surfaces must carry the expected source digest binding, and current temporal observations must qualify the same digest-bound artifact as the surface decision.
