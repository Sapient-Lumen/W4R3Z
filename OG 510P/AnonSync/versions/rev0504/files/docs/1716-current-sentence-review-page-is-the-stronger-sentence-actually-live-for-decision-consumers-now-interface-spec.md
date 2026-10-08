# Current-sentence review page — is the stronger sentence actually live for decision consumers now?

## Purpose

This page is the operator workspace for deciding whether a stronger sentence is truly current and operative.
It exists so the reviewer can test consumer scope, rollout completion, drift, stale surfaces, rollback exposure, and fallback sentence in one place.

## Required review branches

### Branch 1 — authorized but not yet committed

Use this branch when promotion succeeded in principle but currentness has not begun.
The page must show:

- why commitment has not started
- whether the blocker is policy, rollout readiness, subscriber readiness, or stale evidence
- the lower sentence that remains current in the meantime
- the next event that would allow commitment to begin

### Branch 2 — staged rollout in progress

Use this branch when the stronger sentence is current only for a narrower named cohort.
The page must show:

- which cohort already treats the stronger sentence as current
- which required consumers still remain on the lower sentence
- what risk is accepted during the staged period
- what exact condition upgrades the sentence to all-required-consumer current
- what exact condition forces rollback instead

### Branch 3 — all-required-consumer current check

Use this branch when the product claims the stronger sentence is now current everywhere it must be.
The page must show:

- which consumers are required for this row
- how each consumer family was verified
- whether any lagging, stale, or disconnected consumers remain
- whether reconciliation passed across UI, API, receipt, and subscriber state
- what stronger sentence remains blocked despite currentness

### Branch 4 — stale or contradictory surfaces

Use this branch when UI, API, history, receipt, or subscriber observations disagree.
The page must show:

- which surfaces disagree
- whether the disagreement is cosmetic or decision-material
- whether stronger currentness claims freeze immediately
- which lower sentence remains safe meanwhile
- the repair step required before stronger currentness may be spoken again

### Branch 5 — rollback review

Use this branch when a stronger current sentence may need to be downgraded.
The page must show:

- what stronger sentence is currently live
- which rollback trigger occurred
- who may authorize rollback
- what lower sentence would become current afterward
- whether rollback is global or cohort-scoped
- what audit scar and lineage must survive

### Branch 6 — supersession handoff

Use this branch when an even newer sentence is about to replace the current one.
The page must show:

- which sentence is current now
- which newer sentence is candidate to replace it
- whether the current sentence must first be rolled back, superseded directly, or coexist for staged consumers
- which consumers are allowed to move first
- how old-current truth remains preserved in history

## Review invariants

The page must always preserve these invariants:

- promotion does not automatically imply currentness
- currentness is typed by consumer family, not assumed universal
- disagreement across surfaces can weaken stronger claims without erasing lower truths
- rollback preserves history rather than rewriting the past
- supersession is different from rollback and different from mere staged lag

## Required reviewer prompts

- what is the smallest honest current sentence right now?
- what stronger sentence is merely authorized but not yet current?
- which consumers already treat the stronger sentence as current?
- which consumers are still on the lower sentence?
- what would force rollback?
- what would allow upgrade to all-required-consumer current?

## Forbidden shortcuts

This page must not let the reviewer conclude currentness from shortcuts such as:

- `the bell rang earlier`
- `the WebUI shows it`
- `the API endpoint is up`
- `the History tab mentions activity`
- `the rollout probably finished`

Those phrases may inform investigation.
They may not replace the currentness check.

