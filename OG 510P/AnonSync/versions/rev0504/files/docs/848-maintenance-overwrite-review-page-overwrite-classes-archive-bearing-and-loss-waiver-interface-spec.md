# Maintenance overwrite review page — overwrite classes, archive-bearing, and loss-waiver interface spec

## Purpose

A plan alone is not enough when multiple loss classes, salvage holders, and settings-derived caveats collide.
This page exists so the product can answer:

> after review, what exactly would this overwrite destroy, what rescue actually exists, and what stronger no-loss sentence must remain forbidden?

## Core decision

AnonSync must expose one first-class **Maintenance overwrite review** page whenever a destructive heal is still plausible after initial planning or when any user is about to approve overwrite, source-authoritative restore, or local-divergence surrender.

The review exists to answer five things in one place:

1. which loss classes are confirmed
2. which salvage lanes are truly viable versus merely imagined
3. whether archive-bearing locality is sufficient and timely
4. what loss becomes knowingly waived on approval
5. what sentence remains safe afterward

## Fixed page order

1. **Review verdict**
2. **Confirmed loss classes**
3. **Archive-bearing and salvage viability**
4. **Waiver review**
5. **Actions and receipts**

### 1) Review verdict

Show:

- `maintenance_overwrite_review_page_id`
- scope
- governing maintenance or narrow-posture reference
- destructive action under review
- review verdict (`destructive-and-salvageable`, `destructive-with-partial-salvage`, `destructive-with-no-credible-salvage`, `salvage-first-required`, `not-yet-provable`)
- strongest honest summary
- stronger unsupported summary

### 2) Confirmed loss classes

This section is mandatory.
Show row groups for:

- edits to existing files
- local deletes
- local renames / path moves
- local additions
- archive copies already present
- residue that survives only outside same-line history

Each row must show:

- current holder
- likely post-heal fate
- whether the work remains canonical, derivative, residue, or abandoned
- strongest safe sentence

The operator must be able to answer:

> what exactly dies, survives, or strands if I approve this?

### 3) Archive-bearing and salvage viability

Show:

- local archive availability
- remote archive dependency
- trash / recycle dependence
- evidence-export fallback
- successor-branch fallback
- expiry pressure and peer availability pressure

The operator must be able to answer:

> is rescue actually viable, or merely theoretically possible?

### 4) Waiver review

Show:

- consciously waived losses
- unattempted salvage steps
- reasons some rescue lanes are blocked
- stronger rejected sentence
- minimum extra proof needed to narrow the loss sentence

Examples:

- safe: `edited contents on this read-only seat will be replaced by the remote winner; only exported residue preserves the local variant`
- forbidden: `overwrite will put everything back without loss`

### 5) Actions and receipts

Actions may include:

- `Approve destructive heal`
- `Salvage first`
- `Promote successor instead`
- `Open overwrite ledger`
- `Cancel`

Receipts must record confirmed loss classes, salvage viability, knowingly waived loss, and post-heal claim ceiling.

## Public object

### Maintenance overwrite review page

Fields:

- `maintenance_overwrite_review_page_id`
- `scope_ref`
- `maintenance_or_narrow_posture_ref`
- `candidate_action`
- `review_verdict`
- `loss_rows[]`
- `salvage_viability_rows[]`
- `waiver_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. loss class
2. post-heal fate
3. best viable salvage
4. strongest safe sentence
5. next action

Example:

```text
local rename on read-only seat     old name will be re-downloaded and local rename will not become shared history     successor export still viable     same-line rename survival is false unless promoted separately     Salvage first
```

## Non-goals

This page does **not** prove that destructive healing is the best strategy overall.
It proves only the reviewed **loss classes, salvage viability, and waiver boundary** for the proposed action.
