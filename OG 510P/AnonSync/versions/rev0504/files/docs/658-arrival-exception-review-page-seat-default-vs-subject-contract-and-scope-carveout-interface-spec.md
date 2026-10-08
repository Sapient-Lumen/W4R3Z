# Arrival-exception review page — seat default versus subject contract and scope carveout interface spec

## Purpose

This review answers one ordinary question before commit or before accepting a surprising arrival:

> is this subject about to inherit the seat's normal arrival default, or am I approving a one-subject exception with a stronger arrival, role, or writeback contract?

The review exists because an operator should never discover only afterward that one subject kind bypassed the standing default.

## Core decision

Whenever a subject may arrive under a contract that differs from the seat's standing default, the product must open one first-class **Arrival-exception review**.

The review owns:

- seat default now
- subject kind and intended contract
- exact carve-out scope
- actual role/writeback/materialization outcome
- strongest safe sentence afterward

## Fixed page order

1. request summary
2. default-versus-exception compare
3. carveout scope matrix
4. connected-appearance truth card
5. commit review
6. receipt preview

### 1) Request summary

Show:

- subject
- seat
- trigger (`new-arrival`, `backup-enable`, `linked-subject-publication`, `repair-after-surprise`, `other`)
- standing seat default
- requested or inferred subject contract

### 2) Default-versus-exception compare

Columns:

- `seat default would do`
- `subject exception will do`

Rows:

- arrival visibility
- materialization mode
- writeback authority
- upstream publication power
- destination path/bind behavior
- disconnect/reconnect implications

The operator must be able to answer: **what exactly is being bypassed?**

### 3) Carveout scope matrix

This matrix must say whether the exception applies to:

- this subject only
- this subject family
- this source seat and subject family
- a broader standing policy if promoted deliberately

Each row must show:

- `scope`
- `who else is affected`
- `does seat default remain unchanged elsewhere?`
- `can this become precedent later?`

The product must not let one subject-kind exception silently mutate the broader seat default.

### 4) Connected-appearance truth card

This card publishes:

- whether the resulting row/badge/path will look `connected`, `active`, or `present`
- what collaborative powers are actually absent
- whether the subject is storage-only, backup-only, or otherwise non-collaborative
- whether later operators might over-read the visual posture

### 5) Commit review

This section must state:

- standing seat default
- chosen exception outcome
- actual arrival posture afterward
- strongest safe sentence afterward
- stronger unsupported sentence afterward

### 6) Receipt preview

The receipt must preserve:

- standing default in scope
- exception basis
- subject-only versus broader scope
- remedy lane if the operator later wants to restore the default posture
- claim ceiling

## Public object

### `arrival_exception_review`

Fields:

- `arrival_exception_review_id`
- `subject_ref`
- `seat_ref`
- `trigger`
- `standing_default`
- `subject_contract`
- `scope_rows[]`
- `chosen_outcome`
- `remedy_options[]`
- `claim_ceiling`
- `generated_at`

## Review rules

### Rule 1 — `special subject` is not enough

The review must say what the exception changes in actual posture terms, not merely name the feature.

### Rule 2 — subject-local carveouts must stay local unless promoted deliberately

One backup or storage-only exception must not silently rewrite general seat defaults for unrelated arrivals.

### Rule 3 — visual connectedness must be reviewed as a risk

If the result will look like ordinary collaboration while actually being narrower, the review must publish that over-read risk.

## Honest outputs

The review may conclude:

- `Seat default remains disconnected for ordinary linked arrivals. This subject will carve out a storage-only materialized arrival.`
- `Result will look connected in the seat's subject list, but destination edits will not publish upstream.`
- `This exception is subject-local only. Restoring default posture later requires reviewed disconnect/reconnect, not broader mode mutation.`

It may not flatten those outcomes into `OK`, `Connect now`, or `backup enabled` alone.
