# Space pressure page: stop floor, byte owners, and safe-first actions interface spec

## Purpose

This page answers:

> what exact local space floor is active right now, what byte classes are driving pressure, and what safest action can I take first without silently widening into delete, history loss, or continuity damage?

The page exists because `Low disk space`, `storage almost full`, and `cleanup recommended` are not the same truth.

## Core rule

Every serious low-space condition must compile to one first-class **Space pressure** page before any reclaim action is offered.
That page owns:

- active stop floor
- active storage root or drive basis
- top byte-pressure contributors
- safe-first reclaim ladder
- pressure-state receipt

## Primary layout

The page always renders the same regions:

1. pressure verdict
2. active stop-floor card
3. byte-pressure contributors card
4. safe-first action ladder
5. pressure receipt and follow-on links

### 1) Pressure verdict

Show:

- verdict label: `healthy`, `watch`, `warning`, `stopping-soon`, `sync-stopped-by-floor`, `unknown`
- strongest honest one-line summary
- storage root or device basis in scope
- one safest next action

### 2) Active stop-floor card

Show:

- which root / drive / storage class the current floor applies to
- current free bytes
- configured stop floor
- any additive reserves or offsets
- whether progress is already reduced, blocked, or still normal

The operator must be able to answer: **what exact floor is active here, and what path does it apply to?**

### 3) Byte-pressure contributors card

Show top contributors grouped by class:

- materialized payload
- placeholder metadata / namespace only
- retained history / archive
- transfer receipts / downloads / shared-file sinks
- logs / diagnostics / profiler / dumps
- database / settings / service state
- residual / orphaned / temp / in-flight bytes

Each row must show:

- current estimated bytes
- locality / owner (`subject path`, `state root`, `app sandbox`, `service root`, `unknown`)
- reclaimability class
- strongest continuity risk

### 4) Safe-first action ladder

Show a reviewed ladder ordered from least-destructive to most-destructive, such as:

- clear residual and temp bytes
- compact logs / rotate diagnostics within policy
- evict materialized local copies while preserving subject membership
- shorten retained history / archive policy
- remove bounded-transfer receipts
- broader subject or state-root cleanup

Each rung must show:

- expected bytes freed
- required prerequisites
- explicit non-effects
- strongest risk if chosen

### 5) Pressure receipt and follow-on links

Link to:

- Byte-class inventory
- Reclaim preview
- Reclaim receipt

After any accepted action, emit a receipt that preserves:

- pressure verdict before and after
- active floor
- chosen ladder rung
- actual freed bytes observed
- residual blockers still present

## Honest outputs

This page may conclude:

- `warning on state-root floor · safe-first clear residual/log bytes`
- `payload dominates pressure · placeholder-preserving eviction available`
- `archive dominates pressure · retention weakening requires explicit review`
- `pressure source uncertain · inventory review required before reclaim`

It may not collapse these into one generic `Free up space` verdict.

## Rules

### Rule 1 — floor basis must be explicit

Never say only `disk is almost full`.
Say which path class, drive, or state root the floor is about.

### Rule 2 — pressure class and reclaim class must stay separate

Large byte classes are not automatically safe-first reclaim classes.
For example, history may be large yet intentionally preserved.

### Rule 3 — safe-first ladders need non-effects

Every rung must say what it does **not** change.
Examples:

- `does not delete replicated payload on other peers`
- `does not widen subject departure`
- `does not clear crash artifacts`
- `does not weaken retention`

### Rule 4 — stop state must not hide uncertainty

If the product cannot yet tell whether the floor is caused by payload, retained history, diagnostics, or residual state, it must say `unknown` and link to inventory rather than bluffing precision.

## Event language

Use explicit phrases such as:

- `space pressure on state root; sync stop floor reached`
- `history retention is largest reclaimable class but weakens restore posture`
- `residual temp bytes reclaimed; payload and archive unchanged`
- `safe-first ladder exhausted; broader review required`

Avoid vague lines such as:

- `low storage`
- `cleanup advised`
- `space issue resolved`

## Non-clone reason

Current official Resilio docs are usefully candid that free-space floors, placeholders, archive, and hidden storage roots are real.
But the operator still has to reconstruct the active floor and safest action from warnings, power-user settings, Archive notes, and storage-root lore.
AnonSync should instead expose one Space pressure page where stop floor, byte owners, and safe-first actions stay adjacent.
