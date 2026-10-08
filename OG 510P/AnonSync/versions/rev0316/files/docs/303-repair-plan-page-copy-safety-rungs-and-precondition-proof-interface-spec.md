# Repair plan page — copy-safety rungs and precondition proof interface spec

## Purpose

The archive already has integrity-rebuild, repair-ladder, intervention-receipt, and local-fault-recovery language.
What still remained under-specified was the ordinary operator page that should answer:

> which repair rung is actually next, what proof makes it safe, and what environment problem must be fixed before retrying the product action?

Current Resilio docs still make this seam concrete through `Database error`, `Service files missing / Cannot identify destination folder`, `My files don't sync`, and related warnings.
They provide practical ladders, but the ordinary answer is still article-shaped.

## Core decision

AnonSync must expose one first-class **Repair plan** page whenever ordinary actions are no longer enough and a typed repair ladder becomes the honest next step.

## Fixed page order

1. **Repair entry verdict**
2. **Copy-safety gate**
3. **Repair rungs**
4. **Environment preconditions**
5. **Receipts and rollback horizon**

### 1) Repair entry verdict

Show:

- `repair_plan_page_id`
- `repair_family` (`reindex`, `rebind`, `local-db-recreate`, `service-material-reset`, `subject-readd`, `unknown`)
- `why_repair_is_now_justified`
- `lighter_actions_already_tried[]`
- `why_lighter_actions_are_no_longer_enough`

The page must prove why it is time to leave Issue home / Environment conflict and enter a stronger lane.

### 2) Copy-safety gate

Show:

- `copy_safety_verdict` (`safe-to-proceed`, `needs-preservation-first`, `blocked-last-copy-risk`, `blocked-unknown-source-of-truth`)
- `authoritative_byte_witness_rows[]`
- `archive_or_history_rows[]`
- `local_drift_rows[]`
- `preservation_actions[]`

No repair rung may be marked primary until copy-safety is at least `safe-to-proceed`.

### 3) Repair rungs

Each rung row should show:

- `rung_order`
- `rung_kind`
- `what_it_changes`
- `data_loss_risk`
- `expected_success_signal`
- `what_stronger_rung_it_replaces_if_successful`
- `what_next_rung_opens_if_it_fails`

Typical rungs include:

1. recompute evidence only
2. local metadata/database recreate without subject identity replacement
3. path rebind to the same verified bytes
4. service-material reset with continuity proof
5. full subject re-add after preservation receipt

### 4) Environment preconditions

Show the conditions that must be true before the highlighted rung is honest:

- foreign-writer conflict resolved
- storage path mounted and stable
- second-instance collision absent
- sufficient free space / IO health
- route/source proof fresh enough for reseed if needed

This section prevents blind retry in a still-hostile environment.

### 5) Receipts and rollback horizon

Show:

- earlier repair receipts
- preservation receipts
- rollback or re-open conditions
- residue the operator should expect after success
- what still remains unproven even after planned success

## Object model implications

### Repair plan page

Fields:

- `repair_plan_page_id`
- `subject_ref`
- `repair_family`
- `lighter_actions_already_tried[]`
- `copy_safety_verdict`
- `authoritative_byte_witness_rows[]`
- `rung_rows[]`
- `environment_precondition_rows[]`
- `preservation_receipt_refs[]`
- `repair_receipt_refs[]`
- `next_honest_action`

### Repair rung row

Fields:

- `repair_rung_row_id`
- `rung_order`
- `rung_kind`
- `destructiveness_class` (`non-destructive`, `local-metadata-reset`, `subject-identity-reset`, `reseed-required`)
- `expected_success_signal`
- `failure_escalates_to`

## Explicit non-goals

AnonSync should not:

- jump straight from `not syncing` to `remove and re-add`
- hide preservation or last-copy checks behind a later modal
- treat environment conflict as something the repair page may ignore
- present all repair ideas as equally good guesses

## Relationship to nearby specs

This page packages and orders deeper contracts from:

- `199-integrity-rebuild-reindex-and-subject-repair-ladder-interface-spec.md`
- `236-local-fault-recovery-ladder-and-copy-safety-interface-spec.md`
- `281-service-material-page-integrity-damage-origin-and-rebind-receipt-interface-spec.md`
- `81-target-custody-and-exclusive-bind-review-spec.md`
