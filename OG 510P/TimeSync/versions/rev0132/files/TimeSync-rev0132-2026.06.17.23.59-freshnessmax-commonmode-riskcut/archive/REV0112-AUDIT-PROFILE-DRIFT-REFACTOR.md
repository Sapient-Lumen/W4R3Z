# rev0112 audit — profile compatibility drift semantics

## Focus

This revision targeted the profile compatibility drift branch because it remained a compact current-use gate whose digest-equivalence assumptions were not fully executable.

## Closed executable gap

A current profile drift decision now requires the digest relation and supporting digest material to agree:

```text
current + different_digest_without_equivalence -> invalid
current + unknown_or_redacted -> invalid
current + different_digest_with_equivalence without compatibility_statement_digest -> invalid
current digest rollover without prior/current profile digest bindings -> invalid
current digest rollover without successor compatibility statement digest -> invalid
```

This prevents profile compatibility drift from becoming a soft upgrade path where a label says “stricter_or_equal” but no digest-bound equivalence artifact is present.

## Refactor

`tools/profile_drift_semantics.py` extracts matrix and decision checks from `tools/validate_archive.py`. The helper has a local self-test and is included in the validation report.

## Fixture strategy

The new negatives are rendered JSON fixtures for audit review and are also generated from `examples/profile-compatibility-drift-decision-rev0087.json` by `tests/fixture-derivations.yaml`. That keeps the regression cases visible while reducing copy-drift.

## Remaining work

FT-0090 remains open. The next useful pass should continue with one executable concern at a time: semantic-version policy, digest-binding policy, or a remaining profile compatibility statement sub-branch if there is a concrete bypass. Avoid registry or doctrine expansion unless it is needed by a failing executable check.
