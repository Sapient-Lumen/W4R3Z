# Maintenance contract receipt page — achieved semantics, safe sentence, and reopen boundary interface spec

## Purpose

A maintenance plan is not complete until the product leaves behind one durable object saying what was actually achieved.
This page exists to prevent future folklore such as:

> we paused it earlier, so it must still be safe.

## Core decision

AnonSync must emit one first-class **Maintenance contract receipt** whenever a maintenance hold is entered, materially changed, or exited.

The receipt exists to answer five things in one place:

1. what maintenance goal was requested
2. what hold class actually took effect
3. what semantics were achieved versus only requested
4. what sentence is still safe afterward
5. what event would reopen or supersede the receipt

## Fixed page order

1. **Receipt verdict**
2. **Achieved maintenance contract**
3. **Residuals and uncovered risk**
4. **Safe language and forbidden stronger sentence**
5. **Reopen / successor boundary**

### 1) Receipt verdict

Show:

- `maintenance_contract_receipt_page_id`
- scope
- requested goal
- achieved hold class
- receipt state (`entered`, `matched`, `local-only`, `partial`, `superseded`, `failed`)
- strongest honest summary

The operator must be able to answer:

> what maintenance contract do we actually have now?

### 2) Achieved maintenance contract

Show:

- actual entry trigger and entry time
- matched counterpart set
- achieved motion budget
- achieved claim ceiling
- successor link if this replaced an earlier quiet or maintenance receipt

This is the stable answer to:

> what was actually achieved, not merely requested?

### 3) Residuals and uncovered risk

Show:

- allowed residuals still in force
- uncovered seats or scopes
- in-flight debt carried into the receipt
- backlog consequences expected after exit
- destructive or claim-weakening risks still open

This section prevents the receipt from overclaiming.

### 4) Safe language and forbidden stronger sentence

Show:

- strongest safe sentence
- stronger rejected sentence
- basis for the rejection
- minimal next proof needed to upgrade the sentence

The receipt must make it ordinary to answer:

> what can I safely tell another operator or reviewer right now?

### 5) Reopen / successor boundary

Show:

- invalidators
- expected expiry or exit condition
- next likely successor receipt
- evidence that would reopen the contract early
- direct links to quiet-break, residual-classification, or backlog-release successors when relevant

## Public object

### Maintenance contract receipt page

Fields:

- `maintenance_contract_receipt_page_id`
- `scope_ref`
- `requested_goal`
- `requested_hold_class`
- `achieved_hold_class`
- `receipt_state`
- `entry_time`
- `matched_counterpart_refs[]`
- `achieved_motion_budget_rows[]`
- `residual_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `reopen_rows[]`
- `successor_receipt_ref`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. achieved hold class
3. receipt state
4. strongest safe sentence
5. reopen boundary

Example:

```text
Project Alpha     delete-freeze     local-only     this seat will not propagate deletes during repair     reopens if uncovered peer resumes writeback
```

## Non-goals

This receipt does **not** guarantee that maintenance was costless or globally matched.
It proves only the achieved **maintenance contract, safe sentence, and reopen boundary**.
