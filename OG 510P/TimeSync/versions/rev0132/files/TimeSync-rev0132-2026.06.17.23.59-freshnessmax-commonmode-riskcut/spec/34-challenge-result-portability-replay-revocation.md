# 34 — Challenge-result portability, replay, and revocation

rev0071 closes FT-0070 by defining the smallest portable/replayable surface for detached authorized-verifier challenge results.

## Decision

A challenge result may be copied or replayed only as a **commitment-verification receipt** for the same redacted item commitment. It must not become profile evidence, current-actionability evidence, transport-authentication evidence, or a profile reassessment trigger.

The portability decision is expressed in two places:

```text
portability_boundary        declared scope and replay limits for the record
portable_result_state       current non-revoked usability of the result receipt
```

A replayed record may also carry:

```text
replay_context              the intended use and the target summary/assessment/profile digest being replayed against
```

## Portability boundary

`portability_boundary` is required on authorized-verifier challenge records. It states:

```text
portable_result_scope
replay_policy
result_may_be_replayed_for
portable_across_profile_revisions
portable_across_profile_digest_change
portable_across_operators_without_profile_compatibility
portability_does_not_expand_disclosure_scope
portable_result_is_profile_evidence
```

The only allowed replay purpose is:

```text
commitment_verification_only
```

A portable challenge result is still not TimeSync profile evidence. It proves only that an authorized external review matched, failed to match, or verified an external system reference for a specific commitment.

## Replay target binding

If `replay_context` is present, it must preserve:

```text
summary_id
assessment_id
assessed_profile digest
```

Replay across a changed profile digest is rejected. Replay against a different summary or assessment is rejected. Replay for current actionability, profile-obligation evidence, transport authentication, or reassessment is rejected.

## Revocation and current usability

`challenge_result.portable_result_state` is required for challenge-result records. It records:

```text
evaluated_at
not_after
current_status
revocation_check
current_status_does_not_update_profile_assessment
```

A result marked `usable_for_commitment_verification_only` must have `revocation_check.status: checked_not_revoked`.

A revoked result is not usable for portable replay. A result with no revocation check is not usable as a current portable receipt. `not_after` must not extend beyond the original challenge `expires_at`.

This current status does not refresh, reopen, or update the underlying profile assessment.

## Cross-operator portability

Cross-operator challenge-result portability requires a profile compatibility statement digest. This is still not negotiation. The compatibility statement may name the workflow:

```text
authorized_verifier_challenge_result_portability
```

but only when the evidence policy relation is `identical` or `stricter_or_equal`. A weaker evidence policy relation cannot authorize challenge-result portability.

The compatibility statement does not authorize disclosure, verify the external receipt, or change local policy. It is only a digest-bound compatibility artifact that a receiver may evaluate locally.

## Non-upgrade rule

A portable challenge result cannot upgrade any of the following:

```text
TimeState interval
TimeState freshness
traceability posture
source diversity posture
validity horizon
profile conformance
policy acceptance
current actionability
```

The result is replayable only as a bounded receipt over the original commitment binding.

## Negative fixture pressure

rev0071 adds negative fixtures for:

```text
revoked challenge results
usable results with no revocation check
replay as current-actionability/profile evidence
replay against a changed profile digest
cross-operator portability without a profile compatibility statement digest
profile compatibility statements that name challenge-result portability while weakening evidence policy
```
