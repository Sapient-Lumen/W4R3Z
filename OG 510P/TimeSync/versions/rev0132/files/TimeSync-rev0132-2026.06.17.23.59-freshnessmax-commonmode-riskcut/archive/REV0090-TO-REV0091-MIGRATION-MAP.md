# rev0090 to rev0091 migration map

rev0091 is a validation-hardening and cloudtainer-triage revision.

## Executable changes

- `tools/validate_archive.py`
  - enables JSON Schema `FormatChecker`
  - rejects duplicate semantic vector IDs
  - reports rev0091 validation output
- `tools/temporal_coherence.py`
  - rejects current observations after guard evaluation
  - enforces current observation `max_age_seconds`
- `tests/semantic-test-vectors.yaml`
  - fixes duplicate IDs
  - adds three negative vectors

## New negative fixtures

- `examples/negative/wire-claim-invalid-date-time-invalid.json`
- `examples/negative/scope-composition-guard-post-evaluation-observation-invalid.json`
- `examples/negative/scope-composition-guard-max-age-exceeded-invalid.json`

## Non-changes

- TimeState core unchanged
- profile catalog unchanged
- transport adapter catalog unchanged
- evidence class catalog unchanged
- `scope-composition-guard` schema version remains `rev0090`
- FT-0090 remains open for broader temporal reuse and digest canonicalization hardening
