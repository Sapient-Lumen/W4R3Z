# ADR 0024: Decode IoTox frames into a separate per-peer protocol journal

**Status:** accepted and implemented in rev0006

## Context

The global transport event stream deliberately omits packet payloads. Raw custom-packet
hex is useful for diagnostics but does not show whether an IoTox frame is structurally valid,
which protocol version it declares, or which semantic message type it carries.

## Decision

When a lossless packet begins with the IoTox discriminator, the agent applies the strict
bounded frame decoder. Valid incoming frames and successfully queued outgoing frames are
written to the peer's private `protocol` journal with direction, protocol version, message
type, flags, identifiers, sequence, expiry, payload length, and escaped payload.
Malformed candidate IoTox frames are rejected from the decoded journal and reported as a
projection/protocol diagnostic. Non-IoTox lossless packets remain available through the raw
transport seam and are not reinterpreted.

## Consequences

`iotox peer-protocol` and `iotox peer-protocol-watch` make the emerging device protocol
observable through the same executable. This is not yet session negotiation, authorization,
replay protection, or a durable command ledger. It is the inspectable seam on which HELLO,
capabilities, commands, results, and state synchronization can be built.
