# 0004 — Performance and adaptation shape

## Principle

Make adaptation explicit, profile-driven, and measurable.

## Current shape

### Resource profiles

The archive now assumes named resource profiles rather than one universal default:

- desktop-balanced
- desktop-throughput
- mobile-tor-default
- mobile-tor-frugal
- nas-balanced

These profiles are not permanent UX labels. They are internal operating envelopes that can later map to product settings or automatic recommendations.

### Discovery adaptation

The current architectural direction is:

- LAN discovery remains enabled by default
- beacons are invite-scoped, never stable share-scoped
- startup and network-change events may trigger short discovery bursts
- steady-state beaconing should be capped and low-rate
- once a peer relationship is healthy, beaconing should back off rather than keep shouting

This is intentionally profile-aware. Mobile-frugal should back off more aggressively than desktop-throughput.

### Sync engine posture

The sync engine should separate:

- **small-file direct send** for fewer requests and better latency
- **piece-based transfer** for large files and resumability
- **watchers** for responsiveness
- **durable index + rescans** for correctness

### Local state posture

The current archive assumption is a local SQLite-backed index with WAL enabled and no network-hosted database.

## Non-goal in this note

This note does not settle exact beacon intervals, exact piece size, or exact scheduler weights. Those belong to benchmark work and later protocol notes.
