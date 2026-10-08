# Runtime stop contract sheet page: projection class, runtime state, drain state, and no-further-publication claim interface spec

## Purpose

Before an operator trusts a stop, closes a surface, pauses work, or retires a runtime, they need one ordinary page that answers:

> what is actually still running, what merely disappeared from view, what drain work remains, and what is the strongest honest sentence the product can still say about no further publication?

This page exists so `window closed`, `browser tab gone`, `backgrounded`, `service still running`, and `fully stopped` do not remain support-only distinctions.

## Core decision

Every serious runtime must open one first-class **Runtime stop contract sheet**.

The sheet owns:

- projection class
- runtime class
- live runtime state
- drain state
- restart posture
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. stop claim header
2. projection and runtime card
3. drain and publication card
4. restart posture card
5. claim ceiling and next-safe action rail

### 1) Stop claim header

Show at minimum:

- subject / seat / node name
- projection class (`foreground-window`, `tray-shell`, `browser-ui`, `mobile-foreground`, `service-console`, `none-visible`)
- runtime class (`foreground-process`, `background-process`, `service`, `mobile-background`, `stopped`, `unknown`)
- live runtime state (`active`, `paused`, `draining`, `stop-requested`, `stopped-unproven`, `stopped-proven`, `unknown`)
- drain state (`pending-publication`, `transfer-active`, `index-write-pending`, `quiet-observed`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `The browser surface is gone, but the service runtime remains active and the product cannot yet claim a stopped publication boundary.`

### 2) Projection and runtime card

Render rows for:

- current visible projection(s)
- actual runtime actor
- whether the current stop verb targets the projection, runtime, or both
- whether hidden/background execution is still allowed
- whether the operator's current surface can prove runtime state

Each row shows:

- current value
- evidence freshness
- scope
- whether mismatch blocks a stronger stop claim

### 3) Drain and publication card

Render rows for:

- active transfers
- queued outbound publication
- index / metadata writes pending
- last quiet observation time
- no-further-publication proof grade

Each row shows:

- active state
- witness basis
- operational consequence
- what stronger claim remains forbidden

### 4) Restart posture card

Show:

- start-on-boot posture
- service persistence posture
- mobile background / notification priority posture
- external watchdog / launcher posture
- whether an observed stop may be transient

Possible restart postures:

- `will-not-auto-revive`
- `boot-revive-enabled`
- `service-persistent`
- `background-best-effort`
- `external-relauncher-present`
- `unknown`

### 5) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open shutdown drain review`
- `Open stop proof`
- `Disable startup revival`
- `Stop service instead`
- `Emit runtime stop receipt`

## Rules

### Rule 1 — projection and runtime never collapse into one field

The operator must never have to infer from a vanished surface whether the runtime still exists.

### Rule 2 — stop claim must publish its proof ceiling

The page must say whether stop is requested, observed, proven, or still blocked by pending publication.

### Rule 3 — restart posture is mandatory

A stop without restart truth is incomplete.

### Rule 4 — stronger rejected sentence stays adjacent

The page must keep the stronger forbidden claim visible.

## Acceptance criteria

A later operator can:

- tell what surface disappeared and what runtime remains
- tell whether drain work is still pending
- tell whether no-further-publication is proven or not
- tell whether the runtime may auto-revive
- tell what stronger claim remained forbidden
