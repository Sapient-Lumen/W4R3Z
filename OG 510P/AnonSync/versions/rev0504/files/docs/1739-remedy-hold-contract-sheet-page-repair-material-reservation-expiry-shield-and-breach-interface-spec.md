# Remedy-hold contract sheet page — repair material reservation, expiry shield, and breach posture

## Purpose

This page is the operator's compact contract for whether surviving repair substrate is merely available or is actively being preserved for this case.
It exists so the product can distinguish `clean cure is still possible right now` from `clean cure is protected against ordinary decay long enough to remain honest`.

## Core fields

- case identifier
- source remedy-substrate receipt identifier
- harmed cohorts
- required repair target
- current preservation posture rung
- protected material set
- protected locations by material class
- hold owner
- hold basis
- hold start time
- hold expiry or no-expiry basis
- retention override posture
- manual preservation duties still open
- storage reservation posture
- platform coverage ceiling
- source-peer reservation status
- archive reservation status
- placeholder-only excluded set
- breach triggers
- strongest blocked stronger preservation sentence
- next strengthening trigger
- next weakening trigger

## Preservation posture rungs

The page must model at least these distinct rungs:

- cure-capable only
- hold requested
- hold armed but partial
- hold active for named cohorts
- hold active for required cohorts
- hold extended
- hold breached
- hold released intentionally
- hold expired
- preservation-collapsed

## Required distinctions

The page must keep these truths separate:

- bytes still existing versus bytes explicitly reserved for this case
- global retention setting versus case-scoped hold
- archive material versus live-source material under hold
- preservation for named cohorts versus preservation for all required cohorts
- no-expiry claim versus bounded extension with review date
- active hold versus manual operator promise to remember later

## Operator promises

The contract sheet must let the operator say things like:

- `clean cure is currently possible, but no preservation hold is active and decay risk remains ordinary`
- `archive-backed versions on two desktop peers are now under hold for named claimants, though one required mobile cohort remains unprotected`
- `retention is set to never delete, but no case-scoped reservation exists and ordinary storage cleanup may still compete with preservation obligations elsewhere`
- `the only surviving cure lane is manual and under hold until 2026-04-03 unless free-space pressure or folder removal breaches it first`
- `preservation collapsed because the hold was never armed before the Archive horizon closed`

## Invariants

- the page never upgrades cure capability into preservation by omission
- the page never upgrades global `never delete` posture into case-scoped reservation without naming the protected material set
- the page never hides manual duties or storage reservations required to keep the hold honest
- the page always preserves the strongest blocked stronger preservation sentence
