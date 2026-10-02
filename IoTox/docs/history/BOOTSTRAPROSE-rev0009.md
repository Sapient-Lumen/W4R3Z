# BOOTSTRAPROSE — IoTox rev0009, “Sovereign Ledger”

```text
Project:          IoTox
Revision:         rev0009
Version:          0.9.0
Codename:         Sovereign Ledger
Immediate north: one-binary modern ratox successor
Current transport: Tox over native networking
Current session: HELLO, transcript confirmation, authority challenge/proof, device.describe
Current authority: signed local ledger plus bidirectional transcript-bound principal proof
Owned product code: C++20
Public product:   one executable named iotox
Pinned target:    c-toxcore 0.2.23, libsodium 1.0.22
Current date:     2026-08-14 America/New_York
```

This is the lone entrance to the datacube and the office from which an amnesiac successor can
resume the work. It is not a museum plaque. The office holder is expected to modify it
thoroughly when reality, decisions, code, or ordered work change.

The entrance has no maximum length. It does have minimum duties:

```text
state what the project is
state what is implemented
state what is only designed
state what has actually been tested
state what cannot yet be claimed
preserve decisions in force
expose the important hazards and unresolved questions
name the next executable work in order
show how to build, run, inspect, test, and package the cube
leave no hidden sovereign or ambiguous grant of authority
```

Concision means removing duplication and vague comfort. It does not mean omitting the fact an
office holder needs in order to make the next correct change.

---

## 0. `/run` — assume the office

### 0.1 Establish the cube

From the directory containing this file:

```sh
pwd
find . -mindepth 1 -maxdepth 1 -printf '%f\n' | sort
./.datacube/tools/check-lone-entrance.sh
```

The intended root is:

```text
IoTox/
├── BOOTSTRAPROSE.md
├── .gitignore
└── .datacube/
```

`BOOTSTRAPROSE.md` must be the only ordinary visible object. `.datacube/` is hidden so the
next reader meets one governing entrance rather than a wall of files. Nothing in the cube is
secret merely because it is hidden.

Enter the repository:

```sh
cd .datacube
cat REVISION
./build/gcc-debug/iotox --version 2>/dev/null || true
```

The expected identity is:

```text
rev0009
IoTox 0.9.0 rev0009
```

### 0.2 Read records in authority order

Do not rely on a previous assistant summary or on memory. Read current source and retained
records. The practical source-of-truth order is:

1. compiled code and exact tests;
2. accepted decision records that the code has not explicitly superseded;
3. this entrance;
4. current architecture/protocol/threat/roadmap documents;
5. current research and build reports;
6. old bootstrap prose and historical cubes.

Start with:

```sh
sed -n '1,260p' README.md
sed -n '1,320p' MANIFEST.md
sed -n '1,360p' docs/architecture.md
sed -n '1,420p' docs/protocol-session.md
sed -n '1,360p' docs/roadmap.md
sed -n '1,360p' docs/testing.md
sed -n '1,360p' docs/threat-model-draft.md
sed -n '1,260p' docs/decisions/README.md
sed -n '1,300p' docs/research/cloudtainer-build-report.md
```

Then inspect the implementation you intend to change. No prose permission can make code exist,
and no passing mock can make a real network path proven.

### 0.3 Build the owned implementation first

From `.datacube/`:

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel
ctest --preset gcc-debug --output-on-failure
```

The default suite has eight CTest entries. The unit/integration executable currently registers
81 compiled C++ checks. CTest supplies the exact mock toxcore, mock Argon2, and pinned word-list
paths. A deliberate direct run must provide those paths explicitly.

Inspect the product:

```sh
./build/gcc-debug/iotox --version
./build/gcc-debug/iotox --help
./build/gcc-debug/iotox bootstrap-seeds
```

Warnings are errors. Do not accept a green build that silently compiles a second public product
binary or bypasses the one-owner-thread toxcore boundary.

### 0.4 Run the one-binary product fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

The stronger exact fixture starts the actual `iotox run` process and uses that same executable
as the local operator. It crosses:

```text
one CLI/product binary
Unix SOCK_SEQPACKET control
agent dispatcher and bounded owner queue
one toxcore owner thread
exact shared-library C ABI mock
callbacks and bounded event queue
HELLO and transcript confirmation
bidirectional authority challenge/proof
a capability-gated COMMAND / COMMAND_RESULT
ratox-style journals and transactional projections
atomic savedata, device identity, and authority ledger
orderly stop, reload, and identity continuity
```

The mock is a distinct signed IoTox peer, not an echo. It has its own Tox perspective, session
nonce, stable Ed25519 principal, challenge, proof, and device description. The fixture grants
that exact principal `read.telemetry,write.settings,actuate` and proves these facts:

```text
first HELLO, CAPABILITIES, AUTHORITY_CHALLENGE, AUTHORITY_PROOF, and local
  device.describe enqueue each encounter one injected SENDQ
only byte-identical frozen records are retried
both transcript-confirmation directions complete
IoTox verifies the remote principal against the current signed ledger
our stable device identity answers the peer challenge without exporting its secret
a peer command before proof is denied
the same canonical device.describe after proof succeeds
a local device-describe request receives a bound 64-byte description after exact retry
reported peer principal equals the peer's challenge verifier device
runtime projections and private protocol journal converge
saved Tox identity, stable device identity, and authority ledger survive restart
```

`proof-sent` means the local queue accepted our proof; it is not a remote receipt. The exact mock
independently verifies the proof and records that evidence, but the network protocol does not
yet carry a proof acknowledgement.

### 0.5 Run the retained quality matrix

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh
```

The matrix covers:

```text
GCC debug
GCC release
Clang debug
Clang AddressSanitizer + UndefinedBehaviorSanitizer
GCC ThreadSanitizer
five Clang libFuzzer smoke targets
Mutorr preservation build and tests
```

The fuzz targets cover the outer frame, session records, local control, signed authority
records/proofs, and command/result/description records. Source corpora are immutable reviewed
seeds; fuzz growth lives only under a build tree.

Do not suppress a compiler, sanitizer, race, or fuzzer finding to make a lane green. Correct the
program, narrow the claim, or retain the exact platform limitation.

### 0.6 Attempt the product-shaped dependency build

Where outbound HTTPS and normal toolchains exist:

```sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
./dist/standalone/iotox --version
```

This path verifies immutable source archives listed in `dependencies.lock`, builds static
libsodium 1.0.22, compiles c-toxcore 0.2.23 from official source, and links one installed
`iotox` product. The linked provider must compile against official toxcore headers.

Then run:

```sh
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
```

The genuine-peer fixture is prepared to create two independent Tox identities, perform an
actual friend request and acceptance, wait for confirmed IoTox transcripts both ways, deliver
a message, stop, reload savedata, and prove identity continuity.

A DNS failure, missing upstream archive, or unavailable real network does not justify stopping
construction. Record the failed lane exactly and keep building all code whose contract can be
reasoned about and exercised locally. Never report an unexecuted lane as passing.

### 0.7 Research before changing a dependency or protocol contract

Each revision must recheck current upstream facts that materially affect the code. Prefer
release artifacts, official headers, source, and protocol specifications over commentary.
Retain source facts and IoTox inferences separately under `docs/research/`.

rev0009's current records include:

