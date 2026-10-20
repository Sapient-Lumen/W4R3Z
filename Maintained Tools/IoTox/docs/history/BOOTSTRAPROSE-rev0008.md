# BOOTSTRAPROSE — IoTox rev0008, “Transcript Confirmed”

```text
Project:          IoTox
Revision:         rev0008
Version:          0.8.0
Codename:         Transcript Confirmed
Immediate north: one-binary modern ratox successor
Current transport: Tox over native networking
Current session: canonical HELLO plus mutual transcript confirmation
Current authority: none; independent authorization ledger is next
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
rev0008
IoTox 0.8.0 rev0008
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

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel
ctest --preset gcc-debug --output-on-failure
```

The default suite has seven CTest entries. Its unit/integration executable registers 64 C++
checks and receives exact mock/dependency paths from CTest. Running `iotox_tests` directly
without those environment variables is expected to fail integration checks; use CTest unless
you deliberately supply the fixtures.

Inspect the product:

```sh
./build/gcc-debug/iotox --version
./build/gcc-debug/iotox --help
./build/gcc-debug/iotox bootstrap-seeds
```

### 0.4 Run the one-binary product fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

This is not merely an in-process mock test. It starts the actual `iotox run` process and uses
the same binary as the local operator. The path crosses:

```text
CLI
Unix SOCK_SEQPACKET
agent dispatcher
bounded command queue
one toxcore owner thread
exact C ABI shared-library mock
callbacks and bounded event queue
session registry
journals and runtime tree
atomic savedata
shutdown and restart
```

rev0008 requires the mock peer to be distinct. It generates its own protocol nonce and
transport-key perspective, validates the local confirmation, and returns the opposite
canonical sender role. The fixture must observe:

```text
state=confirmed
hello-sent=1
hello-received=1
confirmation-sent=1
confirmation-received=1
application-ready=1
authorization=none-transport-session-only
```

An echo of the local HELLO is no longer sufficient evidence. The fixture independently rejects
the first HELLO and first CAPABILITIES local enqueue with toxcore lossless `SENDQ`, requires
attempt count two for each unchanged frozen record, requires the transient error fields to clear
after acceptance, carries an application COMMAND frame through the confirmed gate, and verifies
that a raw forged HELLO cannot bypass the dedicated session operations.

### 0.5 Run the retained quality matrix

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh
```

The retained matrix covers:

```text
GCC debug
GCC release
Clang debug
Clang AddressSanitizer + UndefinedBehaviorSanitizer
GCC ThreadSanitizer
three Clang libFuzzer smoke targets
Mutorr preservation build and tests
```

Warnings are errors. Do not suppress a warning or sanitizer finding merely to make a lane
green. Correct the program, narrow the claim, or document a genuine platform limitation.

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

Each revision should recheck current upstream facts that materially affect the work. Prefer
primary sources:

```text
c-toxcore release page and official source/header
ratox source and original behavior
protocol specifications rather than commentary
upstream build declarations rather than guessed target names
```

Retain the reading and the inference separately under `docs/research/`. The current session
research is split between `docs/research/tox-session-confirmation-rev0008.md` and
`docs/research/c-toxcore-0.2.23-custom-packet-send-contract-rev0008.md`.

If an upstream fact is current or likely to have changed, browse it again. A historical note is
not a substitute for a current release check.

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
IoTox-rev0008-YYYY.MM.DD.HH.MM-transcript-confirmed-sendq-retry-before-command.zip
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

rev0008 implements through transcript confirmation and structural application admission. It
does not implement stable principal proof or authority.

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

The inbox is live/transient in rev0008. It is not crash-durable, an audit log, or authority.

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

## 3. Current implementation truth — rev0008

### 3.1 Product code

The CMake product graph builds:

```text
iotox_core  internal static C++ library
iotox       one public executable
```

The core currently contains:

```text
agent lifecycle and local dispatcher
CLI/client and foreground run face
Tox profile, presence, peer, request, text, receipt, packet, and file behavior
finite-file manager
network/route model and bootstrap/relay parsing
private runtime tree and versioned local control socket
strict IoTox outer frame
canonical capability session
OS CSPRNG helper
RecallRoot/Argon2 research implementation
private atomic state store
runtime and source-linked toxcore providers
```

### 3.2 What rev0008 added

rev0007 stopped after deterministic HELLO compatibility. rev0008 adds a real transcript commit:

```text
HELLO          64-byte IHL1 payload, sequence 1
CAPABILITIES   256-byte ICF1 payload, sequence 2
```

The confirmation canonically binds:

```text
lower and higher raw Tox public keys
lower and higher exact HELLO bytes
lower and higher per-epoch nonces
selected protocol version
shared feature mask
negotiated maximum frame payload
negotiated maximum finite-file bytes
sender role in the key ordering
```

Canonical frame construction reserves the first local HELLO and confirmation message IDs
before the transport call. The records are therefore frozen before the first send attempt, and
their IDs and bytes do not change when toxcore rejects a local enqueue. The first valid peer
HELLO and confirmation bodies are frozen. Exact retries are idempotent. Changed bodies are
same-epoch conflicts. Per-record send-attempt counters and temporary error classes make local
queue pressure visible; successful enqueue clears the error without erasing the attempt count.

A non-session IoTox frame is admitted only when the session is confirmed and the frame uses the
exact negotiated version, a nonzero message ID, and a payload within the negotiated ceiling.
The same gate protects incoming frames and operator-injected raw IoTox packets.

The transport adapter now preserves c-toxcore custom-packet error meaning. A missing friend is
`not_found`; an offline friend is `unavailable`; a full lossless queue is
`resource_exhausted`; malformed packet contracts are `invalid_argument`. The event pump
services incomplete protocol sessions after later toxcore iterations and retries only records
that never entered toxcore's queue. It never creates a new ID or payload merely because of
`SENDQ`, and it does not blindly resend packets toxcore already accepted.

### 3.3 State vocabulary

The session registry can render:

```text
offline
awaiting-hello
awaiting-confirmation
confirmed
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

