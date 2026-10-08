# rev0105 audit — profile-reference binding refactor

## Why this was the next risky area

After rev0104, most obvious timestamp surfaces had executable checks. The remaining risk was increasingly about cross-boundary metadata that looks authoritative but is not actually bound to the artifact using it.

`assessed_profile.binding` is exactly such a surface. It can provide useful signed metadata about a profile reference, but if it is created after the assessment or omits the digest it appears to support, downstream readers may over-trust it.

## Refactor

Added:

```text
tools/profile_reference_binding.py
```

Moved into the helper:

```text
profile-reference signed binding coverage checks
profile-reference binding.signed_at <= use-time checks
helper self-tests for good, future, and digest-omission cases
```

Wired callers:

```text
check_local_assessed_state
check_evidence_summary
check_authorized_verifier_challenge
```

## Negative fixtures

Added derivation-checked fixtures:

```text
DF-0105-001 local binding signed after assessment_time
DF-0105-002 local binding omits digest from covers
DF-0105-003 authorized-verifier target binding signed after issued_at
```

These fixtures are rendered as JSON for audit readability but are machine-checked against their base fixture plus patch operations.

## Non-goals

rev0105 does not:

```text
verify cryptographic signatures
add a profile-binding authority registry
make signed profile bindings substitutes for normative profile digests
infer profile compatibility from a signed reference
change the TimeState core
```

## Result

The validator lost another small responsibility to a focused helper while gaining checks that reject future-created or under-covered profile-reference binding metadata.
