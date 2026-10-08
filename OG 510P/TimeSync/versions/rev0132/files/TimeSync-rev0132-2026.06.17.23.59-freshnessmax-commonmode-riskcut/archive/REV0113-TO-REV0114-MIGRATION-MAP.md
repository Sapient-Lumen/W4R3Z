# rev0113 to rev0114 migration map

## Summary

rev0114 builds on rev0113 by extracting policy lifecycle-authority digest binding semantics into a helper and adding negative coverage for wrong artifact-class digest bindings.

## New files

```text
tools/policy_authority_digest_semantics.py
examples/negative/policy-lifecycle-authority-sequence-status-wrong-bind-invalid.json
examples/negative/policy-lifecycle-authority-rotation-statement-wrong-bind-invalid.json
examples/negative/policy-lifecycle-authority-successor-authority-wrong-bind-invalid.json
AUDIT-2026.06.13-rev0114.md
archive/REV0114-AUDIT-POLICY-AUTHORITY-DIGEST-REFACTOR.md
archive/REV0113-TO-REV0114-MIGRATION-MAP.md
```

## Changed files

```text
tools/validate_archive.py
tests/semantic-test-vectors.yaml
tests/fixture-derivations.yaml
README.md
START_HERE.md
INDEX.md
VALIDATION-REPORT.md
CHANGELOG.md
REVISION-RECEIPT.json
frontier-ticket.json
MANIFEST.json
```

Current-facing documentation headings and revision lint now target rev0114.
