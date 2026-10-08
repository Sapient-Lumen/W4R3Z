# Rollout-health event timeline page: warning flap, recovery, escalation, and sentence change interface spec

## Purpose

The **Rollout-health event timeline** keeps health truth from collapsing into one latest badge.
It preserves how warnings, graphs, logs, escalations, and safe sentences changed over time.

## Required event families

The timeline must preserve at least:

- new warning appeared
- warning cleared
- warning flapped
- metrics degraded
- metrics recovered
- artifact capture requested
- artifact captured
- escalation opened
- escalation closed
- confidence grade changed
- strongest safe sentence changed
- promotion widened
- promotion frozen
- rollback started
- rollback ended

## Required timeline fields

Every event row must show:

- timestamp
- event family
- affected rings or cohorts
- evidence source
- confidence delta
- sentence delta
- actor class (`system`, `operator`, `support`, `unknown`)

## Hard rules

- a recovered state must not erase the earlier degraded event
- flapping warnings must stay visible as flapping, not as alternating unrelated events
- timeline entries must preserve when sentence strength improved or weakened
- escalation events must preserve whether they produced decision-grade evidence or only more artifacts
