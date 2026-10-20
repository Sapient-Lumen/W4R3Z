# AnonSSH Bond Protocol

AnonSSH Bond Protocol (ABP) is the shipped authenticated, encrypted, dynamically
scheduled multipath byte transport. The current protocol is v6. This document owns its
wire/runtime semantics; the [specification ledger](../../specs/spec_ledger.json) owns
claim status, [architecture.md](architecture.md) owns product policy, and
[evidence.md](evidence.md) owns live-campaign interpretation.

## Goals and invariants

ABP combines reliable Tor, I2P, loopback-test, or future stream lanes into one reusable
session carrying multiple ordered bidirectional streams. It must:

- place distinct sustained payload chunks concurrently on every useful eligible lane;
- adapt to unequal and changing capacity without running at the weakest lane's rate;
- protect low-latency capacity from bulk serialization;
- recover exact bytes and cumulative control state across lane loss;
- bound every peer-controlled allocation and collection;
- authenticate lane membership and topology changes; and
- encrypt non-SSH payload independently of the underlying provider.

A socket count is not proof of useful striping or independent failure domains. A lane
may be active but receive only bounded reprobe traffic when its predicted delivery time
would delay contiguous application delivery.

## Layers

1. `anonssh-bond` implements deterministic framing, topology, capabilities, sender
   retention, reassembly, flow control, scheduling, and adaptive decisions without I/O.
2. `anonssh-bond-tokio` implements lane handshakes, encrypted records, readers/writers,
   liveness, sessions, streams, and generic provider formation.
3. Product providers turn exact Tor SOCKS/onion-control and I2P SAM endpoints into
   reliable lanes. Providers report provenance; they do not grant authorization.
4. Shipped adapters expose Tokio streams, OpenSSH ProxyCommand, named local TCP
   forwarding, and tested SSH-compatible rsync, Git, scp, and SFTP remote commands. V6 reserves a
   capability-gated peer-service preface used by the ALP local transport; see
   [application-interfaces.md](application-interfaces.md).

Deterministic core tests remain separate from public-overlay evidence so malformed
input, ordering, time, and fault transitions are reproducible.

## Versions and negotiation

Lane formation uses fixed-size `ABJ1` client-join and `ABA1` server-accept records. The
HMAC-authenticated nonce fields carry a supported-version mask and selected version
without changing the v1 record size. Both peers select the newest common version;
authenticated selection of an older available version is rejected. A caller may exclude
legacy versions and receive an explicit no-common-version result.

Version behavior is cumulative:

| Version | Added behavior |
| --- | --- |
| v1 | Original join, frame grammar, key schedule, and random-nonce replay ledger. |
| v2 | Negotiated version is bound into the lane key schedule. |
| v3 | Monotonic authenticated join sequence, bounded replay window, and winner-attributed realtime redundancy. |
| v4 | Encrypted cumulative capability advertisements. |
| v5 | One authenticated nonzero server-process incarnation across every session lane. |
| v6 | Capability-gated symbolic service selection before application bytes on each logical stream. |

Versions v1 through v6 retain the `ABP1` frame grammar. V1-v5 application streams retain
the legacy raw-SSH interpretation. V6 gives every application stream an explicit
bounded service preface, including the reserved `ssh` service, so the receiver never
guesses application semantics from payload bytes or traffic class. A replacement lane must
negotiate the established session version. V5 incarnation binding prevents a restarted
listener from joining volatile state owned by its predecessor. The embedded
compatibility matrix tests current/current, both current/v5 and current/v4 directions, current/v3,
current/v2, both current/frozen-v1 directions, no-common-version failure, and
authenticated downgrade rejection.

## Lane authentication and records

Every lane join binds the session ID, lane ID, failure domain, client nonce, server
nonce, negotiated version, and current-version metadata to a separately derived bond
key with HMAC-SHA-256. The server supplies the expected lane descriptor; peer-supplied
provenance is never sufficient. Nonces are random and joins have independent network and
handshake deadlines.

