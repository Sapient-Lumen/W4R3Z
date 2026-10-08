# Seat-role receipt page — requested posture, winning basis, and claim ceiling interface spec

## Purpose

This page answers one ordinary question later:

> what role was requested for this seat, what basis actually won, and what is the strongest honest sentence now?

The page exists because later operators should not have to reconstruct seat authority from linked-family defaults, grant history, workaround keys, and remembered bind ritual.

## Core decision

Every meaningful seat-role event must emit one durable **Seat-role receipt**.
That includes:

- linked-family role adoption
- explicit rights changes affecting this seat
- self-narrowing review commits
- workaround/detour role compilation
- repairs that change role basis or claim ceiling

## Fixed page order

1. event summary
2. requested posture
3. winning basis
4. continuity and detour consequences
5. claim ceiling
6. reopening conditions

### 1) Event summary

Show:

- subject
- seat
- event type
- time
- operator intent in plain language

### 2) Requested posture

Show:

- requested role if any
- prior role
- reviewed alternatives shown
- whether the request was native, compiled, narrowed, widened, or blocked

### 3) Winning basis

Show:

- current role
- winning basis (`linked-identity`, `explicit-grant`, `derived-ceiling`, `native-self-narrowing`, `detour-artifact`, `unknown`)
- any rejected or unavailable basis that materially explains the outcome

### 4) Continuity and detour consequences

Show:

- whether subject lineage stayed the same
- whether a different artifact family or key path was used
- whether manual bind / disconnect / reconnect / separate path consequences occurred
- whether later repairs are likely to be native or workaround-shaped

### 5) Claim ceiling

Show:

- strongest safe sentence now
- stronger unsupported sentence now
- what proof would be needed to regain the stronger sentence

### 6) Reopening conditions

Show:

- what would be required to move this seat to a cleaner native role later
- whether the current system can ever provide that without subject substitution
- whether receipts for bind/reconnect or non-authority continuity must stay attached

## Public object

### `seat_role_receipt`

Fields:

- `seat_role_receipt_id`
- `subject_ref`
- `seat_ref`
- `event_type`
- `operator_intent`
- `requested_role`
- `prior_role`
- `current_role`
- `winning_basis`
- `continuity_consequences[]`
- `claim_ceiling`
- `reopen_conditions[]`
- `issued_at`

## Honest outputs

The receipt may conclude:

- `Requested posture: observer on a linked-family seat. Winning basis: native self-narrowing. Strongest safe sentence: this seat is intentionally narrower within the same subject lineage.`
- `Requested posture: receive-only on a linked-family seat. Native self-narrowing unavailable in the interoperating system; current result uses a detour artifact with manual bind.`
- `Current seat remains Owner by linked identity. Stronger unsupported sentence rejected: this seat was narrowed by explicit same-subject role mutation.`

It may not reduce the event to `permissions changed`, `linked device added`, or `read only connected`.
