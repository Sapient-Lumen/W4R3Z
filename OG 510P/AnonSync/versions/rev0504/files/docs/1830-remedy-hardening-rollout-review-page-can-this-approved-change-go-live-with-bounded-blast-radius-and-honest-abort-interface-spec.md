# Remedy-hardening-rollout review page — can this approved change go live with bounded blast radius and honest abort?

## Purpose

This page is the operator's adjudication surface for whether a case that already achieved retained and change-gated recurrence hardening may let an approved change actually spread.
It exists so the operator can answer one typed question instead of reconstructing rollout safety from linked-device defaults, share-link knobs, sync modes, and disconnect semantics.

## Primary review question

`Does this case merely have an approved change, or may that change actually go live now inside a bounded pilot or broader rollout with an abort path that remains honest?`

## Required review panes

### 1. Spread-surface pane

Show:

- linked-device auto-spread exposure
- Standard-versus-Advanced onward-share exposure
- share-link approval, expiry, and use-limit exposure
- local-share containment status
- strongest blocked stronger sentence caused by spread surface

### 2. Cohort-and-mode pane

Show:

- named pilot cohort
- required rollout cohort
- Disconnected, Selective Sync, and Synced participation map
- whether one lane is only visible, placeholder-only, or fully live
- whether any hidden or future-admission lane defeats the intended ceiling

### 3. Abort-and-unwind pane

Show:

- abort-readiness class
- rollback-honesty class
- whether disconnect or permission lowering only stops future spread
- whether already-landed lanes now require rollback or compensation
- final honest abort ceiling

### 4. Expansion-and-reseal pane

Show:

- pilot success threshold
- broader rollout threshold
- required reseal class after pilot or expansion
- strongest sentence allowed before reseal
- strongest sentence allowed after reseal
- final honest rollout-bounded sentence ceiling

## Required review outcomes

The page must support outcomes such as:

- `the change is approved, but rollout remains unbounded and blocked`
- `the change may go live only for a named pilot cohort`
- `pilot rollout is allowed, but abort honesty is already weaker than operators think`
- `non-pilot spread occurred, so compensation or rollback review is now required`
- `broader rollout may proceed only after pilot proof and reseal`
- `rollout is now bounded tightly enough that the stronger rollout sentence is honest`

## Review discipline

The review must forbid these shortcuts:

- approval equals rollout safety
- link expiry equals blast-radius ceiling
- use limit equals pilot cohort definition
- disconnected icon equals no exposure
- placeholder-only lane equals no semantic adoption risk
- disconnect action equals full unwind
- one device-local trial equals required-cohort bounded rollout
