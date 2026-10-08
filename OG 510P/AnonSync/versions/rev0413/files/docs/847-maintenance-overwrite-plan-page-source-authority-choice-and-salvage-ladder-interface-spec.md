# Maintenance overwrite plan page — source-authority choice and salvage-ladder interface spec

## Purpose

The archive already has maintenance mutation, rejoin, and successor pages.
What it still lacked was one ordinary page for the next question:

> if source-authoritative healing is on the table, what exactly am I about to surrender and what can I still rescue first?

This page exists so a user does not mistake `there is an overwrite option` for `the loss envelope is understood`.

## Core decision

AnonSync must expose one first-class **Maintenance overwrite plan** page whenever a maintenance-era, read-only, backup-like, encrypted-custody, or other narrow-seat incident may be resolved by source-authoritative overwrite or destructive healing.

The page exists to answer five things in one place:

1. which local work classes are at risk
2. what exact destructive action is being considered
3. what salvage lanes still exist before the action
4. which losses become knowingly waived if the action proceeds
5. what sentence is honest before the overwrite begins

## Fixed page order

1. **Overwrite candidate verdict**
2. **Loss-class matrix**
3. **Salvage ladder**
4. **Waiver boundary**
5. **Actions and receipts**

### 1) Overwrite candidate verdict

Show:

- `maintenance_overwrite_plan_page_id`
- scope (`seat`, `subject`, `path slice`, `maintenance window`, or `residue family`)
- governing maintenance or narrow-posture reference
- candidate destructive action (`restore-source-authority`, `overwrite-changed-files`, `discard-local-divergence`, `encrypted-seat-reset`, `unknown`)
- current verdict (`preview-required`, `safe-to-review`, `blocked-until-salvage`, `blocked-until-more-evidence`, `not-destructive-after-all`)
- strongest honest summary
- stronger unsupported summary

The operator must be able to answer:

> what destructive action is actually under consideration here?

### 2) Loss-class matrix

This section is mandatory.
Show rows for at least:

- edited existing files
- locally deleted files
- locally renamed files
- locally added files
- archive-bearing prior versions
- non-bearing local-only residue
- encrypted or backup-like preserved material

Each row must show one state:

- `will be reverted`
- `will be restored over`
- `will remain local-only`
- `salvageable first`
- `already unsalvageable here`
- `unknown until witness expands`

The page must answer:

> which exact kinds of local work are at risk, and how?

### 3) Salvage ladder

Show ordered rescue rungs such as:

- local trash / recycle bin
- local `.sync/Archive`
- remote peer archive
- evidence export
- successor branch or candidate compare
- no remaining easy salvage

Each rung must state:

- locality / holder
- retention or expiry pressure
- proof grade
- whether the rung preserves same-line restoration or only side survival

The operator must be able to answer:

> what can still be rescued before I accept overwrite?

### 4) Waiver boundary

Show, for the candidate action:

- loss that becomes knowingly accepted
- rescue steps still unattempted
- settings or posture that narrowed rescue (`archive off`, short retention, encrypted seat, read-only hardwire, unknown peer availability)
- strongest safe sentence and stronger forbidden sentence

The operator must be able to answer:

> what exactly am I waiving if I continue now?

### 5) Actions and receipts

Actions may include:

- `Open overwrite review`
- `Open salvage ledger`
- `Export at-risk residue`
- `Promote successor instead`
- `Restore from archive first`
- `Accept destructive heal`
- `Cancel`

Receipts must bind candidate loss classes, salvage ladder, waiver boundary, and strongest safe sentence.

## Public object

### Maintenance overwrite plan page

Fields:

- `maintenance_overwrite_plan_page_id`
- `scope_ref`
- `maintenance_or_narrow_posture_ref`
- `candidate_action`
- `loss_class_rows[]`
- `salvage_rows[]`
- `waiver_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. loss class
2. candidate destructive effect
3. best remaining salvage rung
4. strongest safe sentence
5. next action

Example:

```text
edited existing file     will be reverted to remote winner     local archive still bears prior remote-induced version     local edit is at risk unless exported first     Open overwrite review
```

## Non-goals

This page does **not** execute destructive healing.
It proves only the reviewed **candidate surrender scope, salvage ladder, and waiver boundary**.