Aggregate status distinguishes:

```text
protocol-session-count
compatible-protocol-session-count
established-protocol-session-count
negotiating-protocol-session-count
incompatible-protocol-session-count
protocol-error-session-count
```

“Compatible” now means the HELLO negotiation succeeded. “Established/confirmed” means both
canonical confirmations were accepted. Neither means authorized.

### 3.4 What the exact mock proves

The exact loadable mock implements only the consumed toxcore C ABI. It exercises symbol
loading/version checks, lifecycle, callbacks, friendship, packets, files, profiles, savedata,
and iteration without pretending to be the network.

For rev0008 it behaves as a separate IoTox endpoint. It can therefore prove that the C++
implementation:

```text
sets its own Tox public key before session ordering
receives a different peer HELLO
computes the same canonical endpoint order from the opposite perspective
sends the correct local confirmation
accepts the peer's opposite-role confirmation
commits confirmed state through the local socket and runtime tree
keeps authorization absent
```

### 3.5 What is not proven

This cloudtainer has not proven:

```text
official c-toxcore source compiling in the linked product path
two genuine Tox peers
public bootstrap or DHT behavior
NAT traversal
TCP-relay-only behavior
long reconnect/offline behavior
Tox over Tor or I2P
target hardware resource/power behavior
stable signed IoTox identity
authorization ledger
RecallRoot re-entry protocol
durable commands or physical safety
production security
```

No amount of mock detail may erase those labels.

### 3.6 Current upstream posture

The revision research rechecked c-toxcore and retained 0.2.23 as the current pinned target. The
project continues to describe itself as experimental and without an independent formal
cryptographic audit. Keep source pinning, a narrow adapter, application authorization above
Tox, fuzzing, hardening, and a practical update path.

Licensing remains an architecture/business constraint: pinned c-toxcore is GPL-3.0-or-later.
Do not make distribution assumptions without review of the actual product linkage and source
offer obligations.

---

## 4. One-binary operator surface

Run:

```sh
./build/gcc-debug/iotox --help
```

The principal commands are summarized here. The binary help is authoritative for exact syntax.

### 4.1 Agent

```sh
iotox run \
  --state /private/path/device.toxsave \
  --runtime /run/user/UID/iotox \
  --network tox/native
```

Agent controls include explicit library selection for research mode, bootstrap/relay overrides,
queue bounds, file bounds, persistence path, and fixture lifetime.

### 4.2 Identity and profile

```sh
iotox --runtime PATH ping
iotox --runtime PATH status
iotox --runtime PATH address
iotox --runtime PATH profile
iotox --runtime PATH profile-name TEXT
iotox --runtime PATH profile-name-stdin
iotox --runtime PATH profile-status-message TEXT
iotox --runtime PATH profile-status available|away|busy
```

