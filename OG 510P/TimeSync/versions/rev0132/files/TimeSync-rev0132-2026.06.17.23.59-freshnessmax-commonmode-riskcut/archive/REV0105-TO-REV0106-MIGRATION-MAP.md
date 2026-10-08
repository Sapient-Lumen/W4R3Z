# REV0105 to REV0106 migration map

## Theme

rev0106 is an evidence-summary obligation-usability and validator-decomposition revision. The TimeState core, profile catalog, schemas, and transport adapter catalog are unchanged.

## Added

```text
tools/evidence_summary_semantics.py
examples/negative/evidence-summary-met-obligation-absent-item-invalid.json
examples/negative/evidence-summary-met-obligation-ignored-item-invalid.json
examples/negative/evidence-summary-redacted-obligation-without-commitment-invalid.json
AUDIT-2026.06.13-rev0106.md
archive/REV0106-AUDIT-EVIDENCE-SUMMARY-REFACTOR.md
```

## Changed

```text
tools/validate_archive.py
tools/lint_revision_references.py
tests/semantic-test-vectors.yaml
tests/fixture-derivations.yaml
README.md
START_HERE.md
INDEX.md
VALIDATION-REPORT.md
CHANGELOG.md
REVISION-RECEIPT.json
frontier-ticket.json
```

## New semantic vectors

```text
TV-N285 evidence-summary met obligation backed by absent item
TV-N286 evidence-summary met obligation backed by ignored item
TV-N287 evidence-summary met obligation backed by redacted uncommitted item
```

## New derivations

```text
DF-0106-001
DF-0106-002
DF-0106-003
```

## Compatibility

Existing positive examples remain valid. The new failures apply only to evidence summaries that claim an obligation is met while citing evidence that is not present/usable for that result.