The same exchange carries an ephemeral ML-KEM-768 public key and ciphertext. The shared
secret, bond key, transcript, and nonces feed HKDF-SHA-256 to produce independent
directional ChaCha20-Poly1305 record keys. Every ABP frame is inside a mandatory
countered AEAD record. Replay, tampering, truncation, cross-direction use, and
cross-session substitution fail closed. There is no plaintext or downgrade mode.

V3-v6 joins use a fixed 256-bit sliding sequence window. It admits bounded out-of-order
completion while rejecting duplicate and stale joins without lifetime growth. Legacy
v1/v2 sessions retain at most 256 complete random nonces; silently evicting one would
make a captured legacy hello replayable.

I2P has a formation-specific transport requirement: the client join must be SAM
`STREAM CONNECT` initial payload. Waiting for connect success and then writing the hello
can deadlock because the remote stream may not become acceptable before initial data
exists. `BondDialer` therefore prepares the authenticated hello before provider dial and
passes it atomically to the provider.

## Sessions, streams, and lanes

A session is an authenticated membership, scheduling, capability, and topology context
with a random nonzero epoch. A lane is one reliable ordered provider stream in that
session. Provider reliability is insufficient: a successful local write does not prove
peer delivery, so ABP acknowledges and retains data at the bond layer.

Each logical stream has its own parity-separated ID, byte-offset space, traffic class,
send credit, receive credit, half-close state, and application buffer. Traffic classes
are `Control`, `Realtime`, `Interactive`, and `Bulk`. Streams can open concurrently in
both directions. Open, final offset, reset, and close acknowledgement are explicit.

The live-stream limit bounds concurrent state, not lifetime stream count. After both
half-closes and application delivery complete, heavy sender/reassembly state is released
and a compact bounded tombstone preserves exact lifecycle replay. Parity retirement
watermarks reject ID reuse and discard syntactically valid authenticated frames that
arrive after an evicted tombstone; unknown newer IDs still fail closed.

Session shutdown is acknowledged and order independent. Crossing requests complete only
after each locally initiated close receives its acknowledgement. A peer close already
acknowledged before local shutdown satisfies that later request rather than opening an
impossible second exchange.

## Frame grammar

Every frame has a 40-byte network-byte-order header followed by at most 64 KiB of
payload. The header includes `ABP1`, frame kind, flags, header length, session ID, stream
ID, byte offset, payload length, and reserved zeros. Unknown kinds, invalid flags,
nonzero reserved fields, zero required IDs, empty data, overflow, malformed payloads, or
oversized input fail closed.

Frame kinds are:

- data, acknowledgement, and receive-window update;
- lane join and accept grammar identifiers;
- ping and pong;
- stream open, close, and reset;
- endpoint/topology advertisement;
- capability advertisement; and
- session close.

Join/accept authentication is performed by the fixed handshake outside ordinary frame
transport. All application and control frames travel only inside encrypted records.

## Delivery, acknowledgement, and flow control

Data retains one stream offset across initial send and every retransmission. The receiver
accepts exact duplicates, rejects conflicting overlap, buffers out-of-order bytes under
a per-stream limit, and exposes only the largest contiguous prefix. In-order data bypasses
the reorder map.

Acknowledgements carry a cumulative offset plus at most 32 selective ranges. The runtime
decodes ranges into retained scratch, validates before mutation, and releases only the
target stream's ordered sender entries. Acknowledged chunks are folded into one bounded
delivery cohort per latest transmission lane so every byte contributes once while one
acknowledgement does not multiply RTT samples.

The receiver batches cumulative acknowledgement and absolute receive-window updates by
byte threshold. Selective gaps and duplicates trigger immediate evidence; otherwise a
10 ms timer bounds delay. The timer is armed only for streams with pending evidence and
is disarmed during zero-lane intervals. Window updates normally issue after one quarter
of the configured receive window is consumed. Credit returns only after bytes enter the
bounded application-facing buffer, so a stalled reader applies real backpressure.

