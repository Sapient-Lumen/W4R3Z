# Remedy-hold-enforcement contract sheet page — custodian acknowledgment, sensor coverage, and cleanup suppression

## Purpose

This page is the operator's compact contract for whether a named preservation hold is merely declared or is actually binding across the custodians, cleanup paths, and detection lanes that matter.
It exists so the product can distinguish `repair material is under hold in principle` from `repair material is genuinely hard to lose without a visible breach record`.

## Core fields

- case identifier
- source remedy-hold receipt identifier
- current enforcement posture rung
- named custodians
- acknowledged custodians
- unacknowledged custodians
- protected material classes
- protected locations by custodian
- cleanup suppression coverage
- archive-disable suppression coverage
- manual-clear suppression coverage
- dehydration or reclamation suppression coverage
- revocation or folder-removal suppression coverage
- free-space pressure posture
- restart-sensitive setting risk
- notification coverage posture
- rescan fallback window
- blind-spot environments
- breach alarm paths
- last enforcement audit time
- strongest blocked stronger enforcement sentence
- next strengthening trigger
- next weakening trigger

## Enforcement posture rungs

The page must model at least these distinct rungs:

- hold declared only
- hold requested from custodians
- hold acknowledged partial
- hold acknowledged required custodians
- hold enforced but with blind spots
- hold enforced and breach-sensed for named cohorts
- hold breached
- hold disputed
- hold suspended intentionally
- enforcement-collapsed

## Required distinctions

The page must keep these truths separate:

- hold existence versus custodian acknowledgment
- custodian acknowledgment versus cleanup-path suppression
- cleanup suppression versus breach-detection coverage
- no breach observed versus no plausible undetected breach within the covered lanes
- enforcement for named cohorts versus enforcement for all required cohorts
- desktop custody, mobile custody, delegated storage custody, and encrypted/unreadable custody

## Operator promises

The contract sheet must let the operator say things like:

- `the hold is active, but one mobile custodian has not acknowledged it and remains outside strong enforcement`
- `archive bytes survive on two desktop peers, yet manual clear is still possible without interception, so enforcement remains partial`
- `free-space reclamation and dehydration are suppressed on the required repair lane until 2026-04-10`
- `notification loss means breach visibility is delayed to the next rescan window, so no-breach claims stay weaker than audit-clean`
- `the hold was acknowledged by every named custodian, but one delegated storage lane still follows ordinary retention policy`

## Invariants

- the page never upgrades hold declaration into hold enforcement by omission
- the page never upgrades favorable settings into cleanup suppression without naming the protected paths
- the page never upgrades `no warning shown` into `no breach possible`
- the page always preserves the strongest blocked stronger enforcement sentence
