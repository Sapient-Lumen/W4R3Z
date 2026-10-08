# Remedy-hardening-rollout timeline page — pilot, expand, freeze, abort, and reseal events

## Purpose

This page is the ordered event surface for how a case moved from approved change into bounded rollout, leaked spread, abort, rollback debt, or restored bounded rollout.
It exists so later readers can see rollout expansion and abort timing directly rather than reconstructing them from share state, sync mode, or permission history.

## Event types

The timeline must support at least these event kinds:

- approved change registered
- rollout review opened
- named pilot cohort set
- required rollout cohort set
- linked-device spread risk declared
- Standard onward-share risk declared
- local-share pilot lane created
- synchronization-mode map captured
- pilot rollout started
- non-pilot lane landed change
- blast-radius ceiling stressed
- broader rollout frozen
- abort requested
- future spread stopped
- rollback or compensation debt opened
- rollback or compensation closed
- broader rollout approved
- post-rollout reseal opened
- post-rollout reseal completed
- hardening rollout contract collapsed or suspended

## Timeline queries

The page must answer:

- when did rollout first become allowed?
- when did the first non-pilot or non-bounded landing occur?
- when did abort stop being fully honest?
- when was broader rollout frozen or resumed?
- when did rollback or compensation debt open and close?
- when did recurrence-hardened-retained-change-gated-and-rollout-bounded discharge become honest, or collapse again?

## View modes

The page must provide:

- all-events view
- pilot-only view
- non-pilot leakage view
- abort-and-rollback view
- reseal-only view
- collapse-only view
