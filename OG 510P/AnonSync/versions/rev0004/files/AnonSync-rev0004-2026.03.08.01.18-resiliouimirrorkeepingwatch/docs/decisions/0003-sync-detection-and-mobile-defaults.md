# 0003 — Sync detection, encrypted staging, and mobile defaults

- status: accepted
- date: 2026-03-08

## Context

The product should track Resilio's proven operational behavior where reasonable, especially around placeholders, permissions, and change detection. Mobile must be supported early.

## Decision

AnonSync should adopt the following defaults:

- file notifications accelerate detection but do not define truth
- correctness depends on a durable local index plus scheduled rescans
- selective sync / placeholders are the default mobile posture
- mobile defaults to Tor transport
- mobile I2P is opt-in
- encrypted sink mode should be staged before any richer untrusted live-peer mode
- permissions should align closely with RO / RW / Owner semantics

## Consequences

- the index and rescan model must be designed early, not deferred as an implementation detail
- placeholder semantics are part of the core model, not a UI add-on
- mobile storage and battery policies need to be explicit
- future encrypted-peer work should preserve room for a more powerful untrusted mode later
