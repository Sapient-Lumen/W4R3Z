# ADR 0018: Tox file numbers are opaque public handles

**Status:** accepted and implemented in rev0005

## Context

Current c-toxcore uses different public number ranges for incoming and outgoing transfers,
but its API says file numbers may be reused and patterns should not be relied on.

## Decision

Store and return the full `uint32_t` file number exactly as c-toxcore supplies it. Do not
truncate it, derive direction from bit fields, or invent a second local selector. Direction
is maintained as explicit transfer metadata.

## Consequences

The current implementation remains compatible with direction-encoded incoming handles
without binding policy to an undocumented pattern. Friend number plus full file number is
the live operation key; stable 32-byte file ID is the future restart/application key.
