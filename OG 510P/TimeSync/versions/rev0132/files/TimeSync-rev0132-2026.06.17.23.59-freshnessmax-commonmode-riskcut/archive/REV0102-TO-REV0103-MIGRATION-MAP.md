# REV0102 to REV0103 migration map

## Revision intent

rev0103 narrows FT-0090 by extracting transport-envelope integrity/binding-strength semantics from the validator and making signed/authenticated payload coverage claims executable.

## New files

- `tools/transport_integrity.py`
- `examples/negative/transport-signed-payload-without-signature-invalid.json`
- `examples/negative/transport-authenticated-without-semantic-cover-invalid.json`
- `examples/negative/transport-profile-reference-only-cover-invalid.json`
- `AUDIT-2026.06.13-rev0103.md`
- `archive/REV0103-AUDIT-TRANSPORT-INTEGRITY-REFACTOR.md`
- `archive/REV0102-TO-REV0103-MIGRATION-MAP.md`

## Changed files

- `tools/validate_archive.py`
  - imports the new transport-integrity helper and self-test
  - delegates envelope binding-strength/protection/coverage checks to the helper
  - reports rev0103 validation output
- `tests/semantic-test-vectors.yaml`
  - adds `TV-N276` through `TV-N278`
- `tests/fixture-derivations.yaml`
  - adds `DF-0103-001` through `DF-0103-003`
- `tests/TRACEABILITY-MATRIX.md`
  - adds rev0103 transport-integrity traceability rows
- `README.md`, `START_HERE.md`, `INDEX.md`, `VALIDATION-REPORT.md`, `REVISION-RECEIPT.json`, `CHANGELOG.md`, `frontier-ticket.json`, `MANIFEST.json`

## Compatibility notes

No TimeState core field changed. No schemas were expanded. Existing valid transport envelopes remain valid. Newly invalid envelopes are those that claim `signed_payload` or `authenticated_transport` binding while failing to protect the semantic payload, or that use `profile_reference` as the only integrity cover.
