# Current-sentence contract sheet page — authorized, committed, current, and rollback-scoped

## Purpose

This page is the canonical declaration of which sentence is actually current for downstream decision consumers.
It exists so the product can stop pretending that `promotion-authorized`, `visible somewhere`, `current in one UI`, `current for one consumer family`, and `current for every required consumer` are the same truth.

The page must answer:

> given the strongest sentence that is allowed to go live, has that sentence actually become the current operative sentence, for which consumers, by which rollout lane, with what lag, and under what rollback rule?

## Mandatory current-state rungs

At minimum the page must expose these rungs separately:

- not current
- promotion-authorized but not committed
- commit requested
- commit blocked by rollout precondition
- preview-only current
- staged current for a named consumer cohort
- current for core consumers only
- current for all required consumers
- rollback-armed current
- rollback executing
- rolled back to lower sentence
- superseded by a newer stronger sentence
- stale or indeterminate currentness

The implementation may add more rungs, but it may not collapse them into one generic `live` state.

## Mandatory blocks

### A. Source-bundle block

- case identifier
- source promotion receipt identifier
- source authority, time-authority, and publication receipts that still matter
- strongest sentence promotion-authorized
- smallest sentence already guaranteed even if current commit fails
- exact reason a current-sentence sheet is required instead of assuming promotion equals currentness

### B. Consumer-scope block

- required consumer families for this sentence
- optional consumer families
- which consumers already treat the sentence as current
- which consumers are still lagging, stale, disconnected, hidden, or unsubscribed
- whether any consumer family is not allowed to rely on the stronger sentence yet
- whether lower sentence remains current for any residual cohort

### C. Commit-lane block

- whether commit is manual, automatic, or staged
- commit strategy: all-at-once, staged, canary, manual fan-out, or API push plus reconciliation
- commit timestamp and trusted time basis
- whether currentness depends on durable ledger write, subscriber poll, push notification, or explicit acknowledgment
- exact criterion for upgrading from staged current to all-required-consumer current

### D. Rollback-and-fallback block

- rollback authority
- rollback triggers
- whether rollback is automatic or manual
- lower sentence restored on rollback
- whether some consumers may remain on the stronger sentence during partial rollback
- audit obligation after rollback

### E. Drift-and-reconciliation block

- stale-surface detection rules
- reconciliation frequency
- what happens when UI, API, and receipt disagree
- whether disagreement freezes stronger claims or merely annotates them
- exact strongest sentence blocked until reconciliation completes

## Required comparisons

The page must keep these comparisons explicit:

- promotion-authorized versus committed-current
- current in preview versus current for core consumers
- current for core consumers versus current for all required consumers
- current versus rollback-armed
- rolled back versus fully erased from history
- superseded versus rolled back

## Required microcopy

The page must always show, in plain language:

- the strongest sentence merely authorized
- the strongest sentence actually current
- who is already consuming it as current
- who is not yet allowed to rely on it
- what would trigger rollback
- which lower sentence survives if rollback fires

## Forbidden shortcuts

This page must not allow currentness to be concluded from any single shortcut such as:

- green check alone
- bell notification alone
- one UI surface alone
- API availability alone
- optional column visibility alone
- a human saying `it should be live by now`

Those are inputs.
They are not the currentness verdict.

