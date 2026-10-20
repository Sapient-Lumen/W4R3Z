# Cloudtainer build report — IoTox rev0008

**Date:** 2026-08-14 America/New_York  
**Revision:** rev0008  
**Version:** 0.8.0  
**Codename:** Transcript Confirmed  
**Northstar:** one installed C++20 ratox-successor executable  
**Strongest evidence:** compiled, unit-tested, exact-mock-ABI-tested, process-tested,
sanitizer-tested, fuzz-smoke-tested

## Result

rev0008 advances `iotox` from one-sided capability advertisement to a mutually confirmed
machine session. Every true Tox online epoch now has one frozen local HELLO, one frozen peer
HELLO, one deterministic negotiated result, and one canonical confirmation from each endpoint.
Ordinary IoTox application frames remain closed until both peers confirm the same transcript.
Even then the runtime says, explicitly:

```text
authorization=none-transport-session-only
```

This is a transport/session milestone, not an ownership milestone. The independent application
identity and authorization ledger remain the immediate next boundary.

The installed product surface remains exactly one executable:

```text
bin/iotox
```

The core, provider adapters, mocks, tests, fuzzers, and Mutorr preservation programs remain
internal build/evidence components and do not create a second installed product command.

## Product work completed

### Canonical mutual confirmation

The machine-session sequence is now:

```text
Tox friend offline -> online
        |
        +-- create fresh 128-bit OS-CSPRNG epoch nonce
        +-- reserve one nonzero local HELLO message ID
        +-- send exact 64-byte IHL1 HELLO
        +-- freeze first structurally valid peer HELLO
        +-- negotiate version/features/limits
        +-- reserve one nonzero local confirmation message ID
        +-- send exact 256-byte ICF1 CAPABILITIES confirmation
        +-- freeze first structurally valid peer confirmation
        +-- compare against locally reconstructed transcript
        +-- open application gate only after mutual confirmation
```

The confirmation canonically binds:

```text
both raw 32-byte Tox public keys in lexical order
both exact 64-byte HELLO payloads
both 128-bit epoch nonces
the selected protocol version
shared feature mask
negotiated frame payload ceiling
negotiated finite-file ceiling
sender role relative to the ordered endpoint keys
```

The peer's confirmation correlates to the first accepted local HELLO message ID. The local
confirmation correlates to the first accepted peer HELLO message ID. Outer type, version,
flags, sequence, expiry, IDs, and payload length are all constrained.

### Frozen-record retry boundary

The c-toxcore 0.2.23 public custom-packet API distinguishes a successful enqueue from several
explicit failures, including `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` and
`TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_CONNECTED`. IoTox now preserves that distinction.

Before toxcore accepts a handshake packet, IoTox may retry the exact frozen logical record.
After toxcore accepts a lossless packet, transport reliability belongs to toxcore and IoTox
does not blindly retransmit merely because no application reply has appeared.

The first HELLO and confirmation message IDs are reserved during canonical frame construction,
not after enqueue success. A transient rejection therefore cannot cause a later retry to invent
another ID or transcript. The event pump retries unsent protocol records on a bounded best-effort
cadence while the same online epoch remains valid.

The runtime exposes per-record attempt counts and the most recent local send failure. A
successful enqueue clears the error while retaining the attempt count as evidence.

### Semantic failure freezing

The first structurally valid peer HELLO and confirmation payloads are immutable for an online
epoch. Byte identity does not erase the result of semantic validation:

```text
accepted first record + exact replay        -> idempotent success
rejected first record + exact replay        -> same rejection
changed record within the same epoch        -> protocol conflict
true offline transition and reconnect       -> new epoch, nonce, IDs, records
```

This matters because an attacker must not be able to probe with a wrong transcript and then
repair it inside the same transport epoch. It also prevents an incompatible HELLO from becoming
"successful" merely because it was repeated unchanged.

### Post-confirmation application gate

A non-handshake IoTox frame is admitted only when:

```text
the peer session is mutually confirmed
the frame is neither HELLO nor CAPABILITIES
the frame version exactly equals the negotiated version
the message ID is nonzero
the payload does not exceed the negotiated peer ceiling
```

The gate applies both to incoming lossless packets and to the one-binary raw packet seam, so an
operator cannot bypass session establishment by injecting an otherwise well-formed frame.

### One-binary operator and ratox-style surface

The existing executable now exposes explicit session confirmation and richer diagnostics:

```text
iotox sessions
iotox session FRIEND
iotox hello FRIEND
iotox confirm FRIEND
```

The private runtime projection publishes compatibility, transcript confirmation, application
readiness, endpoint role, first message IDs, send attempts, negotiated limits, and errors under
the peer's stable Tox public-key directory. The root `session` file remains the complete-record
commit marker.

`hello` and `confirm` are explicit idempotent retries of the frozen epoch records. They do not
construct a new transcript.

### Exact mock became a real counterparty model

The loadable toxcore ABI mock no longer merely echoes machine packets. For the session path it
acts as a distinct IoTox endpoint with:

```text
its own public-key perspective
its own HELLO nonce
an independently constructed HELLO
validation of the local confirmation
an opposite-role canonical confirmation
independent one-shot SENDQ injection for HELLO and CAPABILITIES
```

The process fixture rejects the first local enqueue for each handshake record, lets the owner
thread iterate, observes exact-record recovery, reaches `state=confirmed`, then proves the
application gate and the explicit absence of authorization.

## Primary-source findings applied

rev0008 rechecked the current c-toxcore release/project posture and retained 0.2.23 as the pinned
target. The implementation was compared against the official 0.2.23 custom-packet declarations
and error contract. Relevant consequences include:

