# Debug capture review page: activation, restart window, and log-rotation cost interface spec

## Purpose

This page answers:

> if I enable debug logging here, when does it become real, how long should it run, how much local log residue can it create, and what stronger sentence about adequacy is still blocked?

The page exists because `enable debug logging` is not the same thing as `sufficient incident evidence now exists`.

## Why this must be a first-class page

Current official Resilio docs still say debug capture can be enabled through settings or a `debug.txt` file, should be followed by restart to ensure it is active, should run for at least 15 minutes after reproduction, rotates around `log_size`, and can leave two large local log bodies (`sync.log` and `sync.log.old`) rather than one tiny artifact.

AnonSync should therefore expose one dedicated **Debug capture review** page.

## Fixed page order

1. activation verdict
2. restart and reproduction card
3. collection-window card
4. rotation and residue card
5. apply / defer rail

### 1) Activation verdict

Show:

- activation path (`ui-toggle`, `debug-file`, `inherited-on`, `unknown`)
- activation state (`off`, `armed-awaiting-restart`, `collecting`, `collecting-after-repro`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `Debug capture has been armed but restart is still the last unfulfilled step before we can treat new log rows as intentional evidence for this incident.`

### 2) Restart and reproduction card

Show:

- whether restart is required
- whether restart has been completed since activation
- whether the target incident has been reproduced yet
- timestamp of the first relevant post-restart observation if known

### 3) Collection-window card

Show:

- recommended minimum collection window
- elapsed collection time after reproduction
- sufficiency verdict (`too-short`, `borderline`, `sufficient`, `stale`, `unknown`)
- next honest act (`keep collecting`, `reproduce now`, `review before send`, `unknown`)

### 4) Rotation and residue card

Show:

- configured rotation size
- practical maximum retained local volume under current rotation rules
- log TTL if known
- mobile adjustability (`adjustable`, `not adjustable`, `unknown`)
- cleanup boundary (`disable only`, `cleanup command available`, `manual deletion needed`, `unknown`)

### 5) Apply / defer rail

Only show actions such as:

- `Restart and begin capture`
- `Mark issue reproduced now`
- `Increase temporary log budget`
- `Proceed to support-lane proof`
- `Stop capture and emit receipt`

## Rules

### Rule 1 — restart must be treated as a truth boundary

The page may not blur `toggle clicked` and `capture certainly active`.

### Rule 2 — duration must be attached to reproduction, not only activation

A page that knows logging has been on for an hour but the incident was reproduced 30 seconds ago must still say `too-short`.

### Rule 3 — residue cost must be public before send

Operators should see the local cost before turning on a larger rotation budget or leaving logs enabled.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- how debug capture was activated
- whether restart is still required
- whether the incident has actually been reproduced yet
- whether enough post-reproduction time has elapsed
- how much local rotated residue this lane can keep
