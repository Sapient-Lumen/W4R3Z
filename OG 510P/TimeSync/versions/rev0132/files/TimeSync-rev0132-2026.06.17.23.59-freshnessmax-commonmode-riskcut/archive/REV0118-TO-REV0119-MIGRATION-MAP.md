# Migration map — rev0118 to rev0119

## Added

- `AUDIT-2026.06.13-rev0119.md`
- `archive/REV0119-AUDIT-CURRENT-CLAIM-MUTATOR-REFACTOR.md`
- Four derivation-checked negative fixtures:
  - `examples/negative/evidence-summary-minimum-validity-horizon-stale-invalid.json`
  - `examples/negative/local-assessment-unsatisfied-actionable-invalid.json`
  - `examples/negative/local-assessment-fallback-upgraded-with-mapping-invalid.json`
  - `examples/negative/local-assessment-accepted-conditional-invalid.json`
- Semantic vectors `TV-N332` through `TV-N335`
- Mutation probes `MP-0119-001` through `MP-0119-004`

## Changed

- `tools/evidence_summary_semantics.py` now treats `assessment.validity_horizon` as a current evidence input, not a timeless assessment fact, for satisfied minimum-summary coverage.
- `tools/assessment_temporal.py` now rejects unsatisfied current actionability and plain accepted policy status with conditional actionability.
- `tools/validate_archive.py` now rejects non-fallback profile assessments that still carry `evaluation_summary.fallback_mapping`.
- `tools/mutation_survivor_audit.py` now runs 22 focused probes.
- `tests/fixture-derivations.yaml` and `tests/semantic-test-vectors.yaml` include the new current-claim negatives.
- Current-facing revision documents now identify rev0119.

## Compatibility

No core TimeState field changed. Existing valid fixtures remain valid. The new failures are limited to internally contradictory current/satisfied claims that were previously schema-shaped but semantically unsafe.
