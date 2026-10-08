# Migration map — rev0083 to rev0084

## Add `authority_lifecycle`

Every `aggregate_correction_authority_reference` now includes:

```text
authority_lifecycle
```

For existing rev0083 records that remain current, set:

```text
lifecycle_state = active
lifecycle_effect = aggregate_interpretation_current
revocation_status = not_revoked
emergency_withdrawal.state = not_applicable
contestation.state = none
```

and include digest-bound lifecycle policy material plus the lifecycle boundary booleans.

## Revoked or expired references

A revoked, expired, unchecked, or unknown lifecycle must not be interpreted as current aggregate publication posture. Use `historical_only`, `contested`, `emergency_withdrawal_required`, or `unknown` effect as appropriate.

## Emergency withdrawal

Emergency withdrawal requires a digest-bound withdrawal record and `suppresses_current_interpretation = true`. It is aggregate-only posture and does not export incident-response details.

## Contestation

Pending or overturned contestation requires a digest-bound contestation record and cannot support current aggregate interpretation.

## Evidence policy

Profiles now forbid `aggregate_correction_authority_lifecycle_summary` from satisfying profile obligations. Profile digests therefore changed in rev0084.