```text
docs/research/c-toxcore-0.2.23-authority-command-route-contract-rev0009.md
docs/research/libsodium-ed25519-authority-ledger-rev0009.md
docs/research/tox-session-confirmation-rev0008.md
docs/research/c-toxcore-0.2.23-custom-packet-send-contract-rev0008.md
```

The current upstream pin remains c-toxcore 0.2.23, released 2026-06-03. Its official header
continues to define lossless custom packets as reliable, ordered packets; the 1373-byte ceiling;
permitted lossless packet IDs; and `SENDQ` as a full local packet queue. The options API exposes
UDP, discovery, DHT-announcement, proxy, and DNS controls useful for later route experiments,
but none of those knobs proves Tox/Tor or Tox/I2P.

If a fact may have changed, browse it again. A historical note is not current evidence.

### 0.8 Leave a complete next cube

Before packaging:

```sh
./tools/check-lone-entrance.sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel
ctest --preset gcc-debug --output-on-failure
./tools/run-mock-node.sh gcc-debug
```

Remove generated build/dependency/install trees from the distributable source tree or let the
archive script exclude them. Preserve current logs and reports only when they honestly match
the revision.

Refresh retained evidence only from a completed matrix whose inputs still exist:

```sh
./tools/refresh-retained-artifacts.sh /path/to/build-matrix.log
```

The ordinary path reads `build/<preset>`. When evidence is being assembled in a clean source
copy from an isolated completed matrix, point at that matrix without moving its CMake caches:

```sh
IOTOX_ARTIFACT_BUILD_ROOT=/absolute/matrix/.datacube/build \
  ./tools/refresh-retained-artifacts.sh /absolute/matrix.log
```

The refresh runs the retained binaries, process fixture, no-build mock lifecycle, checksum
verification, install-surface check, and prebuilt smoke. A copied CMake cache is not evidence;
keep configured build trees at the paths at which CMake created them.

The archive filename contract is:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

For this revision the intended form is:

```text
IoTox-rev0009-YYYY.MM.DD.HH.MM-signed-principals-device-describe-sovereign-operation.zip
```

Use America/New_York local time. The final response presenting a cube must contain one link
only, with the complete filename written as the link text.

---

## 1. What IoTox is

IoTox is a C++20, one-binary, self-owned Tox device agent and modern ratox successor.

Its desired exterior is simple:

```text
start one program
own a peer identity
pair deliberately
inspect peers and state through ordinary files and commands
send text, machine frames, and finite files
watch what happened
restart without losing identity
operate without a mandatory vendor cloud
```

Its interior must be explicit:

```text
bounded data
one toxcore owner
canonical protocol records
atomic persistence
independent application identity
authorization roles and capabilities
durable command lifecycle
idempotency and replay rules
route policy
safe update policy
clear evidence boundaries
```

The project is not trying to replace Tox. Tox remains the primary connection fabric because it
already provides long-lived peer identities, encrypted friend sessions, NAT traversal,
bootstrap discovery, TCP relays, reliable custom packets, human text, and file transfer.

IoTox supplies the product semantics Tox intentionally does not supply:

```text
stable device/application identity above replaceable routes
owner re-entry from a permanent phrase
roles, capabilities, delegation, and revocation
machine-session negotiation and transcript agreement
durable commands, results, and state
physical-device policy
ratox-like local operation
```

The governing sentences are:

> From memory, you can reach your devices.

> From an ordinary shell, you can understand and operate them.

> Simple surface. Explicit semantics. Owner sovereignty.

A complete product may not pan out. The cube should still leave valuable, independently usable
results: a maintained C++ ratox successor, a disciplined toxcore adapter, real-peer fixtures,
bootstrap/relay stewardship tools, canonical device framing, an owner-reconstructible
authorization experiment, and upstream fixes.

---

## 2. Decisions in force

Decision records live under `docs/decisions/`. These summaries guide work but do not replace
the full ADRs.

### 2.1 Tox stays primary

Do not abandon Tox merely because ownership recovery, authorization, or durable commands are
hard. Those are application problems in every transport. Keep Tox behind a narrow boundary and
remove it from the sole root of authority.

```text
Tox answers: which transport peer/session carried these bytes?
IoTox must answer: which stable principal is this, and what may it do now?
```

### 2.2 One installed product executable

The public product is `iotox`.

```text
iotox run ...                 agent face
iotox --runtime ... COMMAND   local client face
iotox OFFLINE-COMMAND         retained read/build face
```

Internal libraries are acceptable. Separate installed daemon/client products are not the
default direction. Tests, fuzzers, mocks, and incubator programs are not products.

### 2.3 C++20 owns the product

Use GCC and Clang. Keep upstream C libraries behind exact C ABI or source-linked adapters. Do
not let C ABI declarations leak across the application. Prefer standard-library facilities and
small explicit dependencies.

### 2.4 One thread owns each `Tox*`

No business subsystem may call toxcore directly. One owner thread serializes creation,
iteration, callbacks, mutations, and destruction. Other code submits bounded operations and
receives copied bounded events.

### 2.5 Source-linked standalone is the product direction

Runtime library loading remains valuable for exact ABI mocks, diagnostics, and integration
experiments. The distributable direction is a pinned source-linked binary so “just werx” does
not require the operator to find a compatible `libtoxcore.so`.

The linked provider must use official toxcore headers. IoTox fallback declarations are only for
the runtime seam and must never be mistaken for source-integration proof.

### 2.6 Permanent RecallRoot remains

A permanent generated phrase, printable and memorable, is a retained feature—not a mistake to
remove. A fixed Argon2id derivation contract permits re-entry from memory.

That joy has a price:

```text
any offline verifier permits offline phrase guessing
password/phrase strength is structural, not optional
human-chosen weak phrases must not pass as safe
parameters, normalization, and domain separation must be fixed
phrase disclosure is ownership compromise
```

Do not “solve” offline guessing by adding an IoTox recovery sovereign.

### 2.7 No vendor reassignment key

IoTox must not possess a secret capable of changing ownership of customer devices. A
manufacturer may eventually attest hardware or sign releases, but it may not override the
owner ledger.

### 2.8 Authorization is independent of friendship

These statements are all distinct:

```text
peer is a Tox friend
peer is online
peer sent a structurally valid HELLO
peer negotiated compatible limits
both peers confirmed the same transcript
peer presented a stable IoTox principal
principal is in the current authorization ledger
principal has a requested capability
command is fresh, valid, and safe to execute
```

rev0009 implements through transcript confirmation, stable local device/owner principals,
and a signed local authority ledger. It does not yet bind a remote session to one of those
principals or authorize remote operations.

### 2.9 Public-key-first peer selection

Tox friend numbers are mutable local handles. Operator-facing durable selection prefers the
64-hex Tox public key. Friend numbers remain an accepted convenience where useful.

### 2.10 Structured core; ratox façade

The authoritative local mutation path is bounded, versioned `SOCK_SEQPACKET`. The ratox-style
filesystem is a private read projection. Future writable files/FIFOs may translate into the
same structured operations; they must not become an authorization store, durable queue, or
ambiguous transaction system.

### 2.11 Human and machine lanes stay separate

Normal/action Tox text is human presentation. IoTox machine traffic uses `0xA0` lossless custom
packets and strict binary frames. Human text is never executed as a device command.

