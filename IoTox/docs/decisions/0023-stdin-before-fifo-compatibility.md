# ADR 0023: Standard input is the first Unix write surface; FIFOs remain a façade

**Status:** accepted and implemented in rev0006

## Context

Ratox's named pipes are elegant, but a FIFO write does not inherently carry request identity,
response routing, deadlines, cancellation, authorization context, or durable acceptance.
IoTox still needs immediate Unix composition while those semantics are built correctly.

## Decision

The single `iotox` executable accepts bounded, exact bytes from standard input for profile
name, status message, normal text, and action text. The data is transported over the same
versioned local `SOCK_SEQPACKET` contract as ordinary CLI operations. Text and hexadecimal
forms remain available for convenience.

Writable ratox-compatible FIFOs are deferred until they can translate into explicit internal
requests and publish errors/results honestly. They will be a compatibility surface over the
structured core, never the source of truth.

## Consequences

Today, ordinary pipelines work without inventing ambiguous FIFO semantics:

```sh
printf '%s' 'hello' | iotox message-stdin PEER_KEY
cat binary-note | iotox action-stdin PEER_KEY
```

The operator still receives a synchronous local result. FIFO compatibility remains a real
northstar, but its implementation cannot silently promise durability or execution that the
core does not yet provide.
