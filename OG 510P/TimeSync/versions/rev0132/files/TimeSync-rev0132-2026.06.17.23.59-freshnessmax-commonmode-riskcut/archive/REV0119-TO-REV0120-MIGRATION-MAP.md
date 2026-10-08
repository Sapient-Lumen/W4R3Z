# Migration map — rev0119 to rev0120

## Added

- `AUDIT-2026.06.13-rev0120.md`
- `archive/REV0120-AUDIT-CHALLENGE-RECEIPT-PORTABILITY-REFACTOR.md`
- `tools/authorized_verifier_result_semantics.py`
- Seven derivation-checked negative fixtures:
  - `examples/negative/authorized-verifier-challenge-record-kind-carries-result-invalid.json`
  - `examples/negative/authorized-verifier-challenge-result-mismatch-inconsistent-invalid.json`
  - `examples/negative/authorized-verifier-challenge-verified-disclosure-not-verified-invalid.json`
  - `examples/negative/authorized-verifier-challenge-receipt-wrong-bind-invalid.json`
  - `examples/negative/authorized-verifier-challenge-scope-material-mismatch-invalid.json`
  - `examples/negative/authorized-verifier-challenge-not-portable-advertises-replay-invalid.json`
  - `examples/negative/authorized-verifier-challenge-receipt-digest-value-mismatch-invalid.json`
- Semantic vectors `TV-N336` through `TV-N342`
- Mutation probes `MP-0120-001` through `MP-0120-007`

## Changed

- `tools/validate_archive.py` now runs authorized-verifier result semantic checks in addition to authorized-verifier temporal checks.
- `tools/mutation_survivor_audit.py` now runs 29 focused probes and covers non-digest challenge/result mutations as well as digest-binding mutations.
- `tests/fixture-derivations.yaml` and `tests/semantic-test-vectors.yaml` include the new challenge-result negative fixtures.
- Current-facing revision documents now identify rev0120.

## Compatibility

No core TimeState field, transport adapter shape, profile map, or evidence-class catalog changed. Existing valid fixtures remain valid. The new failures are limited to internally contradictory authorized-verifier challenge/result records and portability boundaries that were previously schema-shaped but semantically unsafe.