Hex and standard-input forms preserve arbitrary bounded bytes where supported.

### 4.3 Friendship and request decisions

```sh
iotox --runtime PATH transport-peer-request TOX_ADDRESS MESSAGE
iotox --runtime PATH requests
iotox --runtime PATH request-accept PUBLIC_KEY
iotox --runtime PATH request-reject PUBLIC_KEY
iotox --runtime PATH transport-peer-accept PUBLIC_KEY
iotox --runtime PATH transport-peer-remove FRIEND
```

`transport-peer-accept` deliberately accepts a raw key without a live request. It is an
operator power and still creates only a Tox relationship.

### 4.4 Human Tox lane

```sh
iotox --runtime PATH message FRIEND TEXT
iotox --runtime PATH action FRIEND TEXT
iotox --runtime PATH message-stdin FRIEND
iotox --runtime PATH action-stdin FRIEND
iotox --runtime PATH typing FRIEND on|off
```

Tox message receipts are transport receipts, never device-command completion.

### 4.5 IoTox session

```sh
iotox --runtime PATH sessions
iotox --runtime PATH session FRIEND
iotox --runtime PATH hello FRIEND
iotox --runtime PATH confirm FRIEND
iotox --runtime PATH peer-session PUBLIC_KEY
iotox --runtime PATH peer-protocol PUBLIC_KEY
```

HELLO and confirmation normally happen automatically on a real online epoch. The explicit
commands retry the already frozen records; they do not renegotiate them.

### 4.6 Raw lossless seam

```sh
iotox --runtime PATH transport-send FRIEND PACKET_HEX
```

This is useful for research and future protocol construction. If the packet begins with the
IoTox discriminator, non-session application frames must pass the confirmed-session gate. A
raw seam is not a bypass around protocol state.

### 4.7 Finite files

```sh
iotox --runtime PATH file-send FRIEND /absolute/source
iotox --runtime PATH files
iotox --runtime PATH file-receive FRIEND FILE_NUMBER /absolute/destination
iotox --runtime PATH file-cancel FRIEND FILE_NUMBER
```

Incoming offers remain paused until a private destination is acquired. Existing destination
files are not clobbered.

### 4.8 Journals and shutdown

```sh
iotox --runtime PATH events
iotox --runtime PATH watch --watch-ms N
iotox --runtime PATH peer-messages PUBLIC_KEY
iotox --runtime PATH peer-watch PUBLIC_KEY
iotox --runtime PATH peer-protocol PUBLIC_KEY
iotox --runtime PATH peer-protocol-watch PUBLIC_KEY
iotox --runtime PATH stop
```

Global events intentionally omit packet/text bodies. Per-peer message and protocol journals
are private, byte-preserving/escaped, and bounded with one previous segment.

---

## 5. Runtime tree

The runtime root is private and disposable. A representative tree is:

```text
<runtime>/
├── control.sock
├── status
├── address
├── events
├── events.previous
├── self/
│   ├── address
│   ├── connection
│   ├── name
│   ├── name-bytes
│   ├── network
│   ├── revision
│   ├── status
│   ├── status-message
│   └── status-message-bytes
├── requests/
│   └── <PUBLIC_KEY>/
│       ├── public-key
│       ├── message
│       ├── message-bytes
│       └── received-unix-ms
├── peers/
│   └── <PUBLIC_KEY>/
│       ├── number
│       ├── public-key
│       ├── connection
│       ├── online
│       ├── name
│       ├── status
│       ├── status-message
│       ├── typing
│       ├── messages[.previous]
│       ├── protocol[.previous]
│       ├── session
│       └── iotox/
│           ├── state
│           ├── online-epoch
│           ├── hello-compatible
│           ├── transcript-confirmed
│           ├── established
│           ├── application-ready
│           ├── hello-sent
│           ├── hello-received
│           ├── confirmation-sent
│           ├── confirmation-received
│           ├── local-role
│           ├── protocol
│           ├── shared-features
│           ├── maximum-frame-payload
│           ├── maximum-finite-file-bytes
│           ├── authorization
│           └── summary
└── transfers/
    └── <DIRECTION>/<FRIEND>/<FILE>/...
```

Exact files may evolve; source and tests are authoritative. The semantic rules are stable:

```text
owner-only paths
strict public-key directory names
untrusted bytes escaped or written as bytes, never interpreted as paths
detail written before aggregate commit marker
atomic replacement
stale peer/request/transfer directories withdrawn
read projection not authority
```

