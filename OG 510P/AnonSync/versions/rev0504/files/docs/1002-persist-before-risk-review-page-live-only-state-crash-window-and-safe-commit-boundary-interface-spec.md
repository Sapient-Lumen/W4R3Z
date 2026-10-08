# Persist-before-risk review page — live-only state, crash window, and safe commit boundary

## Purpose

Require an explicit review whenever the operator is about to rely on a change that is currently stronger in memory than on disk or at next boot.

This page exists to answer:

- `am I about to take a risky action based on live-only state?`
- `what crash/restart window still exists?`
- `should I persist first, continue live-only, or cancel?`

## Required sections

### 1. Risk summary

Must show:

- dependent action
- state dependency
- current durability class (`live-only`, `live-plus-pending-save`, `persisted-but-not-boot-authoritative`, `boot-authoritative`, `unknown`)
- consequence if the process exits or rebinds before persistence

### 2. Crash window block

Must publish:

- current save cadence or flush posture
- whether a manual flush is available
- whether restart/crash can revert the pending dependency
- whether the state would survive orderly stop only, unclean stop only, both, or neither

### 3. Safer alternatives

Render explicit choices such as:

- `Persist first, then continue`
- `Continue using live-only state`
- `Convert to one-shot execution ticket`
- `Cancel and keep reviewing`

### 4. Strongest safe sentence

Examples:

- `You can continue now, but the new exposure boundary is not yet durably persisted.`
- `Persist first is the safer path because this action depends on settings that may be lost on crash or shadowed on reboot.`

### 5. Blocked stronger sentence

Examples:

- `Continuing now is equivalent to continuing after a persisted save.`
- `If the runtime restarts, the action basis remains the same.`

## Interaction rules

- default primary action should be `Persist first, then continue` when available
- destructive or exposure-widening actions must not silently bypass this page if dependency class is weaker than required
- page must say when no flush primitive exists and therefore the only honest path is one-shot/live-only reliance or cancellation

## Receipt obligations

Any receipt derived from this page must preserve:

- dependent action
- dependency durability class
- chosen continuation posture
- crash-window explanation
- strongest safe sentence
- blocked stronger sentence
