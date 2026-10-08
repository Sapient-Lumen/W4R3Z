# Instrumentation change review page — setting delta, restart gate, and side-effect scope interface spec

## Purpose

Review the exact act of changing runtime posture so the operator can later prove:

- what was changed
- by which route it was changed
- when it became effective
- what restart or dwell debt remained
- what side effects or residual risks were knowingly accepted

This page exists so `I enabled diagnostics` becomes a typed change ledger instead of remembered toggle lore.

## Inputs

- approved instrumentation plan
- live baseline values
- requested deltas and activation route
- restart state
- current participant/runtime context
- known side-effect warnings

## Primary questions this page must answer

1. What exact setting, route, or hidden file changed?
2. Is the change only staged, or actually active?
3. What restart or reproduction gate still stands between intention and effect?
4. What side effects should the operator expect while the delta is active?
5. What stronger sentence about evidence readiness is still unsupported right now?

## Sections

### 1. Delta ledger

Per selected change show:

- control / route name
- before state
- requested after state
- activation route (`settings-ui`, `tray-affordance`, `power-user`, `hidden-file`, `config-edit`, `unknown`)
- change authority
- time of change
- current activation verdict (`staged`, `active`, `restart-pending`, `failed`, `unknown`)

### 2. Restart and activation card

Show:

- whether restart is required
- whether restart has already happened
- whether the product has positive evidence the new posture is active
- whether a dwell or repro window still needs to start
- strongest honest sentence now, such as `debug logging requested but not yet active until restart`

### 3. Side-effect scope card

Show:

- storage growth risk
- rotation / retention side effects
- CPU / latency / responsiveness risk
- privacy/sensitivity expansion
- subject / participant scope affected
- whether the change touches only this incident or broad product posture

### 4. Capture-readiness card

Show:

- earliest trustworthy capture start
- minimum dwell after symptom reproduction
- whether other pending deltas must activate first
- whether the product should open `Coordinated capture run` next or hold for restart

### 5. Overclaim guard card

Show:

- one strongest allowed claim
- one stronger forbidden claim
- what later receipt must preserve about this change

## Required interactions

- `Confirm change applied`
- `Record restart completed`
- `Mark change failed`
- `Rollback this delta`
- `Open coordinated capture run`
- `Hold until restart`
- `Open instrumentation restore review`

## Guardrails

- Never let a staged delta masquerade as active.
- Never hide the route by which a change was made.
- Never claim capture readiness if restart or dwell conditions are still unmet.
- Never suppress side-effect scope just because the change is temporary.
- Never collapse broad posture changes into a per-incident story if they actually affect the whole runtime.

## Output

A reviewed instrumentation-change object preserving exact deltas, activation route, restart truth, side-effect scope, and honest readiness language.
