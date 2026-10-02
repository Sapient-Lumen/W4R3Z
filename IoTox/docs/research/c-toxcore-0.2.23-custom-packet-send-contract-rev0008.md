# c-toxcore 0.2.23 custom-packet send contract — rev0008

**Reviewed:** 2026-08-13 America/New_York  
**Applied to:** IoTox capability-session-v1, custom-packet error mapping, and retry policy  
**Evidence class:** primary-source review plus exact-ABI mock tests; no real toxcore execution in this cloudtainer

## Primary sources

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://github.com/toxext/toxext
https://raw.githubusercontent.com/toxext/toxext/master/DESIGN.md
```

The release page was rechecked during rev0008. c-toxcore 0.2.23 remains the current stable
release found, published 2026-06-03. The release archive used by IoTox's lock is:

```text
c-toxcore-0.2.23.tar.gz
sha256 b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe
```

The release fixes a critical issue found during manual review and states that its public API
was not changed. That supports the selected pin; it does not make the library production-
qualified by itself.

## Exact public-header constraints

The v0.2.23 public header states:

```text
maximum custom packet size: 1373 bytes
lossless application first byte: 69 or 160..191
lossless behavior: reliable and ordered, packet-framed
single Tox instance: no more than one API function at a time
```

IoTox uses discriminator `0xA0` (160), a 41-byte outer header, and therefore a maximum IoTox
frame payload of 1,332 bytes.

The custom-packet error enumeration distinguishes:

```text
NULL
FRIEND_NOT_FOUND
FRIEND_NOT_CONNECTED
INVALID
EMPTY
TOO_LONG
SENDQ
```

`SENDQ` is documented as “packet queue is full.” A false return with `SENDQ` means the packet
was not accepted into the lossless queue. That differs from a successfully queued packet whose
transport delivery is now toxcore's responsibility.

## Applied error semantics

The C++ transport adapter maps the public toxcore result into owned status classes:

```text
FRIEND_NOT_FOUND      -> not_found
FRIEND_NOT_CONNECTED  -> unavailable
SENDQ                 -> resource_exhausted; retry after toxcore iteration
INVALID/EMPTY/TOO_LONG/NULL -> invalid_argument
other/unknown         -> library_error
```

The exact ABI mock can inject bounded `SENDQ` failures generally or independently by IoTox
message type. Unit and process tests prove that IoTox preserves the distinction and eventually
retries both an unsent canonical HELLO and an unsent canonical CAPABILITIES confirmation
without changing either record's message ID or bytes. The runtime projection exposes separate
attempt counters and temporary error classes, then clears the error after successful enqueue.

## Retry inference and boundary

The header promises reliable ordered delivery for packets successfully accepted into the
lossless lane. IoTox therefore does not add an acknowledgement timer that blindly resends
accepted HELLO or CAPABILITIES packets. Such a timer would duplicate traffic without evidence
that toxcore lost it.

IoTox does retry a protocol record when toxcore explicitly rejected the local enqueue because
the friend was temporarily unavailable or the queue was full. The retry runs after later
`tox_iterate` progress and reuses the frozen per-epoch record. This is a local-enqueue recovery
policy, not a second reliability protocol. The public header does not promise that one
`tox_iterate` call or a 500 ms delay will clear `SENDQ`; that cadence is an IoTox scheduling
inference to be measured and tuned against real c-toxcore.

Real c-toxcore testing must still measure:

```text
how quickly SENDQ clears under pressure
whether repeated offline/online callbacks match the assumed epoch boundary
whether relay-only paths preserve expected callback and ordering behavior
whether one 500 ms best-effort service cadence is operationally appropriate
```

## One protocol lane

ToxExt's project documentation notes that ordering should not be assumed between ordinary Tox
messages and custom packets. IoTox therefore keeps HELLO, CAPABILITIES, and future structured
machine traffic in the same `0xA0` lossless custom-packet lane. Human normal/action messages
remain a distinct presentation lane and are not used as protocol barriers.

## Claims not made

This review does not prove real delivery, public bootstrap behavior, NAT traversal, TCP relay
behavior, Tor/I2P routing, congestion fairness, or long-running resource use. It freezes the
contract that the owned code currently targets and gives the first real-peer test specific
failure modes to measure.
