# rev0109 to rev0110 migration map

rev0109 extracted aggregate revision-lineage semantics. rev0110 extracts aggregate privacy-control semantics and tightens digest-class binding for threshold-equivalence and noisy-count policy metadata.

## Added

```text
tools/aggregate_privacy_semantics.py
examples/negative/aggregate-threshold-compatibility-wrong-bind-invalid.json
examples/negative/aggregate-threshold-profile-basis-missing-compat-invalid.json
examples/negative/aggregate-noise-policy-wrong-bind-invalid.json
AUDIT-2026.06.13-rev0110.md
archive/REV0110-AUDIT-AGGREGATE-PRIVACY-REFACTOR.md
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
```

## New semantic vectors

```text
TV-N298
TV-N299
TV-N300
```

## New derivations

```text
DF-0110-001
DF-0110-002
DF-0110-003
```

## Compatibility notes

Existing valid aggregate fixtures remain valid. Invalid aggregate privacy metadata that previously passed may now fail when compatibility or privacy-policy digest objects bind the wrong artifact class, or when profile-compatibility threshold basis omits the compatibility statement digest it depends on.
