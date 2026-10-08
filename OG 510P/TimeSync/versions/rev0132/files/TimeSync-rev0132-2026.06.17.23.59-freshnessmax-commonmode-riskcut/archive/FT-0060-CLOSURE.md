# FT-0060 closure

## Original frontier

rev0060 asked how retained assessed state should treat profiles that are superseded, revoked, or no longer accepted.

## rev0061 closure

The answer is to separate historical assessment from current-policy acceptance.

```text
historical assessment:
  assessment_time
  assessed_profile
  profile_conformance
  applicability

current-policy overlay:
  profile_lifecycle_state
  policy_acceptance
```

## Core rule

Do not rewrite old `profile_conformance` outcomes merely because policy or profile lifecycle changed later.

Attach or recompute:

```text
policy_acceptance = accepted | accepted_with_conditions | rejected | unknown
```

## Why this is enough

This preserves audit truth while preventing stale or revoked profile assessments from being exported as currently actionable. It also avoids turning TimeSync into global revocation infrastructure.
