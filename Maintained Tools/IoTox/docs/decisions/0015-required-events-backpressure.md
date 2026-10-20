# ADR 0015: Required transport events apply backpressure

**Status:** accepted and implemented in rev0005

## Context

An unbounded callback queue permits memory exhaustion. A generic drop-oldest queue can
silently discard friend requests, packets, or file protocol events and corrupt semantics.

## Decision

Bound the transport event queue. Events required to preserve protocol meaning block the
owner producer until capacity exists or shutdown begins. Observational diagnostics may be
evicted. A cumulative drop count is carried into later events and status.

## Consequences

Memory is bounded without pretending all events are equal. Slow consumers can delay toxcore
iteration, so queue sizing and consumer health remain operational concerns. Future durable
application commands need a persistent queue above this transport layer.
