# 39 — Transparency trust-policy lifecycle, expiry, revocation, and drift

## Status

Normative in rev0076.

This section closes FT-0075. It defines the lifecycle boundary for digest-bound transparency trust-policy references and for cross-operator replay-visibility policy equivalence.

## Motivation

rev0075 let a replay-transparency receipt bind threshold interpretation to a trust-policy digest. That was sufficient for static policy comparison, but not for operational use. A digest may expire, be revoked, be retired, be superseded, or roll over to a successor digest. A receiver also needs to know whether a current replay-visibility decision was made under an active, non-revoked, non-weakening policy posture.

TimeSync does not define the external policy repository, trust framework, publication mechanism, transparency log, witness protocol, or revocation service. It records only a compact lifecycle summary for the policy digest already referenced by the replay-transparency record.

## `lifecycle_status`

A `transparency_trust_policy_reference` now contains `lifecycle_status`.

The lifecycle status states:

- the local lifecycle state of the referenced policy digest,
- the time at which that state was evaluated,
- the validity window for the referenced digest,
- the revocation-check result,
- the drift or rollover posture,
- the non-upgrade boundary.

The allowed lifecycle states are:

- `active`
- `pending_activation`
- `expired`
- `revoked`
- `retired`
- `superseded`
- `unknown`

A replay-transparency record may treat replay visibility as `current_at_evaluation` only when the referenced trust-policy lifecycle is active, evaluated within its validity window, checked not revoked, and not drifted to a weaker or unknown threshold posture.

## Revocation boundary

`revocation_check.status` can be:

- `checked_not_revoked`
- `revoked`
- `not_checked`
- `not_applicable`
- `unknown`

A current replay-visibility claim requires `checked_not_revoked`. A revoked policy reference cannot support current replay visibility. This revocation status constrains only replay-transparency policy interpretation; it cannot update TimeState, profile conformance, validity horizon, verifier authorization, or source traceability.

## Drift and rollover boundary

`drift_status.state` can be:

- `no_drift_detected`
- `thresholds_stricter_or_equal`
- `digest_rollover_compatible`
- `thresholds_weakened`
- `digest_rollover_without_equivalence`
- `not_checked`
- `unknown`

Current replay visibility permits only non-weakening drift states:

- `no_drift_detected`
- `thresholds_stricter_or_equal`
- `digest_rollover_compatible`

A compatible digest rollover must identify the successor or current policy digest and the compatibility-statement digest that made the rollover acceptable. A rollover without equivalence is historical or contested, not current.

## Compatibility-statement lifecycle equivalence

When a profile compatibility statement asserts `replay_transparency_policy_equivalence`, its `transparency_policy_equivalence` object now includes `policy_lifecycle_equivalence`.

The lifecycle-equivalence object states:

- whether the equivalence is current, historical, expired, revoked, drifted, or unknown,
- the subject and related policy lifecycle states,
- the equivalence validity window,
- the revocation-check result,
- the drift-check result,
- the non-upgrade boundary.

A current cross-operator replay-visibility equivalence requires both policy states to be active, the equivalence to be within its window, revocation to be checked not revoked, and drift to be known and non-weakening.

## Non-upgrade rule

Lifecycle status and lifecycle equivalence may constrain replay-transparency visibility only. They must not become:

- profile evidence,
- current-actionability evidence,
- profile reassessment triggers,
- TimeSync provenance,
- trust-anchor export,
- policy-language export,
- external policy-repository metadata export.

## Validation requirements

The rev0076 validator rejects:

- current replay visibility under an expired policy reference,
- current replay visibility under a revoked policy reference,
- current replay visibility when drift is unknown or unchecked,
- digest rollover without compatibility-backed lifecycle equivalence,
- compatibility statements with expired/revoked/drifted lifecycle equivalence treated as current,
- lifecycle equivalence that weakens thresholds,
- lifecycle metadata that attempts to update actionability, reopen assessment, or become TimeSync provenance.
