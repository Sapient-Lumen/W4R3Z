# Effect activation contract sheet page: change class, latency, and proof ladder interface spec

## Purpose

Before an operator applies, audits, or revisits any meaningful runtime or policy change, they need one ordinary page that answers:

> what kind of change is this, when does it become live, what proves that, and what old state does it not retroactively rewrite?

This page exists so hidden-file edits, restart-required toggles, next-rescan effects, and future-only rules do not remain folklore.

## Core decision

Every serious settings, rule, or runtime-mutation surface must open one first-class **Effect activation contract sheet**.

The sheet owns:

- change family
- activation class
- save-versus-live truth
- retroactivity boundary
- proof ladder
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. activation claim header
2. change-route ledger
3. latency and trigger card
4. retroactivity boundary card
5. proof ladder and next-safe action rail

### 1) Activation claim header

Show at minimum:

- subject / seat / runtime scope
- change family (`policy`, `runtime`, `diagnostic`, `helper`, `artifact`, `other`)
- activation class (`immediate`, `next-reread`, `next-rescan`, `next-restart`, `next-startup`, `external-proof-needed`, `future-only`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `This Ignore-style exclusion rule is saved and will become active for future arrivals after the next runtime reread; already-synced material is unaffected.`

### 2) Change-route ledger

Render rows for each serious route by which a change may enter:

- ordinary UI control
- power-user preference
- hidden sidecar or policy file
- configuration file
- startup argument or service layer
- external infrastructure change
- imported receipt or bundle

Each row shows:

- current state
- source plane
- activation trigger
- proof freshness
- who can inspect it later

### 3) Latency and trigger card

This card is mandatory.
Show:

- whether the change is already live or merely staged
- what event makes it live
- earliest honest effect window
- latest expected effect window if known
- blockers that may postpone effect (`notifications absent`, `rescan disabled`, `restart pending`, `runtime offline`, `unknown`)

### 4) Retroactivity boundary card

Show separately:

- whether the change affects future work only
- whether already-indexed structure persists
- whether already-synced material remains until later repair
- whether explicit rebind, rescan, reconcile, or disconnect is required for old state

### 5) Proof ladder and next-safe action rail

Only show actions that preserve meaning, such as:

- `Save staged only`
- `Apply and restart now`
- `Force reread`
- `Run manual rescan`
- `Verify effect on named targets`
- `Emit receipt without overclaim`

## Rules

### Rule 1 — save and live are separate claims

The same surface that records a change must also show whether runtime has actually incorporated it.

### Rule 2 — activation class is public, not support knowledge

The operator must never have to remember from lore whether a control is restart-bound, reread-bound, or immediate.

### Rule 3 — retroactivity stays separate from activation

A rule may be fully live for future work while still not rewriting older indexed or transferred state.

### Rule 4 — stronger rejected sentence is mandatory

At least one tempting overclaim must remain visible.

Example rejected sentence:

- `This change has already fully corrected all affected historical material.`

## Acceptance criteria

A later operator can:

- tell how the change entered the system
- tell whether it is saved, live, and proven
- tell what event still must happen if it is not live yet
- tell what older state remains untouched
- tell what stronger sentence is still forbidden
