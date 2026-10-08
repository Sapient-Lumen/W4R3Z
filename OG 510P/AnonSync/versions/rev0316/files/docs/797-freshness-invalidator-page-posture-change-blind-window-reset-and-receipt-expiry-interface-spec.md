# Freshness invalidator page — posture change, blind-window reset, and receipt expiry interface spec

## Purpose

The archive already had detection posture and change-freshness review.
What it still lacked was one fixed page for the next question:

> what changed after the earlier freshness judgment, and does that change keep the old claim alive or expire it?

AnonSync should therefore model freshness invalidation as a first-class **freshness invalidator page**.
The product must never force the operator to infer from scattered warnings or settings that an old `should have been seen by now` statement quietly stopped being trustworthy.

## Core decision

Every serious freshness receipt must become reviewable against later invalidators before it can be reused.
The page must preserve five truths:

1. prior receipt being challenged
2. posture change that occurred later
3. invalidation class and strength
4. temporary versus persistent blind-window reset
5. whether revalidation is mandatory before strong language returns

## Fixed review order

1. **Prior claim under review**
2. **Observed posture change**
3. **Invalidation class**
4. **Blind-window reset shape**
5. **Reuse / downgrade / expire verdict**
6. **Required revalidation event**

## 1) Prior claim under review

Show:

- prior receipt id
- subject scope
- previously declared latency budget
- previously allowed sentence
- timestamp of the older judgment

The operator must be able to answer:

> what exact earlier freshness claim is being questioned?

## 2) Observed posture change

Publish the later change explicitly, for example:

- watcher exhaustion warning appeared
- subject moved onto SMB / UNC / network drive posture
- service runtime or service account changed
- `folder_rescan_interval` widened or disabled
- host entered sleep-preserving cadence posture
- mobile seat entered auto-sleep or battery-saver stop
- share entered forbidden-network posture
- restart / wake / rescan occurred

## 3) Invalidation class

Required classes:

- `no-meaningful-change`
- `narrowed-observation`
- `class-changed`
- `receipt-expired-by-staleness`
- `revalidated-by-stronger-event`
- `unknown-but-suspect`

Each verdict must also carry one strength label:

- `advisory`
- `material`
- `hard-expiry`

## 4) Blind-window reset shape

State the new blindness shape in ordinary language, for example:

- `no reset; old budget still applies`
- `blind window widened to next scheduled rescan`
- `blind window now indefinite until manual probe or restart`
- `mobile wake interval now defines observation opportunities`
- `network policy currently blocks any fresh observation`

## 5) Reuse / downgrade / expire verdict

Required verdicts:

- `old receipt still usable`
- `old receipt usable only with weaker sentence`
- `old receipt expired; revalidation required`
- `old receipt replaced by newer proof`

## 6) Required revalidation event

State the cheapest strong-enough event, such as:

- wait for next scheduled rescan
- manual rescan
- restore watchers and observe healthy notification
- wake mobile seat and observe one check cycle
- restore allowed network and capture fresh evidence
- restart under stable runtime/path posture

## Compact rendering obligations

Any compact card for freshness invalidation must still preserve:

- prior receipt id
- invalidation class
- expiry verdict
- new blind-window label
- cheapest revalidation event

## Anti-clone rule

Do not clone workflows where receipt expiry is learned only from service, SMB, power, or mobile troubleshooting prose while the product still renders the old freshness claim as current truth.

## Receipt consequence

Every later revalidation review or rollover receipt must link back to the exact invalidator version that reopened the claim.
