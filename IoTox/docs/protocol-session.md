# IoTox capability session v1

**Revision implemented:** rev0008; authority v1 in rev0009; durable commands in rev0010; authority v2 in rev0016; signed OTA staging in rev0041
**Transport lane:** c-toxcore lossless custom packets
**Packet discriminator:** `0xA0`
**Current IoTox protocol:** `1.0`

Capability-session-v1 is the mandatory machine-session entrance. It negotiates one exact
online-epoch contract and requires both peers to confirm the same transcript before later IoTox
application frames are admitted.

It is not itself authorization or durability. rev0009 layers a directional signed challenge/proof
over the confirmed transcript. rev0010 admits durable commands only after the relevant principal is
verified and evaluated against the local ledger. rev0016 adds feature-negotiated authority-ledger v2
proofs and migration without advertising or constructing the Ratox terminal service.

## 1. Outer IoTox frame

All multi-byte integers are unsigned, big-endian. The complete packet must fit c-toxcore's
published 1,373-byte custom-packet bound.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 1 | lossless packet discriminator, `0xA0` |
| 1 | 1 | protocol major |
| 2 | 1 | protocol minor |
| 3 | 1 | message type |
| 4 | 1 | flags |
| 5 | 4 | payload length |
| 9 | 8 | message ID |
| 17 | 8 | correlation ID |
| 25 | 8 | sequence |
| 33 | 8 | expiry, Unix milliseconds; zero means not expressed |
| 41 | N | payload |

The maximum outer-frame payload is 1,332 bytes.

## 2. Online epoch

A peer's session epoch starts on a true Tox offline-to-online transition. A continuously online
TCP/UDP presentation change does not create a new epoch. A Tox `NONE` transition ends it.
Removing the friend erases its session record.

Each epoch receives:

```text
fresh nonzero 128-bit local session nonce from the operating system
fresh first local HELLO message ID
fresh first local confirmation message ID
new epoch counter
```

The first local HELLO and confirmation records are created once for that epoch. Their message
IDs are chosen before the first send attempt and never change merely because toxcore rejects a
local enqueue. The first valid peer HELLO body and first valid peer confirmation body are also
immutable. Byte-identical retries are idempotent; changed bodies are conflicts and close the
application gate.

## 3. Phase one: canonical HELLO

### 3.1 Outer-frame invariants

```text
protocol major:     1
protocol minor:     0
message type:       1 (HELLO)
flags:              0
message ID:         unpredictable, nonzero, frozen before first send attempt
correlation ID:     0
sequence:           1
expiry:             0
payload length:     exactly 64
```

### 3.2 Canonical 64-byte HELLO payload

| Offset | Size | Field | Rule |
|---:|---:|---|---|
| 0 | 4 | magic | ASCII `IHL1` |
| 4 | 1 | payload version | `1` |
| 5 | 1 | flags | `0` |
| 6 | 1 | minimum protocol major | nonzero |
| 7 | 1 | minimum protocol minor | range lower bound |
| 8 | 1 | maximum protocol major | nonzero |
| 9 | 1 | maximum protocol minor | range upper bound |
| 10 | 2 | implementation major | diagnostic |
| 12 | 2 | implementation minor | diagnostic |
| 14 | 2 | implementation patch | diagnostic |
| 16 | 2 | cube/build revision | diagnostic |
| 18 | 2 | maximum frame payload | `256..1332` in v1 |
| 20 | 8 | supported feature mask | required bits included |
| 28 | 8 | required feature mask | capability-session-v1 required |
| 36 | 8 | maximum finite-file bytes | zero iff finite-file bit absent |
| 44 | 16 | session nonce | unpredictable and not all zero |
| 60 | 4 | reserved | all zero |

The minimum advertised frame limit is 256 because v1 requires the confirmation record below.
Implementation version and cube revision never decide compatibility by themselves.

### 3.3 Feature bits

| Bit | Name | current status |
|---:|---|---|
| 0 | `capability-session-v1` | implemented and required |
| 1 | `tox-text-lane` | implemented, optional |
| 2 | `finite-file-transfer-v1` | implemented when local finite-file limit is nonzero |
| 16 | `authorization-ledger-v1` | implemented and advertised |
| 17 | `durable-commands-v1` | implemented and advertised in rev0010 |
| 18 | `state-sync-v1` | implemented; advertised only after explicit sync construction |
| 19 | `recall-reentry-v1` | reserved, not advertised |
| 20 | `signed-ota-v1` | implemented only after explicit update construction; requires bits 17, 18, and 26 |
| 21 | `route-binding-v1` | implemented; advertised only by explicitly constructed route workers or as v2 dependency |
| 22 | `mutorr-namespaces-v1` | reserved, not advertised |
| 23 | `ratox-interactive-v1` | implemented; advertised only after explicit host/client construction |
| 24 | `authorization-ledger-v2` | implemented and advertised in rev0016 |
| 25 | `authorization-ledger-v3` | implemented and advertised; requires the v2 lineage bit |
| 26 | `state-sync-ranges-v1` | implemented with sync construction; requires bit 18 |
| 27 | `application-epoch-restart-v1` | implemented with the durable process-incarnation lease |
| 28 | `private-route-binding-v2` | implemented behind explicit private route-worker construction; requires bits 16 and 21 |

