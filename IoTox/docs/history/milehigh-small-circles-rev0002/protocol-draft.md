# IoToxmutorr protocol draft

## Transport lane

The control protocol uses Tox lossless custom packet identifier `0xA0`. The targeted toxcore API caps a custom packet at 1373 bytes. The fixed IoTox frame header is 41 bytes, leaving 1332 bytes for a control payload.

All integer fields are unsigned big-endian values.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 1 | packet identifier `0xA0` |
| 1 | 1 | protocol major |
| 2 | 1 | protocol minor |
| 3 | 1 | message type |
| 4 | 1 | flags |
| 5 | 4 | payload length |
| 9 | 8 | message ID |
| 17 | 8 | correlation ID |
| 25 | 8 | sequence |
| 33 | 8 | expiry Unix time in milliseconds; zero means unspecified |
| 41 | N | payload |

The decoder rejects truncation, oversized packets, wrong packet identifiers, unknown message types, and length mismatches.

## Message types

The inherited types remain:

```text
HELLO, CAPABILITIES, COMMAND, COMMAND_RESULT,
STATE_SNAPSHOT, STATE_EVENT, ACKNOWLEDGEMENT, ERROR,
PAIR_REQUEST, PAIR_RESULT, REVOKE, OTA_MANIFEST
```

rev0002 adds provisional Mutorr control types:

```text
MUTORR_HEAD          announce one linked mutable head
MUTORR_INVENTORY     summarize known heads or immutable objects
MUTORR_WANT          request missing head history or object identifiers
MUTORR_OBJECT_OFFER  advertise a transfer source and object metadata
```

These values are reserved and validated but are not yet a frozen interoperable standard. Large object bytes belong in the future Tox file-transfer manager, not in a home-grown custom-packet fragmentation layer.

## Mutable-head payload

`MUTORR_HEAD` currently carries one fixed 221-byte record.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 1 | head wire version, currently `1` |
| 1 | 32 | namespace ID |
| 33 | 32 | writer signing key |
| 65 | 8 | generation, starting at `1` |
| 73 | 32 | current immutable root digest |
| 105 | 32 | previous root digest; zero for generation `1` |
| 137 | 8 | creation Unix time in milliseconds |
| 145 | 8 | declared content bytes |
| 153 | 4 | declared object count |
| 157 | 64 | opaque signature |

Bytes `0..156` are the canonical signing body. The signature algorithm, key storage, and verification API are intentionally not selected in this revision.

Validation rules:

- namespace, writer, and root must be non-zero;
- generation must be at least one;
- generation one must have a zero previous root;
- later generations must have a non-zero previous root;
- the payload must have the exact fixed size and supported version.

After external signature verification, a receiver compares the candidate with its current head for the same namespace and writer:

```text
no current + generation 1     -> accept initial
same complete record          -> duplicate
earlier generation            -> stale
same generation, different    -> conflict
later + previous=current root -> accept advance
later + other previous        -> request history
other namespace or writer     -> different stream
```

## Planned gossip behavior

1. A writer creates immutable objects, computes a new root, links it to the prior root, signs the canonical head, and announces `MUTORR_HEAD` to its Cube neighbors.
2. A receiver verifies authorization and signature, deduplicates by message/head identity, evaluates progression, and forwards a new announcement to neighbors other than the sender.
3. A receiver missing history or objects sends `MUTORR_WANT` to one or more available peers.
4. Peers answer with inventory or object offers. Bulk transfer uses toxcore file transfer with the object digest as application identity.
5. Periodic anti-entropy compares compact inventories so sleeping devices can catch up without replaying a chatroom.

## Required future limits

Every future variable payload decoder must bound allocation, item count, nesting, string length, inventory count, request count, and total work. Queue pressure, expiry, retry, deduplication, and idempotency remain application responsibilities above Tox transport success.
