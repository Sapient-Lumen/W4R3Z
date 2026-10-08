# Decision timeline page: threshold crossing, deferral, escalation, and reopen events interface spec

## Purpose

A decision is rarely one moment.
The operator needs a timeline that answers:

> when did the threshold actually change, when was action deferred, when did escalation become justified, and when did the earlier proof lose force?

## Timeline event types

Supported `decision_event_type` values:

- `threshold-opened`
- `threshold-cleared`
- `threshold-failed`
- `decision-deferred`
- `monitor-posture-entered`
- `action-authorized`
- `action-blocked`
- `escalation-justified`
- `escalation-declined`
- `proof-expired`
- `proof-revalidated`
- `reopen-trigger-fired`
- `fallback-invoked`

## Required columns

- event time
- prior route
- new route
- evidence delta causing the shift
- uncertainty delta
- stronger sentence gained or lost
- owner after event

## Hard rules

### Threshold shifts must name the cause

A transition from `monitor` to `bounded-action`, or from `bounded-action` to `escalation`, must name the packet, fact, timeout, conflict, or external event that changed the route.

### Deferral is not absence

If the decision is intentionally deferred, the timeline must show:

- why deferred
- what watch is active
- what event will end the deferral

### Reopen must weaken something concrete

A reopen event must say which previously allowed action or stronger sentence lost force.
