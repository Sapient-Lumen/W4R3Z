# IoTox protocol draft

## Transport lane

The frame introduced in rev0001 and retained in rev0002 uses Tox lossless custom packet identifier `0xA0`. c-toxcore permits application lossless identifiers in the 160–191 range and caps a custom packet at 1,373 bytes in the targeted API.

The frame is a testable seed, not yet a frozen interoperable IoTox standard.

## Current envelope

All integer fields are unsigned big-endian values.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 1 | packet identifier: `0xA0` |
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

Maximum payload in this lane is 1,332 bytes.

## Seeded message types

```text
HELLO
CAPABILITIES
COMMAND
COMMAND_RESULT
STATE_SNAPSHOT
STATE_EVENT
ACKNOWLEDGEMENT
ERROR
PAIR_REQUEST
PAIR_RESULT
REVOKE
OTA_MANIFEST
```

The enumeration reserves and validates values so tests and fuzzing can proceed. Numeric assignments, required fields, signatures, and compatibility rules still require a protocol-freeze decision.

## Planned semantics

### Negotiation

Peers begin with `HELLO` and `CAPABILITIES`. Major-version mismatch is terminal unless an explicitly supported compatibility mode exists. Unknown optional fields are ignored. Unknown required capabilities produce a structured incompatibility result.

The handshake must eventually bind:

- application device identity;
- controller identity;
- Tox route endpoint identity;
- current ownership epoch;
- protocol and capability set;
- replay-resistant session context.

### Authorization

Tox session authentication is necessary but insufficient. Hardware-affecting messages must be authorized against the device's independent IoTox ledger. High-consequence commands should carry application-level signatures tied to the target device, ownership epoch, message ID, and deadline.

A friend number is process-local and may change after savedata reload. It must never be a durable authorization identifier.

### Idempotency

A hardware-affecting command carries a stable message ID. The device records enough recent terminal results to recognize a retry and return the prior result without repeating the action.

### Acknowledgement levels

```text
RECEIVED   accepted into the durable inbox
STARTED    execution began
SUCCEEDED  completed successfully
FAILED     terminal failure
EXPIRED    intentionally not executed because its deadline passed
```

Tox transport success is not equivalent to any of these application states.

### Offline behavior

IoTox needs persistent inbox and outbox queues with expiry, retry backoff, deduplication, priority, bounded storage, and replacement semantics for desired-state messages. Tox itself is not treated as an offline mailbox.

### Recall-root re-entry

A future recovery knock or friend request must not transmit the recall phrase or root. It should carry only public/replay-safe discovery material, followed by an authenticated IoTox handshake proving a device certificate and current ownership epoch.

The precise object formats are intentionally not invented in rev0002. They depend on the application key hierarchy and real two-node Tox re-entry experiment.

### Bulk content

Firmware, diagnostics, exports, and other large content should use Tox file transfer rather than a home-grown packet-fragmentation system. A signed manifest belongs in the control protocol; artifact bytes belong in the transfer manager.

## Payload encoding

CBOR is the current preference, but rev0002 keeps the payload opaque. Before selecting a library, evaluate:

- deterministic/canonical encoding support;
- bounded allocation and decoder limits;
- C++ API quality and maintenance;
- license compatibility;
- fuzzing history;
- interoperability with mobile and scripting clients.

## Decoder safety rules

The implemented fixed-frame decoder rejects:

- packets shorter than the fixed header;
- packets larger than the toxcore custom-packet maximum;
- a non-IoTox packet identifier;
- unknown message type values;
- declared payload lengths that do not exactly match packet length.

Future payload decoders must add depth, item-count, string-size, map-size, integer-range, duplicate-key, and recursion limits.

## Time and restart questions

The current expiry field assumes a meaningful Unix clock, which many devices do not possess immediately after boot. Before freezing the wire format, decide how issued-at time, relative TTL, clock confidence, sender epochs, reboot counters, and random message IDs interact. Expiry must never become permission to execute a stale physical command merely because the clock reset.
