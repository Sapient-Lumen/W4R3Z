# IoTox protocol map — rev0051

This document maps the current wire, local, and storage protocols. It is not one undifferentiated
protocol. Each lane has a distinct trust and durability contract.

## Transport lane

Tox currently supplies:

```text
public-key transport identity
friendship and encrypted peer session
bootstrap/DHT/TCP relay connectivity
lossless and lossy custom packets
human text messages and read receipts
finite file transfer
```

Tox/native is the default. Tox/Tor is construction-enabled only through the strict explicit numeric
SOCKS/bootstrap/relay policy in ADR 0190 and has one separately bounded operator-Tor public-route
qualification under ADR 0191. Tox/I2P is a strict explicit route qualified through the actual-I2P
Sandwurm topology under ADR 0253. Direct IoTox-over-Tor or
IoTox-over-I2P would be separate transports.
The old `tox/i2p-construction` spelling from ADR 0213 remains a deprecated reproduction alias. It
maps to the same route; neither spelling changes this peer protocol.

All calls for one `Tox*` are serialized on one owner thread. Friend numbers are transient provider
handles, not durable protocol identities.

Owner admission has three local-only traffic classes:

```text
interactive  human text/typing and latency-sensitive packet work
control      session, authority, command, and transfer control
bulk         file offers, seeks, and chunk service
```

An 8:4:1 weighted schedule services at most 16 calls before `tox_iterate`. This is not a wire
priority bit: a peer cannot select a local class by sending data. Requested and effective iteration
intervals and per-class queue wait are observable.

## IoTox machine lane

The current custom-packet lane carries bounded versioned envelopes with:

```text
protocol major/minor
message type and flags
message ID and correlation ID
sequence number
expiry field
bounded payload
```

The implemented path is:

```text
HELLO
CAPABILITIES / transcript confirmation
AUTHORITY_CHALLENGE / AUTHORITY_PROOF
COMMAND / ACK / RESULT
```

Machine operations are application protocol, not Tox text. A transport friend must still complete
session and authority gates before an operation is admitted. Authority-ledger v2 is separately
negotiated by feature bit 24; v3 requires both that lineage bit and feature bit 25. Feature bit 23 for
the Ratox terminal service is omitted by default
and enters one process's frozen local HELLO only after explicit pre-network activation succeeds.
Feature bit 27, `application-epoch-restart-v1`, is also runtime-gated behind a separate locked,
device-signed durable incarnation. It permits only a strictly greater ordered process/connection
generation to start a fresh application handshake while Tox remains continuously online. It carries
no authority or work across that edge; stale generations are ignored and changed bytes at the same
generation retain the original fail-closed conflict. See `protocol-application-epoch-restart-v1.md`
and ADR 0183.

Feature bit 28, `private-route-binding-v2`, depends on authority-ledger-v1 and route-binding-v1 and
remains outside the default feature mask. Its explicitly gated Agent construction moves the complete
signed route inventory to message type 26 on an exact authority-authenticated primary session.
Message type 27 then proves only one privately expected auxiliary member while binding the complete
inventory digest and auxiliary transcript. Route-binding-v1 type 19 stays frozen. See
`protocol-private-route-binding-v2.md` and ADRs 0198/0199/0200/0201.

