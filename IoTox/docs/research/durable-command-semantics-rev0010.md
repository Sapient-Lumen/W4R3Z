# Durable command semantics — rev0010

**Reviewed:** 2026-08-14 America/New_York  
**Scope:** application receipts, duplicate handling, retry, and restart policy above Tox

## Primary sources

```text
Tox protocol specification
https://toktok.ltd/spec.html

c-toxcore 0.2.23 public API
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h

CoAP message and duplicate-detection model, RFC 7252
https://www.rfc-editor.org/rfc/rfc7252.html

HTTP semantics and automatic retry constraints, RFC 9110
https://www.rfc-editor.org/rfc/rfc9110.html

MQTT 5.0 QoS and packet-identifier state machines
https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html

ACE application identity and authorization framing, RFC 9132
https://www.rfc-editor.org/rfc/rfc9132.html
```

## Source facts

Tox lossless packets are ordered and retransmitted by the transport. c-toxcore's custom-packet
send API can still reject a local send with `SENDQ`; successful return establishes local queue
acceptance, not remote durable admission or application completion.

CoAP and MQTT illustrate that duplicate detection and stronger delivery grades require protocol
identifiers and retained state above an underlying transport. HTTP permits automatic retry only
when the request is known to be idempotent or known not to have been applied. ACE distinguishes an
application identity and its authorized scope from a lower-level communication coordinate.

## IoTox inference

IoTox therefore needs three separate facts:

```text
transport accepted exact bytes locally
remote IoTox committed the exact request and returned RECEIVED
remote operation produced a terminal COMMAND_RESULT
```

None implies the next. The sender's durable identity is its public transport key, persistent sender
epoch, and message id. The receiver stores the exact request before emitting `RECEIVED`; it stores
the exact terminal result before sending it. A duplicate with the same key and same bytes receives
the frozen receipt/result. A duplicate key with different bytes is a conflict.

Local storage adds a direction lane because one process is both sender and receiver. Direction is
not added to the wire identity.

Restart re-execution is operation policy. rev0010 allows it only for the read-only,
principal-bound `device.describe` query. No generic rule authorizes repetition of physical effects.

## Evidence boundary

These semantics are compiled and crossed through the exact ABI peer and one-binary restart fixture.
They have not yet crossed two official c-toxcore builds or a real network. They do not solve clock
trust, cancellation, rollback of an old valid store, disk exhaustion, effect compensation, or
multi-device ownership recovery.