### 2.12 Incoming friend requests require an explicit decision

An incoming request is copied into a bounded live public-key-first inbox. The operator may
accept or reject it. Request arrival or acceptance grants only a transport relationship.

The inbox is live/transient in rev0009. It is not crash-durable, an audit log, or authority.

### 2.13 Peers confirm before application traffic

Every true online epoch receives one canonical HELLO and one canonical CAPABILITIES record per
side. Compatible HELLOs are not enough. Both endpoints must confirm the exact same transcript
before application frames are admitted.

This is an unsigned session barrier, not owner authentication.

### 2.14 Local enqueue acceptance is the retry boundary

A successful lossless custom-packet send hands reliable ordered delivery to toxcore. IoTox does
not retransmit merely because an application response is absent. When toxcore explicitly
rejects the local enqueue with `SENDQ` or a temporary offline result, IoTox may retry only the
same frozen record in the same online epoch.

```text
accepted by toxcore       no blind IoTox retransmit
transiently not accepted  retry exact bytes and IDs after later iterate progress
terminal local failure    expose and stop automatic retry
```

Per-record attempt counters remain visible. A successful enqueue clears the temporary error.
The current 500 ms service cadence is an IoTox policy to measure against real c-toxcore, not an
upstream guarantee. ADR 0029 governs this boundary.

### 2.15 Tox routes are separate from transports

Current model:

```text
peer transport = Tox
route = native | Tor | I2P
```

Only Tox/native is enabled. Reserved routes fail closed. Direct Tor/I2P application transports,
if ever built, are separate designs.

### 2.16 Mutorr is preserved, not north

Small-circle namespace replication remains in an opt-in incubator and history. Do not let it
displace the ratox successor, real Tox integration, authority, or durable command work.

---

## 3. Current implementation truth — rev0009

### 3.1 Product graph

The installed product is one C++20 executable:

```text
iotox_core   internal static library
iotox        only public executable
```

Internal test executables, exact shared-library mocks, fuzzers, and the optional Mutorr
incubator are development facilities, not additional products.

The owned core contains:

```text
one-binary CLI/client and foreground agent
bounded local SOCK_SEQPACKET control
one-thread-owned toxcore adapter with runtime and source-linked provider modes
Tox profile, friendship, request, text, typing, receipt, packet, and finite-file paths
atomic savedata store and private runtime tree
canonical IoTox frame, HELLO, negotiation, and mutual transcript confirmation
stable Ed25519 device identity
RecallRoot-v1 stable owner derivation
canonical signed authority ledger
bidirectional authority challenge/proof state machine
first capability-gated machine operation: device.describe
```

### 3.2 What rev0009 added

rev0009 moves the project across three boundaries.

First, it gives the physical product a stable application identity above Tox. The device seed is
created with private permissions, atomically replaced, validated on load, and used for Ed25519
signing through the narrow libsodium provider. A Tox endpoint may later rotate without changing
this device principal.

Second, it gives ownership a sovereign local constitution. RecallRoot-v1 reconstructs one stable
owner principal. A short-lived client process can bootstrap, grant, or revoke fixed signed
records without sending the phrase, RecallRoot bytes, or owner secret to the daemon. The daemon
validates canonical records, ordering, previous-tail linkage, device binding, signatures, roles,
capabilities, replay, owner continuity, and a bounded record count before atomically committing
the ledger.

Third, it connects that constitution to the network. Each confirmed peer relationship has two
independent authority directions. IoTox challenges the peer against its current local ledger;
the peer signs the exact session/ledger/nonce context. IoTox separately answers the peer's
challenge with its stable device key. Reconnect or local ledger mutation invalidates the relevant
proof state.

The first real operation is `device.describe`. It is fixed-size, read-only, idempotent, and
requires `read.telemetry`. A response is accepted only when its protocol matches the confirmed
session and its stable device principal matches the verifier device named in the peer challenge.
The outbound request survives transient `SENDQ` only as one exact in-memory reservation.

### 3.3 State vocabulary

Keep these facts separate:

```text
Tox endpoint                     routable transport identity
stable device principal          long-lived IoTox application identity
RecallRoot owner principal       reconstructible sovereign owner authority
ledger principal                 role/capability entry under a specific ledger head
friend                           Tox transport relationship only
online                           toxcore connection state only
HELLO-compatible                 protocol overlap exists
transcript-confirmed             both peers confirmed the same session transcript
application-ready                machine frames may pass the session barrier
remote-authorized                peer proved an active local-ledger principal
claimant proof-sent              local tox queue accepted our signed proof
operation admitted               current principal has the required capability
operation completed              one correlated application result was accepted
```

None implies the next unless the code explicitly checks it.

### 3.4 What is locally proven

Current evidence includes:

```text
81 compiled C++ checks and eight default CTest entries
GCC and Clang builds with warnings as errors
ASan/UBSan and TSan matrix lanes
five libFuzzer smoke targets
stable device and owner deterministic/signature tests
ledger corruption, replay, sequence, signer, device, and owner-continuity rejection
a distinct signed mock peer for both authority directions
negative command before proof and success after proof
exact SENDQ retry for HELLO, confirmation, challenge, proof, and device.describe
principal/protocol binding on the returned description
one-product process lifecycle, files, journals, shutdown, and restart
Mutorr incubator preservation
```

### 3.5 What is not proven

Do not claim:

```text
a genuine c-toxcore library has loaded in this container
two real Tox peers have crossed a network
NAT traversal or TCP relay behavior is verified
Tox/Tor or Tox/I2P exists or is leak-free
source-linked static dependency build passes here
remote owner re-entry/discovery is solved
a proof receipt exists
device.describe survives process restart
durable command admission/results exist
any physical actuator is safe to connect
ledger rollback against a hostile old disk image is prevented
the plaintext mode-0600 device seed is hardware protected
production security, cryptographic audit, or target-hardware fitness
```

### 3.6 Current upstream posture

The pin is c-toxcore 0.2.23. That release reports a critical bug found by manual audit and fixes
without removing public APIs. IoTox therefore keeps toxcore behind a narrow boundary, pins and
verifies source artifacts, and signs application authority independently. Tox stays primary;
upstream maintenance evidence is a reason for disciplined updating, not abandonment.

## 4. One-binary operator surface

The public install surface is one executable. `FRIEND` accepts a local friend number or a
64-hex Tox public key; public-key-first selection is preferred.

### 4.1 Agent and inspection

```sh
iotox run [AGENT_OPTIONS]
iotox --runtime PATH ping
iotox --runtime PATH status
iotox --runtime PATH address
iotox --runtime PATH stop
```

### 4.2 Presentation, friendship, and human Tox lane

```sh
iotox --runtime PATH profile
iotox --runtime PATH profile-name TEXT
iotox --runtime PATH profile-name-stdin
iotox --runtime PATH profile-status-message TEXT
iotox --runtime PATH profile-status available|away|busy

iotox --runtime PATH transport-peer-request TOX_ADDRESS MESSAGE
iotox --runtime PATH requests
iotox --runtime PATH request-accept PUBLIC_KEY
iotox --runtime PATH request-reject PUBLIC_KEY
iotox --runtime PATH transport-peer-accept PUBLIC_KEY
iotox --runtime PATH transport-peer-remove FRIEND

iotox --runtime PATH message FRIEND TEXT
iotox --runtime PATH action FRIEND TEXT
iotox --runtime PATH message-stdin FRIEND
iotox --runtime PATH action-stdin FRIEND
iotox --runtime PATH typing FRIEND on|off
```

