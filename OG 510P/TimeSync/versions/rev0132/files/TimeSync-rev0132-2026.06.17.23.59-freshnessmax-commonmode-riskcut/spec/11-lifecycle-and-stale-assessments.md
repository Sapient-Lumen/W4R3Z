# 11 — Lifecycle and stale assessments

## Frontier closed by rev0061

rev0060 left one open question:

```text
How should retained assessed state treat profiles that are superseded, revoked, or no longer accepted?
```

rev0061 resolves this by separating historical assessment validity from current-policy acceptance.

## Two different questions

A retained assessment answers:

```text
Was this state assessed under profile X at assessment time?
```

A current consumer additionally asks:

```text
Does my current policy still accept that assessment for action now?
```

Those are different questions and should not overwrite each other.

## Rule

Do not mutate historical `profile_conformance` merely because the assessed profile was later superseded, revoked, deprecated, or locally disallowed.

Instead, retain or compute a current-policy overlay:

```text
policy_acceptance:
  status: accepted | accepted_with_conditions | rejected | unknown
  checked_at: <time>
  policy_reference?: <local or profile policy reference>
  reason?: <short reason>
```

## Minimum retained assessment context

For retained, detached, audited, safety, or compliance-sensitive exports, include:

```text
assessment_time
assessed_profile with sufficient reference strength
profile_conformance
applicability
```

Tier 3 profile references are preferred where exact rules must be reconstructed.

## Lifecycle states

A local system may report profile lifecycle state:

```text
active
superseded
deprecated
revoked
unknown
```

Lifecycle state is input to current-policy acceptance. It is not itself a rewrite of the historical assessment.

## Stale assessment consequences

Recommended defaults:

```text
profile active + accepted by current policy      => policy_acceptance: accepted
profile superseded but allowed for retention     => policy_acceptance: accepted_with_conditions
profile revoked or explicitly disallowed         => policy_acceptance: rejected
profile status cannot be resolved                => policy_acceptance: unknown
```

If `policy_acceptance` is `rejected` or `unknown`, the assessment must not be exported as currently actionable unless a profile or policy explicitly permits that use.

## Reassessment rule

A new profile, new policy, or new evidence can produce a new assessment. It should not silently edit the old one.

Use:

```text
old retained assessment  -> historical record
new reassessment         -> new profile_assessment entry
```

## Non-goals

This rule does not create:

```text
global profile revocation infrastructure
universal policy lattice
mandatory online profile registry
certificate-transparency-like log
one global lifecycle authority
```

Profiles or deployments may add those if their boundary earns them.
