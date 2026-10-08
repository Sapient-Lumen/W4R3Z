# 47 — Aggregate correction-authority lifecycle, revocation, emergency withdrawal, and contestation

rev0084 closed FT-0083 by adding a compact lifecycle surface to aggregate correction-authority references. rev0086 tightens that surface by requiring a decision-table digest and an explicit current/historical/suppressed lifecycle decision.

The surface exists because rev0083 could bind a correction, withdrawal, supersession, or reconciliation to an authorized correction authority and notification cadence, but it could not say whether that authority was later revoked, expired, emergency-withdrawn, or contested.

## Placement

The field is required inside:

```text
aggregate_summary.aggregate_revision_lineage.correction_authority_reference.authority_lifecycle
```

It is intentionally nested under the correction-authority reference, not under TimeState, profile assessment, evidence summary, replay receipt, transparency trust policy, or aggregate privacy controls.

## Required surfaces

`authority_lifecycle` contains seven bounded surfaces.

### `lifecycle_state`

A compact state value:

- `active`
- `pending_rotation`
- `expired`
- `revoked`
- `emergency_withdrawal`
- `contested`
- `unknown_or_redacted`

Only `active` and `pending_rotation` may support current aggregate interpretation, and only when revocation has been checked as `not_revoked`.

### `revocation_status`

A compact revocation posture:

- `not_revoked`
- `revoked`
- `not_checked`
- `unknown_or_redacted`

`revoked`, `not_checked`, and `unknown_or_redacted` cannot support current aggregate interpretation.

### `emergency_withdrawal`

A compact emergency-withdrawal posture:

- state,
- aggregate-only scope,
- optional digest-bound withdrawal record,
- whether current interpretation is suppressed.

Emergency withdrawal does not export response plans, incident forensics, affected authorities, legal details, repositories, endpoints, keys, or other operational material.

### `contestation`

A compact contestation posture:

- none,
- pending,
- resolved upheld,
- resolved overturned,
- unknown or redacted.

Pending, overturned, and unknown contestation cannot support current aggregate interpretation. A resolved-upheld contestation may support current interpretation only when all other lifecycle and revocation checks also support current interpretation.

### `decision_table_digest` and `current_interpretation_decision`

rev0086 requires every lifecycle reference to bind the aggregate lifecycle decision table and to report the derived decision. Valid decisions are:

- `current_supported`,
- `current_supported_guarded`,
- `historical_only`,
- `suppressed_by_emergency_withdrawal`,
- `suppressed_by_revocation`,
- `suppressed_by_contestation`,
- `suppressed_by_unknown_lifecycle`,
- `suppressed_by_notification_staleness`,
- `suppressed_by_portability_failure`.

The explicit decision must match the posture derived from lifecycle state, revocation status, emergency withdrawal, contestation, notification freshness, and portability.

### `lifecycle_boundary`

The boundary explicitly forbids exporting:

- authority rosters,
- authority key material,
- revocation endpoints,
- repository topology,
- incident forensics,
- legal-process details,
- emergency-response plans,
- contestation-party identities,
- external lifecycle records as TimeSync provenance.

The boundary also states that lifecycle posture may update only aggregate replay-visibility / aggregate-publication interpretation posture.

## Non-upgrade rule

Correction-authority lifecycle can constrain aggregate publication interpretation only. It cannot:

- update TimeState,
- update profile conformance,
- update current actionability,
- satisfy profile obligations,
- upgrade individual replay visibility,
- rewrite prior aggregate publications,
- export suppressed deltas,
- identify verifiers, notification recipients, contesting parties, or authorities,
- become TimeSync provenance.

## Failure semantics

A revoked, expired, emergency-withdrawn, contested, unknown, or unchecked lifecycle cannot support current aggregate interpretation.

Emergency withdrawal requires a digest-bound withdrawal record, a concrete resynchronization state, and must suppress current interpretation.

Pending or overturned contestation requires a digest-bound contestation record and must not be treated as current aggregate interpretation.

## Discovery

Lifecycle-bearing `aggregate_correction_authority_reference` objects may be returned through discovery. Discovery-returned references are schema-validated and semantically checked with the same non-upgrade and non-leakage rules.

## Evidence class

`aggregate_correction_authority_lifecycle_summary` is a non-satisfying evidence class. It may appear in evidence summaries as review context, but cannot be used for `profile_obligation` or to mark an obligation as met.

## rev0086 tightening note

The detailed executable rows live in `spec/48-aggregate-lifecycle-decision-table.md` and `tests/aggregate-lifecycle-decision-table.yaml`. Implementations should treat this file as the lifecycle object description and spec 48 as the decision authority.