Feature bit 29, `state-sync-content-v2`, depends on state-sync-v1 and remains outside the default
feature mask. Canonical message types 28/29 request and answer one exact manifest page or artifact
chunk bound to namespace, frozen signed-HEAD record digest, object digest, logical index, byte size,
and FileId. Types 30/31 carry one exact bounded little-endian page/chunk availability window for the
same frozen HEAD. The Agent dynamically advertises and dispatches the feature only after content
services, startup recovery, and authenticated live-graph validation succeed. Local flat/paged
publication signs HEAD last; the subscriber bootstraps the root and accepts only after whole-artifact
CAS; activation is explicit; and maintenance is quarantine-only. The one-source primary-carrier path
passes genuine c-toxcore over direct UDP and forced TCP. The deterministic product receiver also
consumes exact sparse windows from explicit independently authorized primary peers while preserving
the original frozen HEAD. Genuine direct-UDP multi-source carriers now pass in the three-agent
Sandwurm gate. Atomic owner-local multi-source admission and explicit fail-closed recovery after
selected-source loss now pass over direct UDP. A device-authenticated availability-only replica
record also cold-starts the partial source without entering publication, acceptance, or activation
state. One-source actual-Tor content now passes with native primary authority/HEAD and an exact
Tor worker carrier. Genuine complementary multi-source also passes with two native publisher
authority sessions and two distinct exact Tor worker identities; this does not claim separate Tor
circuits or physical paths. Selected-worker loss also passes through two public relay records.
Bounded same-source page/chunk concurrency now passes with two exact lanes over direct UDP and forced
TCP while root and HEAD remain serial. Stable-session cap `1/2/4/8` science finds a forced-TCP
throughput knee at cap 4 and a noisy non-monotonic direct-UDP result, so default one remains frozen
pending repeated and competing Ratox-latency evidence. One stable source/authority session now also
passes whole-object distribution over two distinct exact Tor workers; both paths contribute while
their route-local friend numbers collide safely. Byte striping, useful multipath speedup, independent
circuits/physical paths, I2P content, and transparent same-job continuation remain unqualified. Thirteen bounded
relay/admission/rendezvous cells did not retain a
second source through v3 authority; the strongest hybrid only confirmed transiently before returning
offline. See `protocol-sync-content-v2.md` and ADRs 0244–0263.

Feature bit 30, `state-sync-tree-v2`, depends on state-sync-v1 and is dynamically advertised when
synchronization services are active. Lossless types 32/33 request and return at most 16 canonical
signed writer-branch record identities. Types 34/35 request one exact branch record, manifest, or
file digest and bind its following primary-lane Tox offer to a nonzero FileId and declared byte
count. The subscriber closes every signed predecessor/observation edge and commits CAS before branch
pointers before writable projection. The complete fixed payload layouts and status values are
frozen in `protocol-sync-tree-v2.md`; ADRs 0272/0273 define causality and activation.

Feature bit 31, `state-sync-tree-checkpoint-v2`, depends on feature bit 30 and is advertised with an
active tree-v2 service. It adds no message type. A format-2 signed branch record is a conflict-free
checkpoint whose observations authenticate the exact subsumed frontier but terminate graph fetch.
The publisher refuses an inventory containing one unless bit 31 was negotiated, and the subscriber
independently refuses such a record without the same bit. Ordinary format-1 branch bytes and types
32--35 remain unchanged (ADR 0275).

## Authority format boundary

A valid unmigrated ledger remains v1 and knows only capability bits 0 through 6. One owner-self-signed
`migrate-v2` record extends the exact v1 tail under independent record/digest domains and retains the
owner at exactly `0x7f`. Existing principals are not widened. Bit 7, `interactive.terminal`, can appear
only in a later explicit signed v2 grant that also satisfies the format-specific role ceiling.

One later owner-self-signed `migrate-v3` record extends only an exact v2 tail under a third independent
record/digest domain and preserves every principal's exact capability mask. Bits 8 through 11 name
`sync.admin`, `sync.publish`, `sync.subscribe`, and `sync.activate`; none appears through migration.
The owner must explicitly self-grant missing v3 rights before delegating them.

V2 challenge/proof records carry ledger format 2 and require the shared `authorization-ledger-v2`
feature for the exact confirmed epoch. Remote mutation preparation and application bind the exact
format, ownership epoch, sequence, and tail. A private committed/pending guard detects rollback,
deletion, or fork of the ledger alone and recovers either exact interrupted replace state.
Coordinated replacement of both ledger and guard still requires an external monotonic witness. See
`protocol-authority-v2.md`, `protocol-authority-v3.md`, ADR 0063, and ADR 0091.

## Durable identity and commit order

Transport friend number, Tox public key, IoTox stable principal, and command identity are different
values.

A durable command is keyed by stable sender identity, sender epoch, and message ID. Its immutable
request bytes and terminal result are signed/stored under explicit policy.

Required order:

```text
validate bounded syntax and authority
commit durable request/admission state
only then send ACK or begin effect
commit terminal result
only then send/result-replay it
```

Transport reliability does not imply application completion. Retries return the prior result for an
already completed command rather than repeating an effect.

