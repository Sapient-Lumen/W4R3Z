# rev0095 to rev0096 migration map

## Baseline

rev0095 hardened retained-export artifact-time checks and introduced patch-derived fixture validation.

## rev0096 changes

```text
+ tools/transport_envelope_temporal.py
+ tools/semantic_vectors.py
+ examples/negative/transport-discovery-result-freshness-after-sent-invalid.json
+ examples/negative/transport-local-assessment-after-sent-invalid.json
+ examples/negative/transport-retained-export-after-sent-invalid.json
+ AUDIT-2026.06.12-rev0096.md
+ archive/REV0096-AUDIT-TRANSPORT-SEMANTIC-RUNNER-REFACTOR.md
```

Updated files:

```text
tools/validate_archive.py
tests/semantic-test-vectors.yaml
tests/fixture-derivations.yaml
frontier-ticket.json
README.md
START_HERE.md
INDEX.md
VALIDATION-REPORT.md
CHANGELOG.md
REVISION-RECEIPT.json
MANIFEST.json
tools/lint_revision_references.py
```

## Compatibility note

No TimeState core fields, profile IDs, transport adapter IDs, schema IDs, or evidence-class IDs changed. rev0096 only tightens transport-envelope artifact-time validation and moves semantic-vector runner mechanics into a helper module.
