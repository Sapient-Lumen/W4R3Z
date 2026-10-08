# 35 — Replay transparency receipts and aggregate verifier audit summaries

rev0072 closes FT-0071 by defining a detached replay-transparency surface for authorized-verifier challenge-result replay.

## Decision

TimeSync may carry a compact **replay-transparency receipt** or an **aggregate verifier audit summary**, but only as review metadata about replay visibility. These records are not profile evidence, current-actionability evidence, transport authentication, external authorization proof, or TimeSync provenance.

The surface is intentionally detached:

```text
challenge_result replay
  -> optional replay_transparency_receipt
  -> optional aggregate_verifier_audit_summary
```

A transparency receipt may say that a replay event was included in an append-only or external transparency surface. An aggregate summary may say how many replay events were observed over a period. Neither may reveal verifier rosters, verifier identities, legal-authority detail, salt/preimage material, commitment values in aggregate reports, raw timing observations, source rosters, path history, or clock algorithms.

## Replay-transparency receipt

A `challenge_replay_transparency_receipt` binds:

```text
challenge_id
result_id
summary_id
assessment_id
assessed_profile_digest
commitment_values
replay_event_digest
transparency_anchor
```

If a referenced challenge result is included, the receipt scope must match the referenced challenge id, result id, summary id, assessment id, profile digest, and commitment values.

A receipt must be anchored as one of:

```text
external_transparency_log_receipt
local_append_only_log_checkpoint
aggregate_audit_batch_digest
```

An exported receipt with `anchor_kind: not_logged` is rejected because it pretends to be a transparency receipt while declaring no transparency anchor.

## Aggregate verifier audit summary

An `aggregate_verifier_audit_summary` carries only bucketed or aggregate replay counts for a period. The minimum group size is explicit and counts below the threshold must be suppressed.

The record may include:

```text
total_replay_events
unique_challenge_results
portable_result_reuses
denied_or_revoked_replays
mismatches_reported
small_group_suppressed
```

It must not include per-verifier rows, verifier identity, verifier roster, commitment values, legal authority detail, salt/preimage material, or external authorization workflow contents.

## Boundary rules

Replay-transparency records cannot upgrade any of the following:

```text
TimeState interval
TimeState freshness
traceability posture
source diversity posture
validity horizon
profile conformance
policy acceptance
current actionability
profile obligation satisfaction
transport authentication
TimeSync provenance
```

The evidence class `replay_transparency_receipt` is non-satisfying. If an evaluator evidence summary mentions such a receipt, it is a review/supporting record only.

## Discovery behavior

The following flat request/result items may be returned when supported:

```text
replay_transparency_receipt
aggregate_verifier_audit_summary
```

Returned values are nested-validated. Negative results still use the normal `unavailable`, `unknown`, or `omitted` lanes and must not carry values.

## Negative fixture pressure

rev0072 adds negative fixtures for:

```text
unanchored transparency receipts
transparency receipts used to upgrade replay purpose
salt/preimage material exported through transparency records
aggregate summaries with unsuppressed small groups
aggregate summaries leaking verifier identity
replay transparency receipts used as profile-obligation evidence
malformed discovery-returned replay transparency records
```

## rev0073 tightening

See `spec/36-transparency-anchor-freshness-and-checkpoint-boundary.md` for the required `anchor_evaluation` object on replay-transparency receipts. rev0072 established replay visibility records; rev0073 distinguishes current replay visibility from historical, contested, or unknown visibility using anchor freshness, checkpoint consistency, and split-view/equivocation status.
