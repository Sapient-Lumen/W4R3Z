# Shutdown drain review page: stop target, pending publication, and quiet boundary interface spec

## Purpose

This review appears whenever an operator requests a meaningful stop, especially one that they may later rely on as a quiet boundary before migration, repair, export, or custody handoff.
The review exists to answer one ordinary question before commit:

> what exactly am I stopping, what pending work still exists, what quiet boundary can the product honestly promise, and what restart risk survives after apply?

## Trigger conditions

Open this review when any of the following become true:

- the operator requests stop for a runtime that can continue in background or service mode
- active transfer or queued publication exists
- the stop could be relied on for migration, custody, or repair safety
- startup / service persistence could revive the runtime later
- the current surface cannot prove runtime disappearance by itself

## Fixed page order

1. stop delta header
2. targeted runtime card
3. pending publication card
4. quiet boundary card
5. decision footer

### 1) Stop delta header

Show:

- current runtime class
- requested stop class
- changed risk class
- strongest safe sentence after apply
- stronger rejected sentence after apply

Example safe sentence:

- `After this action the foreground projection will close and the runtime will enter draining; the product still cannot claim that no further publication will occur until drain proof completes.`

### 2) Targeted runtime card

Show:

- projection(s) affected
- runtime(s) affected
- service / background actor affected or untouched
- whether the requested verb is `close-projection`, `pause-runtime`, `stop-runtime`, `retire-service`, or `stop-and-disable-revive`
- whether another runtime of the same seat remains alive

### 3) Pending publication card

Show:

- active transfer count
- queued publication count
- metadata/index writes pending
- last observed outbound activity
- whether drain is cancellable, immediate, timed, or proof-required

Possible drain states:

- `already-quiet`
- `draining-now`
- `drain-pending-proof`
- `cannot-drain-cleanly`
- `unknown`

### 4) Quiet boundary card

Show:

- strongest honest quiet-boundary sentence
- stronger rejected sentence
- what witness is still missing
- restart / revive posture after stop
- whether chronology risk remains if later reopened

### 5) Decision footer

Available decisions:

- `Stop projection only`
- `Stop runtime and watch for proof`
- `Stop and disable startup revival`
- `Return and finish pending work`
- `Emit reviewed stop receipt`

## Rules

### Rule 1 — stop target must be typed

The review must name whether the operator is stopping a projection, runtime, service, or revival posture.

### Rule 2 — quiet boundary is not implied by button label

`Stop`, `Quit`, and `Exit` do not themselves define proof.

### Rule 3 — chronology risk stays visible

If later reopen can be meaningful for overwrite interpretation or re-indexing, the page must say so.

### Rule 4 — restart posture is part of the decision footer

The operator must see whether the thing they just stopped can come back.

## Acceptance criteria

A later operator can:

- tell what was actually targeted
- tell what pending work existed
- tell what quiet boundary was or was not promised
- tell whether revival remained possible
- tell what stronger claim remained forbidden
