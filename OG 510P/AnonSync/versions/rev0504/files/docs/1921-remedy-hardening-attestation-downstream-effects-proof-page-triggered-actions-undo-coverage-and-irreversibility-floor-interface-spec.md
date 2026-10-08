# Remedy-hardening-attestation downstream-effects proof page — triggered actions, undo coverage, and irreversibility floor

## Purpose

This page is the evidence-heavy proof surface for downstream-effect posture.
It exists so the product can prove not only that stale truth stopped being served, but also which consequences already landed, which ones were frozen, which were undone, which were merely compensated, and which remained irrecoverable.

## Proof bundle requirements

Every downstream-effects proof page must preserve evidence for at least:

- triggering stale version token and successor version token
- actor or queue that consumed the stale version
- whether the action was queued, started, completed, retried, or externally observed
- restore point or governed copy evidence where rollback is claimed
- undo execution evidence where reversal is claimed
- compensation issuance and acceptance evidence where compensation is claimed
- irreversibility declaration basis where restoration is impossible or unverifiable
- evidence horizon and blind spots that still block stronger restoration language

## Required proof states

The page must support proof states such as:

- stale version could have triggered, but action evidence incomplete
- queued action frozen before execution
- executed action traced and undone
- executed action traced and partially undone
- executed action not restorable but compensated
- irreversible effect declared with containment actions
- named cohort restored with proof
- broader restoration floor blocked by unknown or externalized effects

## Fixed rendering order

Every downstream-effects proof page must render the same sections in the same order:

1. **Current restoration floor**
2. **Trigger and actor evidence**
3. **Undo and restore-point evidence**
4. **Compensation and containment evidence**
5. **Irreversibility ceiling and blocked stronger sentences**

## Hard rules

The page must never silently upgrade:

- `restore point exists` into `restore point applied`
- `undo requested` into `undo completed`
- `compensation initiated` into `harm neutralized`
- `irreversible effect contained` into `original world restored`
- `no remaining evidence found` into `no remaining downstream effect exists`

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- what concrete evidence shows a stale-triggered action happened or was prevented
- what concrete evidence shows rollback, restore, or compensation actually occurred
- which cohorts have proof-backed restoration and which do not
- what irreversibility ceiling still constrains the case
- exactly why the strongest blocked restoration sentence is still blocked