`peers/<PUBLIC_KEY>/session` is the complete per-peer session record and is replaced last. It
must always retain the explicit authorization line.

---

## 6. Local control contract

The local mutation path is Unix `SOCK_SEQPACKET`, not ad hoc file polling. The current binary
protocol is major 1, minor 7, with a 24-byte header and 60 KiB payload maximum.

Each packet carries:

```text
magic/version
request or response kind
operation
request ID
status code
payload length
bounded payload
```

The socket preserves packet boundaries. The request ID connects one response to one request.
The daemon rejects unknown major versions and newer unsupported minor versions.

Current operation groups are:

```text
ping/inspect/address/shutdown
self profile get/set
transport peer request/add/remove/list
message/action/typing/lossless
incoming request list/accept/reject
protocol HELLO/session list/show/confirmation
finite file send/receive/cancel/list
```

The protocol version is independent of IoTox's over-Tox protocol version. Do not increment it
merely because the product revision changed; increment it when local wire compatibility
changes.

Future local authorization is not automatically solved by Unix filesystem permissions. A
local process with access to the control socket currently has operator power. Product
deployment must define the runtime owner/group, privilege separation, and which local calls
require application credentials.

---

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

## 9. Independent authorization — immediate implementation northstar

The next substantive code should implement the smallest honest authority layer, not pretend the
Tox key or confirmed session is enough.

### 9.1 Required separation

Proposed layers:

```text
hardware identity or attestation, optional and product-specific
stable IoTox device/application identity
owner/controller principals
independent authorization ledger
replaceable transport route bindings
current confirmed Tox session
```

A route key may rotate without changing the device. Ownership may change without pretending the
new owner is the old owner. A native/Tor/I2P endpoint may eventually be delegated from one
stable device identity.

### 9.2 Minimum ledger concepts

The first ledger should be small and canonical:

```text
ledger/device identity
ownership epoch
principal identity
role
capability set
issuer
subject
issuance sequence or record ID
validity/freshness conditions
revocation or supersession rule
signature
```

Roles may include owner, administrator, operator, viewer, automation controller, and temporary
service principal. Capabilities should be explicit verbs such as:

```text
read.telemetry
write.settings
actuate.relay
manage.principals
install.firmware
export.diagnostics
factory.reset
```

Do not begin with an unrestricted policy language. Freeze a bounded representation and obvious
rules that can be tested.

### 9.3 Session-bound proof

A newly online peer should prove a stable principal under the current ownership epoch and bind
the proof to the current confirmed transcript. Candidate structure:

```text
challenge nonce from verifier
stable device/principal identifier
ownership epoch
canonical session-transcript digest
requested or asserted role context
expiry/freshness value
canonical signature
```

The signing primitive and canonical digest are not yet selected. Choose a mature audited
library/primitive with straightforward C++ integration; do not invent cryptography.

### 9.4 Required behavior

```text
friend but no confirmed transcript -> application closed
confirmed transcript but no principal proof -> authorization absent
valid principal but revoked/stale epoch -> denied
valid current principal without capability -> denied
valid current capability -> operation enters its own safety/durability checks
```

Project authorization state separately from session state. Do not overload `confirmed`.

### 9.5 Persistence and rollback

The ledger must persist atomically and independently from Tox savedata. It needs a strategy for
rollback, interrupted writes, corrupt records, and ownership epoch transition. Hardware without
a monotonic counter makes rollback detection difficult; keep that question visible rather than
claiming an answer.

Do not advertise feature bit 16 until the complete proof, decision, persistence, projection,
and negative tests exist.

---

## 10. RecallRoot and owner re-entry

RecallRoot-v1 is retained research code and contract. Its purpose is to make this true:

> From a permanent generated phrase, the owner can reconstruct the root material needed to
> approach their devices without an IoTox account or recovery key.

The contract uses a fixed Argon2id derivation. Fixed means independent implementations can
reproduce the same root. It also means an attacker can test guesses offline when they have a
suitable verifier. The product must therefore enforce generated high-entropy phrase structure
and communicate that a permanent phrase is equivalent to durable owner power.

The future hierarchy may resemble:

```text
RecallRoot-v1 material
  -> owner signing key seed
  -> controller delegation domain
  -> device discovery/re-entry domain
  -> local encrypted-data domain
```

