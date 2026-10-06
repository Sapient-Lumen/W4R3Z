# ADR-0018: Resource limits are enforced by OS primitives (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD enforces resource profiles using FreeBSD primitives (rctl + cpuset) rather than an internal scheduler.

## Consequences
- fewer moving parts in DeriveBSD
- leverages well-tested kernel features
- requires clear documentation of limitations and accounting prerequisites
