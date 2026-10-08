# Maintenance mutation receipt page — surviving work, overwritten work, and reopen boundary interface spec

## Purpose

A mutation review is not complete until the product leaves behind one durable object saying what local work, if any, survived the maintenance window honestly.
This page exists to prevent later folklore such as:

> we edited there during the hold, but it was probably fine.

## Core decision

AnonSync must emit one first-class **Maintenance mutation receipt** whenever local work under a maintenance contract is acknowledged, repaired, exported, overwritten, or explicitly waived.

The receipt exists to answer five things in one place:

1. what local work was attempted
2. what of that work survived versus was overwritten or stranded
3. what follow-up was completed versus still open
4. what sentence is still safe about work performed during the hold
5. what event reopens or supersedes this receipt

## Fixed page order

1. **Receipt verdict**
2. **Work survival summary**
3. **Open obligations and waived risks**
4. **Safe language and forbidden stronger sentence**
5. **Reopen / successor boundary**

### 1) Receipt verdict

Show:

- `maintenance_mutation_receipt_page_id`
- scope
- governing maintenance contract reference
- receipt state (`no-work`, `survived`, `local-only`, `repaired`, `overwritten`, `mixed`, `superseded`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what is the durable verdict on local work during the hold?

### 2) Work survival summary

Show:

- requested or observed local work classes
- surviving work set
- overwritten work set
- exported-elsewhere work set
- paths still suspended or awaiting repair
- whether the maintenance claim ceiling was narrowed by this work

This is the stable answer to:

> what actually made it through this window, and under what continuity story?

### 3) Open obligations and waived risks

Show:

- remaining repair obligations
- remaining export or branch-promotion obligations
- consciously waived overwrite risks
- proofs already gathered to close earlier concerns
- whether a stronger future sentence is blocked until closure

### 4) Safe language and forbidden stronger sentence

Show:

- strongest safe sentence
- stronger rejected sentence
- basis for rejection
- minimal next proof needed to upgrade the sentence

Examples:

- safe: `local inspection notes were exported; no shared continuity is claimed here`
- forbidden: `maintenance edits were safely preserved in place`
- safe: `two local edits were overwritten by the reviewed heal plan`
- forbidden: `no local work was lost`

### 5) Reopen / successor boundary

Show:

- invalidators
- successor receipts or repair cases
- future event that reopens the receipt
- direct links to maintenance contract, repair, export, or evidence successors when relevant

## Public object

### Maintenance mutation receipt page

Fields:

- `maintenance_mutation_receipt_page_id`
- `scope_ref`
- `maintenance_contract_ref`
- `receipt_state`
- `work_attempt_rows[]`
- `survival_rows[]`
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
4. strongest surviving risk
5. reopen boundary

Example:

```text
Read-only maintenance seat     mixed     local scratch survived only in exported branch     in-place continuity claim remains false     reopens if exported branch is promoted back
```

## Non-goals

This receipt does **not** prove that the maintenance contract itself was globally matched.
It proves only the local **mutation outcome, safe sentence, and reopen boundary**.
