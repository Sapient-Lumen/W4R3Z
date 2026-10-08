# 31 — Event Log + Delta Semantics (v0.19)

You are already building an “unreliable network” coordination system, except the network is:
- unknown slice counts
- truncation
- human interruptions
- terminal broadcast glitches

So the control plane should behave like an **append-only event log** with bounded summaries, and the worker agents should mostly consume **deltas**.

## Cursor model
- Every WS mutation increments `CURSOR`.
- A delta feed is `DELTA(since_cursor)` and MUST be bounded.
- Full refresh is reserved for:
  - bootstrap
  - emergency recovery
  - explicit zoom requests

## Delta classification
- Mandatory deltas: always shown (cannot be muted)
- Global HOT deltas: shown based on deterministic promotion rules (see 27_global_hot_promotion_table.md)
- Local deltas: shown based on ROLE subscription + TOUCH overlap
- Exploration deltas: controlled (and optionally rare true random)

## Why not CRDT (initially)
CRDTs are powerful for concurrent text edits, but they add complexity and surprise semantics.
In v0.x, prefer:
- soft/hard leases
- patch-shaped exports
- deterministic integrator arbitration

CRDT-like thinking *is* still useful for:
- representing your control state as deltas
- supporting eventual consistency of views under jitter

## “Exactly-once” is a fantasy
Design for:
- at-least-once deltas
- occasional repeats
- occasional missing deltas (bounded damage)
The BCC anytime packet + WS strictness is your compensating control.

Anytime packet principle aligns with anytime algorithms; see 67_blackboard_rationale_anytime_packets.md.
