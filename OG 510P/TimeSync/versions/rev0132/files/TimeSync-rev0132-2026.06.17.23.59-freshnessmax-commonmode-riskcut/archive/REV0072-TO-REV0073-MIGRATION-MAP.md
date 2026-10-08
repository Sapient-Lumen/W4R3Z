# Migration map — rev0072 to rev0073

## Summary

rev0073 adds anchor freshness, checkpoint consistency, and split-view/equivocation status to replay-transparency receipts.

## Required change for replay-transparency receipts

Every `challenge_replay_transparency_receipt` must add:

```text
anchor_evaluation
```

with:

```text
evaluated_at
current_visibility_status
anchor_freshness
checkpoint_consistency
split_view_boundary
```

## Interpretation change

A replay-transparency receipt may be treated as `current_at_evaluation` only when:

```text
transparency_anchor.inclusion_status == included
anchor_freshness.status == fresh_at_evaluation
checkpoint_consistency.status == checked_consistent
split_view_boundary.status == no_conflicting_view_observed
```

Otherwise replay visibility is historical, contested, or unknown.

## No profile migration required

No TimeState field, profile map, profile digest, transport adapter, profile compatibility statement, or evaluator evidence class changes are required by this migration.
