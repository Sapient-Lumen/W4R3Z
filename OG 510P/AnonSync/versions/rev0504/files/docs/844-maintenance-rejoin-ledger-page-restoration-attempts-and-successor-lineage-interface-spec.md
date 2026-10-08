# Maintenance rejoin ledger page — restoration attempts and successor-lineage interface spec

## Purpose

A single plan or review is not enough once local work accumulates, retries happen, and multiple restoration paths are attempted.
This page exists so the product can answer:

> what has already been tried to bring this maintenance-era work back, what happened, and which branch of lineage is now authoritative?

## Core decision

AnonSync must expose one first-class **Maintenance rejoin ledger** page whenever local work from a maintenance or narrow-seat posture has more than one restoration-relevant event or when any promotion, widening, compare, overwrite, or preservation-only decision has already occurred.

The ledger exists to answer five things in one place:

1. what local work sets are still pending versus already settled
2. which restoration attempts have been made in order
3. which attempts created successor artifacts or branches
4. which work is now preserved-only, rejoined, overwritten, or abandoned
5. what receipt is current for each residue family

## Fixed page order

1. **Ledger summary**
2. **Attempt timeline**
3. **Lineage and successor map**
4. **Outstanding gaps and blocked paths**
5. **Actions and receipts**

### 1) Ledger summary

Show:

- `maintenance_rejoin_ledger_page_id`
- scope
- governing maintenance contract or posture basis
- pending work count
- settled work count
- current dominant lineage state (`same-line restored`, `successor promoted`, `preserved-only`, `mixed`, `abandoned`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what is the current overall restoration state of this maintenance-era work?

### 2) Attempt timeline

This section is mandatory.
Show ordered attempt rows for at least:

- local work observed
- rejoin plan opened
- rights widened or refused
- compare opened
- successor promoted
- source-authoritative restore chosen
- overwrite / abandonment accepted
- receipt emitted

Each row must show:

- attempt kind
- affected work family
- resulting state
- whether the attempt narrowed, preserved, or ended rejoin possibility
- linked receipt or successor object when available

### 3) Lineage and successor map

Show:

- original maintenance-era residue families
- work restored into the original shared line
- work diverted into successor branch or artifact
- work kept as local-only evidence
- work overwritten or abandoned
- whether multiple candidate lines remain unresolved

The operator must be able to answer:

> which line is now canonical, and which lines merely survive as evidence or successors?

### 4) Outstanding gaps and blocked paths

Show:

- missing compare proof
- missing rights or posture changes
- missing counterpart/source availability
- blocked encryption / selective-sync / local-disconnect conditions
- strongest safe sentence now
- stronger sentence still forbidden

The page must answer:

> what is still preventing final restoration truth?

### 5) Actions and receipts

Actions may include:

- `Retry reviewed restoration`
- `Request authority change`
- `Promote successor`
- `Close as preserve-only`
- `Close as abandoned`
- `Open current receipt`

Receipts must bind attempt history, current lineage verdict, unresolved branches, and successor references.

## Public object

### Maintenance rejoin ledger page

Fields:

- `maintenance_rejoin_ledger_page_id`
- `scope_ref`
- `maintenance_contract_or_posture_ref`
- `attempt_rows[]`
- `lineage_rows[]`
- `blocked_path_rows[]`
- `current_lineage_verdict`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `successor_refs[]`
- `current_receipt_ref`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. affected work family
2. latest attempt
3. current lineage verdict
4. strongest unresolved barrier
5. next action

Example:

```text
Read-only maintenance edits     compare opened     successor promoted candidate pending final receipt     remote source still stronger until review closes     Open current receipt
```

## Non-goals

This ledger does **not** prove that any one restoration path was morally correct.
It proves only the ordered **attempt history, current lineage state, and unresolved restoration gaps**.
