# Control-absence receipt page — intent, missing basis, substituted action, and claim ceiling interface spec

## Purpose

This page answers one ordinary question after the fact:

> I asked for one action, the product could not provide it here, so what exactly was missing, what did I do instead, and what is the strongest honest sentence now?

The page exists because later operators should not have to infer a missing-control episode from UI screenshots, memory, or edition folklore.

## Core decision

Every substitution or blocked-control episode must emit one durable **Control-absence receipt**.
That receipt is the canonical witness for:

- original intent
- exact unavailable control
- basis for unavailability
- substitute committed or declined
- claim ceiling after the episode

## Fixed page order

1. request summary
2. missing-control proof
3. substitute outcome
4. claim ceiling
5. reopening conditions

### 1) Request summary

Show:

- subject
- seat / surface
- requested action
- requested outcome in plain language
- time of request

### 2) Missing-control proof

Show:

- exact control that was absent
- proof basis (`edition`, `posture`, `surface`, `temporary blocker`, `unknown`)
- whether the control exists elsewhere in the product
- whether the absence was acknowledged by the operator

### 3) Substitute outcome

Show:

- whether a substitute was committed, deferred, or declined
- actual action committed
- strongest harm delta versus the request
- local / remote byte outcome
- scope of effect

### 4) Claim ceiling

Show:

- strongest safe sentence now
- stronger unsupported sentences
- residue or follow-up work that still blocks the original requested claim

### 5) Reopening conditions

Show:

- what would make the original requested control available later
- whether a different surface, seat posture, or capability change is enough
- whether the prior substitute changed that possibility

## Public object

### `control_absence_receipt`

Fields:

- `control_absence_receipt_id`
- `subject_ref`
- `seat_ref`
- `requested_action`
- `requested_outcome_sentence`
- `missing_control`
- `absence_basis`
- `substitute_actions_considered[]`
- `committed_action`
- `harm_delta`
- `claim_ceiling`
- `reopen_conditions[]`
- `issued_at`

## Honest outputs

The receipt may conclude:

- `Requested: disconnect this seat only. Missing control basis: current capability tier on this surface. Committed instead: remove. Strongest safe sentence: syncing stopped here with broader severance scope than originally requested.`
- `Requested action was unavailable because this subject posture has no path-preserving severance rung.`

It may not reduce the event to `feature unavailable` or `removed successfully`.
