# Remedy-hardening-retention timeline page — drift detection, carry-forward, and reseal events

## Purpose

This page is the ordered event surface for how a case moved from recurrence hardening into retained hardening or back into retention debt.
It exists so later readers can see drift timing directly rather than reconstructing it from scattered overrides, onboarding, and restart history.

## Event types

The timeline must support at least these event kinds:

- recurrence hardening achieved
- retention review opened
- manual override applied
- global default changed
- share detached from current default
- peer-local rule diverged
- linked-device carry-forward expanded scope
- later-admission surface added
- service principal changed
- storage world fork detected
- re-add or re-share required
- retained scope proven for original cohort
- retained scope proven for future carry-forward
- retained hardening achieved
- retention debt assigned
- retained hardening collapsed or rolled back

## Timeline queries

The page must answer:

- when did retained-hardening review actually begin?
- when did one-off recurrence hardening become retained hardening?
- when did drift first appear?
- when did carry-forward scope expand beyond the original audit?
- when did service or storage continuity break?
- when did recurrence-hardened-and-retained discharge become honest, or collapse again?

## View modes

The page must provide:

- all-events view
- drift-only view
- carry-forward-only view
- override-and-default view
- world-continuity view
- collapse-only view
