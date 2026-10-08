# Remedy-hardening-attestation successor beneficiary-usability timeline page — land, placeholder, hydrate, block, open, fix, and withdraw events

## Purpose

This page records the life of one landed reviewed result from initial landing through placeholder exposure, hydration, open success, permission failure, source disappearance, blocker repair, contradiction, supersession, or withdrawal.
It exists so the product can tell whether a result that landed also became beneficiary-usable, stayed merely visible, or later lost usability again.

## Required event families

The timeline must support at least these events:

- reviewed beneficiary action bound
- landed result received
- folder visible only
- placeholder created or preserved
- hydration requested
- hydration succeeded
- hydration failed due to missing source peer
- shell or handler affordance missing
- permission denied
- lock observed
- path or encoding blocker observed
- filesystem error observed
- open succeeded
- modify succeeded
- update-liveness degraded
- blocker repaired
- beneficiary-usable sentence upgraded
- beneficiary-usable sentence narrowed
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched subject identifier if applicable
- before state
- after state
- whether beneficiary-usability confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- reviewed beneficiary action bound
- first landed or visible event
- first hydration or blocker event
- first beneficiary-usable upgrade
- first later narrowing or supersession

### Full audit view

Show:

- every placeholder, hydration, open, modify, and blocker event
- every source-dependency change
- every access and update-posture change
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- visible only
- placeholder only
- source-dependent
- bytes local
- open succeeded
- modify succeeded
- workaround required
- permission blocked
- lock blocked
- path or encoding blocked
- update posture degraded
- usable sentence blocked
- receipt superseded

## Hard rules

The timeline must never allow:

- `landed` to silently become `usable`
- `visible` to silently become `materialized`
- `bytes local` to silently become `permitted and live-updating`
- `opened once` to silently become `usable as intended in general`
