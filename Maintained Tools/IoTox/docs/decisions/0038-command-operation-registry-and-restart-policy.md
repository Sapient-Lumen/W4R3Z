# ADR 0038 — Command operation registry and explicit restart policy

**Status:** accepted and partially implemented in rev0010  
**Date:** 2026-08-14 America/New_York

## Context

Adding a numeric command enum without binding its authorization, encoding, idempotency, and crash
behavior would let protocol declarations drift away from execution. That is tolerable for a
read-only research query and dangerous for settings or physical effects.

## Decision

Every admitted operation must have one registry entry that binds at least:

```text
stable wire name
stable numeric operation value
advertised operation bit
required application capabilities
read-only versus mutating class
restart/re-execution policy
```

The registry is the source used by parsing, advertisement, capability checks, and durable recovery.
An enum value with no registry entry is rejected. rev0010 registers only `device.describe` and
marks it read-only and safe to re-execute after restart.

Before any mutating operation is registered, the policy object must also grow explicit input
bounds, idempotency/effect semantics, expiry policy, cancellation policy, and result schema.

## Consequences

- The implementation cannot advertise an operation merely because an enum value exists.
- Automatic restart recovery is an operation policy, not a blanket journal behavior.
- `device.describe` may be reconstructed and retried from exact durable bytes.
- Physical actions remain prohibited from generic re-execution until their effect contract is
  separately accepted and tested.
- The current registry is intentionally small and may be extracted from `agent.cpp` with the
  durable engine, without changing the wire values.
