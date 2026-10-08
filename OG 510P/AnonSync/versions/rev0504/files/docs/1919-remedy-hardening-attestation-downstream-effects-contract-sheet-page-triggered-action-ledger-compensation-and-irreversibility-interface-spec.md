# Remedy-hardening-attestation downstream-effects contract sheet page — triggered action ledger, compensation, and irreversibility

## Purpose

This page is the compact contract for a case whose stale sentence is no longer allowed to be served, but whose downstream consequences may already have been triggered.
It exists so the product can distinguish `stale reading blocked`, `new trigger blocked`, `already-triggered work still draining`, `undo in progress`, `compensation required`, and `irreversibility ceiling declared`.

## Core fields

- case identifier
- source subscriber-invalidation receipt identifier
- current governing receipt identifier
- triggering stale version token
- current downstream-effects class
- action inventory class
- named downstream actor count
- unknown historical downstream actor flag
- queued action count
- executed automated action count
- executed human action count
- externalized action count
- reversible action count
- partially reversible action count
- irreversible action count
- undo required count
- undo completed count
- correction-required human decision count
- compensation required count
- compensation completed count
- queue-drain posture
- new-trigger quarantine flag
- restoration-from-governed-copy count
- irreversibility ceiling class
- strongest currently safe restoration sentence
- strongest blocked restoration sentence
- next evidence that upgrades downstream-restoration confidence
- next evidence that forces compensation, escalation, or ceilinging now

## Downstream-effects classes

The page must model at least these distinct classes:

- no downstream action inventory yet
- stale trigger possible, inventory incomplete
- new triggers blocked, historical effects still unknown
- queued actions frozen before apply
- reversible automated actions pending undo
- reversible human actions pending correction
- compensation required for named cohort
- compensation complete for named cohort only
- irreversible external consequence declared
- named cohort restored
- named cohort compensated but not restored
- broader restoration sentence blocked

## Downstream actor classes

The page must support at least these actor types:

- queued internal job
- executed automation or workflow
- file rewrite, delete, restore, or rename effect
- permission or routing change
- export or message issuance
- human reviewer or approver
- external dependent system
- same-world mirror or local-share actuator
- linked-device or cohort-wide propagation lane
- offline or delayed actor
- unknown historical downstream actor

## Reversibility classes

For every action or actor the page must preserve at least these classes:

- not yet applied
- fully reversible by product action
- reversible only with operator assistance
- reversible only from governed restore point
- compensable but not restorable
- irrecoverable but containable
- structurally unknown reversibility

## Fixed rendering order

Every downstream-effects contract sheet must render the same sections in the same order:

1. **Strongest currently action-safe sentence**
2. **Triggering stale version and downstream action inventory**
3. **Queue drain, undo ownership, and compensation obligations**
4. **Irreversibility ceiling and blocked restoration language**
5. **Next evidence that upgrades or collapses the restoration claim**

## Hard rules

The page must never silently upgrade:

- `stale serving blocked` into `downstream world restored`
- `old versions remain in archive` into `rollback available`
- `new triggers quarantined` into `already-triggered actions neutralized`
- `one named cohort restored` into `all downstream consequences restored`
- `compensation offered` into `original state restored`
- `no further effect observed` into `no further effect possible`

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- which stale version actually triggered the downstream concern
- which downstream actors or action classes already executed or may still execute
- which effects are reversible, which are only compensable, and which are irrecoverable
- whether new triggers are blocked while already-triggered work drains
- what the highest honest restoration sentence is right now
- exactly which stronger restoration sentence remains blocked and why
