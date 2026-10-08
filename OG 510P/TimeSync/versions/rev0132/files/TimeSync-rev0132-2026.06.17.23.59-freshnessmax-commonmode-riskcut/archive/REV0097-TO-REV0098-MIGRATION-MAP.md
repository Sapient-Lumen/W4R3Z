# rev0097 to rev0098 migration map

rev0098 does not change the TimeState core, profile catalog, transport adapter catalog, evidence-class catalog, schema IDs, or JSON digest profile.

## New executable checks

Aggregate verifier audit summaries now fail semantic validation when:

```text
issued_at > aggregate_record_created_at
```

The existing aggregate period interval check is now handled by `tools/aggregate_temporal.py` instead of inline validator code.

Fixture derivation validation now rejects:

```text
duplicate derivation IDs
multiple derivations targeting the same rendered output file
```

## New files

```text
+ tools/aggregate_temporal.py
+ AUDIT-2026.06.12-rev0098.md
+ archive/REV0097-TO-REV0098-MIGRATION-MAP.md
+ archive/REV0098-AUDIT-AGGREGATE-TEMPORAL-FIXTURE-REFACTOR.md
+ examples/negative/aggregate-issued-after-created-invalid.json
```

## Modified files

```text
~ tools/validate_archive.py
~ tools/fixture_derivations.py
~ tests/semantic-test-vectors.yaml
~ tests/fixture-derivations.yaml
~ README.md
~ START_HERE.md
~ INDEX.md
~ VALIDATION-REPORT.md
~ REVISION-RECEIPT.json
~ frontier-ticket.json
~ CHANGELOG.md
~ tests/acceptance-tests.md
~ tests/TRACEABILITY-MATRIX.md
~ tools/lint_revision_references.py
~ MANIFEST.json
```

## Compatibility note

Existing valid rev0097 aggregate verifier audit summaries remain valid when the publication `issued_at` is not later than `aggregate_record_created_at`. New failures indicate a previously implicit artifact-time ordering error rather than a TimeState or profile semantics change.
