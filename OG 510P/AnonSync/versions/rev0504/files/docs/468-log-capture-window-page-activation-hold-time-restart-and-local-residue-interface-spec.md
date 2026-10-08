# Log capture window page: activation, hold time, restart, and local residue interface spec

## Purpose

This page answers:

> what exact diagnostic capture family is active right now, what had to be changed to activate it, how long must it run before it is meaningful, and what local residue does it leave behind?

The page exists because `Enable debug logging`, `send statistics`, `profiler`, `debug.txt`, and `restart` are not the same capture contract.

## Core rule

Every non-trivial diagnostic capture change must expose one first-class **Log capture window** page before the operator treats the evidence as sufficient.
That page owns:

- capture family
- activation route
- restart boundary
- hold-time sufficiency
- local artifact / retention residue

## Primary layout

The page always renders the same regions:

1. capture verdict
2. activation card
3. hold-time sufficiency card
4. local artifact and retention card
5. stop / export / residue card

### 1) Capture verdict

Show:

- capture label
- capture verdict: `anonymous-metrics`, `debug-logs`, `debug-logs-awaiting-restart`, `profiler-window`, `crash-artifact-awaiting-failure`, `mixed`, `unknown`
- strongest honest summary
- one next honest action

### 2) Activation card

Show:

- how the capture was enabled (`settings-toggle`, `advanced/power-user`, `debug-file`, `service/runtime switch`, `unknown`)
- whether restart is still required or already satisfied
- when activation last changed
- which capture family this activation actually affects

The operator must be able to answer: **what did I really turn on, and is it actually active yet?**

### 3) Hold-time sufficiency card

Show:

- minimum recommended capture window
- current elapsed time since activation or reproduction
- whether evidence is `too-short`, `probably-sufficient`, `sufficient`, or `stale-after-repro`
- whether additional reproduction is still required

### 4) Local artifact and retention card

Show:

- local artifact classes currently being written (`sync.log`, rotated log zip, `profiler.dat`, crash dump placeholder, metrics only)
- retention basis (`ttl`, `size cap`, `rotation`, `until manually cleared`, `unknown`)
- strongest current footprint estimate
- whether the capture lives in a different storage root because of service account or config mode

### 5) Stop / export / residue card

Show:

- whether the capture auto-stops or must be manually disabled
- whether stopping capture also clears old artifacts or only future collection
- whether any artifacts remain after export or stop
- the next reviewed page: `Report send` or `Crash artifact`

## Honest outputs

This page may conclude:

- `debug logs enabled but restart still pending`
- `capture active · 4m elapsed · not yet sufficient`
- `profiler active · local profiler.dat rotating`
- `anonymous metrics only · no debug evidence window active`
- `crash-capture path armed · waiting for failure event`

It may not collapse these into one vague `diagnostics on` verdict.

## Rules

### Rule 1 — activation route must remain visible after the fact

A later operator must be able to see whether capture came from a UI toggle, hidden file, or advanced override.

### Rule 2 — stop must never imply cleanup unless cleanup is actually proven

Disabling logging is not the same as proving rotated logs or profiler traces were removed.

### Rule 3 — sufficiency must never be inferred from send alone

A packet can be sent while still being too thin or too stale for the diagnosed incident.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what exact capture family is active now
- whether restart is still required
- whether enough evidence time has elapsed
- which local artifacts are being written and retained
- what will remain after stop or export
