# Placeholder removal page: local evict, global delete, and guardrail policy interface spec

## Purpose

This page answers one ordinary question:

> when I remove this placeholder or partially present file, am I evicting bytes locally, destroying the object everywhere, or invoking a guardrail that converts destruction back into local-only eviction?

The page exists because `Delete`, `Remove from this device`, `Remove from all devices`, and `recreate placeholders on removal` are not the same action.

## Core decision

Every seat must render one first-class **Placeholder removal** page whenever a materialization-reducing or removal action targets a placeholder-capable subject.
That page owns:

- action class
- propagation scope
- last-full-copy risk
- guardrail policy in force
- surface asymmetry
- safe alternatives

The workbench must not force the operator to learn these differences from file-browser context menus or hidden advanced toggles.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. current presence card
3. action semantics card
4. guardrail card
5. last-copy risk card
6. receipts

### 1) Subject strip

Show:

- object label
- current seat label
- current verdict: `local-evict`, `global-delete`, `guarded-evict`, `blocked-delete`, `ambiguous-removal`
- one next honest action

### 2) Current presence card

This card publishes:

- whether the target is placeholder-only, partially materialized, or fully materialized locally
- whether the seat has read-only or read-write destructive authority
- known full-copy witnesses on other seats
- whether subfolder semantics widen the action to descendants

The operator must be able to answer: **what is actually here right now, and who else still has the bytes?**

### 3) Action semantics card

This card publishes:

- candidate action verbs and exact propagation class
- local result after action: removed, reverted to placeholder, unchanged, or blocked
- remote result after action: no change, object deleted, descendants deleted, or unknown
- special-case meaning on surfaces with no shell integration

The operator must be able to answer: **what exactly happens if I press this verb on this surface?**

### 4) Guardrail card

This card publishes:

- whether a removal guardrail is active
- whether destructive delete is being remapped into placeholder recreation / local-only eviction
- scope and provenance of the guardrail: seat default, subject policy, emergency mode, or unknown
- any surfaces where the guardrail is unavailable or bypassed

The operator must be able to answer: **is a safety rail protecting me from accidental all-peer destruction here?**

### 5) Last-copy risk card

This card publishes:

- whether at least one trustworthy other full copy exists
- whether all known seats may already be placeholders only
- risk class: `safe-evict`, `at-risk`, `no-other-full-copy-proven`, `unknown`
- safer alternatives such as hold, fetch elsewhere, or verify another witness first

The operator must be able to answer: **am I about to turn the last real bytes into zero-byte promises?**

### 6) Receipts

Receipts show:

- action previews acknowledged
- delete/evict conversions performed
- last-copy proof checks performed
- actual propagation result observed

## Non-negotiable rules

### Rule 1 — local eviction and global destruction must never share one unlabeled affordance

The page must keep them separate even if the current surface historically conflated them.

### Rule 2 — safety rails must be visible

If a hidden setting or seat policy remaps deletion into placeholder recreation, the page must say so plainly.

### Rule 3 — last-copy uncertainty must block casual language

The UI must not say `remove from this device` casually when no other trustworthy full copy is proven.

## Honest outputs

The page may conclude:

- `This action will evict local bytes only and leave a placeholder because a delete guardrail is active.`
- `Deleting this placeholder with current authority would remove the object from all peers.`
- `No other full-copy witness is currently proven; local eviction is blocked until another seat is verified.`

It may not collapse those outcomes into a single `remove` button label.