These operations manage transport and human communication. They grant no IoTox capability.

### 4.3 Stable identity and sovereign authority

```sh
iotox --runtime PATH identity
iotox --runtime PATH authority
iotox --runtime PATH principals
printf '%s
' 'eight generated words ...' |
  iotox --runtime PATH authority-bootstrap-recall-stdin
printf '%s
' 'eight generated words ...' |
  iotox --runtime PATH authority-grant-recall-stdin PUBLIC_KEY ROLE CAPABILITIES
printf '%s
' 'eight generated words ...' |
  iotox --runtime PATH authority-revoke-recall-stdin PUBLIC_KEY
```

The permanent phrase is read by the short-lived client from standard input. It is not sent over
the control socket. The client asks the daemon for an exact unsigned canonical record body,
derives/signs locally, wipes its buffers best-effort, and submits only the signed record.

### 4.4 Session and directional authority

```sh
iotox --runtime PATH sessions
iotox --runtime PATH session FRIEND
iotox --runtime PATH hello FRIEND
iotox --runtime PATH confirm FRIEND
iotox --runtime PATH authority-sessions
iotox --runtime PATH authority-session FRIEND
iotox --runtime PATH authority-challenge FRIEND
iotox --runtime PATH authority-prove-device FRIEND
printf '%s
' 'eight generated words ...' |
  iotox --runtime PATH authority-prove-recall-stdin FRIEND
```

Normal confirmed sessions automatically challenge the peer and automatically answer a peer
challenge with the stable device principal. The explicit commands exist for inspection,
interoperability, controlled retry, and owner-reentry research.

### 4.5 First machine operation

```sh
iotox --runtime PATH device-describe FRIEND
iotox --runtime PATH peer-description FRIEND
```

The first command reserves and sends one canonical read-only request. The second reports the
current correlated result. It is not a durable queue, does not survive restart, and must not be
used as the template for physical effects without the durable layer in ordered work.

### 4.6 Raw packet and finite-file seams

```sh
iotox --runtime PATH transport-send FRIEND PACKET_HEX
iotox --runtime PATH file-send FRIEND /absolute/source
iotox --runtime PATH files
iotox --runtime PATH file-receive FRIEND FILE_NUMBER /absolute/destination
iotox --runtime PATH file-cancel FRIEND FILE_NUMBER
```

The raw packet operation is a research seam and cannot forge session readiness in the dedicated
registries. Finite-file transfer remains bounded, paused-before-accept, path-policy checked, and
separate from firmware authorization.

### 4.7 Ratox-style observation

```sh
iotox --runtime PATH events
iotox --runtime PATH watch --watch-ms N
iotox --runtime PATH peer-messages PUBLIC_KEY
iotox --runtime PATH peer-watch PUBLIC_KEY
iotox --runtime PATH peer-session PUBLIC_KEY
iotox --runtime PATH peer-protocol PUBLIC_KEY
iotox --runtime PATH peer-protocol-watch PUBLIC_KEY
```

The filesystem and journal surfaces are private observations over structured state. They are not
constitutional storage and do not turn a write into a completed remote operation.

## 5. Runtime tree

The runtime root is private, disposable, and normally under a same-user runtime directory.
Durable Tox savedata, device identity, and authority ledger live outside it.

```text
<runtime>/
├── control.sock
├── status
├── events
├── self/
│   ├── address
│   ├── connection
│   ├── network
│   ├── name
│   ├── status
│   └── status-message
├── authority/
│   ├── device-public-key
│   ├── initialized
│   ├── ownership-epoch
│   ├── sequence
│   ├── tail-digest
│   └── principals/<principal>/...
├── requests/<tox-public-key>/...
├── peers/<tox-public-key>/
│   ├── number
│   ├── connection
│   ├── messages
│   ├── protocol
│   └── iotox/
│       ├── summary and session fields
│       ├── authority/
│       │   ├── verifier-state
│       │   ├── remote-authorized
│       │   ├── remote-principal
│       │   ├── remote-role
│       │   ├── remote-capabilities
│       │   ├── claimant-state
│       │   ├── local-claimant-principal
│       │   └── send-attempt diagnostics
│       └── description/
│           ├── state
│           ├── request-message-id
│           ├── result-message-id
│           ├── outcome
│           ├── send-attempts
│           ├── device-principal
│           ├── product/version/revision/protocol
│           ├── supported-features
│           └── offered-operations
└── transfers/<direction-friend-file>/...
```

Multi-file records are written through a staging directory and renamed into place before their
commit marker changes. Local commands that return a description publish the exact immutable
snapshot they return, making the projection a synchronization barrier rather than a later best-
effort approximation.

Security rules:

```text
runtime permissions are part of admission
peer keys, not names, select directories
untrusted bytes are escaped or stored separately
runtime projection is evidence and convenience, never authoritative state
journals are bounded by policy work still to be completed
```

A future FIFO façade may translate ordinary reads/writes into the same structured operations.
FIFOs must not become the durability or authorization model.

## 6. Local control contract

The single executable speaks a private Unix `SOCK_SEQPACKET` protocol to itself.

```text
major:              1
minor:              11
header:             24 bytes
maximum payload:    60 KiB
request/response:   correlated by uint64 request ID
admission:          same effective user on supported Unix credentials
```

The minor version now includes stable identity/ledger operations, directional authority
inspection and proof operations, and:

```text
51 protocol-device-describe
52 protocol-peer-description-show
```

Packet boundaries are preserved. Decoders reject unknown kinds/operations, reserved values,
length mismatches, and oversized payloads before dispatch. Public control mutations use exact
binary records or length-delimited data; presentation text is never confused with authorization.

The control socket is a local mechanism, not an ownership oracle. Product deployment must still
define runtime owner/group, service sandboxing, filesystem labels, and which local processes may
invoke the operator surface.

## 7. Toxcore boundary

### 7.1 Narrow consumed seam

The adapter consumes only the functions required for:

```text
options and instance lifecycle
savedata and self identity/profile
iteration and connection state
bootstrap and TCP relay
friend request/list/key/connection/remove
normal/action messages, typing, receipts
lossless custom packets
finite file offer/control/seek/ID/chunks
callbacks for the above
```

Keep exact limits and enum conversions in the boundary. Application code should use IoTox
values and `Status`/`Result`, not toxcore error enums.

### 7.2 Provider modes

```text
runtime provider
  loads an explicit shared library
  supports exact ABI mocks and operator integration
  uses IoTox fallback declarations

linked provider
  compiles pinned c-toxcore source
  requires official upstream headers
  is the standalone product direction
```

Both populate one function table and feed one owner-thread implementation. A provider must pass
version and required-limit checks before the agent claims readiness.

### 7.3 Owner-thread invariant

Public calls enqueue bounded operation objects. The owner thread is the only place that may
call toxcore. It iterates according to toxcore's interval and turns callbacks into copied
bounded events.

A timeout before an operation begins may cancel it. Once an operation begins, current local
semantics can return an indeterminate timeout while work finishes. This must be resolved before
physical commands use the same abstraction.

