# c-toxcore 0.2.23 as the durable-command carrier — rev0010

**Review date:** 2026-08-14 America/New_York  
**Implementation revision:** IoTox rev0010  
**Question:** Which guarantees belong to c-toxcore, and which guarantees must the ratox successor own?

## Sources reviewed

Primary upstream material:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/security/advisories/GHSA-42vg-9mg3-399f
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://toktok.ltd/spec.html
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://github.com/pranomostro/ratox
```

The upstream release page marked c-toxcore 0.2.23 as the latest release on the review date. It was
released 2026-06-03. Its release notes say that it fixes a critical bug and does not remove or
modify the public APIs. The associated advisory describes an unauthenticated stack-buffer overflow
in group-chat onion announcement handling, with 0.2.23 as the patched release. IoTox therefore
pins 0.2.23 rather than treating an older distro package as equivalent evidence.

This note records source facts separately from IoTox design inferences. It is not evidence that the
current cloudtainer executed official c-toxcore.

## 1. The owner-thread boundary matches the public contract

The public `tox.h` threading section says that no more than one API function may operate on a
single `Tox` instance at a time. It describes a common design in which one thread owns a simple
`tox_iterate` loop. It also warns that size/read pairs can be invalidated by another mutating call.

IoTox therefore gives one C++ owner thread exclusive possession of the `Tox *`. Other product
components submit bounded commands and receive normalized events. The design does not depend on
c-toxcore's experimental per-instance locking option.

This rule is constitutional:

```text
No operation handler, filesystem adapter, local-control client, or durable-store component calls
c-toxcore directly. The provider and owner thread are the sole ABI boundary.
```

The public header recommends compiling with `TOX_HIDE_DEPRECATED`. IoTox does so. `Tox_Options`
must be allocated with `tox_options_new`, configured through accessors, and released with
`tox_options_free`; its visible layout is explicitly not an ABI contract and is intended to become
opaque in 0.3.0.

## 2. Lossless custom packets are the correct small command carrier

c-toxcore defines lossless custom packets as reliable and ordered, comparable to TCP but retaining
packet boundaries. The maximum custom packet size in 0.2.23 is 1,373 bytes. IoTox reserves a
41-byte frame header, leaving 1,332 bytes for one bounded application payload.

The API distinguishes important local failures:

```text
FRIEND_NOT_CONNECTED   no active friend connection
INVALID                packet identifier outside the permitted lossless range
EMPTY                  zero-length packet
TOO_LONG               exceeds the c-toxcore custom-packet ceiling
SENDQ                   c-toxcore's local packet queue is full
```

IoTox uses packet identifier `0xA0`, inside c-toxcore's permitted lossless range. It rejects an
oversized application record before calling the provider.

The useful guarantee is narrow:

```text
successful send call
    means c-toxcore accepted the packet into its local transport path

successful send call
    does not mean the remote IoTox process received, persisted, authorized, started, or completed
    the command
```

`SENDQ` is likewise a local backpressure result. It is not a remote negative acknowledgement.

## 3. Exact retry must be an IoTox property

A retryable local error is safe only if the logical operation keeps one identity and one canonical
frame. Generating a fresh message id after `SENDQ`, disconnect, process restart, or lost result can
create a second command.

rev0010 therefore freezes and commits before transport:

```text
peer Tox public key
persistent sender epoch
message id
operation
canonical request frame
```

A retry reuses those exact bytes. An outgoing record is written before the first c-toxcore call. An
incoming record is written before an application receipt. A terminal result is written before the
result is sent.

This is an IoTox inference built above the upstream transport contract. c-toxcore does not provide
a durable application outbox, execution journal, idempotency key, or business-operation receipt.

## 4. `RECEIVED` is deliberately above Tox

rev0010 introduces an IoTox application acknowledgement:

```text
RECEIVED = the remote IoTox process durably committed the exact request
```

It does not mean:

```text
the current authority ledger admitted the request
the operation began
the operation completed
the effect occurred safely
```

Those are separate state transitions and terminal evidence. Keeping them separate prevents a
ratox-style write from making an unverifiable promise.

For exact duplicates, the receiver replays the frozen receipt and terminal result. Reusing the same
sender epoch and message id with different request bytes is a protocol conflict.

## 5. Tox identity is transport identity, not the authorization ledger

The Tox protocol specification says users are identified by public keys, while initial key exchange
is outside the Tox protocol. It also says compromise of the secret key compromises that Tox
identity and requires a new identity.

IoTox therefore separates:

```text
Tox public key
    route/session identity used by the carrier

