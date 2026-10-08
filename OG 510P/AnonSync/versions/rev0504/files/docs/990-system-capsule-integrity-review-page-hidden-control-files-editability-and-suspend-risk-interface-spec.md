# System capsule integrity review page — hidden control files, editability, and suspend risk

## Purpose

Review a pending action that may damage, replace, omit, regenerate, or relocate service-critical control substrate.

This page is required before:

- deleting hidden control entries
- moving a subject without its capsule
- rehoming / rebinding while regenerating capsule state
- importing a tree whose capsule lineage is uncertain
- cleaning hidden files in bulk

## Inputs

- subject identifier
- current control-substrate sheet
- pending action intent
- observed capsule contents and health
- any archive / salvage presence

## Must show

### 1. Pending mutation summary

Use explicit language such as:

- `Delete service capsule`
- `Regenerate service capsule`
- `Move user content without capsule`
- `Replace current capsule with imported capsule`

Never compress this to `clean hidden files` or `fix folder`.

### 2. Risk verdict

Possible verdicts:

- `safe visibility-only`
- `policy-only change`
- `capsule health repair`
- `capsule lineage fork`
- `capsule deletion suspends sync`
- `unknown; inspect before apply`

### 3. Direct consequences

Must enumerate likely outcomes:

- sync continues unchanged
- sync pauses pending reread
- sync suspends until re-add
- subject becomes new synchronization instance
- archive/salvage implications
- downstream peers see successor rather than continuation

### 4. Preservation ladder

Offer reviewed alternatives in order:

1. export/snapshot capsule and sidecars
2. export archive/salvage material
3. perform non-destructive health check
4. prepare successor branch
5. destructive regenerate / remove

### 5. Human-readable warning copy

The warning must say when the system is about to cross from `repair` into `new instance` or from `cleanup` into `sync suspension`.

## Approval barrier

When verdict is `capsule deletion suspends sync`, `capsule lineage fork`, or `unknown`, the operator must approve against:

- subject identity
- local path
- current owner
- consequence class
- preservation status

## Receipt obligations

The resulting receipt must preserve:

- requested action
- final verdict
- preservation steps taken or declined
- whether subject continuity survived
- stronger blocked sentence such as `this was harmless cleanup`