A full connection sender ledger, exhausted stream window, or zero active lanes blocks the
calling stream without blocking the session actor. Writers sleep on a lossless progress
epoch advanced by acknowledgement, increasing credit, lane restoration, or released
stream state. They do not poll.

## Control replay and topology

A successful lane-queue operation is not delivery evidence. After lane loss, the runtime
reconstructs a bounded replay queue from cumulative authenticated state:

- unacknowledged stream opens and closes;
- open and remote-close acknowledgements;
- current absolute receive credit;
- the newest topology and capability snapshots; and
- pending session-close request/acknowledgement state.

Exact duplicate lifecycle or same-generation cumulative control is idempotent. A changed
class, initial window, final offset, topology body, or capability body at the same
generation is a protocol error. Newer generations replace older cumulative state;
reordered older generations are harmlessly ignored.

Topology descriptors identify action, provider, lane ID, failure domain, and bounded
endpoint. A local exact policy must authorize all fields before network work. Add and
replace authenticate the new lane before runtime activation; replace then fails the old
generation. Drain retires only an authorized lane. One advertisement carries at most 32
descriptors, each endpoint is at most 1,024 bytes, and descriptor 33 is rejected.

V4 capability snapshots report bounded provider feature/readiness counts, active-lane
and session ceilings, resource ceilings, startup estimates, queue delay, and delivered
goodput. Intersection uses only bilateral providers, minimum ceilings, and conservative
maximum startup/congestion costs. It can avoid futile optional startup but cannot grant
topology permission.

## Scheduling

Each direction schedules independently. Per-lane state includes smoothed RTT and
variation, acknowledged delivery rate, queued and unacknowledged bytes, predicted writer
availability, health, timeout history, provider, and failure-domain provenance.

For a candidate, the scheduler predicts delivery from the later of current time and the
lane's queued-through time, plus serialization and path delay. The earliest eligible
prediction wins. Delivery rate uses aggregate acknowledged bytes; pipelined cohorts use
positive acknowledgement spacing when overlap proves it valid, while first, idle,
zero-spacing, and replacement cohorts use bounded send-to-acknowledgement intervals.

Every eligible bulk lane receives a 16 KiB probe budget on activation, restoration, and
each 15-second eligibility interval. Normal predicted-delivery scheduling resumes after
that budget. This bounds exploration while allowing an obsolete estimate to recover.

Bulk lane and size are selected together. A lane's bandwidth-delay estimate proposes a
chunk clamped to 16-64 KiB and remaining application bytes. One RTT of queued
serialization halves the proposal; two RTTs select the floor. Selective gaps and timeout
retransmissions halve a session pressure ceiling; clean cumulative delivery restores it
geometrically after eight ceiling-sized bytes. Retained data is never re-chunked.

Scheduling uses at most two bounded lane-map passes and no heap-backed decision scratch.
The first pass determines the eligible traffic-class pool; the second folds probe state,
adaptive size, and earliest delivery into scalar candidates.

## Low-latency protection

The configured number of best healthy lanes form a protected pool. Where possible, a
mixed pool reserves one lane from each provider; a homogeneous pool uses independent
failure domains. Configured RTT seeds initial ranking. A healthy incumbent moves only
when a measured challenger clears a 10 percent smoothed-RTT hysteresis margin; inactive
incumbents and missing provider coverage are repaired immediately.

Control and `Realtime` use protected lanes. An `Interactive` chunk up to 2 KiB receives
the same treatment; larger chunks use bulk policy. Bulk excludes protected lanes while
another healthy lane exists. Separate bounded writer queues dequeue control, realtime,
and typing-sized records before queued bulk after the current encrypted record completes.
Nagle is disabled on AnonSSH-owned application TCP sockets.

Under negotiated v3 or later, eligible data sends one primary plus at most one shadow
copy on a distinct protected lane. Both frames share one immutable payload, stream
offset, and logical sender/window charge. First authenticated receipt wins. A full or
closed shadow queue records a drop but cannot fail accepted primary delivery. The winner
receives an immediate acknowledgement on its ingress lane when possible. V1/v2 remain
single-copy because their acknowledgement path cannot attribute the winner safely.

