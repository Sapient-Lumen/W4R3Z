# rev0110 audit — aggregate privacy-control digest semantics

## Targeted branch

The target was the aggregate privacy-control branch inside `tools/validate_archive.py`. It was dense, copy-prone, and mixed publication cadence, threshold equivalence, statistical noise, compromise-era suppression, and recovery rollup semantics.

## Why this was worth doing

This branch is not merely documentation. It decides whether an aggregate publication can be interpreted safely without leaking identities, weakening suppression, or treating compatibility metadata as profile evidence. A wrong digest class here can make a compact aggregate surface look bound while pointing at the wrong kind of object.

## Extracted helper

```text
tools/aggregate_privacy_semantics.py
```

The helper now owns:

```text
aggregate privacy boundary checks
publication-cadence reconstruction/differencing checks
suppression-threshold equivalence checks
statistical-noise policy binding checks
compromise-era suppression aggregate-count checks
recovery-audit rollup aggregate-count and compatibility checks
```

## New fail-closed rules

```text
profile-compatibility threshold basis requires compatibility_statement_digest binding profile_compatibility_statement
cross-operator threshold equivalence requires compatibility_statement_digest binding profile_compatibility_statement
noisy aggregate counts require privacy_policy_digest binding aggregate_privacy_policy_rules
```

## Fixtures

```text
DF-0110-001 -> aggregate-threshold-compatibility-wrong-bind-invalid.json
DF-0110-002 -> aggregate-threshold-profile-basis-missing-compat-invalid.json
DF-0110-003 -> aggregate-noise-policy-wrong-bind-invalid.json
```

## Non-goals

rev0110 does not introduce:

```text
privacy-budget arithmetic
operator-equivalence registry
publication repository
compatibility authority workflow
identity disclosure mechanism
```

It only makes existing compact digest claims executable.
