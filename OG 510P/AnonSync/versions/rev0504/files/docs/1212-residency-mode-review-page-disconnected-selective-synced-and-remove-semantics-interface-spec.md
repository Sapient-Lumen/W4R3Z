# Residency-mode review page — disconnected, selective, synced, and remove semantics

## Purpose

Review a concrete folder or object before the interface states that it is simply `available`, `connected`, or `removed`.
This page exists because disconnected rows, placeholder-backed folders, and fully synced folders are not the same truth.

## This review must distinguish

- disconnected row with no path yet;
- connected path in Selective Sync with placeholder-only residency;
- mixed mode where some items are materialized and some remain placeholders;
- fully synced local residency;
- remove or disconnect actions that change row state, path state, or shared existence differently.

## Inputs the page must collect

### Presence facts

- subject folder or file reference
- current sync mode
- whether a local path is bound
- placeholder count and materialized count
- whether placeholders were recently removed by disconnect or path change

### Source and fetch facts

- peers currently online with matching bytes
- whether fetchability depends on linked-device mode or remote swarm state
- any active `no source peers online` warning
- whether a parent source share is itself placeholder-only

### Action facts

- requested gesture (`connect`, `disconnect`, `remove from this device`, `remove from all devices`, `sync to this device`)
- current permission authority
- active safety rail settings affecting placeholder deletion or remove-all visibility
- archive consequence, if any

## Decision ladder

### Branch 1 — disconnected row only

Use this branch when the object is shown for later action but has no local path.
The page should show:

- that visibility is row-level, not byte-level
- the path that will be proposed on connect, if known
- that later connect may create a new directory rather than restore the old path automatically
- that no fetch claim is safe yet

### Branch 2 — placeholder-backed presence

Use this branch when a path exists but content is represented primarily by placeholders.
The page should show:

- that namespace is present without local bytes
- whether at least one source peer is currently proven for materialization
- that `Remove from this device` is a residency reversion, not shared deletion
- whether disconnect will remove placeholders from the local filesystem

### Branch 3 — mixed residency

Use this branch when some content is materialized and some remains placeholder-backed.
The page should show:

- local byte coverage percentage
- whether future fetch still depends on remote source health for the placeholder remainder
- whether current action affects only local materialized bytes or the shared object globally
- whether a parent-source dependency weakens downstream guarantees

### Branch 4 — fully synced residency

Use this branch when local bytes are fully present.
The page should show:

- that current access does not prove future remote fetchability is irrelevant
- whether delete-like actions are local, shared, or reviewed destructive acts
- whether disconnect preserves local bytes while changing sync participation
- whether a later reconnect may bind to a new path unless corrected

## Future-risk mitigation panel

The page must include a separate panel for policy, not merged with the current verdict.
It must offer:

- `Prefer selective residency on this device`
- `Prefer full residency on this device`
- `Block destructive placeholder deletion paths`
- `Require explicit review before remove-from-all gestures`

The panel must say plainly that mode choice is about future residency posture, not proof that bytes are recoverable later.

## Required warnings

- `Disconnected visibility is weaker than local path existence.`
- `Placeholder presence is weaker than byte residency.`
- `Materialized now is weaker than durable future fetch guarantee.`
- `Disconnect and remove do not have the same blast radius.`
- `Reconnect may create a different local path unless path authority is reviewed.`

## Review outputs

- residency-mode class
- local byte coverage summary
- current fetchability grade
- action blast-radius grade
- optional future residency recommendation
