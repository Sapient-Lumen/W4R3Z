# ADR 0035: Make `device.describe` the first bounded IoTox machine operation

**Status:** accepted and implemented in rev0009

## Context

The ratox successor needs real application behavior, not only transport, projections, and
handshake proofs. The first operation must exercise authorization, canonical request/result
correlation, retry pressure, protocol journaling, and one-binary control without risking a
physical effect before durable command semantics exist.

## Decision

IoTox protocol v1 defines one machine operation: `device.describe`.

The request is a fixed eight-byte `ICQ1` record. It requires the caller's currently verified
principal to hold `read.telemetry`. The result is a bounded `ICR1` header plus an optional body.
A successful response body is one fixed 64-byte `IDD1` device description containing:

- product revision and semantic version;
- the negotiated IoTox protocol version;
- the responder's stable device principal;
- implemented feature bits;
- offered operation bits.

Before authority proof, the same canonical request receives `denied`. After proof, it receives
`succeeded`. The response principal must equal the stable verifier device named in the peer's
authority challenge, and its protocol version must equal the confirmed session result. A
mismatch is a conflict, not a usable description.

The local command `iotox device-describe FRIEND` reserves one canonical request. If toxcore
returns a retryable queue error before acceptance, IoTox retries only those identical bytes and
message identifier. `iotox peer-description FRIEND` returns the immutable current snapshot and
commits the same snapshot to the private ratox-style tree.

## Consequences

The product now performs a complete harmless operation across:

```text
one iotox binary
  -> local SOCK_SEQPACKET request
  -> transcript-confirmed Tox session
  -> directional principal proof
  -> capability check
  -> canonical COMMAND / COMMAND_RESULT
  -> result correlation and principal binding
  -> private filesystem projection
```

This operation is intentionally **not durable**. Its reservation lives only for the current
process and online epoch. It is read-only and idempotent, so loss after a crash is acceptable.
No actuator, setting mutation, firmware action, or deletion may reuse this provisional
contract.

The current response sender does not durably retry a `COMMAND_RESULT` after local `SENDQ`.
Durable admission, result retention, deduplication, cancellation, expiry, and restart recovery
remain prerequisites for physical effects.

## Rejected alternatives

- **Start with GPIO or settings:** risks double execution before durability exists.
- **Return free-form JSON/text:** weakens canonical decoding and bounded allocation.
- **Trust the response's claimed principal:** permits a session peer to describe another device.
- **Send before local claimant proof:** makes operation ordering ambiguous to the remote peer.
- **Advertise `durable_commands_v1`:** would overstate the implemented contract.