## Human Tox text lane

Normal and action messages use c-toxcore's friend-message API and callbacks. They have their own
ratox-style `message` and `action` FIFOs plus bounded journals.

Text send acceptance means c-toxcore admitted the local message. Read receipt means the remote Tox
client acknowledged the Tox message number. Neither means an IoTox command executed or authority was
granted.

rev0018 retains the pinned provider text limits/error mapping and performs no hidden durable retry.

## Interactive research lane

rev0018 consumes both official c-toxcore custom-lossless and custom-lossy APIs. Two diagnostic
echoes isolate their latency from human-text read receipts and may be deterministically padded from
10 through 1,200 bytes for pacing science:

```text
0xA1  custom-lossless request/reply
0xC8  custom-lossy request/reply (c-toxcore application range; 0xC0..0xC7 are ToxAV)
```

Each packet contains only request/reply kind, one random nonzero 64-bit nonce, and validated
nonce-bound padding. The agent answers only for a transcript-confirmed IoTox peer, reply size equals
request size, and the seam is reachable only through an explicit local research operation. These
IDs are not IoTox protocol 1.0 frames and are not advertised features.

The founding-host gates choose paced custom lossless as the first Ratox interactive carrier. Lossy
is not a terminal reliability protocol, and text remains chat. ADR 0061 freezes packet `0xA2` Ratox
1.0 framing with complete attachment fencing and cumulative byte positions. rev0020 retains the
strict codec, R1 session/replay engine, R2 authority bit, R3 fixed-profile PTY boundary, R4 Agent
coordinator, and R5 controller behind explicit default-off gates.

A live inbound `0xA2` packet is dispatched only when the current online epoch is transcript-confirmed,
both peers negotiated bit 23, the peer has an authenticated stable principal, and the exact current
authority-ledger head grants `interactive.terminal`. The coordinator reserves replay output before an
effect, stages whole INPUT frames, ACKs only complete PTY commitment, retains outbound packets across
retryable toxcore rejection, detaches stale routes, and begins closure on exact authority loss. See
`protocol-ratox-v1.md` and ADR 0065.

## Local terminal policy and process lane

This lane is not a wire protocol. It is an owner-only local policy/store plus a private parent/child
handoff used by native tests:

```text
ROOT/profiles/<profile-id>.profile
ROOT/bindings/<stable-principal-hex>.binding
parent -> hidden iotox child: canonical bounded binary manifest + open descriptors
hidden child -> parent: readiness record, structured setup error, or close-on-exec success EOF
```

Profile and binding records use strict canonical text described by `terminal-profile-v1.md`. The
registry resolves one enabled profile for one stable principal and freezes a policy generation,
fixed argv, cwd, exact environment, dimensions, identity, limits, and close graces. The network
carries none of these values and cannot name the profile.

The binary manifest is private local IPC, not Ratox framing. It is decoded and re-encoded
canonically, bounded to 128 KiB, and accepted only by the exact hidden child entrance. The child
receives PTY slave, target executable, and cwd through fixed descriptors; readiness plus status-fd
close-on-exec EOF proves final exec. Feature bit 23 remains unset by default and is selected only by
the explicit host Agent activation gate after this local policy is securely loaded.

## Private local terminal controller lane

The controller uses a separate persistent local stream rather than finite administrative RPC:

```text
<runtime>/terminal.sock
Linux AF_UNIX SOCK_SEQPACKET, owner-only mode 0600, same UID by SO_PEERCRED
32-byte canonical ITTS/1.0 header + 0..16384 payload bytes
```

Header bytes are frozen as: magic `ITTS`; major/minor; packet type; flags; nonzero stream ID;
cumulative sequence; two-byte typed status; two-byte payload length; and four reserved zero bytes.
A golden vector freezes the complete 32-byte image. OPEN/OPENED, INPUT/OUTPUT, RESIZE, DETACH, CLOSE,
OUTPUT_ACK, OUTPUT_GAP, EXIT_STATUS, ERROR, PING, and PONG have exact direction and payload rules in
`terminal-client-v1.md`.

