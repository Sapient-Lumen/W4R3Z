# 36 — Transparency-anchor freshness and checkpoint consistency boundary

rev0073 closes FT-0072 by adding a compact `anchor_evaluation` object to replay-transparency receipts.

## Decision

TimeSync may summarize whether a replay-transparency anchor was fresh, checkpoint-consistent, and free of an observed split-view signal at a specific evaluation time. It must not carry Merkle proof material, witness rosters, gossip transcripts, transparency-service internals, verifier identities, salt/preimage material, legal-authority details, or external-log provenance.

The object answers one narrow question:

```text
Can this replay-transparency receipt be treated as current replay visibility at evaluated_at?
```

It does not answer whether the original profile assessment remains fresh, whether the profile was satisfied, whether a verifier was authorized, whether a source clock was traceable, or whether an external transparency log is globally trustworthy.

## Shape

A `challenge_replay_transparency_receipt` now carries:

```text
anchor_evaluation:
  evaluated_at
  current_visibility_status
  anchor_freshness
  checkpoint_consistency
  split_view_boundary
```

`current_visibility_status` is one of:

```text
current_at_evaluation
historical_only
contested
unknown
```

`current_at_evaluation` is permitted only when all of the following are true:

```text
transparency_anchor.inclusion_status == included
anchor_freshness.status == fresh_at_evaluation
checkpoint_consistency.status == checked_consistent
split_view_boundary.status == no_conflicting_view_observed
```

Everything else is historical, contested, or unknown replay visibility.

## Anchor freshness

`anchor_freshness` records a local-policy freshness check:

```text
status: fresh_at_evaluation | stale_at_evaluation | not_checked | not_applicable
basis: logged_at | checkpoint_issued_at | local_policy_window | not_applicable
basis_time
max_age_seconds
freshness_does_not_update_profile_assessment: true
```

The freshness check is about the transparency anchor, not the original TimeState, assessment time, validity horizon, or policy acceptance. A fresh transparency anchor cannot make a stale timing assessment actionable.

## Checkpoint consistency

`checkpoint_consistency` is a compact status:

```text
status: checked_consistent | not_checked | failed | not_applicable
checked_at
current_checkpoint_digest
proof_material_exported: false
external_log_interpreted_as_timesync_provenance: false
```

The digest is a binding handle only. TimeSync does not define inclusion proof formats, consistency proof formats, Merkle tree algorithms, witness quorums, gossip mechanisms, or transparency-log APIs.

## Split-view / equivocation boundary

`split_view_boundary` records only bounded status:

```text
status: no_conflicting_view_observed | conflicting_view_reported | not_checked | not_applicable
conflict_details_exported: false
allegation_updates_profile_assessment: false
allegation_interpreted_as_timesync_provenance: false
```

A conflicting view may make replay visibility contested. It cannot become profile evidence, TimeSync provenance, source traceability evidence, transport authentication, current-actionability evidence, or a profile reassessment.

## Aggregate summaries

Aggregate verifier audit summaries may also carry `anchor_evaluation` when an operator wants to summarize the freshness or consistency of the aggregate integrity binding. The field is required only for replay-transparency receipts.

## Negative fixture pressure

rev0073 adds negative fixtures for:

```text
stale anchor treated as current replay visibility
checkpoint consistency not checked but treated as current
checkpoint consistency failed but treated as current
split-view/conflicting view treated as current
split-view allegation interpreted as TimeSync provenance
```
