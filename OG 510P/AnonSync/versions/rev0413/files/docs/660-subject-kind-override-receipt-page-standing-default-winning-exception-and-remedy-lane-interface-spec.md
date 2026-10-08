# Subject-kind override receipt page — standing default, winning exception, and remedy lane interface spec

## Purpose

This page answers one ordinary question later:

> what seat default was in scope, what subject-kind exception actually won, and what remedy lane remains if a later operator wants the default posture restored?

The page exists because later operators should not have to reconstruct override truth from mode settings, backup docs, and remembered reconnect ritual.

## Core decision

Every meaningful subject-kind override event must emit one durable **Subject-kind override receipt**.
That includes:

- enabling a storage-only/backup subject
- linked arrival that bypasses the standing seat default
- repair after surprise connected appearance
- reconnect performed only to restore reviewed posture
- promotion of a subject-local exception into broader policy

## Fixed page order

1. event summary
2. standing default in scope
3. winning exception
4. actual posture and claim ceiling
5. remedy lane
6. reopening conditions

### 1) Event summary

Show:

- subject
- seat
- event type
- time
- operator intent in plain language

### 2) Standing default in scope

Show:

- seat's standing arrival default at the time
- what that default would ordinarily have produced
- whether the default remained unchanged for other subjects

### 3) Winning exception

Show:

- subject kind
- winning exception basis (`subject-kind-storage-only`, `capture-ingest-contract`, `policy-exception`, `manual-repair`, `unknown`)
- whether the result was expected, surprising, or repaired after surprise
- any rejected alternative that materially explains the outcome

### 4) Actual posture and claim ceiling

Show:

- visible posture after the event
- actual writeback/materialization contract after the event
- strongest safe sentence now
- stronger unsupported sentence now

### 5) Remedy lane

Show:

- least-strong remedy if the operator later wants the standing default restored
- whether that remedy is same-subject or replacement-shaped
- whether disconnect/reconnect/manual bind/manual review remain attached

### 6) Reopening conditions

Show:

- what must happen to remove the exception entirely
- whether the current system can ever express the preferred posture natively
- whether this subject-local exception could accidentally teach broader policy later

## Public object

### `subject_kind_override_receipt`

Fields:

- `subject_kind_override_receipt_id`
- `subject_ref`
- `seat_ref`
- `event_type`
- `operator_intent`
- `standing_default`
- `subject_kind`
- `winning_exception_basis`
- `visible_posture`
- `actual_contract`
- `claim_ceiling`
- `remedy_lane[]`
- `reopen_conditions[]`
- `issued_at`

## Honest outputs

The receipt may conclude:

- `Standing default: disconnected. Winning exception: storage-only backup subject required materialized arrival on this seat.`
- `Visible posture after event: connected. Strongest safe sentence: this seat holds a storage-only sink copy without upstream writeback authority.`
- `Least-strong remedy: reviewed disconnect/reconnect to restore the intended seat posture for this subject.`

It may not reduce the event to `backup enabled`, `mode mismatch fixed`, or `connected`.