The first complete `OPEN` is subject to a finite 1 ms..60 s local admission lease (5 s default).
While one stream is active, the implementation consumes at most four contender connections per
service cycle and gives the batch one shared 20 ms window for first records. That record may be decoded only to bind
the typed busy response to its stream ID; it is never dispatched. Before OPENED, an ERROR may be
connection-scoped because admission can fail before the requested ID is known or committed. Every
success/progress packet and all admitted-stream traffic still require exact stream-ID equality.

The socket pathname is an adapter to one pure controller state machine. It owns local framing,
credential/path/inode hardening, and terminal restoration. The Agent owns exact live-peer resolution,
Ratox route identity, replay bounds, and transport admission. The remote host remains responsible for
authority, fixed profile selection, and PTY creation. The reliable local link rejects duplicate or
inconsistent state; only the Ratox network layer performs replay reconciliation.

The public one-binary commands are:

```text
iotox terminal PEER_PUBLIC_KEY_HEX
iotox terminal-resume SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]
```

Both host and controller gates remain disabled by default. The implementation permits one admitted
local stream, bounds pre-OPEN contention, and reserves a signed host incarnation before networking.
Local and deterministic-provider process gates cover controller death/replacement, reconnect, SENDQ
pressure, revocation, and explicit daemon-restart failure. Genuine two-guest ADR 0197 evidence adds
transport-loss PTY retention: a heartbeat miss is warning-only; authoritative peer-offline returns
typed `unavailable` locally while leaving the bounded remote PTY detached; explicit resume requires
a higher authenticated epoch and exact session/incarnation/byte positions. It does not claim PTY
survival across Agent/host restart, power-cut durable recovery, or automatic route migration.

## Friendship lifecycle lane

Friendship is local transport mutation, not an IoTox wire message or authority record.

### Outgoing request

The ordinary root adapter is:

```text
RUNTIME/request
<76 hex complete Tox address><TAB><1..921 message bytes><LF>
```

The line adapter removes LF, decodes the complete 38-byte address, and passes exact message bytes to
the same typed Agent operation as:

```text
transport-peer-request(address, message)
```

c-toxcore remains authoritative for checksum, own-key, duplicate/already-sent, changed-nospam, and
provider errors. Local admission does not prove remote observation or acceptance.

The local record is not an IoTox over-wire frame and has no durable identity, expiry, or retry
semantics. A future outbox must be a separately specified facility.

### Incoming request and established removal

A callback projects `requests/<PUBLIC-KEY>/`; `accept` calls `tox_friend_add_norequest`, `reject`
withdraws only the live IoTox record, and `remove` resolves/deletes by public key in one owner-thread
operation.

Every friendship mutation leaves the independent signed authorization ledger unchanged.

## Ratox-successor local ingress

The private local surfaces are adapters to typed Agent operations:

```text
Unix SOCK_SEQPACKET control
root request FIFO
incoming accept/reject FIFOs
per-peer remove/message/action/command/file FIFOs
regular-file projections and bounded journals
```

The filesystem does not become a second business-logic implementation. Local adapters own framing,
credential/path hardening, and evidence publication. Agent/transport/store components own semantics.

Local-control v1.36 operation 39 exposes `route-health [FRIEND]`. Empty payload samples exact
c-toxcore self-connection truth and the local route boundary; an eight-byte friend/timeout payload
adds the already defined transcript-confirmed lossless echo. The text response is content-free and
explicitly auxiliary. It is not a machine-lane frame, carrier-state transition, session heartbeat,
or online-epoch transition (ADR 0192).

`route-health-watch [FRIEND]` remains an owner-CLI loop over operation 39 rather than a new local
protocol operation. It strictly parses the canonical report and keeps independent bounded
process-local hysteresis; no monitor state is installed in the Agent. The local terminal PING is a
different existing ITTS operation: the Agent maps it onto the exact current frozen-v1 Ratox PING and
returns local PONG only after the correlated remote PONG. One exact Ratox PING message ID is reused
per attachment to bound the never-evicted replay cost (ADR 0193).

Local-control v1.37 operation 84 exposes one explicit `route-target-health` sample. Its four-byte
payload contains only a 1..5000 ms deadline. The Agent, never the request, selects index zero of the
already validated explicit numeric Tox/Tor TCP-relay configuration, performs a complete SOCKS5
no-auth numeric CONNECT, sends no application bytes, and returns only stage, typed health, RTT, and
numeric SOCKS reply. Native routes, arbitrary targets, names, watch integration, carrier mutation,
and session effects are absent (ADR 0194).