### 7.4 Savedata

The state store creates an unpredictable private temporary file, writes fully, synchronizes,
renames atomically, and synchronizes the parent directory. Mutation persistence is separate
from graceful shutdown persistence.

Current savedata is not encrypted by an owner-keystore layer. Do not imply that mode `0600`
solves device theft or privileged local compromise.

---

## 8. Capability session v1

The exact contract is `docs/protocol-session.md`. This section is a wake-from-amnesia summary.

### 8.1 Outer frame

```text
offset  size  field
0       1     discriminator 0xA0
1       1     protocol major
2       1     protocol minor
3       1     message type
4       1     flags
5       4     payload length, big-endian
9       8     message ID
17      8     correlation ID
25      8     sequence
33      8     expiry Unix milliseconds
41      N     payload
```

Tox maximum custom packet: 1,373 bytes. Current frame payload maximum: 1,332 bytes.

### 8.2 Canonical HELLO

Outer:

```text
protocol 1.0
type HELLO (1)
flags 0
nonzero unpredictable frozen message ID
correlation 0
sequence 1
expiry 0
payload exactly 64 bytes
```

Payload:

```text
0..3    IHL1
4       payload version 1
5       flags 0
6..9    minimum and maximum protocol versions
10..17  implementation version and cube revision
18..19  maximum frame payload, 256..1332
20..27  supported features
28..35  required features
36..43  maximum finite-file bytes
44..59  nonzero 128-bit session nonce
60..63  zero reserved
```

Current implemented features:

```text
bit 0 capability-session-v1, required
bit 1 tox-text-lane
bit 2 finite-file-transfer-v1 when nonzero limit
```

Named but not advertised:

```text
bit 16 authorization-ledger-v1
bit 17 durable-commands-v1
bit 18 state-sync-v1
bit 19 recall-reentry-v1
bit 20 signed-ota-v1
bit 21 route-binding-v1
bit 22 mutorr-namespaces-v1
```

### 8.3 Negotiation

Select the highest protocol in the range intersection. Require that each side supports every
feature required by the other. Intersect supported features. Select the smaller frame limit
and, when finite-file-v1 is shared, the smaller finite-file limit.

Negotiation must be symmetric. Implementation version is diagnostic, not a compatibility
shortcut.

### 8.4 Canonical confirmation

Outer:

```text
exact negotiated protocol version
type CAPABILITIES (2)
flags 0
nonzero unpredictable frozen message ID
correlation = peer's first accepted HELLO message ID
sequence 2
expiry 0
payload exactly 256 bytes
```

Payload:

```text
0..3      ICF1
4         payload version 1
5         flags 0
6         sender role: 0 lower transport key, 1 higher
7         zero reserved
8..9      selected protocol version
10..11    negotiated maximum frame payload
12..19    shared feature mask
20..27    negotiated maximum finite-file bytes
28..59    lower raw Tox public key
60..91    higher raw Tox public key
92..107   lower HELLO nonce
108..123  higher HELLO nonce
124..187  exact lower HELLO payload
188..251  exact higher HELLO payload
252..255  zero reserved
```

The public keys are ordered lexicographically as raw 32-byte arrays. This role ordering does
not depend on connection initiator or message timing.

The decoder preserves wire values, validates them against the embedded exact HELLOs, and only
then reconstructs diagnostic text. Never replace received fields with recomputed values before
comparison; that would hide tampering.

### 8.5 Online epoch and freeze

A true Tox `NONE -> online` transition starts an epoch with a new nonce and IDs. A UDP/TCP
presentation change while continuously online does not start a new epoch. A return to `NONE`
ends it.

```text
first local HELLO ID and bytes are frozen before the first send attempt
first local confirmation ID and bytes are frozen before the first send attempt
first valid peer HELLO body is frozen
first valid peer confirmation body is frozen
identical body retry is idempotent
changed body retry is conflict
```

### 8.6 Local enqueue recovery

c-toxcore's public API distinguishes a successfully accepted lossless packet from a packet that
never entered its queue. IoTox keeps that distinction:

```text
success                         toxcore owns reliable ordered delivery
FRIEND_NOT_CONNECTED            same unsent handshake record may retry after progress
SENDQ                           same unsent handshake record may retry after progress
invalid/empty/oversized packet  contract failure; do not retry as congestion
```

The current agent revisits incomplete sessions on a 500 ms best-effort cadence after toxcore
iterations. Successful HELLO or CAPABILITIES records are not retransmitted by an IoTox response
timer. This policy is exact-mock-tested and remains subject to real toxcore pressure testing.

### 8.7 Application gate

After both confirmations, later frames must:

```text
not be HELLO or CAPABILITIES
use exact negotiated protocol version
have nonzero message ID
fit negotiated payload maximum
```

This gate says that the frame belongs to the established machine language. It does not say the
sender may perform the requested operation.

### 8.8 Why the barrier exists

Reliable transport delivery does not itself prove that two implementations retained the same
advertisements and negotiation. Mature handshake designs use an explicit transcript commit
before ordinary application traffic. IoTox adopts that state-machine discipline without
claiming that unsigned CAPABILITIES adds a new cryptographic identity beyond Tox.

The future authorization proof should bind a stable application principal and ledger epoch to
this frozen session transcript.

---

## 9. Independent authority — signed directional proof and first operation

### 9.1 Separation in force

```text
Tox friend             transport relationship
confirmed session      exact online application channel
stable principal       Ed25519 identity above route/Tox keys
signed ledger          local roles and capabilities
challenge/proof        principal binding to this exact session and ledger head
command admission      capability check for one operation
```

Friendship never grants ownership. Session confirmation never grants authority. Proof of a
principal not present in the current local ledger is denied.

### 9.2 Canonical ledger v1

The durable ledger is an append-only sequence of fixed 256-byte signed records. Every record
binds the stable device principal, ownership epoch, sequence, previous-tail digest, action,
role, capability mask, issuer, subject, and Ed25519 signature. Replay computes the exact current
snapshot and rejects malformed records, broken sequence/linkage, wrong device, bad signatures,
unauthorized issuers, impossible owner continuity, invalid capability masks, and excessive
history.

Bootstrap creates the first owner. Grant/revoke records require a current active owner with
`manage.principals`. The ledger is atomically replaced and projected only after successful
replay. Ordinary files do not prevent rollback to an older internally valid image; that limit
remains explicit.

### 9.3 Roles and capability vocabulary

```text
roles: owner, administrator, operator, viewer, automation, service
capabilities:
  read.telemetry
  write.settings
  actuate
  manage.principals
  install.firmware
  export.diagnostics
  factory.reset
```

This is deliberately not a general policy language.

### 9.4 Directional network proof

`AUTHORITY_CHALLENGE` is one canonical 160-byte payload. `AUTHORITY_PROOF` is one 192-byte body
plus a 64-byte Ed25519 signature. The outer frame sequences are 3 and 4 after HELLO and
confirmation.

Each direction binds:

```text
verifier stable device principal
verifier ownership epoch, ledger sequence, and tail digest
canonical confirmed-session transcript digest
fresh 32-byte nonce
challenge message ID
claimant stable principal
signature over the entire canonical proof body
```

The first valid records freeze the online epoch. Changed transcript, nonce, device, ledger head,
message ID, principal, or signature fails. Local ledger mutation invalidates accepted remote
authority. Offline/reconnect creates a new transcript and authority exchange.

