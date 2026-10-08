# Restart provenance page: stop origin, revival cause, and chronology risk interface spec

## Purpose

When a runtime returns after a stop, the operator needs one page that answers:

> why did this come back, what stop boundary did it cross, what revival mechanism caused it, and does that restart change how later edits, indexing, or overwrite chronology should be interpreted?

This page exists so comeback events do not remain `it reopened somehow` folklore.

## Core decision

Restart provenance is a first-class object.
The page owns:

- prior stop receipt or proof
- revival cause
- elapsed quiet interval
- chronology risk sentence
- current claim ceiling

## Fixed page order

1. restart event header
2. prior stop boundary card
3. revival-cause card
4. chronology-risk card
5. next-safe action rail

### 1) Restart event header

Show:

- subject / seat / node name
- restart time
- prior stop proof or receipt id
- revival cause class (`boot-revive`, `service-persistence`, `user-reopen`, `watchdog-relaunch`, `mobile-background-return`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Prior stop boundary card

Show:

- what was actually proven at stop time
- what remained unproven
- how old that proof was before restart
- whether the restart invalidates the prior receipt fully or partially

### 3) Revival-cause card

Show:

- startup-on-boot setting status
- service install status
- background privilege / notification priority status
- user action evidence
- external launcher / scheduler evidence

### 4) Chronology-risk card

Show:

- whether re-index or modification-time reinterpretation risk exists
- whether offline edits were present before stop
- whether restart can change later overwrite reading
- what stronger calm sentence is now forbidden

### 5) Next-safe action rail

Only show actions that preserve meaning, such as:

- `Open runtime stop proof`
- `Disable revival source`
- `Open contested repair review`
- `Emit restart receipt`

## Rules

### Rule 1 — restart cause must be typed, not narrated loosely

The operator must be able to tell whether comeback came from service persistence, boot startup, user action, or unknown cause.

### Rule 2 — prior proof stays visible

The page must not hide what was proven before the restart.

### Rule 3 — chronology risk is part of restart meaning

If reopen can matter for re-indexing or overwrite interpretation, the page must say so.

### Rule 4 — unknown cause remains explicit

Do not imply a reason without witness.

## Acceptance criteria

A later operator can:

- tell why the runtime came back
- tell what prior stop boundary it crossed
- tell whether chronology risk changed
- tell what stronger claim became forbidden
- tell what next-safe action exists