Domain separation labels and exact key derivation must be frozen before use. Do not use raw
Argon2 output for every purpose.

Still unresolved:

```text
signature primitive
stable owner identifier
how a reconstructed owner discovers route bindings
challenge/response flow
multiple owners
phrase compromise and ownership epoch transition
local data encryption and whether old ciphertext remains recoverable
```

No IoTox vendor service may become a required oracle for re-entry.

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
2. An online peer is not a compatible IoTox peer.
3. Compatible HELLOs are not a confirmed transcript.
4. A confirmed transcript is not authorization.
5. Authorization is not command freshness, safety, or successful execution.
6. Tox receipts are not execution receipts.
7. File transfer is not firmware authorization.
8. The runtime tree is not authoritative state.
9. A local path or peer byte string may not control filesystem traversal.
10. Queues and parsers are bounded.
11. One thread owns each `Tox*`.
12. Reserved routes fail closed; no silent native fallback.
13. The permanent phrase remains high entropy because offline guessing is possible.
14. IoTox has no vendor reassignment key.
15. Source-linked, real-peer, target, and production claims require their own evidence.
16. Unknown required protocol features fail closed; unknown optional features grant nothing.
17. Same-epoch handshake retries may not mutate logical content.
18. A generic raw packet seam may not bypass the IoTox session gate.
19. Untrusted transferred bytes remain data until independently authorized and verified.
20. An external library supplied with `--library` is native code execution, not a sandboxed
    plugin.

The current threat model is `docs/threat-model-draft.md`. Update it whenever a new asset,
principal, persistence store, route, or physical effect is introduced.

---

## 14. Verification facility and claim discipline

### 14.1 Current checks

The unit/integration executable registers 64 checks. Current coverage includes:

```text
C ABI shape and provider behavior
network/route parsing and fail-closed reserved routes
bootstrap/relay inputs
state-store atomic replacement
RecallRoot structure and Argon2 boundary
outer frame encoding/decoding
HELLO and confirmation canonicality
session state, freeze, negotiation, independent HELLO/confirmation `SENDQ` recovery,
per-record attempt diagnostics, and application gate
local control codec/socket
runtime tree transactions and journals
agent/process behavior through exact toxcore mock
profile, friendship, requests, text, receipts
finite file sender/receiver behavior
bounded queues and event backpressure
savedata mutation and restart continuity
```

### 14.2 Fuzz targets

```text
iotox_frame_fuzzer          outer machine frame
iotox_session_fuzzer        HELLO + confirmation payload/frame
iotox_local_control_fuzzer  local request/response packet
```

Reviewed source seeds are copied into build-local corpora for each smoke. Do not retain mutated
work corpora as source truth.

### 14.3 Defects the facility has already found

Retained examples:

```text
incorrect C++ function-pointer ABI in the early toxcore mock
weaker savedata temporary-file replacement discipline
agent-start visibility race
possible masking of confirmation wire mutation by premature recomputation
manual HELLO retry changing its message ID before canonical per-epoch freezing
first-enqueue failure leaving the handshake message ID unreserved until later success
byte-identical replay incorrectly reporting success for a confirmation rejected on first comparison
loss of c-toxcore `SENDQ` meaning behind one generic library error
stale assumption that HELLO compatibility meant session readiness
```

Tests are earning their place when they change the implementation, not when they merely count
green lines.

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

Use the narrowest label. `mock-ABI-tested` is not a synonym for `real-peer-tested`.

### 14.5 External handoff

On the eventual CLI:

```sh
cd .datacube
./tools/build-standalone.sh
./tools/verify-standalone.sh
./tools/run-real-peer-smoke.sh
```

Retain compiler versions, dependency hashes, command output, topology, and failures. Correct
source/API drift rather than bypassing official headers or hash checks.

---

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

Do not treat this as an absolute prohibition on fixing a nearby defect. It is the default order
for substantive construction.

### 16.1 Execute the source-linked product build

On the first networked CLI, run the pinned dependency path. Fix genuine c-toxcore API/CMake
mismatches in the narrow adapter/build integration. Preserve official headers and hashes.

Definition of done:

```text
one installed iotox
linked to pinned toxcore/libsodium as intended
no runtime toxcore/libsodium dependency
version/help/start work
retained exact build log
```

### 16.2 Cross two genuine native peers

Use the prepared fixture, then add lossless application-frame and file-transfer assertions.
Test TCP-relay-only mode and offline/reconnect epochs. Do not redesign around a mock-only
assumption once real behavior is known.

