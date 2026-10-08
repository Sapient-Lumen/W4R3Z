# rev0110 to rev0111 migration map

## Scope

rev0111 keeps the six-field TimeState core unchanged and continues FT-0090 with an external transparency receipt binding/refactor pass.

## Added

```text
tools/external_receipt_semantics.py
examples/negative/external-receipt-statement-wrong-bind-invalid.json
examples/negative/external-receipt-checkpoint-wrong-bind-invalid.json
examples/negative/external-receipt-receipt-wrong-bind-invalid.json
examples/negative/discovery-external-receipt-wrong-bind-invalid.json
AUDIT-2026.06.13-rev0111.md
archive/REV0111-AUDIT-EXTERNAL-RECEIPT-REFACTOR.md
```

## Changed

```text
tools/validate_archive.py
tests/semantic-test-vectors.yaml
tests/fixture-derivations.yaml
README.md
START_HERE.md
INDEX.md
CHANGELOG.md
VALIDATION-REPORT.md
REVISION-RECEIPT.json
frontier-ticket.json
```

## Semantic impact

Validated external transparency receipt references now fail closed unless their statement, checkpoint, and receipt digest fields bind the expected artifact classes. Discovery-returned external receipt references receive the same semantic check path.

## Non-goals

No transparency-log verifier, receipt-verification algorithm, monitor registry, external proof format, or provenance graph was added.