The automatic claimant is the stable device principal because its secret is already held by the
running product. RecallRoot owner proof is explicit and phrase-fed through a short-lived client.
The two directions may complete independently.

### 9.5 Current first operation

The first application operation is defined in `docs/protocol-command-v1.md`:

```text
COMMAND request       8-byte ICQ1 record
COMMAND_RESULT        16-byte ICR1 header plus bounded body
device description    64-byte IDD1 record
required capability   read.telemetry
```

Before proof, the operation is denied. After proof by a principal with `read.telemetry`, it
returns version, revision, negotiated protocol, stable device principal, implemented features,
and offered operations. The receiver binds the description principal back to the peer's
challenge verifier device.

The outbound local request freezes exact bytes before toxcore. Retry occurs only when toxcore
did not accept the packet. A successful enqueue waits for one correlated result. An exact result
duplicate is harmless; a second non-identical result for the same correlation is a conflict.

### 9.6 Current limits

```text
proof-sent is not a remote proof receipt
inbound command results are not durably retried on SENDQ
outbound request/result state is process-local
no durable inbox/outbox, deduplication store, or completion journal exists
no physical effect is admitted
a hostile old valid ledger image is not rollback-detected
stable device secret storage is mode-0600 plaintext seed mode
```

Therefore `authorization_ledger_v1` is advertised, but `durable_commands_v1` is not.

## 10. RecallRoot and owner re-entry

RecallRoot-v1 is now connected to the product's owner-signing path. Its governing promise is:

> From a permanent generated phrase, the owner can reconstruct the same owner principal without
> an IoTox account, a vendor oracle, or a vendor reassignment key.

The fixed contract remains:

```text
word list:     EFF long list, 7776 entries, pinned SHA-256
phrase:        exactly 8 generated list words
normalization: lowercase ASCII, whitespace collapsed, internal hyphens only
KDF:           Argon2id v1.3
memory:        65536 KiB
iterations:    3
parallelism:   4
salt:          16 fixed bytes "IoToxRecallRoot1"
output:        32 bytes
entropy:       about 103.4 bits when words are independently uniform
```

Fixed parameters make independent re-entry possible and also permit offline guessing against a
verifier. Password strength is therefore structural, not optional. User-chosen quotations,
short phrases, predictable word substitutions, and reused human passwords violate the design.
The permanent printed or remembered phrase is deliberately retained; it is sovereign owner
power, not a disposable login secret.

The current owner derivation is:

```text
RecallRoot-v1[32]
  -> keyed BLAKE2b-256 using domain "iotox-owner-signing-seed-v1"
  -> deterministic Ed25519 owner seed/keypair
```

The phrase, root, seed, and secret key stay in the short-lived `iotox` client invocation. They
are not sent over the local socket and are not stored in the ledger. The owner public key and
its signatures are public constitutional material.

Current consequences:

```text
the same phrase reconstructs the same owner principal on every device
offline phrase guessing is possible if an attacker has a verifier
phrase compromise compromises owner signing authority until an epoch/transfer design exists
forgetting the phrase does not reveal it through IoTox or a vendor service
printing and retaining the permanent phrase is a supported primary recovery practice
```

Still unresolved:

```text
how reconstructed owners discover current device route bindings without a vendor directory
network challenge/proof and controller delegation
multiple independent owners and quorum policy
phrase compromise, ownership transfer, and ownership-epoch transition
whether per-device delegated principals should reduce cross-device linkability
local data-encryption domains and old-ciphertext recovery
secure terminal entry and hostile-host resistance
```

No IoTox vendor service may become a required oracle for re-entry or a holder of a universal
reassignment credential.

---

## 11. Persistence, files, and future physical effects

### 11.1 Tox savedata

Current savedata continuity is real under the mock provider. The write discipline is sound for
power-loss resistance, but there is no encrypted keystore integration. A stolen state file may
expose the Tox identity.

Tox transport recovery should eventually be ordinary: generate/restore a new route identity,
bind it from the stable IoTox identity, increment the route binding epoch, and revoke the old
binding. A Tox profile must not be the sole ownership constitution.

### 11.2 Finite file path

The manager currently enforces regular-file sources, configured size/count limits, immutable
source checks, paused incoming offers, private temporary destinations, no-clobber publication,
and cleanup. This is useful product code now.

### 11.3 Firmware is not a file-transfer flag

A future OTA path needs:

```text
signed manifest
artifact digest and immutable identifier
target hardware/model/version constraints
storage reservation
anti-rollback value
staged write and post-write verification
safe boot/recovery strategy
health confirmation
explicit firmware capability
```

Tox encryption and file sender identity do not make executable bytes safe.

### 11.4 Durable commands

Physical effects require a durable lifecycle beyond transport acceptance:

```text
local submission accepted
peer received durably
execution started
execution succeeded or failed
command expired or was cancelled before start
```

Stable message IDs and idempotency are mandatory. A lost success acknowledgement must not cause
an unlock, payment, or actuator pulse to repeat accidentally.

The current owner-queue timeout semantics are suitable for research/control operations but not
yet for physical commands. Once an operation begins, the caller needs an operation ID and a
queryable result rather than an ambiguous timeout.

---

## 12. Network direction

### 12.1 Tox/native

This is the only enabled route. The next external gate is to compile pinned real toxcore and
cross two genuine peers. Then measure bootstrap, reconnect, TCP relay, NAT, idle traffic,
memory, CPU wakeups, and long offline behavior.

### 12.2 Tox/Tor

Reserved only. A plausible experiment requires TCP-oriented toxcore behavior, UDP and local
discovery disabled, explicit proxy/tunnel and relay policy, no native DNS, and automated leak
tests. Route selection must never silently fall back to native.

### 12.3 Tox/I2P

Reserved only. A plausible experiment needs reproducible local stream tunnels and Tox
bootstrap/relay endpoints reachable through I2P. It must measure initial connection, restart,
latency, resource cost, and no-clearnet behavior.

### 12.4 Route identity

One Tox key reused across native, Tor, and I2P is easy to operate but linkable. Separate route
keys improve separation but require a stable IoTox identity that delegates each endpoint.
This decision belongs in the future identity/route-binding protocol.

### 12.5 Owner-operated infrastructure

Tox is not a durable offline mailbox. A sleeping phone and disconnected device cannot exchange
a command. An optional owner-operated hub may provide encrypted durable queues, automation,
state history, bootstrap/relay capacity, or discovery assistance.

The hub must be replaceable and subordinate to the owner's ledger. IoTox should work without a
mandatory vendor account or vendor-controlled hub.

### 12.6 Stewardship

If IoTox benefits from the Tox network, it should contribute:

```text
bootstrap and TCP relay capacity
deployment and monitoring tools
documentation for owner/community operation
upstream bug reports and fixes
current compatibility testing
```

Do not centralize this into a hidden IoTox sovereign.

---

## 13. Security invariants

Keep these in code review, tests, docs, and runtime output:

