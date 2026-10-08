# Residual classification receipt page — event verdict, surviving claim, and reopen boundary interface spec

## Purpose

A quiet event review is not complete until a future operator can see what was decided.
This page is the durable receipt that answers:

> when the event arrived, what verdict did we reach, and what quiet claim survived afterward?

## Core decision

Every completed residual allowance review must emit a **residual classification receipt**.
It preserves both the event verdict and the claim-survival verdict.

## Fixed review order

1. **Challenged quiet receipt**
2. **Observed event**
3. **Final classification**
4. **Surviving claim**
5. **Language boundary**
6. **Reopen boundary**

## 1) Challenged quiet receipt

Show:

- prior quiet receipt id
- subject and covered scope
- issued stillness class
- issue time

## 2) Observed event

Show:

- event id
- event time
- event class
- originating seat
- evidence basis

## 3) Final classification

Allowed values:

- `allowed-residual`
- `outside-prior-claim`
- `quiet-claim-narrowed`
- `quiet-violation`
- `insufficient-evidence`

Also preserve:

- why stronger verdicts lost
- review id
- reviewer / engine basis

## 4) Surviving claim

Show one of:

- `unchanged`
- `narrowed`
- `superseded`
- `not-earned-for-this-scope`
- `unknown`

If narrowed or superseded, link the successor receipt or required next review.

## 5) Language boundary

The receipt must preserve:

- strongest allowed sentence
- stronger forbidden sentence

This is mandatory.

## 6) Reopen boundary

State what later condition would reopen the classification, such as:

- another event of a forbidden class arrives
- scope evidence changes
- better proof reclassifies the originating seat
- a successor receipt supersedes this one

## Example projection

```text
Residual classification receipt — rcr_01P

Challenged quiet receipt
  receipt ............... qcr_01K
  scope ................. finance/share-a writable cohort

Observed event
  event ................. evt_01L
  class ................. index-growth
  seat .................. nas-01

Final classification
  verdict ............... allowed-residual
  review ................ rar_01O

Surviving claim
  state ................. unchanged

Language boundary
  allowed ............... prior quiet claim still stands; indexing growth was an allowed residual
  forbidden ............. no movement happened during the quiet window

Reopen boundary
  reopen if ............. any forbidden-class event lands inside the covered writable cohort
```

## Commands

```text
anonsync residual-receipt show <receipt_id>
anonsync residual-receipt list --receipt <quiet_receipt_id>
```

## Success condition

A good residual classification receipt lets a future operator answer:

- what event was reviewed
- whether it was allowed residue or a real violation
- what quiet claim survived afterward
- what stronger sentence stayed forbidden
