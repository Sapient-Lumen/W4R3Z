# Maintenance overwrite ledger page — surrendered work, salvage attempts, and loss-history interface spec

## Purpose

One destructive-heal review is not enough once salvage steps, retries, approvals, and later regrets accumulate.
This page exists so the product can answer:

> what did we risk losing, what did we try to rescue, what was actually overwritten, and what remains recoverable now?

## Core decision

AnonSync must expose one first-class **Maintenance overwrite ledger** page whenever destructive healing has been reviewed more than once, any salvage step has begun, or any part of the at-risk work has already been overwritten, exported, archived, or waived.

The ledger exists to answer five things in one place:

1. which work families entered the destructive-heal zone
2. which salvage attempts ran in what order
3. what was rescued, overwritten, stranded, or waived
4. which rescue lanes are still open versus spent
5. what receipt is current for each surrendered work family

## Fixed page order

1. **Ledger summary**
2. **Attempt timeline**
3. **Salvage and surrender map**
4. **Remaining rescue gaps**
5. **Actions and receipts**

### 1) Ledger summary

Show:

- `maintenance_overwrite_ledger_page_id`
- scope
- governing maintenance contract or posture basis
- at-risk work count
- rescued work count
- overwritten work count
- current dominant state (`salvage-pending`, `partially-rescued`, `destructive-heal-approved`, `destructive-heal-complete`, `mixed`, `unknown`)
- strongest honest summary

### 2) Attempt timeline

This section is mandatory.
Show ordered attempt rows for at least:

- destructive action proposed
- overwrite plan opened
- salvage review completed
- export attempted
- archive restore attempted
- successor promotion attempted
- destructive heal approved
- destructive heal executed
- receipt emitted

Each row must show:

- attempt kind
- affected work family
- resulting state
- whether the attempt narrowed loss, preserved side survival, or simply recorded waiver
- linked receipt or successor object when available

### 3) Salvage and surrender map

Show:

- work rescued into local archive / trash / export / successor branch
- work overwritten in place
- work still pending destruction
- work already unsalvageable here
- work whose only remaining proof lives elsewhere

The operator must be able to answer:

> which bytes were saved, which were surrendered, and where surviving remnants actually live?

### 4) Remaining rescue gaps

Show:

- expiring archive dependencies
- unreachable peer / holder dependencies
- missing export proof
- unreviewed waiver rows
- strongest safe sentence now
- stronger sentence still forbidden

### 5) Actions and receipts

Actions may include:

- `Retry salvage`
- `Approve remaining destructive heal`
- `Close waived loss`
- `Open current overwrite receipt`
- `Promote successor from rescued residue`

Receipts must bind work-family history, executed destructive steps, surviving rescue lanes, and claim ceiling.

## Public object

### Maintenance overwrite ledger page

Fields:

- `maintenance_overwrite_ledger_page_id`
- `scope_ref`
- `maintenance_contract_or_posture_ref`
- `attempt_rows[]`
- `salvage_rows[]`
- `loss_rows[]`
- `remaining_gap_rows[]`
- `current_state`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `current_receipt_ref`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. affected work family
2. latest attempt
3. current loss / rescue state
4. strongest remaining gap
5. next action

Example:

```text
maintenance-era edited file set     export completed before overwrite     local variant preserved only as evidence export     no same-line survival claim remains     Open current overwrite receipt
```

## Non-goals

This ledger does **not** prove that every rescued byte is easy to reintroduce later.
It proves only the ordered **salvage history, surrender history, and surviving rescue lanes**.