Unknown optional bits do not grant behavior. An unknown required bit makes the negotiation
incompatible unless the local implementation explicitly advertises it.

A HELLO carrying bit 20 without `durable-commands-v1`, `state-sync-v1`, and
`state-sync-ranges-v1` is structurally invalid. Sharing bit 20 enables only the authority-gated
`update.stage` command from ADR 0186; it grants no update capability by itself.

### 3.4 Symmetric negotiation

For two structurally valid HELLOs:

1. Select the highest protocol version in the range intersection.
2. Fail with `incompatible-version` when the ranges do not intersect.
3. Fail with `incompatible-features` when either endpoint lacks a feature required by the
   other.
4. Intersect supported feature masks.
5. Select the smaller maximum-frame limit.
6. Select the smaller finite-file limit when finite-file-v1 is shared; otherwise select zero.

Reversing local and peer arguments produces the same selected version, shared mask, and limits.
A compatible HELLO result advances only to `awaiting-confirmation`.

## 4. Phase two: canonical CAPABILITIES confirmation

### 4.1 Outer-frame invariants

```text
protocol version:   exact negotiated version
message type:       2 (CAPABILITIES)
flags:              0
message ID:         unpredictable, nonzero, frozen before first send attempt
correlation ID:     peer's first accepted HELLO message ID
sequence:           2
expiry:             0
payload length:     exactly 256
```

### 4.2 Canonical endpoint roles

The two raw 32-byte Tox public keys are compared lexicographically:

```text
lower-transport-key
higher-transport-key
```

This ordering is independent of who connected first, who sent HELLO first, or which side is
currently rendering the record. The sender role byte says which canonical endpoint emitted the
confirmation.

### 4.3 Exact 256-byte payload

| Offset | Size | Field | Rule |
|---:|---:|---|---|
| 0 | 4 | magic | ASCII `ICF1` |
| 4 | 1 | payload version | `1` |
| 5 | 1 | flags | `0` |
| 6 | 1 | sender role | `0` lower, `1` higher |
| 7 | 1 | reserved | `0` |
| 8 | 1 | selected protocol major | recomputed from HELLOs |
| 9 | 1 | selected protocol minor | recomputed from HELLOs |
| 10 | 2 | negotiated maximum frame payload | recomputed from HELLOs |
| 12 | 8 | shared feature mask | recomputed from HELLOs |
| 20 | 8 | negotiated finite-file bytes | recomputed from HELLOs |
| 28 | 32 | lower Tox public key | nonzero and less than higher key |
| 60 | 32 | higher Tox public key | nonzero and greater than lower key |
| 92 | 16 | lower session nonce | equals lower HELLO nonce |
| 108 | 16 | higher session nonce | equals higher HELLO nonce |
| 124 | 64 | exact lower HELLO | canonical `IHL1` record |
| 188 | 64 | exact higher HELLO | canonical `IHL1` record |
| 252 | 4 | reserved | all zero |

The decoder preserves received negotiated values, decodes both embedded HELLOs, recomputes the
negotiation, and rejects any mismatch. It never overwrites wire values before validating them.
Only human-readable diagnostic text is reconstructed after successful validation.

### 4.4 Mutual confirmation

Each side constructs the same canonical transcript bytes except for the sender-role byte. A
received confirmation must:

```text
match the expected opposite sender role
contain the exact two locally known HELLOs
contain the exact two transport public keys
contain the exact two epoch nonces
contain the exact selected result
correlate to the first local HELLO ID
fit the frozen peer payload and frame limits
```

The first accepted peer confirmation message ID is retained for audit. A later frame with a
fresh outer ID and an identical body is idempotent. A changed body is
`conflicting-confirmation`.

## 5. State machine

```text
offline
  -> awaiting-hello
  -> awaiting-confirmation
  -> confirmed
```

Terminal/fail-closed observations for an epoch include:

```text
incompatible-version
incompatible-features
malformed-frame
malformed-hello
conflicting-hello
hello-send-failed
malformed-confirmation
conflicting-confirmation
confirmation-send-failed
```