Local-control v1.38 operation 85 adds a versioned sync-pull policy entrance. Its payload is one
canonical failover byte (`1 available`, `2 fail-closed`), friend number u32, then 1..64 namespace
bytes. Operation 68 remains valid and captures the daemon default. Operation 85 freezes the named
value on the created job; a conflicting retry is rejected. This changes no IoTox peer frame
(ADR 0221).

Local-control v1.39 operation 86 extends that entrance with one leading route-class byte (`1 any`,
`2 tox/native`, `3 tox/tor`, `4 tox/i2p`). Named classes require an exact
authenticated auxiliary worker and never silently use the primary carrier. This remains local
policy. ADR 0253 changes only the canonical text for byte 4; the construction alias still parses
to it and existing requests remain valid (ADRs 0222 and 0253).

Local-control v1.40 operation 87 adds one source to an active content-v2 pull. Its payload is exactly
one nonzero job identifier u64 followed by a friend number u32. The selected primary peer must be
application-ready with bit 29 and independently satisfy exact-v3 `sync.publish` plus writer
membership. This owner-local mutation cannot replace the original frozen HEAD, activate content, or
select an auxiliary carrier. It only permits exact sparse-window scheduling through the added
authenticated peer (ADR 0254).

Local-control v1.41 operation 88 atomically starts a content-v2 pull with every known source. Its
payload is auxiliary-count u8 (`1..15`), primary friend u32, that many distinct auxiliary friend u32
values, then 1..64 namespace bytes. The Agent authenticates every source and registers all
auxiliaries before dispatching the primary HEAD. Any pre-dispatch failure cancels the new job. The
operation changes no peer frame and grants the auxiliaries neither HEAD nor activation authority
(ADR 0256).

Local-control v1.42 operation 89 imports one canonical 296-byte foreign-writer content-v2 HEAD after
one namespace-length byte and the namespace. The complete root/page graph must already verify in
CAS. A fixed local-device custody signature persists the original signed record under
`replica-heads/`; later imports must be duplicate or one same-writer exact linked advance. This
availability state may serve the frozen record after restart but is never local publication, remote
HEAD acceptance, or activation authority (ADR 0257).

Local-control v1.43 operation 90 atomically starts a content-v2 multi-source pull with one named
auxiliary route class. Its payload is route-class u8 (`2 tox/native`, `3 tox/tor`, `4 tox/i2p`),
auxiliary-count u8 (`1..15`), primary friend u32, that many source friend u32 values, then 1..64
namespace bytes. Distinct source values mean distinct principals; a repeated source value requests
another distinct exact carrier for the same principal/authority session (ADR 0269). Agent
independently authenticates every primary source session, selects one ready bit-29 worker in that
exact class for each requested path, freezes all source carrier
bindings, and only then releases the HEAD request on the original primary session. Workers accept
only existing content types 28--31; HEAD, authority, and activation framing do not move. Exact worker
loss fails the whole job (ADR 0258). Owner-private status renders one bounded per-source authority/
carrier record; it changes no local-control or peer wire bytes. ADR 0259's accepted actual-Tor gate
uses those records to bind two source principals to two distinct worker keys before verifying
complementary object contribution, HEAD-last acceptance, and explicit activation.
ADR 0269's same-source gate instead binds one principal and primary authority tuple to two distinct
route/worker keys. Per-path requested/committed/fetched counters prove positive whole-object
contribution on both, and full-carrier correlation permits equal route-local friend numbers.

Local-control v1.44 operations 91--94 install and inspect owner-local synchronization automation;
they add no peer frame. Local-control operation 95 creates a managed namespace and policy. Its v1.45
payload is interval milliseconds u32, namespace-length u8, 1..64 namespace bytes, then one canonical
absolute source path. Local-control v1.46 retains that form and adds an extended form: the namespace
length's high bit is set, one mode byte follows (`1` sole-writer, `2` read-write), then the same
namespace and path. A sole-writer regular file selects content-v2 and a directory selects
treepack-v1. Read-write requires a directory and selects tree-v2. The generated root is private local
state and may not overlap the source.

