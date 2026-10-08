# REV0102 audit — policy-equivalence temporal refactor

## Finding

The profile compatibility statement temporal helper enforced statement-level issue/signature/expiry ordering and compatibility-drift timing, but the replay-transparency policy-equivalence section still had timestamp logic embedded in `tools/validate_archive.py` and lacked two important artifact-time checks:

1. lifecycle-equivalence revocation/drift checks could occur after the equivalence evaluation;
2. lifecycle-equivalence evaluation could occur after the compatibility statement signature that claimed to bind it.

This was not a schema problem. The JSON was syntactically valid. It was a semantic artifact-time problem.

## Executable correction

`tools/policy_equivalence_temporal.py` now owns:

```text
policy_lifecycle_equivalence.equivalence_not_before < policy_lifecycle_equivalence.equivalence_not_after
current policy lifecycle equivalence evaluates inside the equivalence window
expired policy lifecycle equivalence evaluates after equivalence_not_after
revocation_check.checked_at <= evaluated_at
drift_check.checked_at <= evaluated_at
evaluated_at <= compatibility statement binding.signed_at
evaluated_at <= compatibility statement expires_at
```

## Fixture correction

The positive policy-equivalence fixture had a real timestamp flaw:

```text
binding.signed_at = 2026-05-22T19:45:05Z
policy_lifecycle_equivalence.evaluated_at = 2026-05-22T19:45:10Z
```

rev0102 moves the signature to `2026-05-22T19:45:15Z` and normalizes copied negatives that inherited that incidental bug.

## New negative coverage

- `profile-compatibility-policy-equivalence-after-signature-invalid.json`
- `profile-compatibility-policy-revocation-after-equivalence-invalid.json`
- `profile-compatibility-policy-drift-after-equivalence-invalid.json`

All three are rendered JSON fixtures and derivation-checked from `profiles/compatibility/p3-replay-transparency-policy-equivalence.json`.

## Non-goals

rev0102 does not add a policy repository, a lifecycle registry, a new digest surface, or a new compatibility authority model. It only makes the existing policy-equivalence artifact-time contract executable.
