# Mutation delay page: file-class batch window and lock-avoidance interface spec

## Purpose

`44`, `45`, and the activity-phase work already recognize that `changed now` is not always `ship immediately`.
This document turns that into one ordinary page.

The page exists to answer one ordinary operator question:

> why is this mutation waiting, for how long, and is the wait a healthy batching policy or a hidden conflict symptom?

## Core decision

Every subject that supports delayed shipment of local mutations must render one first-class **Mutation delay** page.
That page is the semantic home of:

- file-class delay policy
- live pending-delay rows
- lock-risk or churn explanation
- immediate-send versus continue-delay actions
- receipts for policy change and manual release

The page must not make operators edit raw config files or restart the product just to understand the timing contract.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. timing verdict strip
2. effective delay-policy card
3. pending-mutation lane
4. lock / churn explanation card
5. action matrix
6. receipts and recent releases
7. unsafe bypass drawer

### 1) Timing verdict strip

The strip shows:

- subject or path focus
- one timing verdict
- one delay-source verdict
- one next-honest-action button

Allowed timing verdicts:

- `no delay active`
- `healthy delay window running`
- `delay expired and eligible to ship`
- `lock-risk suspected`
- `delay policy conflict`

Allowed delay-source verdicts:

- `baseline policy`
- `subject override`
- `path-class override`
- `temporary operator hold`

### 2) Effective delay-policy card

Show typed policy rows with:

- file class or matcher
- current delay duration
- rationale class (`avoid partial-write churn`, `editor lock avoidance`, `bulk batching`, `manual hold`)
- policy origin
- whether restart-free update is supported

The page must make shipped defaults visibly different from later local tuning.

### 3) Pending-mutation lane

For each pending row show:

- path or artifact ref
- file-class match
- first observed change time
- most recent change time
- scheduled release time
- current countdown or overdue state
- whether the file is still mutating

### 4) Lock / churn explanation card

Show:

- whether the current wait is simple delay, ongoing rewrite churn, explicit lock conflict, or uncertain filesystem observation
- strongest evidence supporting that classification
- whether touching / rescanning / manual release would change anything
- whether peer-visible chronology risk exists if forced early

### 5) Action matrix

Render ordered actions such as:

- `Keep current delay policy`
- `Release this mutation now`
- `Shorten delay for this class`
- `Convert to temporary hold`
- `Escalate to lock/conflict review`

Each row shows:

- scope touched
- effect on current pending rows
- reversibility
- chronology / conflict risk
- expected receipt

### 6) Receipts and recent releases

Show recent delay-related receipts with:

- actor
- policy delta or manual release action
- affected rows count
- rationale
- resulting timeline change
- rollback availability

### 7) Unsafe bypass drawer

If a release would knowingly bypass a safety delay, place it behind a drawer such as `Force immediate shipment`.
That drawer may contain:

- release despite active churn
- ignore recommended batching window
- ship while lock risk remains uncertain

The page must state the chronology and conflict risk before enabling the action.

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- whether a delay is active
- when the next release becomes eligible
- whether the wait is healthy policy versus suspected conflict
- next admissible action

## Acceptance criteria

This spec is satisfied when:

- operators can see why a mutation is waiting without opening raw config material
- healthy delay windows are distinguishable from lock/conflict symptoms
- file-class timing policy is inspectable and editable through one page contract
- manual release actions publish chronology risk honestly
- policy edits and forced releases leave durable receipts
