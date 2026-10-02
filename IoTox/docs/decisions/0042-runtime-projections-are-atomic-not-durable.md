# ADR 0042 — Runtime projections are atomic but not durable

- Status: accepted
- Revision: rev0011
- Date: 2026-08-14
- Clarifies ADR 0019

## Context

IoTox publishes an ordinary private tree under `/run` (or a configured runtime directory). Readers
should not observe torn multi-byte files, but the tree is recreated on every process start and must
never be mistaken for durable product state.

Using the full durable write sequence—file `fsync`, atomic rename, and directory `fsync`—for every
status update would add needless flash traffic and latency to explicitly disposable projections.
Appending a bounded operator journal also does not make it an audit authority.

## Decision

Small runtime projection files are written to a private temporary regular file and atomically
renamed into place. Transactional directory records continue to publish their commit marker last.
Runtime projection writes deliberately do not call `fsync` and are not crash-durable.

The new per-peer `command-events` journal is likewise a bounded, rotating observation surface. It
records ingress admission or rejection and the durable key when one exists. It is not signed, not
replayed into product state, and may be lost on power failure, daemon restart, runtime-directory
cleanup, or rotation.

Authoritative durable state remains limited to stores with their own explicit contracts:

```text
Tox savedata
device identity
authority ledger
durable command store
future explicitly versioned durable stores
```

## Consequences

Readers see complete projection files without paying durable-write cost for high-churn status.
Removing or corrupting the runtime tree cannot mutate the signed stores. On restart, the daemon
reconstructs projections from authoritative state and current transport events.

Documentation and operator tools must use words such as `projection`, `journal`, and `evidence`
carefully. A line in `command-events` helps an operator correlate an ordinary write with a durable
key; only the signed command store establishes durable admission and terminal evidence.
