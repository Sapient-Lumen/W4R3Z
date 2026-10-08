# Materialization lineage receipt page: visible entry, local bytes, and source-witness boundary

This receipt exists so later operators do not have to guess what `downloaded`, `kept`, `removed`, or `still available` meant at the time of action.
One durable artifact must preserve the materialization class actually reviewed and the stronger sentence that remained blocked.

## Operator question

> After a hydrate / pin / revert / delete action, what exactly became visible, what bytes became local or ceased to be local, what source witness existed, and what stronger promise was still blocked?

## When this receipt must be written

Write it whenever:

- a placeholder is hydrated
- a subtree is promoted into ongoing local residency
- local bytes are reverted to placeholders
- a propagate-delete action is accepted or blocked
- a ghost-risk or no-source warning materially changes the contract
- a placeholder-capable share is removed or its mode changes

## Receipt fields

### 1) Object identity

Record:

- receipt id
- timestamp
- operator / actor handle if known
- object kind and object id
- path at time of action
- share / seat / device context

### 2) Before-state

Record:

- prior materialization class
- prior local-byte witness (`none`, `partial`, `full`, `unknown`)
- prior future-arrival commitment
- prior source-byte witness freshness
- prior ghost-risk verdict if any

### 3) Requested intent

Record the reviewed intent:

- `hydrate-now`
- `pin-locally`
- `revert-to-placeholder`
- `delete-everywhere`
- `remove-share`
- `ignore-ghost-warning`
- `other-reviewed-intent`

### 4) Outcome

Record:

- resulting materialization class
- resulting local-byte witness
- resulting future-arrival commitment
- propagation scope actually crossed
- survivor map summary

### 5) Source-witness boundary

Record:

- source peers with byte witness if known
- freshness of that witness
- whether offline-open guarantee was allowed, conditional, or blocked
- whether the mesh risked placeholder-only state

### 6) Blocked stronger sentence

Record the strongest blocked claim, for example:

- `This file is safe to open offline indefinitely.`
- `Removing this from the device does not endanger any full copy.`
- `The visible placeholder guarantees bytes still exist somewhere.`
- `This subtree is now equivalent to sync-all.`

### 7) Reopen trigger

Record which later observations should reopen review, such as:

- last known source peer goes offline
- new arrivals beneath the pinned subtree
- share mode changed
- ghost warning fired
- permissions changed

## What this receipt must never collapse

It must never collapse these into one generic outcome line:

- visible entry vs local bytes
- one-time hydration vs ongoing residency promise
- local revert vs mesh-wide delete
- stale source witness vs proven source witness
- offline-capable now vs offline-guaranteed later