- successful lossless custom packets are reliable, ordered, and packet-framed;
- custom-packet send failure is explicit and includes queue pressure, offline peer, invalid
  packet, empty packet, and oversize packet conditions;
- the reliable packet size ceiling remains 1,373 bytes, leaving 1,332 bytes after the IoTox
  outer frame header;
- c-toxcore does not define IoTox's application retry schedule, transcript, authorization, or
  execution semantics;
- one `Tox*` remains exclusively serialized on its owner thread;
- current upstream still presents c-toxcore as experimental and not independently formally
  audited, so application signatures, sandboxing, source pinning, and update discipline remain
  product requirements rather than optional polish.

The research also reviewed ToxExt negotiation and the transcript barriers used by TLS 1.3,
DTLS 1.3, and Noise. IoTox adopts only the applicable state-machine lesson: both sides should
commit the same frozen handshake context before ordinary application traffic. The unsigned
`ICF1` record is not represented as a TLS Finished message, a Noise handshake hash, or an
application authorization proof.

The exact sources and the distinction between quoted upstream behavior and IoTox inference are
retained in:

```text
docs/research/tox-session-confirmation-rev0008.md
docs/research/c-toxcore-0.2.23-custom-packet-send-contract-rev0008.md
docs/research/sources.md
docs/decisions/0028-mutual-transcript-confirmation.md
docs/decisions/0029-custom-packet-acceptance-and-retry.md
```

## Verification retained

The final isolated source snapshot was exercised through the repository matrix with warnings as
errors in normal compiler lanes:

```text
GCC 14 debug                          build pass; CTest 7/7
GCC 14 release                        build pass; CTest 7/7
Clang 17 debug                        build pass; CTest 7/7
Clang 17 ASan + UBSan                 build pass; CTest 7/7
GCC 14 ThreadSanitizer                build pass; CTest 7/7
owned unit/integration executable     64 checks; 0 failures
frame decoder libFuzzer               5,000 runs; no crash
HELLO/confirmation libFuzzer          5,000 runs; no crash
local-control decoder libFuzzer       5,000 runs; no crash
Mutorr preservation configuration     build pass; CTest 9/9
one-binary mock lifecycle             pass
installed executable count            1 (`bin/iotox`)
lone-entrance layout                  pass
```

Sanitizer and fuzzer success applies only to the executed paths and inputs. It is not proof of
memory safety, parser completeness, race freedom, cryptographic security, or production fitness.

The complete matrix was run in an isolated copy rather than in the mutable assembly tree. This
prevented incremental edits or cleanup from invalidating another lane's build directory. The
retained matrix log and per-lane CTest logs are the authoritative execution record.

## Defects found while constructing rev0008

The facility changed the implementation in several material ways:

```text
HELLO compatibility was initially treated too much like session readiness
confirmation decoding could mask wire mutation by recomputing fields too early
message IDs were initially frozen only after successful enqueue
one exact replay path could report success for a confirmation rejected on first comparison
c-toxcore SENDQ was initially collapsed into a generic library error
an optimizer-only test warning exposed unchecked vector indexing
one matrix attempt used overlapping mutable build directories and was discarded
```

The final source reserves the canonical ID before enqueue, preserves official send-error
meaning, keeps rejected frozen records rejected, and isolates retained matrix evidence.

## Source-linked attempt

The dependency lock remains:

```text
c-toxcore 0.2.23
sha256 b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe

libsodium 1.0.22
sha256 adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349
```

`tools/fetch-pinned-dependencies.sh` was executed again. The shell resolver could not resolve
`download.libsodium.org`; curl exhausted its configured retries and returned error 6. No hash
was weakened, no arbitrary substitute source was used, and the source-linked lane remains
**not executed**.

The repository still contains the product-shaped source-linked build, verification, and
real-peer smoke paths for a networked CLI.

## What rev0008 proves

```text
owned C++20 source compiles under GCC and Clang
one executable owns the daemon and local client surface
one thread owns the consumed toxcore ABI
canonical HELLO and confirmation codecs are implemented and bounded
both endpoints can deterministically reconstruct and confirm one online-epoch transcript
transient pre-enqueue SENDQ pressure retries the exact frozen record
accepted lossless packets are not blindly duplicated by IoTox
rejected frozen confirmations remain rejected on exact replay
application frames remain closed until mutual confirmation
session establishment remains visibly separate from authorization
the exact consumed C ABI and process path work through a distinct deterministic mock peer
the install graph exposes one product executable
```

## What rev0008 does not prove

```text
official c-toxcore source compiles and links with this exact revision
two genuine Tox peers confirm across the real network
real packet timing, congestion, reconnect, NAT, bootstrap, or relay behavior
that the current 500 ms protocol-service cadence is optimal
Tor- or I2P-routed Tox or leak prevention
stable IoTox application identity
owner/controller signatures or an authorization ledger
durable commands, execution receipts, replay cache, or idempotent physical effects
RecallRoot re-entry to an existing live ownership domain
encrypted keystore, rollback-resistant authorization epochs, or signed OTA
target-hardware resource, power, suspend, or flash behavior
production readiness
```

## Next product boundary

Do not inflate `confirmed` into authority. The next ratox-successor code should introduce a
stable application device identity and an independent authorization ledger with canonical
records, explicit epochs, capabilities, revocation, and a proof bound to the confirmed session
transcript. Source-linked real-toxcore compilation and two genuine peers should proceed in
parallel because measured upstream behavior may still correct adapter and timing assumptions.