An offline transition resets all per-epoch transcript material. A later online transition
starts a new epoch with a new local nonce and IDs.

### 5.1 Local enqueue recovery

A packet accepted by toxcore's lossless send function is not resent on an IoTox response timer.
Toxcore owns reliable ordered delivery after acceptance. When the call instead reports
`FRIEND_NOT_CONNECTED` or `SENDQ`, the packet never entered that queue. The agent retains the
frozen unsent protocol record and services incomplete sessions after later toxcore iterations,
currently on a 500 ms best-effort cadence.

```text
accepted by toxcore          no IoTox blind retransmit
friend temporarily offline   retry same frozen record after progress
lossless SENDQ full          retry same frozen record after progress
permanent contract error     fail closed; do not retry as congestion
```

This is local-enqueue recovery, not an additional transport reliability protocol. Successful
application-frame sends are not covered by this handshake retry service. Person messaging has
its own reviewed outbox and retry-plan porch; a generic application outbox for every frame class
remains separate work.

## 6. Application gate

A non-session IoTox frame is admissible only when the peer snapshot is fully `confirmed` and:

```text
connected=1
negotiated-compatible=1
confirmation-sent=1
confirmation-received=1
application-ready=1
```

The frame itself must:

```text
not be HELLO or CAPABILITIES
use the exact negotiated protocol version
have a nonzero message ID
fit the negotiated maximum payload
```

This gate applies to incoming frames and to locally injected raw IoTox frames. It prevents a
shell operator or future subsystem from bypassing the session machinery by writing an `0xA0`
packet directly through the generic lossless seam.

The generic session gate does not itself evaluate roles, capabilities, or command durability.
The authority layer proves a stable principal and evaluates the current ledger. In v2, the exact
ledger format is carried in the challenge/proof, the proof uses an independent signature domain, and
feature bit 24 is part of the confirmed shared-feature transcript. rev0010 then commits the fixed
`device.describe` request before acknowledgement or execution, emits a durable `RECEIVED` receipt,
and commits the terminal result before sending it. General cancellation, trusted expiry,
effect-specific idempotency, and physical-operation safety remain future work.

## 7. Operator and runtime surface

```sh
iotox sessions
iotox session FRIEND
iotox hello FRIEND
iotox confirm FRIEND
iotox peer-session PUBLIC_KEY
iotox peer-protocol PUBLIC_KEY
```

`hello` and `confirm` are explicit operator retransmission requests for the current epoch. They
reuse the first message ID and exact canonical payload; neither command can rewrite the
transcript. `confirm` is available only after a compatible two-HELLO exchange.

The ratox-style private projection includes:

```text
peers/<PUBLIC_KEY>/iotox/state
peers/<PUBLIC_KEY>/iotox/hello-compatible
peers/<PUBLIC_KEY>/iotox/transcript-confirmed
peers/<PUBLIC_KEY>/iotox/established
peers/<PUBLIC_KEY>/iotox/application-ready
peers/<PUBLIC_KEY>/iotox/confirmation-sent
peers/<PUBLIC_KEY>/iotox/confirmation-received
peers/<PUBLIC_KEY>/iotox/local-role
peers/<PUBLIC_KEY>/iotox/protocol
peers/<PUBLIC_KEY>/iotox/summary
peers/<PUBLIC_KEY>/session
```

`peers/<PUBLIC_KEY>/session` is the detail commit marker. Aggregate status distinguishes:

```text
compatible-protocol-session-count
established-protocol-session-count
negotiating-protocol-session-count
incompatible-protocol-session-count
protocol-error-session-count
```

Compatibility means HELLO negotiation succeeded. Establishment means both confirmations were
accepted. Neither count implies authorization.

## 8. Security and evidence boundary

The underlying Tox friendship associates packets with a Tox transport key and provides the
transport's encrypted reliable lane. Capability-session-v1 then proves that IoTox's current
implementation accepted one exact, mutually matching online-epoch transcript.

It does not by itself prove stable IoTox identity, ownership, delegation, or permission. The
authority layer binds a signed stable principal to the transcript and consults the local ledger.
Authority-ledger v2 additionally refuses its challenge, proof, and remote mutation paths unless bit
24 was negotiated for that exact epoch. rev0010 adds command persistence and receipt/result replay
above that boundary.
`docs/decisions/0034-transcript-bound-directional-stable-principal-proof.md` freezes authority;
`docs/decisions/0036-commit-command-before-transport-or-effect.md` freezes durable ordering.

The session and authority paths are unit-tested, exact-mock-ABI-tested, one-binary process-tested,
and retained across two genuine source-linked c-toxcore peers in both founding-host normal-native
and TCP-only fixtures. Those named fixtures do not establish every provider, route, NAT, or
packet-loss condition.
