# Commitment capacity proof page: load envelope, headroom, and overcommitment guard interface spec

## Purpose

This page is the durable proof for why a promise was admitted, narrowed, deferred, or blocked on capacity grounds.

## Core decision

AnonSync must expose one first-class **Commitment capacity proof** page whenever commitment admission changes because of shared load, protected reserve, or overcommitment risk.

## Fixed page order

1. **Proof header**
2. **Current-envelope card**
3. **Headroom and reserve card**
4. **Admission proof card**
5. **Blocked-stronger-sentence card**

### 1) Proof header

Show:

- proof id
- linked capacity object id
- linked promise proposal id
- final admission verdict
- current load posture
- current headroom class
- current overcommitment risk
- proof freshness

Supported `headroom_class` values:

- `ample`
- `workable`
- `tight`
- `reserve-only`
- `none`
- `unknown`

### 2) Current-envelope card

Show:

- admitted promise count and classes
- active background-work burden considered
- known throttle or pause windows considered
- discovery lag or rescan burden considered
- release triggers expected soon
- expiry of the envelope proof

Hard rule:

The envelope must say what counts inside it.
`current load` without boundaries is invalid.

### 3) Headroom and reserve card

Show:

- amount or class of headroom claimed
- protected reserve class
- whether reserve is intact, borrowed, or violated
- whether proposed work is allowed to spend reserve
- strongest fact that could invalidate the headroom claim quickly

Supported `reserve_integrity` values:

- `intact`
- `soft-borrowed`
- `hard-borrowed-by-approval`
- `violated`
- `not-applicable`

### 4) Admission proof card

Show:

- admitted promise as published
- narrower or weaker substitution if applicable
- why the promise fits within the current envelope
- why a stronger version does not fit
- next review or release trigger

Supported `fit_verdict` values:

- `fits-cleanly`
- `fits-only-if-narrowed`
- `fits-only-if-weakened`
- `fits-only-with-reserve-spend`
- `does-not-fit`
- `cannot-be-proven`

### 5) Blocked-stronger-sentence card

The page must preserve:

- strongest stronger promise blocked by load
- exact reason it is blocked
- event that would unlock it
- whether trust or authority would still block it even after capacity clears

Hard rule:

Capacity proof may not overclaim by hiding stronger blocked options.
It must keep the ceiling explicit.

## Sentence requirement

The page must end with one sentence in this shape:

- `Current admitted load leaves only [headroom class] headroom; therefore [promise class] for [scope] is [admitted/narrowed/deferred/blocked], and the stronger sentence [X] remains blocked until [release trigger].`
