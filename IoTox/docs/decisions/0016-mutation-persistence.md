# ADR 0016: Transport mutations and shutdown have separate save policies

**Status:** accepted and implemented in rev0005

## Context

Saving only on graceful shutdown loses newly accepted or removed friends after a crash.
Always coupling every lifecycle to the same switch hides that difference.

## Decision

Expose independent `save_state_after_mutation` and `save_state_on_stop` policies. Friend
addition/removal can be durably committed immediately using atomic private replacement.

## Consequences

Tests can isolate both behaviors. Products may tune flash-write policy deliberately rather
than accidentally relying on graceful shutdown. More advanced batching requires an explicit
durability contract.
