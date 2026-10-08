# Restoration waterfall contract sheet page — creditor order, partial relief, and probation window

## Purpose

This page is the canonical object for any burst-debt case that cannot be fully repaired in one step.
It must answer the next operator question after debt is known and restoration is not yet complete:

> if we only have limited restoration room now, who gets repaired first, what partial relief already counts, what remains open, and what future-burst probation still binds the claimant?

## Primary questions the page must answer

1. What debt case does this waterfall serve?
2. Which creditor tiers exist, and in what order must they be cleared?
3. How much restoration budget is available right now?
4. Which tiers or creditors have already received partial relief?
5. What probation or burst embargo survives while any tier remains open?

## Required fields

### A. Source-debt block

- source burst-debt object
- claimant name
- debt class summary
- total restoration amount originally owed
- current residue still open
- debt-age band
- source settlement verdict if any

### B. Waterfall-order block

- waterfall mode (`default-tiered`, `manual-tiered`, `waiver-modified`, `carry-forward-modified`)
- tier 1 creditor class
- tier 2 creditor class
- tier 3 creditor class
- explicit tier-order reason
- cross-tier skipping allowed (`no`, `manual-only`, `typed-waiver-only`)

### C. Tier detail block

For each tier the page must show:

- creditor class name
- named creditor set or cohort basis
- original amount owed to tier
- amount already relieved
- amount still open
- distribution method inside tier (`single-creditor`, `severity-order`, `pro-rata`, `manual-sequenced`)
- strongest surviving harmed-neighbor sentence for the tier

### D. Available-restoration-budget block

- current restoration budget amount
- budget source (`reclaimed-room`, `future-cap-reduction`, `manual-compensation`, `carry-forward-limit`, `mixed`)
- budget horizon (`one-shot`, `staged`, `recurring-window`)
- next expected relief slice
- missed-slice consequence

### E. Probation-and-future-exception block

- future-burst posture (`blocked`, `manual-review-only`, `narrowed-cap-only`, `ordinary-policy-resumed`)
- probation start time
- probation minimum duration
- probation lift conditions
- strongest clean-restoration sentence still blocked
- recurrence trigger that would tighten probation again

## Required states

The page must keep these states separate:

- `no-waterfall-needed`
- `waterfall-open-tier-1`
- `waterfall-open-tier-2`
- `waterfall-open-tier-3`
- `partial-relief-applied`
- `waiver-pending`
- `carry-forward-conversion-pending`
- `probation-active`
- `final-verification-pending`
- `clean-restoration-released`

## Page obligations

- never let `some creditors relieved` impersonate `all creditors cleared`
- always show creditor order and distribution method on the same page as remaining residue
- always show the current budget slice and the next missing slice
- always show future-burst probation on the same page as tier status
- always link backward to the debt object and forward to waterfall review, proof, timeline, and receipt

## Stronger-sentence guard

The page may say `reserve restored; named harmed claimants still open under probation`.
It may not say `claimant fully restored` until every required creditor tier is cleared or a typed waiver defines the weaker surviving sentence that remains.