Operation 96 prepares a read-only share from friend u32, the reconstructed 32-byte owner public key,
and 1..64 namespace bytes. It returns a grant-required byte, the exact 32-byte stable peer principal,
and, only when needed, the canonical authority-record body for client-side RecallRoot signing.
Operation 97 commits friend u32, namespace-length/name, the prepared stable principal, and zero or one
complete signed authority record. The Agent rechecks friend/principal binding, durably grants only
`sync.subscribe` when required, then adds only subscriber membership. These operations do not choose
recipient-local policy (ADR 0271).

Local-control v1.46 operations 98/99 are the corresponding read-write prepare/commit transaction.
They preserve the operation 96/97 shapes but require a tree-v2 namespace, grant both
`sync.subscribe|sync.publish`, add the exact stable peer to subscriber and writer membership, and
replace only an existing local `writable`/same-peer `bidirectional` automation with a
stable-principal-bound `bidirectional` record. The Agent rechecks application readiness, authority-v3
device proof, membership bounds, publisher replay quiescence, active pulls, durable authority, and
the prepared principal before each effect (ADR 0273).

Local-control v1.47 operations 100--105 add owner-local tree-v2 maintenance without changing peer
message types. Operations 100, 103, and 104 carry a 1..64-byte namespace. Operations 101/102 append
one exact 32-byte branch-record digest; operation 105 appends one exact 32-byte stable writer key.
They respectively checkpoint, show maintenance state, restore authenticated quarantine, pin, unpin,
and establish an exact terminal writer cutoff. Existing operation 77 dispatches tree-v2
`dry-run|quarantine` GC through the same public command spelling used by the immutable sync engines.
Every mutating operation runs under the namespace transaction (ADR 0275).

Local-control v1.48 operations 106--107 add content-free retained-controller session inspection and
exact authenticated session close. A detached close request traverses the unchanged Ratox RESUME and
CLOSE frames; neither operation changes Ratox v1 or local terminal-socket v1 framing (ADR 0285).

Local-control v1.49 introduced operation 108 with an empty payload and the Agent-validated
`iotox-diagnostics-redacted-v1` text projection; v1.55 replaces new responses with the backward-
inspectable v2 projection described below. It never returns the signed recorder, device key,
signature, paths, content, identities, or timestamps. The CLI validates that projection before
building a separately bounded identity-free bundle; no peer, Ratox, synchronization, authority, or
terminal framing changes (ADR 0291).

Local-control v1.50 operations 109--113 add owner-local peer-alias list, set, rename, remove, and
resolve. Requests use bounded canonical alias codecs; resolve returns one exact 32-byte Tox key.
Set rechecks that key against the current friend inventory, while deletion of a transport peer does
not mutate the alias store. These operations grant no authority, create no friendship, and change no
peer, Ratox, command, or synchronization framing (ADR 0292).

Local-control v1.51 operation 114 accepts the canonical bounded invitation-create request and returns
one exact 320-byte stable-device-signed artifact for the Agent's current complete Tox address. It
does not write a file or create friendship/authority. Offline inspect/import and explicit acceptance
compose file-local validation plus existing operations 18, 20, and 110; no peer, Ratox, command, or
synchronization wire framing changes (ADR 0293).

Local-control v1.52 operations 115--119 add owner-local tree-v2 history, diff, conflict, forward-
restore plan, and forward-restore apply. Operation 115 carries limit u16 then a 1..64-byte namespace.
Operations 116--119 carry namespace-length u8 and namespace; diff appends two record digests,
conflicts appends zero or one record digest, plan appends a target record, and apply appends target
record plus exact plan ID. Paths in text results are hexadecimal and detail has explicit omission.
Apply re-derives the optimistic-concurrency plan and authors a higher local branch generation; it
never makes the target record current. Operation 104 remains quarantine repair. No peer, Ratox,
command, or synchronization wire framing changes (ADR 0294).

