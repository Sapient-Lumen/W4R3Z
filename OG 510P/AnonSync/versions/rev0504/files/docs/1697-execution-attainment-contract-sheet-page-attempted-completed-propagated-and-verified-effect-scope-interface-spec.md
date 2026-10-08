# Execution-attainment contract sheet page — attempted, completed, propagated, and verified effect scope

## Purpose

This page is the canonical declaration of what completion means for a typed effect.
It exists so the product can stop pretending that `execution happened`, `green check visible`, `no warning showing`, `connected peers caught up`, and `required outcome attained` are the same truth.

The page must answer:

> for this act version and effect lane, what exactly counts as local completion, what exactly counts as attained outcome, which cohort must be covered, what residue is tolerated, under what verification basis does the claim become durable, and what stronger completion sentence remains blocked?

## Mandatory attainment rungs

At minimum the page must expose these rungs separately:

- execution attempted
- execution locally committed
- propagation started
- connected-cohort complete
- required-cohort complete
- verification pending
- verified attained
- verified attained with residue
- no-source / ghost residue present
- attainment reopened

The implementation may add more rungs, but it may not collapse them into one generic `done` state.

## Mandatory blocks

### A. Act-and-effect block

- source act identifier
- source version identifier
- exact effect lane being measured
- exact question this page is answering
- exact reason this effect needs an attainment contract instead of a generic status indicator

### B. Cohort-and-threshold block

- intended beneficiary / target cohort
- currently observable cohort
- required cohort for honest completion
- whether `connected peers` is only an operational subset
- whether disconnected, offline, placeholder-only, or unavailable members remain part of the required cohort
- exact threshold for `complete enough to count`
- strongest blocked stronger sentence if cohort coverage remains under-proved

### C. Propagation-and-residue block

- whether the effect landed locally
- whether the effect propagated outward
- whether any recipients only received metadata, placeholders, or notice without usable effect
- whether no-source / ghost residue exists
- whether partial files, stuck temp files, or abandoned sync states are present
- exact reason stronger completion remains blocked when residue survives

### D. Verification-and-durability block

- current verification basis
- whether the page is relying on event traces, connected-peer state, required-peer receipts, rescans, rechecks, or adjudicated override
- whether hidden tasks may still change the answer
- whether a calm UI state is sufficient or insufficient
- whether later reconnect, rescan, or touch can strengthen or weaken the claim
- what must happen before the product will say `verified attained`

### E. Reopen-and-failure block

- what reopens the attainment question
- whether clock correction, reconnect, rescan, dispute, ghost-file discovery, or source-peer loss can downgrade the verdict
- whether stronger irreversible sentences are blocked until verification hardens
- whether compensating action is required when attainment fails after execution
- what must be preserved for later review

## Required comparisons

The page must keep these comparisons explicit:

- `execution attempted` vs `execution locally committed`
- `locally committed` vs `propagated`
- `propagated to connected peers` vs `attained for required cohort`
- `activity quiet` vs `durably verified`
- `warning absent` vs `residue absent`
- `ghost/no-source residue` vs `attainment truly failed`

## Required badges

- `execution-attempted`
- `local-commit-earned`
- `propagation-active`
- `connected-cohort-complete`
- `required-cohort-incomplete`
- `verification-pending`
- `verified-attained`
- `verified-with-residue`
- `ghost-residue-present`
- `attainment-reopened`

Badges must stack instead of collapsing meaning.
For example, `local-commit-earned`, `connected-cohort-complete`, and `verification-pending` may coexist with `ghost-residue-present` when the effect looks locally finished but a stronger required-cohort completion sentence is still blocked.

## Stronger-sentence guard

This page may say `the effect committed locally, propagated to all connected participants, and remains under verification because two required recipients are offline and one announced artifact is now ghost/no-source residue`.
It may not say `the effect is fully complete for everyone` unless that stronger sentence is truly earned.
