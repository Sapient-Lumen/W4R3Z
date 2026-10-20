# ADR 0037 — Directional local command lanes

**Status:** accepted and implemented in rev0010  
**Date:** 2026-08-14 America/New_York

## Context

A durable wire command is identified by the sender's Tox public key, persistent sender epoch, and
message identifier. The same IoTox process can both send to and receive from one peer. A peer can
legitimately choose a wire tuple equal to a tuple selected locally; direction is not part of the
wire identity and must not be invented on the network.

A local journal, however, must be able to retain both transactions. Keying the store only by the
wire tuple allows an incoming record to collide with an unrelated outgoing record.

## Decision

The canonical local locator is:

```text
direction + peer Tox public key + sender epoch + message id
```

`direction` is `incoming` or `outgoing` and is local metadata. For an outgoing record, `peer` is
the receiver and the sender epoch is IoTox's persistent local epoch. For an incoming record,
`peer` is the sender and the sender epoch came from the request frame.

The wire format remains unchanged. Receipts and results correlate with the sender-defined tuple;
the local direction lane only prevents storage and operator-lookup ambiguity.

## Consequences

- Equal wire identifiers in opposite directions coexist without mutation or accidental replay.
- Store ordering, signatures, CLI lookup, and runtime-tree paths include direction.
- Duplicate detection is lane-local and still compares the exact frozen request bytes.
- A migration from command-store v1 to v2 is explicit; old transient keys are not silently
  reinterpreted.
- Any future database schema must preserve this distinction even if it uses separate tables.
