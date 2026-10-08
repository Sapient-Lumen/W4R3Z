# Self-edge lineage receipt page: source, target, self-peer lane, and suspension boundary

This receipt exists so same-host derivatives leave durable evidence.
Later operators should not have to rediscover whether a target was an ordinary share, a self-edge derivative, a recreated successor, or a suspended derivative that died with its source or license.

## Receipt purpose

Preserve the reviewed truth for one self-edge derivative event, including:

- source identity and path at review time
- target identity and path at review time
- topology verdict
- self-peer / discovery-bypass posture
- rights ceiling
- lifecycle coupling and reattach boundary
- source byte witness class
- entitlement dependency and suspension outcome
- strongest safe sentence allowed and stronger sentence blocked

## Required receipt sections

### 1) Event identity

Show:

- receipt id
- timestamp
- event class: `create`, `re-share`, `suspend`, `resume`, `remove-with-source`, `reattach-review`, `blocked`
- initiating actor / channel if known

### 2) Source and target lineage

Show:

- source subject id and path
- derivative target path
- whether the derivative belonged to a fanout set
- predecessor receipt if this event replaced an earlier derivative object

### 3) Topology verdict

Show:

- relationship class between source and target
- loop verdict
- whether the target was blocked or approved
- why a stronger topology sentence was refused, if applicable

### 4) Self-peer and route posture

Show:

- self-edge confirmation
- explicit route class: `self-only`, `not ordinary peer discovery`
- any evidence that the operator had confused the object with an ordinary peer lane

### 5) Rights and lifecycle ceiling

Show:

- source rights at event time
- derivative rights ceiling at event time
- whether `Owner` was unavailable
- whether future edits require remove-and-re-share
- what source disconnect/removal would do
- what source return would still require

### 6) Materialization and entitlement posture

Show:

- source byte witness class
- derivative byte promise allowed at the time
- entitlement state
- whether the derivative was active, suspended, or removed
- whether suspension was caused by source loss, entitlement loss, or explicit operator choice

### 7) Strongest safe sentence

Examples:

- `Approved as loop-safe self-edge derivative with read-only ceiling.`
- `Approved as writable self-edge derivative, but byte promise is limited to source-held files.`
- `Blocked because target is a parent/child overlap with the source.`
- `Suspended because required entitlement is no longer active.`
- `Source returned, but manual derivative reattach is still required.`

### 8) Reopen triggers

Show the exact condition that should reopen review, such as:

- source rights change
- source disconnect/removal
- source reappearance after teardown
- source materialization improvement
- entitlement restoration or expiry
- target relocation

## What the receipt must never collapse

It must never collapse these into one vague outcome:

- created vs recreated
- suspended vs removed with source
- self-edge vs ordinary share
- rights ceiling vs rights actually exercised
- policy independence vs byte independence
- entitlement warning vs entitlement-caused stoppage

## CLI expectation

`anonsync receipt show <id>` must be enough to reconstruct the derivative's topology, ceiling, suspension cause, and reattach boundary without opening support notes or historical UI screenshots.