1. A Tox friend is not an owner.
2. A Tox key is not the stable IoTox device identity.
3. An online peer is not a compatible IoTox peer.
4. Compatible HELLOs are not a confirmed transcript.
5. A confirmed transcript is not authorization.
6. A locally active ledger principal is not a remotely proven principal.
7. Authorization is not command freshness, safety, or successful execution.
8. Tox receipts are not execution receipts.
9. File transfer is not firmware authorization.
10. The runtime tree is not authoritative state.
11. A local path or peer byte string may not control filesystem traversal.
12. Queues, parsers, ledger records, and histories are bounded.
13. One thread owns each `Tox*`.
14. Reserved routes fail closed; no silent native fallback.
15. The permanent phrase remains high entropy because offline guessing is possible.
16. The phrase, RecallRoot, owner seed, and owner secret are not sent to the daemon.
17. The final active owner cannot be revoked under ledger format v1.
18. A ledger record is not durable until signature verification, replay, atomic write, and
    directory synchronization succeed.
19. IoTox has no vendor reassignment key.
20. Source-linked, real-peer, target, and production claims require their own evidence.
21. Unknown required protocol features fail closed; unknown optional features grant nothing.
22. Same-epoch handshake retries may not mutate logical content.
23. A generic raw packet seam may not bypass the IoTox session gate.
24. Untrusted transferred bytes remain data until independently authorized and verified.
25. `proof-sent` means local toxcore queue acceptance, not remote verification or durable
    authorization receipt.
26. A process-local `device.describe` result proves neither durable command semantics nor safe
    physical actuation.
27. A returned device description is accepted only when its principal and protocol bind to the
    already challenged and confirmed peer session.
28. An external library supplied with `--library`, `--sodium-library`, or
    `--argon2-library` is native code execution, not a sandboxed plugin.

The current threat model is `docs/threat-model-draft.md`. Update it whenever a new asset,
principal, persistence store, route, or physical effect is introduced.

---

## 14. Verification facility and claim discipline

### 14.1 Current checks

The default unit/integration executable registers 81 checks. Coverage includes:

```text
exact C ABI providers and error mapping
network/route separation and fail-closed reserved routes
atomic savedata, identity, and ledger persistence
RecallRoot structure, embedded list, Argon2 boundary, stable owner KAT
Ed25519/BLAKE2b provider boundaries and stable device persistence
signed ledger bootstrap/grant/revoke/replay/tamper/owner-continuity rules
outer frame, HELLO, negotiation, transcript confirmation, and epoch freeze
exact SENDQ retry and attempt/error diagnostics
bidirectional authority challenge/proof and negative cases
first command/result/description codecs and capability mapping
local control codec/socket and one-binary CLI process lifecycle
runtime transactions, peer/private journals, authority, and description projections
Tox profile/friend/request/text/receipt/typing paths
finite file send/receive and bounded queues/backpressure
savedata, stable identity, and authority continuity across restart
```

### 14.2 Fuzz targets

```text
iotox_frame_fuzzer          outer IoTox frame
iotox_session_fuzzer        HELLO and confirmation
iotox_local_control_fuzzer  local request/response
iotox_authority_fuzzer      ledger/challenge/proof records
iotox_command_fuzzer        command/result/device-description records
```

### 14.3 Defects found while constructing rev0009

In addition to earlier retained defects, rev0009's facility exposed:

```text
a stale explicit-claimant policy that prevented automatic stable-device proof
duplicate CLI dispatch left by an interrupted edit stream
a synthetic unsigned peer fixture that could not prove real authority semantics
a runtime projection race after an immutable operation result
a process assertion that confused proof-sent with the peer having processed the proof
a lock-order seam while reporting an unmatched command result
the process-fixture watchdog was too short for RecallRoot Argon2 work
the process fixture still expected obsolete manual stable-device proof
ledger loading held its mutex across blocking file I/O
```

The response was not to weaken assertions. The mock became a distinct Ed25519 peer; the product
implemented both directions; the CLI returns/publishes one immutable snapshot; asynchronous
peer evidence is polled explicitly; the nested lock was removed; fixture watchdogs now allow
password-hardening work without masking a hang; automatic device proof is the sole fixture
expectation; and ledger bytes are read/replayed privately before one locked state commit.

- Clang rejected the embedded 7,776-word RecallRoot list as one 108,800-byte string literal
  under strict `-Woverlength-strings`. The representation now uses three sub-48 KiB literals
  joined once into the exact same embedded text; the warning was not suppressed.

### 14.4 Evidence vocabulary

```text
designed
source-reviewed
compiled
unit-tested
mock-ABI-tested
process-tested
sanitizer-tested
fuzz-smoke-tested
source-linked
real-peer-tested
target-tested
production
```

Use the narrowest true label. A passing exact mock does not become a real Tox network claim.

## 15. Repository map

```text
BOOTSTRAPROSE.md                 this lone governing entrance
.gitignore                       hidden generated-tree policy
.datacube/
  README.md                      concise project entry inside the cube
  BUILDING.md                    build and provider instructions
  MANIFEST.md                    revision inventory and claims
  PACKAGE.md                     archive/install contract
  CHANGELOG.md                   ordered revision history
  REVISION                       machine-readable cube revision
  dependencies.lock              pinned upstream archives and hashes
  CMakeLists.txt                 product/test graph
  CMakePresets.json              compiler/sanitizer presets
  include/iotox/                 C++ interfaces
  src/                           one-binary implementation
  tests/                         checks, mocks, process tests, fuzzers
  tests/corpus/                  immutable reviewed fuzz seeds
  tools/                         build, test, standalone, peer, package tools
  docs/
    architecture.md
    protocol-draft.md
    protocol-session.md
    protocol-authority-v1.md
    protocol-command-v1.md
    recovery-and-ownership.md
    networks.md
    threat-model-draft.md
    roadmap.md
    testing.md
    open-questions.md
    what-iotox-is-becoming.md
    decisions/                   accepted/rejected architectural decisions
    research/                    dated upstream reading and evidence reports
    governance/                  office, claim, and change discipline
    history/                     previous entrances and imported cubes
  incubator/mutorr/              opt-in preserved small-circle research
  third_party/                   attributed retained inputs/licenses
  artifacts/                     revision evidence, never generated build trees
```

Before adding a new top-level file, ask whether it belongs in this entrance or under the hidden
cube. The lone-entrance shape is deliberate.

---

## 16. Immediate ordered work

The first stable-principal binding and harmless capability-gated operation are now implemented.
The next work must deepen the ratox successor rather than widening into unrelated transports.

### 16.1 Execute the source-linked product build

On the first networked CLI, run the pinned dependency path and correct real header, target,
linkage, or timing mismatches without contaminating the application core.

Definition of done:

```text
one installed iotox
pinned c-toxcore 0.2.23 and libsodium 1.0.22 verified by hash
linked provider compiled against official headers
no runtime toxcore/libsodium dependency in the standalone product
exact retained build/dependency log
```

### 16.2 Cross two genuine native peers

Use `tools/run-real-peer-smoke.sh`, then extend it to assert:

```text
friend request/accept
two confirmed transcripts
two authority directions with distinct stable principals
device.describe both ways
SENDQ/reconnect observations where reproducible
savedata and application-identity continuity
finite file transfer
TCP-relay-only mode
```

Real behavior may correct mock-only timing assumptions. Record the correction rather than
protecting the mock.

### 16.3 Build the durable command core

This is the immediate internal-code northstar.

Create a bounded durable inbox/outbox/result store with an explicit command state machine:

