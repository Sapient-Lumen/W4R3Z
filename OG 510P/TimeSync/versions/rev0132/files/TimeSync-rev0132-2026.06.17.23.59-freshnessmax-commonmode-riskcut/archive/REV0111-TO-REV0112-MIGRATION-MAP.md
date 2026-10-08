# rev0111 to rev0112 migration map

rev0112 keeps the six-field TimeState core unchanged and continues FT-0090 with a profile compatibility drift/refactor pass.

## Added

```text
tools/profile_drift_semantics.py
AUDIT-2026.06.13-rev0112.md
archive/REV0112-AUDIT-PROFILE-DRIFT-REFACTOR.md
examples/negative/profile-compatibility-drift-current-missing-compat-digest-invalid.json
examples/negative/profile-compatibility-drift-current-without-digest-equivalence-invalid.json
examples/negative/profile-compatibility-drift-rollover-missing-bound-digests-invalid.json
```

## Changed

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
tools/lint_revision_references.py
```

Current-use profile compatibility drift decisions now fail closed unless digest-distinct compatibility is backed by a digest-bound compatibility statement, and current digest rollover compatibility carries bound prior/current/successor material.

## Unchanged boundary

No TimeState core fields changed. No profile registry, compatibility repository, credential workflow, or proof-disclosure format was added.
