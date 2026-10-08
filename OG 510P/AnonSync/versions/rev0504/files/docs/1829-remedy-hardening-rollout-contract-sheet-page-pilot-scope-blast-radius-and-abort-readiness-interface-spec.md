# Remedy-hardening-rollout contract sheet page — pilot scope, blast radius, and abort readiness

## Purpose

This page is the operator's compact contract for whether a case that already achieved recurrence-hardened-and-retained-and-change-gated discharge may let one approved change actually go live in a bounded way.
It exists so the product can distinguish `the change was approved` from `the change may spread now inside an honest rollout ceiling with an honest abort path`.

## Core fields

- case identifier
- source remedy-hardening-change-gate receipt identifier
- triggering cause family
- current hardening-rollout posture rung
- current approved change class
- rollout initiator class
- rollout scope class
- named pilot cohort
- required rollout cohort
- linked-device auto-spread exposure status
- Standard-versus-Advanced onward-share exposure status
- share-link exposure status
- local-share containment status
- synchronization-mode participation map
- blast-radius ceiling class
- expansion threshold class
- abort-readiness class
- rollback-honesty class
- compensation-if-abort debt class, if any
- required reseal class after pilot or expansion
- highest honest current rollout-bounded sentence
- strongest blocked stronger rollout-bounded sentence
- next strengthening trigger
- next weakening trigger

## Remedy-hardening-rollout posture rungs

The page must model at least these distinct rungs:

- change approved; rollout still unbounded
- rollout proposal restricted to named pilot cohort
- pilot live inside scope ceiling
- pilot live but blast-radius budget stressed
- pilot exceeded ceiling or leaked to non-pilot lane
- broader rollout blocked pending pilot proof
- broader rollout approved pending reseal
- abort still honest for unspread lanes only
- abort requested after spread debt exists
- rollback or compensation pending for already-landed lanes
- rollout reseal complete; bounded rollout restored
- recurrence-hardened-retained-change-gated-and-rollout-bounded discharge achieved
- hardening rollout contract collapsed or suspended

## Required distinctions

The page must keep these truths separate:

- approved change versus rollout-bounded change
- named pilot scope versus required rollout scope
- one disconnected or selective lane versus the whole blast radius being bounded
- abort armed versus abort still honest
- stopping future spread versus unwinding already-spread change
- pilot proof complete versus rollout reseal complete
- one device-local safe trial versus required-cohort bounded rollout

## Operator promises

The contract sheet must let the operator say things like:

- `the change is approved, but it may only reach the named pilot cohort for now`
- `pilot spread remains inside the blast-radius ceiling, but linked-device auto-spread still blocks the stronger rollout sentence`
- `abort remains honest only for lanes that have not yet landed the change`
- `broader rollout is blocked until pilot proof and reseal complete`
- `the change may now spread broadly without reopening the cause family because rollout bounding is explicitly proven`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- pilot cohort not yet named
- blast-radius ceiling not yet proven
- linked-device auto-spread still open
- Standard onward-share exposure still open
- share-link exposure still open
- local-share containment too weak
- non-pilot lane already landed change
- abort honesty already degraded by spread debt
- required reseal still pending
- evidence basis too weak to claim bounded rollout
