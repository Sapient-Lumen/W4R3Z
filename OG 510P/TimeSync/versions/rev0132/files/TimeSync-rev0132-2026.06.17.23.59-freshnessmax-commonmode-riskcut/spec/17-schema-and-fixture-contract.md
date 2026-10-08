# 17 — Schema and fixture contract

## Role of schemas

The schemas are shape contracts for review and implementation experiments. They intentionally do not encode every profile-specific timing rule.

## Role of semantic validation

`tools/validate_archive.py` checks mechanical semantic invariants that are awkward or impossible to express clearly in JSON Schema:

```text
interval ordering
profile-local label membership
fallback target is defined by profile map
fallback target is not stronger by profile-local rank
required/default item presence for fixture profiles
current-policy actionability consistency
manifest hash integrity
JSON Schema date-time format assertions
semantic vector ID uniqueness
```

## Positive and negative fixtures

`tests/semantic-test-vectors.yaml` marks each fixture as one of:

```text
pass
fail_schema
fail_semantic
```

Negative fixtures are part of the contract. A validator that accepts them has missed an invariant.

## Limit of the fixture contract

Passing the rev0091 validator does not prove that a real clock, source-selection algorithm, oscillator, grandmaster, network path, or regulatory deployment is correct. It proves that the archive's semantic objects are internally coherent according to rev0091 rules.