Redundancy reduces path-jitter tails; it does not reorder one stream past missing earlier
bytes and does not predict terminal output.

## Liveness and recovery

After bounded receive silence, each active lane writes an encrypted Ping and expects its
matching Pong on that lane. The response deadline begins only when the writer confirms
the probe record was written. Probe RTT updates latency evidence but does not invent
throughput.

Retained payload retransmits after four times its latest lane's smoothed RTT, clamped to
a two-second product floor and thirty-second ceiling. A failed reader, writer, liveness
probe, or timeout marks that lane inactive and makes retained chunks eligible on another
lane without changing offsets. An authenticated replacement enters with a new runtime
generation.

A session may remain alive temporarily with zero active lanes. It retains bounded sender,
receiver, topology, and control state and applies backpressure until repair. Explicit
close, a protocol violation, or the product's zero-lane terminal deadline ends it.

## Hot-path ownership

Sender chunks, initial frames, shadow frames, and retransmissions share immutable payload
storage. A lane writer copies header and payload once into its reusable final record
buffer and encrypts in place with one retained self-zeroizing AEAD context per direction.
The reader reuses its context, decrypts the socket allocation in place, and decodes owned
slices. A reordered run coalesces at most once when contiguous application bytes require
it.

Session-local scratch covers decoded selective ranges, sender release keys, acknowledged
chunks, delivery cohorts, pending delayed controls, and scheduled frames. The common
cumulative-only acknowledgement shares one constant empty-range payload. Protected-pool
ranking refreshes once after all cohorts in one acknowledgement are applied.

## Bounds

The runtime validates configurable maximum frame payload, unacknowledged bytes, reorder
bytes per stream, live streams, lanes, acknowledgement ranges, topology descriptors,
endpoint bytes, and queue capacity. Product defaults include a 64 KiB frame ceiling, 8
MiB reorder ceiling per stream, 64 receive streams, 32 acknowledgement ranges, and 32
runtime lanes. All arithmetic is checked; limit exhaustion rejects or backpressures new
work rather than evicting authenticated established state.

Product ingress admits at most 16 incomplete and 64 active sessions, prepares at most 32
handshakes per provider listener, and completes at most 32 admissions concurrently. An
incomplete initial pool expires after five minutes. These are product limits, not fields
that an unauthenticated peer can raise.

## Public API and proof

`BondedStream` implements Tokio `AsyncRead` and `AsyncWrite`. `BondSession` opens and
accepts role-separated streams, changes predeclared lanes, reports bounded telemetry, and
closes cleanly. `BondDialer` and `BondListener` own provider lookup, policy, formation,
dynamic addition/replacement, progress, and cancellation; their exact contract is in
[provider-api.md](provider-api.md).

The deterministic suites cover codec rejection, fixed-seed parser mutation, join
authentication, version compatibility, record tamper/replay, exact reassembly, lifecycle,
backpressure, full-duplex progress, zero-lane repair, topology replay, liveness, adaptive
scheduling, resource bounds, payload/scratch reuse, and controlled paced-lane efficiency.
Public overlay campaigns prove product integration and are catalogued in
[evidence.md](evidence.md). Exact historical measurements are not protocol guarantees.

## Explicit non-solutions

- Round robin is not acceptable scheduling for unequal lanes.
- Opening several sockets through one router does not create independent failure domains.
- Reliable provider writes do not replace bond-level acknowledgement and retention.
- One monolithic SSH stream per destination is not acceptable for concurrent commands.
- Treating the private broker socket as a stable public API is not acceptable.
- A peer-selected address or filesystem path is not an acceptable service registry.
- Blindly echoing opaque encrypted SSH bytes is not safe terminal prediction.
- Maximum lane count is a safety bound and test dimension, not a performance target.
- Custom multipath semantics do not justify custom cryptographic primitives.
