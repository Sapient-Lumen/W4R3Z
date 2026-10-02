# ADR 0025: Begin every online peer epoch with one canonical IoTox HELLO

**Status:** accepted and implemented in rev0007

## Context

A Tox friendship proves that toxcore recognizes a transport peer. It does not prove that the
peer implements IoTox, speaks a compatible IoTox protocol, accepts the same finite-file
limits, or implements any future device feature. rev0006 could decode arbitrary IoTox frames
but had no connection-scoped negotiation state. Sending device traffic merely because a
friend was online would therefore be ambiguous and unsafe.

Tox lossless custom packets are reliable, ordered within that lane, and bounded to the
published custom-packet capacity. ToxExt independently demonstrates the value of explicit,
composable extension negotiation and warns against assuming ordering between ordinary Tox
messages and custom packets. IoTox therefore keeps its machine protocol entirely in the
lossless custom-packet lane.

## Decision

On each transition from offline to an online Tox friendship, IoTox creates an unpredictable
128-bit session nonce and automatically sends one canonical, fixed-size HELLO frame. The
HELLO advertises:

```text
supported IoTox protocol range
IoTox implementation version and cube revision
maximum accepted IoTox frame payload
supported and required feature masks
maximum finite file size
per-online-epoch session nonce
```

The payload has exactly one 64-byte big-endian representation. Reserved fields must be zero.
The outer HELLO frame has fixed bootstrap semantics: protocol 1.0, flags zero, nonzero random
message ID, correlation ID zero, sequence one, and no expiry.

The first valid remote HELLO is frozen for the current online epoch. A byte-identical retry is
idempotent even when its outer message ID changes. A changed HELLO in the same epoch is a
protocol conflict, not in-place renegotiation. A true offline transition clears the frozen
transcript and the next online transition increments the epoch and generates a fresh nonce.
Changing between TCP and UDP while continuously online does not create a new epoch.

Required feature negotiation fails closed. The current required bit is
`capability-session-v1`; current optional implemented bits are `tox-text-lane` and
`finite-file-transfer-v1`. Named future bits remain unadvertised until their behavior exists.

## Consequences

The agent can now distinguish an ordinary Tox friend from a compatible IoTox transport
session and can state why negotiation failed. Session state is available through the one
binary and the private ratox-style runtime projection. Non-HELLO IoTox frames received before
compatibility are journaled for evidence but not dispatched as application traffic.

`compatible` means only that this process received a valid peer HELLO whose version and
feature requirements intersect with its own. It grants no ownership, role, capability,
firmware authority, actuator authority, command durability, or application signature trust.

rev0007 does not yet send a separate transcript-confirmation/CAPABILITIES frame. Reliable
ordering means each implementation sends its HELLO before later machine frames, but an
explicit mutual transcript acknowledgement remains required before physical command
execution is introduced.

**rev0008 amendment:** ADR 0028 implements that explicit canonical CAPABILITIES confirmation
and closes application traffic until both sides confirm the same transcript. The paragraph
above remains as historical rev0007 scope, not current implementation truth.
