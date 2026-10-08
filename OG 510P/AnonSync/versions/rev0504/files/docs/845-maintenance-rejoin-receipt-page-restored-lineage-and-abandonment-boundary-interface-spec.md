# Maintenance rejoin receipt page — restored lineage and abandonment boundary interface spec

## Purpose

A rejoin effort is not complete until the product leaves behind one durable object saying what maintenance-era work actually made it back into the shared line and what did not.
This page exists to prevent later folklore such as:

> we fixed it after the hold, so all of those local edits are part of the shared history now.

## Core decision

AnonSync must emit one first-class **Maintenance rejoin receipt** whenever maintenance-era local work is restored in place, promoted into a successor, preserved without rejoin, overwritten, or explicitly abandoned.

The receipt exists to answer five things in one place:

1. what work was under restoration review
2. what of that work rejoined the original shared line versus moved into a successor or stayed local
3. what work was overwritten or abandoned knowingly
4. what sentence is still safe about restoration
5. what event reopens or supersedes this receipt

## Fixed page order

1. **Receipt verdict**
2. **Restoration outcome summary**
3. **Open obligations and waived losses**
4. **Safe language and forbidden stronger sentence**
5. **Reopen / successor boundary**

### 1) Receipt verdict

Show:

- `maintenance_rejoin_receipt_page_id`
- scope
- governing maintenance or narrow-posture reference
- receipt state (`restored-in-place`, `restored-after-widening`, `promoted-successor`, `preserved-only`, `abandoned`, `overwritten`, `mixed`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what is the durable verdict on bringing this maintenance-era work back?

### 2) Restoration outcome summary

Show:

- work restored into the original shared line
- work promoted into successor branch or artifact
- work preserved only as local or evidentiary residue
- work overwritten or abandoned
- whether the original maintenance claim ceiling remains narrowed by any unresolved residue

This is the stable answer to:

> what actually became shared again, and what definitely did not?

### 3) Open obligations and waived losses

Show:

- remaining compare or promotion obligations
- remaining export or branch-promotion duties
- consciously accepted overwrite or abandonment decisions
- proofs already gathered to close earlier restoration concerns
- whether a stronger future sentence is blocked until more closure

### 4) Safe language and forbidden stronger sentence

Show:

- strongest safe sentence
- stronger rejected sentence
- basis for rejection
- minimal next proof needed to upgrade the sentence

Examples:

- safe: `two held edits were restored only through a reviewed successor branch; same-line continuity is not claimed`
- forbidden: `all maintenance edits were put back exactly where they belonged`
- safe: `source-authoritative restore replaced local maintenance edits; those edits remain preserved only in evidence export`
- forbidden: `no maintenance work was lost`

### 5) Reopen / successor boundary

Show:

- invalidators
- successor receipts or promoted branches
- future event that reopens the receipt
- direct links to maintenance contract, compare, promotion, export, or abandonment receipts when relevant

## Public object

### Maintenance rejoin receipt page

Fields:

- `maintenance_rejoin_receipt_page_id`
- `scope_ref`
- `maintenance_or_narrow_posture_ref`
- `receipt_state`
- `restoration_rows[]`
- `successor_rows[]`
- `open_obligation_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `reopen_rows[]`
- `successor_ref`
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
Backup-like evidence seat     promoted-successor     local work survived only via reviewed successor export     in-place shared-line restoration remains false     reopens if successor is later merged back
```

## Non-goals

This receipt does **not** prove that the original maintenance posture was wise.
It proves only the final **restoration outcome, safe sentence, and successor or abandonment boundary**.