### 16.3 Implement stable application identity and ledger skeleton

This is the immediate internal-code northstar even while external toxcore remains unavailable.

Recommended sequence:

1. Research and select a mature signature primitive/library compatible with the product build.
2. Define fixed-size stable principal identifiers.
3. Define a canonical bounded ledger record without a general policy language.
4. Implement atomic ledger storage and deterministic replay into current state.
5. Implement ownership epoch and revocation/supersession rules.
6. Add read-only runtime/CLI projection explicitly separate from Tox peers.
7. Add challenge/proof messages bound to the confirmed session transcript.
8. Keep all application dispatch denied until proof and capability checks succeed.
9. Add negative tests for stale epoch, bad signature, changed transcript, revoked principal,
   duplicate record, rollback, and corrupt/truncated storage.

Do not advertise `authorization-ledger-v1` early.

### 16.4 Implement durable command semantics

After authority exists, build a durable bounded inbox/outbox and result store. Freeze command
IDs, expiry/freshness, deduplication, idempotency, cancellation, retry, priority, and disk-full
rules before connecting physical actuators.

### 16.5 Implement RecallRoot re-entry

Derive owner/application key material from the retained fixed Argon2id contract, then prove it
through a fresh session-bound challenge. The permanent phrase remains. No vendor key is added.

### 16.6 Complete the ratox façade

Add writable files/FIFOs only after the underlying structured operation has an exact response,
authorization rule, and durability behavior. Favor the surface that “just werx” for shell users
without lying about completion.

### 16.7 Extend Tox stewardship and routes

Package owner-operated bootstrap/relay tools, contribute upstream, and measure native Tox.
Then perform separate fail-closed Tor and I2P route research. Do not build direct Tor/I2P
transports as part of the current northstar.

### 16.8 Target hardware

Choose an honest first class—likely embedded Linux, router, NAS, gateway, or Raspberry Pi-class
appliance. Measure before claiming suitability for constrained microcontrollers.

### 16.9 Mutorr remains optional

Return to small-circle replicated namespaces only when a real agent, authority, durability,
and native network path exist. Preserve its code and decisions meanwhile.

---

## 17. Questions that must stay visible

The full list is `docs/open-questions.md`. The questions most likely to alter architecture are:

```text
Which stable signature primitive and library?
Which key classes: hardware, device, owner, route, data?
What exact ledger record and delegation rules?
How is ledger rollback detected without secure monotonic storage?
What exact transcript digest does the authorization proof sign?
How often is authorization re-proven across online epochs?
What wall-clock/freshness model works after an untrusted boot clock?
What is the local-operation result after owner-thread work has begun but caller timeout occurs?
Which durable store survives disk-full and interrupted compaction cleanly?
How are current route bindings discovered from RecallRoot without a vendor directory?
What happens after permanent phrase compromise?
Can native toxcore build and connect exactly as prepared?
Can Tox/Tor and Tox/I2P be made leak-free and operationally tolerable?
Which physical operations are too consequential until stronger independent review?
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

## 19. rev0008 handoff

rev0008 changes IoTox from “peers advertise compatible machine capabilities” to “peers
mutually commit one canonical online-epoch transcript before application traffic.”

The implementation now knows the difference among:

```text
friend
online
HELLO-compatible
transcript-confirmed/application-ready
authorized
```

Only the first four exist, and the fourth explicitly says authority is absent.

The exact mock is no longer a passive echo for the session path. It behaves as a distinct peer,
which forced endpoint ordering, correlation, opposite roles, state projection, application
gating, and tests to become real code. It can also apply bounded lossless send-queue pressure,
which forced IoTox to distinguish “toxcore accepted this packet” from “the packet never entered
the queue” and to retry only the latter without rewriting the transcript.

The next office holder should not spend the next revision polishing the wording of
“confirmed.” Use this stable boundary as the entrance to stable application identity and the
independent authorization ledger.
Continue the source-linked/real-peer handoff in parallel, because genuine toxcore behavior may
correct assumptions in the adapter or session timing.

The project remains ambitious and may remain a side project. That is acceptable. The immediate
measure of success is whether each cube leaves a more coherent, runnable ratox successor and a
smaller set of honest unknowns.

```text
Tox stays.
The permanent RecallRoot stays.
No vendor sovereign appears.
The local surface stays simple.
The internal semantics become stricter.
One binary remains the product.
```
