# Target legality receipt — rev0173

## Why this cut exists

CR 608.2b-style target resolution is a high-risk replay seam because the legality check happens late, after choices and cost payments but before payload application. MTGSim already modeled all-illegal and partial-target resolution, but the durable `StackResolutionRecord` mostly carried counts and flags. That was enough for broad correctness assertions, but not enough for challengeable replay: an auditor could not see which target failed, which zone/identity was observed at resolution, or whether the effect payload reused the same late legality decision.

## What changed

rev0173 adds `TargetResolutionCheckRecord` and embeds an ordered `target_resolution_checks` vector in each `StackResolutionRecord`. Each entry stores:

- the one-based target index and original `TargetRef` snapshot;
- the source controller used for source-aware legality;
- `legal_on_resolution`;
- `TargetLegalityFailureKind` for illegal targets;
- the observed object zone and zone-change identity at resolution for object targets.

`resolve_top_of_stack(...)` now computes these checks once as resolution begins. It derives `legal_targets_on_resolution` from the receipt and passes that vector to `apply_effect_payload(...)`. Targeted payload branches no longer independently re-run target legality predicates while applying effects. This makes the resolution-time target check a single auditable transaction boundary.

## Failure kinds

The current failure taxonomy is deliberately narrow and engine-facing: `empty_target`, `target_kind_not_allowed`, `player_missing_or_lost`, `object_missing`, `object_zone_not_allowed`, `object_zone_change_mismatch`, `shroud`, `hexproof`, and `protection`. It is not yet a full Oracle target-restriction language; it names the failure classes represented by today’s scaffold.

## Validation and coverage

Validation rejects:

- target-check count mismatches against `chosen_targets`;
- target-check index drift;
- target receipts that disagree with chosen target snapshots;
- legal targets carrying failure reasons;
- illegal targets with no failure reason;
- legal-count drift between aggregate `legal_target_count` and per-target checks;
- missing object-zone snapshots for object targets.

Regression coverage now proves three distinct late-target cases:

- a multi-target spell partially resolves for the surviving legal target while preserving the illegal target’s graveyard-zone failure;
- an all-illegal multi-target spell applies no payload and explains both target failures;
- a blinked target that returned to the battlefield is illegal specifically by `object_zone_change_mismatch`, not by object id alone.

## Remaining gaps

This is still not a complete target subsystem. It does not model target groups with different restrictions, target changing, ward, “same target” exceptions, arbitrary Oracle-derived target predicates, or per-instruction legality nuances beyond the homogeneous target-vector scaffold. The value of this cut is narrower: resolution-time target legality is now typed, ordered, and replay-auditable.
