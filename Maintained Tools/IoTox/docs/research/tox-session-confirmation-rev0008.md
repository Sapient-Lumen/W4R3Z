# Tox session confirmation research — rev0008

**Reviewed:** 2026-08-13 America/New_York  
**Scope:** current c-toxcore release status, custom-packet session behavior, ToxExt, and
transcript-confirmation patterns from established protocols

## Primary sources

```text
https://github.com/TokTok/c-toxcore/releases
https://github.com/TokTok/c-toxcore
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://github.com/toxext/toxext
https://raw.githubusercontent.com/toxext/toxext/master/DESIGN.md
https://www.rfc-editor.org/rfc/rfc8446.html
https://www.rfc-editor.org/rfc/rfc9147.html
https://noiseprotocol.org/noise.html
```

## Current upstream check

c-toxcore 0.2.23 remains the newest published release found during this revision. The public
project still describes itself as an experimental cryptographic network library without an
independent formal cryptographic audit. IoTox therefore continues to pin the source target,
keep the consumed API narrow, retain a runtime exact-ABI seam, and require application-level
identity and authorization above Tox before physical authority exists.

No new public c-toxcore API was required for rev0008. The implementation remains inside the
existing friend connection callback and lossless custom-packet functions reviewed for
rev0007.

## Why a second session message exists

The HELLO exchange proves only that each side sent one syntactically valid advertisement. A
single side can locally compute a negotiation result, but that does not make the result a
mutually committed transcript. A future implementation defect, optional feature ordering,
message replacement, or downgrade path could leave peers with different views while both
believe they are ready.

Three bodies of prior work point in the same direction:

### TLS 1.3

TLS 1.3's Finished message authenticates the handshake transcript. The RFC allows ordinary
application data after a side has sent its Finished and received and validated the peer's
Finished, apart from specifically constrained early-data exceptions. IoTox does not copy TLS
cryptography—the Tox session already supplies its transport channel—but it adopts the clear
state-machine lesson: negotiation and application traffic should have an explicit commit
barrier.

### Noise

Noise keeps a handshake hash and recommends binding prior negotiation into the prologue so
rollback cannot silently alter the parties' views. It also distinguishes channel binding from
the application's decision about whether a remote static key is acceptable. IoTox makes the
same separation visible: the canonical transcript is one input to a later authorization
protocol, not authorization itself.

### ToxExt

ToxExt demonstrates the usefulness of negotiated optional extensions over lossless Tox custom
packets and of keeping extension traffic in an explicit protocol lane. IoTox takes the
negotiation principle but owns its device-specific wire contract rather than making a dormant
extension library a critical product dependency.

DTLS additionally reinforces two implementation disciplines useful to IoTox even though Tox's
lossless lane is not raw datagram transport: a handshake has explicit sequencing, and a
retransmitted logical handshake message must not mutate its content. rev0008 therefore freezes
the first local IDs and peer payloads for one online epoch.

## Chosen v1 representation

The CAPABILITIES confirmation is a fixed 256-byte payload. The endpoints are ordered by the raw
32-byte Tox public key, not by initiator/responder timing. The payload contains both exact
64-byte HELLOs, both endpoint keys, both 16-byte nonces, the negotiated result, and the sender's
canonical role.

Exact bytes are retained instead of introducing a new hash primitive at this stage because:

- 256 bytes is comfortably below the negotiated Tox custom-packet ceiling;
- the transcript remains directly inspectable and reproducible;
- the strict decoder can validate every field against the embedded HELLOs;
- fuzzing can mutate assigned and reserved bytes without an additional crypto dependency;
- a later signed authorization message can hash/sign this canonical record with an explicitly
  selected application identity primitive.

The confirmation's outer correlation ID points to the peer's first accepted HELLO message ID.
The first peer confirmation body is frozen independently from the outer message ID, so an exact
retry can remain idempotent while a changed body fails closed.

The retry rule is intentionally narrower than a second reliability protocol. A packet accepted
by toxcore is not resent on an IoTox response timer. When toxcore explicitly rejects the local
enqueue with `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ`, or the peer is temporarily unavailable, the
frozen protocol record remains unsent and may be attempted again after later toxcore iterations.
The message ID and payload do not change. See
`c-toxcore-0.2.23-custom-packet-send-contract-rev0008.md`.

## What the confirmation proves—and does not prove

After both confirmations, IoTox knows that the current Tox friend session produced two exact
HELLOs and two matching confirmation records under one online epoch. This is a stronger and
more testable statement than “both sides looked compatible.” It is sufficient to open the
machine-protocol framing gate.

It does **not** independently prove:

```text
stable IoTox device identity
owner identity
role or capability
authorization-ledger membership
command signature validity
physical possession
safe actuator intent
```

Those remain application-layer work. Runtime output deliberately says:

```text
authorization=none-transport-session-only
```

## Implementation findings

The rev0008 tests found two useful correctness issues during construction:

1. The initial decoder was about to replace received negotiated values with a locally
   recomputed object before comparison. That would have hidden wire mutations instead of
   rejecting them. The decoder now preserves every wire value, validates it against the two
   embedded HELLOs, and reconstructs only non-wire diagnostic text afterward.
2. Existing process tests treated `compatible` as the terminal state. Converting the mock into
   a distinct peer and requiring `confirmed` forced the runtime, CLI, aggregate counts, and
   filesystem projection to distinguish compatibility from establishment.
3. A generic `SENDQ` test proved the transport mapping but did not prove both handshake retry
   paths. The mock now rejects HELLO and CAPABILITIES independently; the process fixture
   requires the same frozen records to succeed on their second attempts and exposes those
   attempts without leaving a false daemon-wide failure.
4. A later source review found that the payload and nonce were frozen before enqueue but the
   local message ID was assigned only after successful enqueue. A rejected first attempt could
   therefore generate a different ID on retry. Canonical frame construction now reserves the
   first ID before the transport call, and failure-first registry tests reject replacement IDs
   for both HELLO and CAPABILITIES.
5. The first implementation treated any byte-identical repeat of the frozen peer confirmation
   as a successful idempotent retry. That was correct only when the frozen confirmation had
   already passed local transcript reconstruction. An exact repeat of a first, structurally
   valid but semantically wrong confirmation could therefore return success while the session
   correctly remained closed. The registry now preserves both dimensions: frozen bytes cannot
   change, and a record rejected on first semantic comparison remains rejected on every exact
   replay in that online epoch.

## Evidence boundary

```text
source-reviewed:      current upstream/release and prior protocol designs
compiled:             C++20 canonical HELLO + confirmation implementation
unit-tested:          exact codecs, mutations, negotiation, freeze, gate
mock-ABI-tested:      distinct peer HELLO and opposite-role confirmation
process-tested:       one binary, local control, journals, runtime projection
source-linked:        not executed in this cloudtainer
real-peer-tested:     not executed in this cloudtainer
cryptographically authorized: not implemented
```
