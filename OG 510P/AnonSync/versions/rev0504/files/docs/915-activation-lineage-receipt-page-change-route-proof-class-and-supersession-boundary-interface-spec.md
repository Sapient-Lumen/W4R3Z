# Activation lineage receipt page: change route, proof class, and supersession boundary interface spec

## Purpose

Any meaningful change whose effect can be delayed, staged, or only partially proven must leave behind one durable receipt that answers:

> what changed, how did it enter the system, what made it live, what proof class supports the claim, and what stronger sentence is still forbidden?

This receipt exists so later operators do not have to reconstruct activation truth from memory.

## Receipt contents

### Required fields

- `activation_lineage_receipt_id`
- `target_ref`
- `change_family`
- `change_summary`
- `source_plane`
- `activation_class`
- `activation_trigger`
- `saved_at`
- `became_live_at` nullable
- `proof_class` (`save-only`, `reread-observed`, `rescan-observed`, `restart-observed`, `external-proof`, `example-matched`, `mixed`, `unknown`)
- `retroactivity_boundary`
- `historical_residue_summary`
- `safe_sentence`
- `rejected_stronger_sentence`
- `supersedes_receipt_ref` nullable
- `superseded_by_receipt_ref` nullable

### Optional fields

- `witness_examples[]`
- `staleness_horizon`
- `pending_trigger_summary`
- `operator_acknowledgements[]`
- `related_review_refs[]`

## Rendering order

1. change summary
2. route and trigger summary
3. live/proof summary
4. retroactivity and residue summary
5. supersession boundary

### 1) Change summary

State exactly what changed and where it entered:

- UI
- power-user setting
- sidecar file
- config file
- runtime/service layer
- imported artifact
- external infrastructure

### 2) Route and trigger summary

Say whether the change was:

- instant
- reread-bound
- rescan-bound
- restart-bound
- startup-bound
- future-only
- external-proof-bound

### 3) Live/proof summary

Example sentence:

- `Saved through hidden sidecar edit at 07:41; runtime reread observed at 07:44; named-example verification recorded at 07:45.`

### 4) Retroactivity and residue summary

Example sentence:

- `Future arrivals now obey the new rule. Historical material already indexed before activation remains outside receipt scope.`

### 5) Supersession boundary

The receipt must say whether:
- it remains current
- a newer receipt replaced it
- its proof is now stale because runtime basis changed
- it still matters for historical interpretation only

## Rules

### Rule 1 — proof class is mandatory

A receipt may not imply more than the strongest proof it actually has.

### Rule 2 — supersession does not erase history

A newer change may replace the active rule, but the older receipt remains necessary to explain earlier state.

### Rule 3 — receipts preserve the stronger forbidden sentence

The product should keep visible what the receipt does *not* prove.

## Acceptance criteria

A later operator can:

- tell how the change entered the product
- tell what made it live
- tell what proof class supports the claim
- tell what old state remains out of scope
- tell whether a newer change has replaced it
