# Maintenance overwrite receipt page — overwritten scope, preserved remnants, and claim-ceiling interface spec

## Purpose

A destructive-heal path is not complete until the product leaves behind one durable object saying what was overwritten, what was preserved elsewhere, and what sentence still remains safe.
This page exists to prevent later folklore such as:

> we healed it by overwrite and nothing important was lost.

## Core decision

AnonSync must emit one first-class **Maintenance overwrite receipt** whenever destructive healing is executed, when a waiver closes without salvage, or when rescued residue survives only outside the restored line.

The receipt exists to answer five things in one place:

1. what work was in scope for destructive healing
2. what was overwritten in place
3. what survived in archive, trash, evidence export, or successor branch
4. what loss was knowingly waived
5. what event reopens or supersedes this receipt

## Fixed page order

1. **Receipt verdict**
2. **Overwrite outcome summary**
3. **Preserved remnants and waived losses**
4. **Safe language and forbidden stronger sentence**
5. **Reopen / supersession boundary**

### 1) Receipt verdict

Show:

- `maintenance_overwrite_receipt_page_id`
- scope
- governing maintenance or narrow-posture reference
- receipt state (`destructive-heal-complete`, `destructive-heal-with-salvage`, `salvage-only-no-heal`, `waived-loss-without-salvage`, `mixed`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what is the durable truth about this destructive-heal event?

### 2) Overwrite outcome summary

Show:

- work overwritten in place
- work reverted to remote / source winner
- work restored from remote after delete
- work left local-only and non-shared
- work that never rejoined but survived elsewhere

This is the stable answer to:

> what exactly changed, and what did not survive same-line healing?

### 3) Preserved remnants and waived losses

Show:

- archive-held remnants
- trash / recycle dependence
- evidence-export remnants
- successor-branch remnants
- consciously waived loss rows
- whether a stronger future sentence is blocked until more recovery completes

### 4) Safe language and forbidden stronger sentence

Show:

- strongest safe sentence
- stronger rejected sentence
- basis for rejection
- minimal next proof needed to upgrade the sentence

Examples:

- safe: `source-authoritative healing reverted three edited files; the local variants survive only in evidence export`
- forbidden: `overwrite fixed everything without any real loss`
- safe: `one locally added file remains preserved only as residue and was not restored into the shared line`
- forbidden: `all local maintenance work was recovered`

### 5) Reopen / supersession boundary

Show:

- invalidators
- later archive restore or successor promotion that could supersede the receipt
- retention-expiry boundary
- direct links to salvage ledger, rejoin receipt, successor receipt, or abandonment receipt when relevant

## Public object

### Maintenance overwrite receipt page

Fields:

- `maintenance_overwrite_receipt_page_id`
- `scope_ref`
- `maintenance_or_narrow_posture_ref`
- `receipt_state`
- `overwrite_rows[]`
- `preserved_remnant_rows[]`
- `waived_loss_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `reopen_rows[]`
- `superseding_receipt_ref`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. receipt state
3. strongest safe sentence
4. strongest remaining risk
5. reopen boundary

Example:

```text
read-only repair seat     destructive-heal-with-salvage     local edits were overwritten and now survive only in archive export     no no-loss claim is justified yet     reopens if rescued residue is later promoted or expires
```

## Non-goals

This receipt does **not** prove that destructive healing was the only possible strategy.
It proves only the final **overwrite scope, preserved remnants, waived loss, and claim ceiling**.
