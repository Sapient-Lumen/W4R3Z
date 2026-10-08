# Next observation opportunity page — duty class, preconditions, and due-time interface spec

## Purpose

The archive already had background delivery, change freshness, and freshness invalidation.
What it still lacked was one fixed page for the next operator question:

> when is this seat honestly expected to get its next chance to notice, publish, or fetch this change under its current posture?

AnonSync should therefore model the answer as a first-class **next observation opportunity page**.
The product must never force the operator to mentally combine wake intervals, rescan cadence, network policy, runtime class, and power gates before deciding whether `late` is even fair.

## Core decision

Every serious delay incident must publish one reviewed next-opportunity object before stronger delay language is allowed.
The page must preserve six truths:

1. seat / subject under review
2. current duty class
3. unmet preconditions
4. next honest opportunity type
5. due time or `not schedulable yet`
6. strongest allowed sentence right now

## Fixed review order

1. **Current duty verdict**
2. **Opportunity class**
3. **Preconditions and blockers**
4. **Due-time basis**
5. **Lateness gate**
6. **Cheapest honest action**

## 1) Current duty verdict

Show:

- seat / subject scope
- current duty class
- current strongest summary
- whether the seat is continuous, interval-based, rescan-based, foreground-only, blocked, or unknown

Required duty classes:

- `continuous-runtime`
- `interval-wake`
- `rescan-backed`
- `foreground-only`
- `precondition-blocked`
- `manual-probe-only`
- `unknown`

## 2) Opportunity class

State the next honest opportunity type, for example:

- `immediate-notification path`
- `next Android wake window`
- `next periodic rescan`
- `next foreground resume`
- `next allowed-network return`
- `next source-return window`
- `manual probe only`

## 3) Preconditions and blockers

Publish the preconditions explicitly, such as:

- background eligibility intact
- notifications still active
- battery above threshold
- allowed network available
- source peer online
- watcher coverage healthy
- runtime actually running

Each blocker row must show:

- blocker class
- whether it removes the opportunity entirely or merely delays it
- exact condition that restores opportunity

## 4) Due-time basis

The page must explain where the due time comes from:

- current wake interval
- current rescan cadence
- foreground return requirement
- restored eligibility event
- source return event
- healthy-notification expectation

If no honest due time can be produced, the page must say so explicitly with `not schedulable until blocker clears`.

## 5) Lateness gate

Required verdicts:

- `not due yet`
- `due at scheduled opportunity`
- `due now under current posture`
- `overdue under current posture`
- `cannot judge until blocker clears`

This verdict is mandatory.

## 6) Cheapest honest action

Examples:

- wait for scheduled wake
- wait for next periodic rescan
- bring app to foreground
- restore notifications / background priority
- restore allowed network
- run manual rescan now
- verify source peer presence

## Compact rendering obligations

Any compact card for next observation opportunity must still preserve:

- duty class
- next opportunity type
- due-time label
- lateness gate
- cheapest honest action

## Anti-clone rule

Do not clone workflows where the operator still has to read several support articles before the product can answer `this was not late yet` or `this is overdue now`.

## Receipt consequence

Every late-claim review and opportunity receipt must link back to the exact duty class and due-time basis that carried the judgment.
