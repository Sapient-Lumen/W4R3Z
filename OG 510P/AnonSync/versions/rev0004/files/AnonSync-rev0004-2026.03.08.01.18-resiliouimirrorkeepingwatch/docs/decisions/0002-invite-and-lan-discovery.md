# 0002 — Invite model and LAN discovery posture

- status: accepted
- date: 2026-03-08

## Context

The project wants invite-only sharing while also keeping LAN discovery enabled by default for ergonomics and performance.

## Decision

AnonSync will follow a Resilio-like sharing posture centered on folder-level sharing permissions, but the canonical invite primitive should behave as a **folder + device + permission bundle**.

LAN discovery remains **enabled by default**, but the discovery signal should represent an **invite-derived rotating token**, not a stable share identifier.

## Consequences

- invite objects must carry enough information to bind folder scope, recipient device scope, and permission scope
- LAN beacons need rotation semantics and an unlinkability story
- the implementation should not copy Resilio's discovery wire image literally
- invite-only remains the baseline; broader discovery is not assumed
