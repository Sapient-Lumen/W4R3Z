# ADR 0036: Commit a durable command before transport acknowledgement or execution

**Status:** accepted and implemented for `device.describe` in rev0010

**Supersedes:** the deliberately transient command reservation described by ADR 0035; ADR 0035
continues to define the first operation and its capability/principal binding.

## Context

A successful c-toxcore custom-packet call means the packet entered toxcore's local send queue. It
does not prove that the remote IoTox process received, persisted, authorized, started, or completed
the operation. Process death, reconnect, local `SENDQ` pressure, a lost result, or duplicate
transport delivery can otherwise create ambiguous execution.

The ratox successor should remain simple at the operator surface, but a FIFO write or CLI return
must not become an implicit execution guarantee. The first read-only operation is suitable for
constructing the stronger state machine before any setting or physical effect exists.

## Decision

When both peers negotiate `durable_commands_v1`, IoTox identifies a command by:

```text
sender Tox public key
persistent nonzero sender epoch
sender-chosen message id
```

Direction is part of the local journal locator because each peer may legitimately choose the same
epoch/message pair. Process-local friend numbers and one online epoch are not durable identity.

IoTox writes one stable-device-signed, private, bounded command snapshot in format v2. The current
implementation atomically replaces and fsyncs the complete snapshot on each accepted transition.

For outgoing requests:

1. canonical request bytes are frozen and committed before the first toxcore send;
2. each send attempt and terminal local error is committed;
3. retryable `SENDQ` reuses the exact frame, sender epoch, and message id;
4. received application receipt and result bytes are frozen and committed;
5. unfinished requests are recovered after restart or reconnect.

For incoming requests:

1. the canonical request is committed before any receipt is sent;
2. one exact `RECEIVED` receipt is frozen and committed;
3. authority admission and its current ledger head are committed;
4. `STARTED` is committed before the operation runs;
5. terminal outcome and exact result bytes are committed before the result is sent;
6. an exact duplicate replays frozen receipt/result bytes;
7. different bytes reusing the same durable key are a conflict.

`RECEIVED` means durable local admission only. It does not mean authorized, started, or completed.
Transport queue acceptance remains a separate delivery observation.

Only `device.describe` uses this path. No physical effect may be added without an operation-specific
idempotency, cancellation, crash recovery, expiry, and safety contract.

## Consequences

The one product binary now preserves command identity and terminal evidence across restart. A lost
transport acknowledgement no longer requires inventing a new logical request. Exact duplicate
replay is deterministic.

The store is integrity protected but not confidential. An attacker able to restore an older valid
signed file can still roll state back. The full-snapshot write strategy is simple and auditable but
may be unsuitable for high command rates or flash-heavy appliances. Those limitations are explicit
future work.

A client timeout still cannot mean that an operation is cancelled. The durable record must remain
inspectable until the protocol defines cancellation and a terminal cancellation result.

## Rejected alternatives

- **Treat toxcore enqueue as completion:** confuses transport with execution.
- **Generate a new message id after `SENDQ`:** duplicates one logical command.
- **Acknowledge before disk commit:** can promise receipt and forget the request after a crash.
- **Execute then persist:** permits an effect with no durable evidence or duplicate guard.
- **Use friend number plus online epoch as identity:** loses meaning across restart/reconnect.
- **Store only decoded fields:** cannot prove or replay exact canonical bytes.
- **Add GPIO immediately:** durability mechanics are not yet an actuator safety contract.