```text
reserved -> locally-queued -> received -> admitted -> started -> succeeded|failed|expired
```

Freeze and test:

```text
stable command IDs and sender epochs
application receipts distinct from Tox enqueue
expiry with untrusted boot clocks
idempotency and exact duplicate results
cancellation before and after admission
retry and backoff
queue priority/replacement
crash recovery and compaction
disk-full behavior
shutdown semantics
authority or ownership-epoch changes while queued
```

Only after this may a setting mutation or actuator operation be added.

### 16.4 Make authority re-entry operational

The owner principal is reconstructible and can explicitly answer a peer challenge locally. Next
solve how a recalled owner discovers and reaches current device route bindings without a vendor
directory, then how narrower controller credentials are delegated. Preserve the permanent
phrase and never introduce a vendor reassignment key.

### 16.5 Complete the ratox façade

Use the structured operations already present to add shell-native write/watch surfaces. A FIFO
or file command must expose request ID, admission, completion, error, and durability truth. Keep
the outside ordinary; never make pipe closure mean remote success.

### 16.6 Harden identity and ledger storage

Define optional platform-keystore/secure-element support, ledger rollback detection, backups,
ownership transfer, phrase-compromise epochs, and multi-owner policy. Keep the current portable
file mode as an explicit compatibility mode, not an unqualified secure-storage claim.

### 16.7 Extend Tox stewardship and routes

After native behavior is measured, package owner-operated bootstrap/relay guidance and upstream
useful fixes. Then research Tox/Tor and Tox/I2P as separate, fail-closed routes. Direct Tor/I2P
transports remain outside the immediate product path.

### 16.8 Target hardware

Choose an honest first Linux-class target and measure memory, threads, descriptors,
bootstrap/reconnect latency, idle traffic, wakeups, flash writes, suspend/resume, and power.

### 16.9 Mutorr remains optional

Preserve its build/tests and architecture boundary. Do not let replication displace the ratox
successor, native Tox proof, durable commands, or local simplicity.

## 17. Questions that must stay visible

The full list is `docs/open-questions.md`. The questions most likely to alter architecture are:

```text
What explicit receipt proves that a remote peer verified our principal proof, rather than only
that toxcore accepted the proof bytes locally?
Which bounded durable store and state machine survive duplicates, process death, disk-full,
interrupted compaction, cancellation, and ownership-epoch changes without executing twice?
How are expiry and replay windows defined when an IoT device boots without trustworthy wall
clock time?
How does a recalled owner discover current device route bindings without a vendor directory?
How are narrow controller credentials delegated, rotated, and revoked without exposing the
RecallRoot or stable owner secret to the daemon?
How is an internally valid old ledger detected after malicious filesystem rollback?
How do ownership transfer and phrase-compromise epochs work without a vendor sovereign?
Should per-device delegated owner keys reduce global owner-principal linkability?
Which additional key classes are required for hardware attestation, route binding, and encrypted
data?
Can pinned native toxcore build, link, bootstrap, reconnect, relay, and transfer exactly as the
adapter and exact mock currently predict?
Can Tox/Tor and Tox/I2P be made leak-free and operationally tolerable?
Which physical operations remain too consequential until durable commands, stronger review,
and target evidence exist?
```

Do not resolve one of these only in casual prose. Record the decision, rationale, rejected
alternatives, consequences, implementation, and tests.

---

## 18. Governance and revision discipline

### 18.1 Office-holder freedom

The office holder may reorganize, compress, expand, and rewrite this entrance. Do not preserve
stale prose merely because it was eloquent. Preserve the truth and the reasons that still
govern.

A good revision of this file should make it easier for a competent stranger to answer:

```text
What are we building?
Why does it matter?
What currently runs?
What was actually proven?
What is dangerous to assume?
Which decisions are settled?
What should I code next?
How do I leave the repository better than I found it?
```

### 18.2 Decision changes

For an architectural change:

1. read the existing ADR;
2. write a new ADR that supersedes or amends it;
3. update code and tests;
4. update this entrance and current docs;
5. retain old records rather than rewriting history;
6. state migration and compatibility consequences.

### 18.3 Claim maturity

A passing unit test does not make a network route real. A source review does not make a build
pass. A real peer test does not make a product safe for a lock. A production claim requires
sustained operational and security evidence.

Use explicit maturity labels in reports. Include failures and unavailable lanes.

### 18.4 Revision contents

A useful datacube revision contains:

```text
buildable source
current tests and tools
updated lone entrance
new/changed ADRs
current architecture/protocol/threat/roadmap docs
fresh research for external facts used
fresh build/test report
retained logs or hashes where appropriate
old entrances/history
clean archive with no host state or secrets
```

### 18.5 Filename and response contract

Always increment the four-digit revision. Package with America/New_York timestamp and a
meaningful lowercase hyphenated summary/codename:

```text
IoTox-rev####-YYYY.MM.DD.HH.MM-summary-highlight-codename.zip
```

When handing the cube to the user, provide exactly one link. The complete filename is the link
text. Do not add a second source, report, or explanatory link in that response.

### 18.6 Secrets and generated state

Never package:

```text
real Tox savedata
owner phrases or derived keys
private ledger keys
download caches/build trees/install trees
host-specific runtime directories
unreviewed mutable fuzzer corpora
```

The cube may include deterministic mocks, public test fixtures, and attributed word lists.

---

## 19. rev0009 handoff

rev0009 now changes IoTox from a confirmed Tox-native session with a local constitution into a
small but complete application path:

```text
stable device identity
RecallRoot-derived stable owner
signed owner-controlled ledger
confirmed Tox session
bidirectional transcript-bound principal proof
capability check
canonical read-only command and correlated result
principal-bound peer description
ratox-style observation through one product binary
```

The code knows the difference among queue acceptance, transcript confirmation, principal proof,
capability admission, and operation completion. Preserve those distinctions.

The most important new product behavior is not merely that a packet codec exists. The exact
process fixture creates two distinct signed IoTox devices. One command is denied before proof;
the same operation succeeds after the caller proves a ledger-authorized principal. The local
binary can then ask the peer for its description, survive one toxcore `SENDQ` with byte-identical
retry, correlate the result, bind the returned principal to the authority exchange, and publish
it through the ratox-style tree.

The product-shaped standalone build was attempted on 2026-08-14 and stopped before compilation
because shell DNS could not resolve `download.libsodium.org`. A focused Clang analyzer finding
also moved ledger file I/O outside its mutex; the follow-up focused pass completed without a
diagnostic. Neither fact changes the genuine-network boundary: official source-linked toxcore
and two real peers still have not run in this cloudtainer.

This remains deliberately harmless and non-durable. Do not connect an actuator to it. The next
internal construction is the durable command/result state machine and store; the next external
gate is genuine source-linked c-toxcore peers.

The project may remain a side project. A clean modern ratox successor, a strong C++ toxcore
boundary, owner-reconstructible authority, useful bootstrap/relay stewardship, and rigorous
protocol fixtures are each worthwhile outcomes.

```text
Tox stays.
The permanent RecallRoot stays.
The printed/remembered permanent phrase stays.
No vendor sovereign appears.
Friendship never becomes authority by accident.
The local surface stays simple.
The internal semantics tell the truth.
One binary remains the product.
The next code is durable command machinery.
```

