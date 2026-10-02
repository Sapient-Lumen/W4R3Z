# ADR 0003: Structured core first, ratox-style façade second

**Status:** accepted in principle

## Context

Ratox’s files and named pipes are elegant and highly scriptable, but FIFOs do not natively encode durable request, response, deadline, authorization, idempotency, and error semantics.

## Decision

Build the primary local API as a structured Unix-domain protocol. Add a ratox-inspired filesystem/FIFO façade later as an adapter over that API.

## Consequences

- Shell simplicity remains a product feature.
- The filesystem surface is not forced to become the durable database.
- CLI, mobile bridges, and automation services share one set of semantics.
- The façade can preserve “just werx” workflows without hiding failure states.
