# Instrumentation restore review page — baseline return, residue, and retention interface spec

## Purpose

Review how the product leaves temporary diagnostic posture and returns toward baseline without lying about what remains.

This page exists so `we're done collecting` and `the system is back to normal` are separated into explicit review decisions.

## Inputs

- instrumentation plan and change review
- capture window outcome
- current live settings
- retained artifacts and active rotations
- policy for keeping or removing diagnostic residue
- recipient asks that may require posture to remain active

## Primary questions this page must answer

1. Which temporary deltas should now be reversed, kept, or deferred?
2. What baseline value or posture are we returning to?
3. What diagnostic residue remains on disk or in hidden storage even after rollback?
4. What obligations remain because evidence requests are still open?
5. When would restoration be premature or dishonest?

## Sections

### 1. Return-to-baseline ledger

Per active delta show:

- current live value/state
- baseline target value/state
- proposed action (`restore-now`, `leave-on-until-return`, `keep-by-policy`, `cannot-restore-yet`, `unknown`)
- reason
- expected result after action

### 2. Residue and retention card

Show:

- retained logs / profiler traces / crash-watch outputs
- rotation and TTL behavior still in force
- whether larger buffers remain allocated
- whether hidden files or advanced overrides still exist
- what remains inspectable locally even after restoration

### 3. Pending-obligation card

Show:

- open recipient asks or capture plans that still depend on elevated posture
- whether another reproduction run is scheduled
- whether rollback would risk losing still-needed evidence
- whether cleanup may safely wait until export confirmation or ask closure

### 4. Restoration verdict card

Possible outputs:

- `safe to restore fully now`
- `restore debug logging now but keep retained artifacts`
- `keep profiler armed until next run`
- `cannot restore because restart-pending delta never actually activated`
- `cannot claim baseline yet; hidden override still present`

### 5. Next-step card

Show the smallest honest next move:

- `restore and issue posture receipt`
- `hold elevated posture for next run`
- `remove hidden override and restart`
- `reopen instrumentation change review`
- `open evidence manifest / ask fulfillment review`

## Required interactions

- `Restore selected delta`
- `Keep delta active with reason`
- `Acknowledge residue remains`
- `Schedule later restore checkpoint`
- `Open instrumentation posture receipt`
- `Reopen capture plan`

## Guardrails

- Never equate settings rollback with residue removal unless both are separately proven.
- Never hide that retained artifacts still exist after posture returns to baseline.
- Never restore a delta blindly when an open ask still depends on it.
- Never let a hidden route remain active without explicit visibility here.
- Never produce a `fully restored` verdict while any meaningful delta or override is still live.

## Output

A reviewed restoration decision preserving baseline target, still-active deltas, retained residue, deferred cleanup, and honest restoration status.