Local-control v1.53 operation 120 carries namespace-length u8, include-count u8, exclude-count u8,
the namespace, then length-prefixed canonical rules. Zero rules inspects; nonzero rules atomically
replace both local sets. Operation 121 carries one namespace and clears to complete intent. These
recipient-local controls change no peer frame, authority, or destination path. Tree pulls retain the
complete authenticated branch/manifest graph while requesting only selected file objects; status,
repair, and GC expose exact partial custody (ADR 0295).

ADR 0296 widens the already frozen owner-local operations 87--88 to tree-v2 jobs without changing
their payloads or values. Operation 88 registers every primary-lane source before the primary
inventory request leaves; operation 87 can extend an active job. The existing tree object result is
the authenticated availability probe: `absent`/`unavailable` advances the exact digest to the next
source, while `denied`, binding drift, or exhaustion fails closed. The primary alone supplies the
frontier, and no peer frame or feature bit changes.

ADR 0329 changes no frame, operation number, or feature bit. It lets one tree-v2 pull keep a bounded
local vector of active exact-object requests after the manifest has expanded. The effective cap is
the minimum of process `--max-sync-tree-lanes`, namespace `maximum-lanes`, and namespace
`maximum-outstanding-requests`; status reports `tree-lane-cap`, `active-lanes`, and one
`tree-lane-job=` record per FileId/source/staging binding.

Local-control v1.54 operation 122 carries a mode byte (`0=cached`, `1=refresh`) followed by one
namespace. It verifies or refreshes one fixed stable-device-signed content-free tree-v2 health
record. The derived result covers selected custody, convergence, conflicts, cutoffs, automation,
active-store pressure, and last exact-probe source evidence. It changes no peer, Ratox, command,
authority, or synchronization-object frame (ADR 0297).

Local-control v1.55 retains no-payload operation 108 and changes only its self-described response to
`iotox-diagnostics-redacted-v2`. The Agent verifies cached tree-v2 health records and exports anonymous
aggregate counts without names, paths, keys, content, namespace/policy commitments, or stable
per-namespace slots. Standalone inspection retains v1 compatibility. The outer bundle and every
peer-facing frame are unchanged (ADR 0298).

Local-control v1.56 retains operation 108 and emits `iotox-diagnostics-redacted-v3`. The Agent reuses
the administrative host sampler in passive/no-fork mode, then exports only closed capability grades,
known-controller/interface masks, and an unknown-controller count. Standalone inspection retains v1
and v2 compatibility. No raw host path/text or peer-facing frame is added (ADR 0299).

A FIFO write is not a receipt. Evidence must distinguish:

```text
kernel byte admission
local parser admission/rejection
Agent/provider admission/rejection
durable command commit
remote transport observation
application execution and terminal result
```

## Finite-file lane

IoTox exposes c-toxcore finite file transfer through local path/control records rather than carrying
file bytes in FIFOs.

```text
file-send      absolute local source path
file-receive   file number + TAB + absolute destination
file-control   file number + TAB + pause|resume|cancel
```

Incoming publication is atomic and no-clobber. Tox completion means transport completion; it does not
make the received object trusted, executable, durable across restart, or authorized firmware.

Signed manifests, immutable artifact identity, digest verification, anti-rollback, inactive-slot
staging, and health recovery are implemented behind explicit local construction. Remote
`update.stage` names only an exact accepted HEAD and additionally requires bilateral feature
negotiation plus current `install.firmware` authority. File receipt alone still grants none of those
rights, and remote apply/restart/confirm remains absent.

## Local friendship record bounds

The root request maximum including LF is 999 bytes. The actual opened FIFO's `_PC_PIPE_BUF` must be
at least that large, and a producer must issue one complete write. Reader call boundaries are not
record boundaries.

Malformed request evidence is identity-aware:

```text
no trustworthy key prefix             public-key=unknown
valid 64-hex key prefix only           key may be recorded as a hint
complete decoded address               provider disposition bound to key
```

No all-zero pseudo-peer is introduced.

## Evolution

Protocol additions require:

- explicit version/feature negotiation;
- bounded allocation and parser behavior;
- unknown optional versus required feature rules;
- stable error mapping;
- replay/duplicate semantics where effects are possible;
- an ADR when they change an ordinary local contract or authority boundary.

Compatibility may not silently route around a requested Tor/I2P policy, treat friendship as
permission, or weaken commit-before-effect ordering.