stable IoTox device principal
    Ed25519 identity used to sign local constitutional state

RecallRoot owner principal
    deterministic authority reconstructed from the permanent generated phrase

authorization ledger
    roles, capabilities, sequence, grant, revoke, and ownership evidence
```

A friend relationship is not ownership. A confirmed IoTox session is not authorization. The
current authority head and a transcript-bound principal proof determine whether an operation may
be admitted.

The durable command locator contains the Tox sender key because that is the actual carrier identity
for the received frame. It also records the independently proven principal and authority head so
that transport and authority evidence are not conflated.

## 6. Ratox's interface remains the product inspiration

Ratox demonstrates the strongest part of the desired human contract:

```text
run one process in a directory
inspect ordinary files
write to named pipes
follow peer output
send a message or file without embedding toxcore
```

Its documented surface includes peer `text_in`, `text_out`, `file_in`, `file_out`, online state,
friend requests, profile fields, and errors. That simplicity is worth preserving.

IoTox changes what those files mean internally:

```text
ratox-inspired file or FIFO
    local adapter and projection

private SOCK_SEQPACKET protocol
    bounded correlated request/response path

signed durable command store
    truth for command identity and progress

signed authority ledger
    truth for permission
```

A FIFO is not itself a durable queue. A successful local write is not itself remote completion.
The user-facing surface can stay ordinary because the one binary supplies the missing semantics
underneath it.

## 7. Route options make space; they do not prove Tor or I2P

The 0.2.23 options API exposes controls relevant to future routed Tox experiments:

```text
UDP enable/disable
local discovery enable/disable
DHT announcement enable/disable
proxy type, host, and port
hole punching enable/disable
experimental DNS disable
TCP relay server port
```

The header says disabling UDP forces TCP-only communication through relay nodes. It notes that DNS
can be disabled when the application resolves names itself, including a Tor use case.

These switches justify retaining explicit route policy for:

```text
Tox/native
Tox/Tor
Tox/I2P
```

They do not prove leak-free routing. A future route test must demonstrate that bootstrap, DNS,
proxy, relay, reconnect, and fallback behavior stay inside the selected overlay. An explicitly
selected private route must fail closed rather than silently use native networking.

Direct IoTox-over-Tor or IoTox-over-I2P transports remain a separate future architecture. They are
not aliases for routing Tox through those networks.

## 8. Security maintenance is part of the product contract

The 0.2.23 security fix matters to a long-running IoT agent even though rev0010 does not use group
chat as a product feature. The affected subsystem could be initialized by a linked build, and the
advisory describes unauthenticated remote memory corruption.

Consequences:

```text
pin an exact reviewed c-toxcore release and archive digest
retain a rapid dependency-update path
compile warnings as errors
keep the ABI surface narrow
sandbox the one binary where the target permits
fuzz every IoTox decoder independently of Tox encryption
never let transport authentication alone authorize a physical effect
```

The narrow provider makes a future c-toxcore update or replacement possible without rewriting the
operator surface, command engine, authority ledger, or durable store.

## 9. Evidence boundary for rev0010

Constructed and exercised here:

```text
C++20 owner-thread provider boundary
exact consumed c-toxcore 0.2 ABI mock
lossless packet callbacks and injected SENDQ
canonical 41-byte IoTox frame header
1,332-byte payload ceiling
persistent outgoing and incoming command records
application RECEIVED receipt
terminal result persistence
exact duplicate replay
process stop/restart and sender-epoch continuity
one product executable and ratox-style projections
```

Not established here:

```text
official source-linked c-toxcore compilation
real bootstrap or DHT participation
two genuine Tox peers
NAT traversal or TCP relay behavior
real disconnect/reconnect timing
Tox/Tor or Tox/I2P routing
power-failure durability on target storage
safe mutable settings, GPIO, OTA, or ownership mutation
```

The next networked CLI should compile the pinned sources against the official headers, launch two
real `iotox` nodes, complete friendship/session/principal proof, cross one durable
`device.describe`, force disconnect/reconnect and restart, and retain exact evidence. Any real API
or timing defect should be corrected in this architecture rather than used as a reason to stop
building the product.

## 10. Decision

Keep Tox as the primary connection fabric. Keep ratox's ordinary Unix feeling. Make IoTox own the
semantics that neither one claims:

```text
persistent command identity
application receipts
capability admission
idempotency and exact replay
restart recovery
operator-visible evidence
route policy
```

That is the path from a beautiful FIFO Tox client to a stronger, standalone ratox successor.
