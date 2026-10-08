# rev0084 to rev0085 migration map

## Required changes for lifecycle-bearing aggregate correction-authority references

Add to every `authority_lifecycle` object:

```text
decision_table_digest
current_interpretation_decision
```

Known lifecycle states should also carry `lifecycle_policy_digest` binding `aggregate_correction_authority_lifecycle_rules`.

Concrete emergency withdrawal now requires:

```text
emergency_withdrawal.resynchronization_state
emergency_withdrawal.withdrawal_digest
emergency_withdrawal.resynchronization_policy_digest when concrete
```

Any non-`none` contestation state requires `contestation_digest`, including `resolved_upheld`.

## Aggregate verifier audit summaries

Add `aggregate_record_created_at` to aggregate verifier audit summaries so the validator can distinguish publication event time from artifact creation time.

Ensure these observation times are not after the artifact creation time:

```text
authorization_checked_at
lifecycle_checked_at
revocation_checked_at
notification.issued_at
last_notification_at
```

## Optional new aggregate surfaces

Add only when useful:

```text
aggregate_summary.aggregate_correction_authority_lifecycle_rollup
external_transparency_receipt_reference
aggregate_summary.aggregate_privacy_controls.statistical_disclosure_control_reference
```

These surfaces are aggregate-only and do not satisfy profile obligations.

## Optional profile/evidence hooks

P5 and P6 may request:

```text
extension_hooks.pnt_risk_posture
```

`timescale_realization` may now include UTC transition planning fields. These hooks remain outside TimeState.

## New tests

Add positive vectors equivalent to TV-191 through TV-193 and negative vectors equivalent to TV-N207 through TV-N215 for any implementation test suite.
