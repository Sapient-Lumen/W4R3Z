# BOOTSTRAPROSE — IoTox rev0007, “Peers Speak First”

```text
project:          IoTox
revision:         rev0007
version:          0.7.0
codename:         Peers Speak First
current date:     2026-08-13 America/New_York
northstar:        one-binary C++20 ratox successor
primary network:  Tox/native
upstream target:  c-toxcore 0.2.23
lone entrance:    this file
working tree:     .datacube/
```

IoTox is a self-owned device agent built around Tox and shaped by ratox's Unix simplicity.
The intended installed product is one executable, `iotox`, which can run the agent and operate
that agent from the same command.

Two sentences govern the work:

> **From memory, you can reach your devices.**
>
> **From an ordinary shell, you can understand and operate them.**

This file is the wake-from-amnesia office. It is not a frozen constitution and not a marketing
page. The current office holder is expected to edit it thoroughly whenever code, evidence,
decisions, or priorities change. There is no maximum length. There is a minimum duty: a new
incumbent must be able to recover the project's meaning, build it, inspect it, distinguish
proof from hope, and continue in the correct direction from this file alone.

The complete repository is intentionally hidden under `.datacube/`. That is an interface
choice, not a secrecy boundary.

---

## 0. `/run` — assume the office

### 0.1 Establish the cube

From the extracted `IoTox/` directory:

```sh
pwd
ls -la
cat BOOTSTRAPROSE.md
cd .datacube
cat REVISION
```

Expected revision:

```text
rev0007
```

The root layout must remain:

```text
IoTox/
  BOOTSTRAPROSE.md       only ordinary visible root object
  .datacube/             complete repository
  .gitignore             hidden support file
```

Check it:

```sh
./tools/check-lone-entrance.sh
```

### 0.2 Read the records that can overrule recollection

Read in this order:

```sh
cat ../BOOTSTRAPROSE.md
cat README.md
cat docs/decisions/README.md
cat docs/architecture.md
cat docs/protocol-session.md
cat docs/roadmap.md
cat docs/testing.md
cat docs/open-questions.md
cat CHANGELOG.md
```

Then inspect the exact ADR or research note relevant to the next change. Historical files are
context, not current authority.

### 0.3 Build the owned implementation

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel
ctest --preset gcc-debug --output-on-failure
```

The normal local result for this cube is seven passing CTest entries. The unit/integration
executable contains 60 registered C++ checks.

Inspect the one public product:

```sh
./build/gcc-debug/iotox --version
./build/gcc-debug/iotox --help
./tools/run-mock-node.sh gcc-debug
```

Expected identity:

```text
IoTox 0.7.0 rev0007
```

### 0.4 Run the retained quality lanes

```sh
./tools/build-matrix.sh
```

The intended matrix covers:

```text
GCC 14 debug
GCC 14 release
Clang 17 debug
Clang 17 AddressSanitizer + UndefinedBehaviorSanitizer
GCC 14 ThreadSanitizer
three Clang libFuzzer smoke targets
optional Mutorr preservation build
```

A toolchain/environment failure is evidence, not permission to relabel an unrun lane as a
pass. Fix owned defects when possible. Record environmental limitations exactly.

### 0.5 Attempt the product-shaped dependency build

Where outbound HTTPS works:

```sh
./tools/fetch-pinned-dependencies.sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
```

Then:

```sh
./dist/standalone/iotox --version
```

The standalone direction is one `iotox` executable with pinned c-toxcore and libsodium in its
link graph. The dynamic provider remains a test and explicit integration seam.

This cloudtainer could not resolve the upstream download hosts during rev0007. Do not weaken
hashes, substitute unreviewed source, or call the source-linked lane passed. The exact failure
is retained under `artifacts/`.

### 0.6 Continue construction even when a validation lane is unavailable

Missing real toxcore is not a command to stop writing the product. It changes the evidence
label. When an external validation gate is unavailable:

1. source-review the pinned contract;
2. isolate the external boundary;
3. implement the plausible owned behavior;
4. test it through exact mocks and process fixtures;
5. retain a real-source/real-peer handoff script;
6. state what remains unproven;
7. continue with the next owned seam that does not depend on pretending the gate passed.

IoTox is implementation-forward and evidence-honest.

### 0.7 Leave a complete cube

Before packaging:

```sh
./tools/check-lone-entrance.sh
find . -name '*.toxsave' -o -name '__pycache__' -o -name '*.pyc'
grep -RInE 'Prebuilt rev0006|IoTox rev0006|version:[[:space:]]*0\.6\.0' \
  README.md BUILDING.md MANIFEST.md PACKAGE.md artifacts/README.md \
  docs/research/cloudtainer-build-report.md || true
```

Update current docs, preserve prior BOOTSTRAP under `docs/history/`, retain exact logs, remove
generated build/dependency trees from the archive, and create the next revision with
`tools/make-revision-archive.sh`.

---

## 1. What IoTox is

IoTox is a modern ratox successor for devices.

It is not primarily:

```text
a cloud account service
a new peer-to-peer network
a GUI
an MQTT broker with Tox bolted on
a vendor-controlled recovery system
a Mutorr product
```

It is:

```text
one self-owned local agent
one shell-operable executable
one Tox identity and peer surface today
one explicit machine-session lane
one future application identity and authorization system above Tox
one path toward permanent owner re-entry from memory or paper
```

Tox is kept because it already does difficult connection work beautifully: peer identities,
encrypted sessions, bootstrap discovery, NAT traversal, TCP relays, reliable custom packets,
and file transfer. IoTox should contribute useful fixes, deployment tools, bootstrap/relay
capacity, and governance back to that commons rather than treating it as disposable plumbing.

Ratox is kept as an aesthetic and operator ancestor:

```text
inspect ordinary paths
compose with pipes
watch streams
copy files
run one small service
understand failure without a web account
```

IoTox is a rewrite because the device product needs structured requests, bounded queues,
explicit persistence, protocol negotiation, independent authorization, durable command
semantics, safe file policy, and room for routed Tox. The outside should remain ordinary. The
inside must tell the truth.

---

## 2. Product axioms and decisions in force

### 2.1 Tox stays primary

The default network family is:

```text
Tox/native
Tox/Tor       reserved, fail closed
Tox/I2P       reserved, fail closed
```

These are one transport with different routes. Future direct Tor and direct I2P transports
are separate ideas and must not be confused with routing Tox through those overlays.

### 2.2 One installed product executable

The product command is `iotox`.

```text
iotox run ...       foreground agent
iotox status        local inspection
iotox peers         transport peers
iotox requests      live incoming requests
iotox sessions      IoTox transport sessions
iotox message ...   human Tox lane
iotox file-send ... finite bulk lane
```

Internal libraries, mocks, tests, fuzzers, and incubator programs may exist. They do not become
additional public products. The rev0007 install graph was exercised into a clean prefix and
contained exactly one executable: `bin/iotox`. Research programs are build/test instruments and
are deliberately absent from installation.

### 2.3 C++20 owns the product

IoTox-owned implementation is C++20. c-toxcore and its dependencies remain external C code
behind a narrow typed table. GCC and Clang are first-class. Warnings are errors.

### 2.4 One thread owns each `Tox*`

One owner thread creates, iterates, calls, snapshots, and destroys the `Tox*`. Other services
use bounded commands and normalized events. No local socket handler, runtime projector,
session registry, file policy, or future authorization component may call toxcore directly.

### 2.5 Source-linked standalone is the product direction

The intended product compiles pinned upstream source into the dependency graph and presents
one executable. The runtime-loaded provider exists for exact ABI mocks, operator-supplied
integration, and diagnosis. A linked build must compile against canonical c-toxcore headers;
fallback declarations may not silently validate the product path.

### 2.6 Permanent RecallRoot stays

IoTox deliberately keeps a permanent generated phrase that may be remembered or printed.
Under a fixed Argon2id derivation contract, the same phrase reconstructs the same root material.

This is the joy of the design:

> From memory, you can reach your devices.

It also permits offline password guessing. Phrase strength is therefore structural, not
optional. The phrase must be generated from the retained canonical word list and meet the
frozen contract. A casual human-chosen sentence is not an equivalent substitute.

RecallRoot is not yet wired into the product's identity/authorization system. Its current code
freezes and tests the derivation boundary only.

### 2.7 No IoTox/vendor reassignment sovereign

The project, company, service operator, bootstrap operator, relay operator, and software author
must not possess a key that can reassign customer devices.

Manufacturer attestation may someday say what hardware was made. It may not silently replace
the owner.

### 2.8 Authorization is independent of Tox friendship

A Tox friend is a recognized transport peer. A compatible IoTox HELLO is a recognized machine
protocol session. Neither grants:

```text
ownership
administrator role
actuator capability
firmware authority
delegation authority
factory-reset authority
access to encrypted application data
```

A separate signed ledger must define stable application identities, roles, capabilities,
ownership epochs, delegation, and revocation.

### 2.9 Public-key-first operator selection

Tox friend numbers are local indices and may change after savedata reload. IoTox projects and
selects current peers by their 32-byte public key, resolving to a friend number only at the
transport boundary. Friend numbers remain accepted where useful for local diagnosis.

The Tox public key is still not the future stable IoTox device identity.

### 2.10 Structured core; ratox façade

The primary mutation interface is a bounded, versioned Unix `SOCK_SEQPACKET` protocol.
Filesystem records and journals are a private read projection. Standard input already offers
exact-byte Unix composition. Writable FIFO/path compatibility should later translate into
structured requests rather than becoming the queue or source of truth.

### 2.11 Human and machine traffic are separate lanes

Normal/action Tox messages, typing, profile, and receipts are useful human/presentation
features. Machine semantics use reliable custom packets beginning with `0xA0`. Finite large
bytes use Tox file transfer.

A Tox message receipt is not a device execution receipt.

### 2.12 Incoming friend requests require an explicit decision

An incoming callback becomes a bounded live request record keyed by public key. The operator
may list, accept, or reject it. `request-accept` requires a matching live record.
`transport-peer-accept` is a separate deliberate low-level operation for adding a known key.

The request inbox is transient. It is not savedata, a pairing proof, an audit log, or authority.

### 2.13 Peers speak first

A real offline-to-online transition creates one session epoch and one canonical local HELLO.
The first valid peer HELLO is frozen for that epoch. Identical retries are idempotent. A changed
advertisement is a conflict. Required features fail closed.

A compatible session is explicitly rendered as:

```text
authorization=none-transport-session-only
```

### 2.14 Mutorr is preserved but not the northstar

Mutorr remains an optional disabled-by-default incubator for bounded namespace replication.
It does not define the current product, ownership, session, or shell surface. The immediate
northstar is the ratox successor.

---

## 3. Current implementation truth — rev0007

### 3.1 What the code now contains

The C++ product currently implements:

```text
one toxcore owner thread and lifecycle
runtime and linked provider table
private atomic Tox savedata
bootstrap and TCP relay configuration
Tox/native route selection
self profile and presence
friend request, accept, reject, list, remove
live incoming request inbox
normal/action text, typing, and receipts
bounded peer message journals
strict IoTox outer frame
canonical HELLO and per-peer session registry
bounded decoded protocol journals
finite native Tox file send/receive/cancel/list
private ratox-style runtime projection
same-user bounded local control socket
one executable as agent and client
RecallRoot-v1 isolated derivation contract
```

### 3.2 What rev0007 adds

When toxcore reports a friend online, the agent:

1. resolves and records the peer public key;
2. starts or updates the true online epoch;
3. generates a nonzero OS-CSPRNG 128-bit session nonce;
4. builds the exact canonical 64-byte local HELLO;
5. sends it in an IoTox reliable custom-packet frame;
6. records the outgoing frame;
7. strictly decodes an incoming peer HELLO;
8. freezes the first valid peer payload;
9. negotiates protocol, feature, frame, and finite-file limits;
10. atomically projects the complete session result.

Incoming Tox friend requests are copied immediately from callback memory, exposed by public
key, and consumed by explicit accept or reject.

Only `iotox` enters the install graph. A clean-prefix installation was inspected and contained
exactly one executable; optional research programs remain non-installed evidence facilities.

The `files` operation is now an authoritative observation barrier: before replying, the agent
refreshes toxcore-derived transfer state and commits the aggregate status and transactional
runtime transfer tree. An empty reply therefore cannot race a stale visible transfer.

### 3.3 What the exact mock process proves

The loadable mock exports the exact C symbols and callback signatures consumed by IoTox. The
process fixture launches the actual `iotox run` command and uses that same executable as the
client. It crosses:

```text
CLI
Unix SOCK_SEQPACKET
control decoder
agent service
bounded owner queue
C function table
loadable C ABI mock
callbacks
bounded event queue
session/request state
runtime projection and journals
savedata state store
```

It deterministically exercises automatic HELLO echo/negotiation, a live incoming request,
profile, text, typing, receipt, peer projection, protocol/session inspection, idempotent HELLO
retry, clean stop, and identity restart.

### 3.4 What is not proven

This cube does **not** prove:

```text
official c-toxcore source compiles with IoTox
real Tox cryptography or DHT behavior
NAT traversal
public bootstrap operation
real TCP relay behavior
two genuine peer connectivity
network timing, congestion, or hostile interleavings
Tor or I2P route privacy
stable IoTox application identity
authorization or revocation
durable device commands
RecallRoot re-entry to a live device
OTA safety
actuator safety
target hardware resources or power
production readiness
```

Strongest current label: **compiled, unit-tested, exact-mock-ABI-tested, process-tested**.

### 3.5 Source-linked attempt

Pinned fetch inputs:

```text
c-toxcore 0.2.23
sha256 b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe

libsodium 1.0.22
sha256 adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349
```

The fetch was attempted. Shell DNS could not resolve the upstream host. The failure is retained
as evidence; no source-linked claim is made.

---

## 4. The one-binary operator surface

Run the agent:

```sh
iotox run \
  --state /private/path/device.toxsave \
  --runtime /private/path/run
```

The configured defaults are research defaults, not an installation policy. The eventual
service layout remains open.

### 4.1 Identity and status

```sh
iotox --runtime RUN ping
iotox --runtime RUN status
iotox --runtime RUN address
iotox --runtime RUN profile
```

Profile mutation:

```sh
iotox --runtime RUN profile-name 'Workshop Node'
printf '%s' 'Workshop Node' | iotox --runtime RUN profile-name-stdin
iotox --runtime RUN profile-status-message 'just werx'
iotox --runtime RUN profile-status available|away|busy
```

Hex and stdin forms preserve bounded arbitrary bytes where exposed.

### 4.2 Outgoing friendship

```sh
iotox --runtime RUN transport-peer-request TOX_ADDRESS_HEX 'request message'
```

### 4.3 Incoming live request inbox

```sh
iotox --runtime RUN requests
iotox --runtime RUN request-accept PUBLIC_KEY_HEX
iotox --runtime RUN request-reject PUBLIC_KEY_HEX
```

`request-accept` fails if no matching live request exists. It creates only a Tox friendship.
`request-reject` removes the local record; the current Tox API has no rejection packet.

Deliberate direct acceptance remains:

```sh
iotox --runtime RUN transport-peer-accept PUBLIC_KEY_HEX
```

### 4.4 Peer inspection and removal

```sh
iotox --runtime RUN peers
iotox --runtime RUN transport-peer-remove FRIEND
```

`FRIEND` may be the current friend number or the 64-hex public key. Prefer the public key in
scripts.

### 4.5 Human Tox lane

```sh
iotox --runtime RUN message FRIEND 'hello'
iotox --runtime RUN action FRIEND 'waves'
printf 'binary\0bytes\n' | iotox --runtime RUN message-stdin FRIEND
iotox --runtime RUN typing FRIEND on|off
```

Read or follow a peer journal:

```sh
iotox --runtime RUN peer-messages PUBLIC_KEY_HEX
iotox --runtime RUN peer-watch PUBLIC_KEY_HEX
iotox --runtime RUN --from-start --watch-ms 5000 peer-watch PUBLIC_KEY_HEX
```

### 4.6 IoTox machine session

```sh
iotox --runtime RUN sessions
iotox --runtime RUN session FRIEND
iotox --runtime RUN hello FRIEND
iotox --runtime RUN peer-session PUBLIC_KEY_HEX
iotox --runtime RUN peer-protocol PUBLIC_KEY_HEX
```

`hello` retries the frozen canonical local HELLO for the current epoch. It is not in-place
renegotiation.

### 4.7 Raw lossless seam

```sh
iotox --runtime RUN transport-send FRIEND PACKET_HEX
```

This is a research/escape seam. It does not bypass toxcore packet limits. Candidate `0xA0`
IoTox frames are decoded and journaled; future authorized command dispatch must not be exposed
as an unstructured raw-send shortcut.

### 4.8 Finite files

```sh
iotox --runtime RUN file-send FRIEND /absolute/source
iotox --runtime RUN files
iotox --runtime RUN file-receive FRIEND FILE_NUMBER /absolute/destination
iotox --runtime RUN file-cancel FRIEND FILE_NUMBER
```

Incoming offers remain paused until explicit acceptance. Files are finite regular files with
bounded size/concurrency. The path is not yet an OTA policy.

### 4.9 Global journals and shutdown

```sh
iotox --runtime RUN events
iotox --runtime RUN watch
iotox --runtime RUN stop
```

The global event journal intentionally omits packet and human-message bodies. Per-peer journals
hold the bounded escaped content.

---

## 5. Runtime tree

Representative private projection:

```text
RUN/
  control.sock
  status
  address
  events
  events.previous
  self/
    address
    name
    status-message
    status
    profile
  requests/
    <PUBLIC_KEY>/
      public-key
      message
      message-bytes
      received-unix-ms
  peers/
    <PUBLIC_KEY>/
      number
      connection
      online
      name
      status-message
      status
      typing
      messages
      messages.previous
      protocol
      protocol.previous
      session
      iotox/
        state
        compatible
        online-epoch
        protocol
        features
        feature-bits
        maximum-frame-payload
        maximum-finite-file-bytes
        local-session-nonce
        peer-session-nonce
        detail
  transfers/
    ...
```

Properties:

- runtime root must be absolute and owner-private;
- the local socket uses peer credentials and admits the same user;
- complete structured records are published through temporary paths and rename;
- session details are written before the root `session` commit marker;
- request and transfer directories appear complete, not half-written;
- a completed `files` reply implies the current transfer tree and counts are committed;
- journals rotate to one previous bounded segment;
- arbitrary bytes are escaped into one physical line;
- public keys, not aliases, name peer/request directories;
- runtime state is disposable and rebuilt;
- savedata and future durable ledgers are separate stores.

Do not put security authority in `/run`.

---

## 6. Local control contract

The private protocol is currently version 1.6.

It is:

```text
Unix SOCK_SEQPACKET
one complete request per datagram
one correlated response
24-byte fixed header
60 KiB maximum payload
strict magic/version/kind/operation/status/reserved validation
same-user admission
bounded receive and send timeouts
```

The binary response codecs preserve bounded profile, peer, and friend-request records without
turning arbitrary bytes into accidental C strings.

The local protocol is not yet a stable public SDK promise. Wire values covered by tests should
still be changed only deliberately and documented.

---

## 7. Toxcore boundary

### 7.1 Narrow consumed API

Owned code consumes a typed function table covering only the lifecycle, options, savedata,
bootstrap/relay, profile, friendship, connection, message, packet, and file operations it
needs. The provider boundary prevents toxcore types and calls from spreading through the
product.

### 7.2 Provider modes

```text
runtime-loaded provider
  exact loadable mock
  explicit operator/integration library
  startup version and numeric-limit verification

source-linked provider
  official canonical headers required
  pinned upstream CMake source target
  same function table
  intended standalone product path
```

### 7.3 Threading invariant

No more than one operation acts on one `Tox*` at a time. Size/read pairs occur in the owner
thread without intervening mutations. Callbacks copy data before it can escape callback
lifetime.

### 7.4 Upstream risk

c-toxcore is a large security-sensitive dependency. Its own documentation describes an
experimental network library and does not supply IoTox's physical-device threat model.
Pinning, rapid patching, sandboxing, fuzzing, application signatures, and safe local policy
remain necessary even when the transport works correctly.

### 7.5 Licensing

The pinned c-toxcore release declares GPL-3.0-only. A linked distribution requires a real
corresponding-source and compliance process. Runtime loading is an architecture seam, not a
license escape. IoTox's own license remains undecided.

---

## 8. Capability session v1

### 8.1 Outer frame

Every IoTox machine packet currently uses:

```text
byte 0       0xA0 reliable custom-packet discriminator
byte 1       protocol major
byte 2       protocol minor
byte 3       message type
byte 4       flags
bytes 5..8   payload length, big-endian
bytes 9..16  message ID
bytes 17..24 correlation ID
bytes 25..32 sequence
bytes 33..40 expiry Unix milliseconds
bytes 41..   payload
```

Maximum packet: 1,373 bytes. Maximum payload: 1,332 bytes.

### 8.2 Canonical HELLO

HELLO is message type 1. Its outer frame is protocol 1.0, flags zero, nonzero random message
ID, correlation zero, sequence one, expiry zero, and exactly 64 payload bytes.

The payload carries:

```text
IHL1 magic and payload version
minimum and maximum IoTox protocol
implementation version and cube revision
maximum frame payload
supported features
required features
maximum finite file bytes
16-byte session nonce
zero reserved bytes
```

Current advertised bits:

```text
required  capability-session-v1
optional  tox-text-lane
optional  finite-file-transfer-v1
```

Named future bits remain unset until behavior exists.

### 8.3 Online epoch

A true `offline -> TCP|UDP` transition starts a new epoch. A continuous TCP/UDP presentation
change does not. Offline ends the epoch. The first peer HELLO is immutable until the next
online epoch.

### 8.4 Negotiation

The selected version is the highest common version. Required feature support is checked in
both directions. Shared features are the intersection. Frame and finite-file limits take the
smaller supported value. No common version or missing required feature fails closed.

### 8.5 States

```text
offline
awaiting-hello
compatible
incompatible-version
incompatible-features
malformed-hello
conflicting-hello
hello-send-failed
```

### 8.6 Security boundary

HELLO answers:

```text
Does this connected Tox friend speak a compatible IoTox transport protocol?
```

It does not answer:

```text
Who owns this physical device?
Which principal signed this command?
May this principal perform this operation?
Did the operation execute?
```

The next session slice should explicitly confirm both nonces and the selected transcript before
application commands exist.

---

## 9. Friend-request inbox semantics

c-toxcore reports a 32-byte public key and at most 921 message bytes. IoTox copies both during
the callback and creates one live record per key.

`request-accept`:

1. requires the key in the current live inbox;
2. calls `tox_friend_add_norequest` through the owner thread;
3. consumes the current local request;
4. refreshes peers and savedata policy;
5. grants no IoTox authority.

`request-reject` consumes only the local record. There is no remote rejection packet in the
consumed API.

The live inbox is intentionally not crash-durable in rev0007. If durable request history is
later desired, define a separate bounded private store with retention, redaction, replay, and
storage-full behavior. Do not quietly turn `/run` into that store.

---

## 10. Persistence and files

### 10.1 Tox savedata

The state store:

1. serializes bytes from the owner thread;
2. creates a private unpredictable temporary file;
3. writes all bytes;
4. synchronizes the file;
5. atomically renames it over the live path;
6. synchronizes the parent directory;
7. uses mode `0600`.

Friend mutation persistence does not depend solely on graceful shutdown.

The savedata is not yet encrypted by an IoTox keystore and is not the stable application
identity ledger.

### 10.2 Finite file path

Outgoing files are finite regular files whose identity/size/mtime are checked during transfer.
Incoming offers stay paused until an explicit private destination and same-directory temporary
file are acquired. Completion synchronizes and publishes without clobbering an existing final
path.

Full c-toxcore file numbers are opaque. Do not encode assumptions into their bit pattern.

### 10.3 Future firmware

Tox file transfer can carry firmware bytes, but authority and safety require a separate signed
manifest, immutable digest, target constraints, anti-rollback state, staging, health check,
and recovery path. Friendship is not firmware authority.

---

## 11. Ownership and RecallRoot direction

The target hierarchy remains conceptually separate:

```text
permanent RecallRoot phrase
        |
domain-separated owner root material
        |
stable IoTox owner/controller identities and authorization ledger
        |
explicit bindings to replaceable Tox route endpoints
```

Possible device classes:

```text
hardware attestation identity        optional, says which hardware this is
stable IoTox device identity         application identity and ownership epochs
Tox endpoint identity                replaceable route/transport address
local data-encryption identity        protects retained application data
```

The exact signing primitive, canonical ledger encoding, derivation tree, endpoint binding, and
re-entry transcript are not frozen.

Recovery cases must remain distinct:

```text
transport profile replacement
controller replacement/revocation
owner re-entry from the permanent phrase
destructive physical reset
ownership transfer
```

The permanent phrase is intentionally retained. The no-vendor-sovereign rule is equally
permanent. The design work is to make those coexist through explicit epochs, signatures,
revocation, and destructive boundaries—not to remove either premise.

---

## 12. Network direction

### 12.1 Tox/native

This is the only enabled route. Bootstrap and TCP relay inputs may use compiled defaults or
complete operator replacement. Operating a bootstrap or relay provides a road, not ownership.

### 12.2 Tox/Tor

Reserved. Likely requires TCP-only toxcore policy, explicit proxy/tunnel handling, known
relay topology, disabled native discovery, DNS/UDP leak tests, and fail-closed operation. The
pinned 0.2.23 public options header includes the experimental DNS-disable setter specifically
for client-controlled resolution such as Tor; it is useful but must be re-reviewed at every
upstream pin because the upstream contract labels it experimental.

### 12.3 Tox/I2P

Reserved. Likely requires explicit stream tunnels and overlay-reachable bootstrap/relay
infrastructure, plus restart, endpoint-distribution, latency, and resource tests.

### 12.4 Identity across routes

Reusing one Tox key across native, Tor, and I2P improves continuity but creates linkability.
Route-specific endpoint keys under one stable IoTox device identity may be preferable. No
choice is frozen.

### 12.5 Owner-operated infrastructure

IoTox should make it easy for owners and communities to run bootstrap nodes, relays, and later
optional durable hubs. Such infrastructure must be replaceable and must not receive hidden
ownership authority.

---

## 13. Security invariants

Keep these true or write an ADR that explicitly changes them:

1. A Tox friend is not an IoTox owner.
2. A compatible HELLO is not authorization.
3. A Tox receipt is not physical execution.
4. A file is not trusted firmware.
5. `/run` is not durable authority.
6. One thread owns one `Tox*`.
7. Public-key directories never derive from unvalidated path text.
8. Untrusted lengths are bounded before allocation or copy.
9. Required semantic events do not disappear silently.
10. A requested reserved route never silently falls back to native.
11. A timed-out future physical command must not execute later without explicit semantics.
12. Duplicate future physical commands must not execute twice accidentally.
13. The permanent phrase remains susceptible to offline guessing by design; weak phrases are
    not accepted as equivalent.
14. No IoTox-controlled key may reassign a customer device.
15. Source review, mock execution, source linking, real peers, routes, hardware, and production
    are separate evidence classes.

Before high-consequence actions, require at least:

```text
confirmed session transcript
stable application device/principal identities
application signature
authorization epoch and capability
expiry and replay rules
idempotency or desired-state semantics
durable receipt and terminal result
safe local policy or physical interlock
```

---

## 14. Verification facility

### 14.1 Registered checks

Current default owned-code count:

```text
60 registered C++ tests
7 CTest entries
3 libFuzzer targets
```

The tests cover network-route modeling, frame/session/local codecs, CSPRNG, RecallRoot contract,
state replacement, owner queue/event behavior, toxcore transport adapter, bootstrap inputs,
profile/text/receipt behavior, friend requests, runtime tree, file transfer, CLI, and one-binary
agent integration. Final retained lanes pass under GCC debug/release, Clang debug, Clang
ASan/UBSan, and GCC TSan; each of the three fuzz targets completed 5,000 smoke runs, and the
optional Mutorr preservation configuration passed nine CTest entries. These are bounded local
results, not source-linked or real-network evidence.

### 14.2 Fuzz targets

```text
iotox_frame_fuzzer
iotox_session_fuzzer
iotox_local_control_fuzzer
```

A smoke run proves bounded executions under a named build. It is not a parser proof.
Canonical seeds live under `tests/corpus/`; the smoke script copies them into build-local
corpora so libFuzzer never rewrites reviewed repository inputs.

### 14.3 Defects already found by the facility

Earlier revisions found and repaired, among other things:

- an incorrect C++ function-pointer boundary in the first toxcore mock;
- unsafe/incomplete state replacement details;
- owner startup visibility ordering;
- process-fixture path dependence;
- observer ceilings that hid eventual callback projection;
- rev0007's mistaken assumption that friend acceptance immediately meant online connection;
- a missing explicit authority boundary in the session projection;
- a session-summary/detail publication race, repaired with an explicit commit marker;
- a configured session fuzzer source that had no executable target in the build graph;
- an authoritative empty `files` response racing stale transfer projection;
- process-fixture failure paths that could abandon a live child agent.

The facility is expected to find mistakes. Its purpose is not to prove that none were made.
A stale pre-final matrix process also deleted shared build directories in an older working
tree; final evidence was regenerated in an isolated tree rather than treating an interrupted
command window as a source failure.

### 14.4 Real-peer handoff

`tools/run-real-peer-smoke.sh` is prepared for a networked CLI. It should launch two source-
linked agents, request/accept friendship, wait for compatible sessions both directions, send
traffic, stop, restart, and verify identity continuity. It is not counted as passing here.

### 14.5 Evidence labels

```text
planned
source-reviewed
compiled
unit-tested
mock-ABI-tested
process-tested
source-linked
real-peer-tested
route-tested
target-device-tested
production-qualified
```

Never collapse these labels.

---

## 15. Repository map

From `.datacube/`:

```text
CMakeLists.txt / CMakePresets.json   build graph and named lanes
include/iotox/                       owned public/internal headers
src/                                 one-binary implementation
tests/                               tests, exact mocks, fuzzers, seed corpora
tools/                               build, test, standalone, real-peer, package scripts
docs/decisions/                      append-only ADR ledger
docs/research/                       pinned source readings and build reports
docs/governance/                     office/change/claim rules
docs/history/                        superseded entrances and historical branches
incubator/mutorr/                    optional non-default research
third_party/                         retained word list and license material
artifacts/                           reviewed prebuilt evidence and exact logs
dependencies.lock                    immutable upstream pins
REVISION                             current cube revision
```

Key current documents:

```text
docs/architecture.md
docs/protocol-session.md
docs/protocol-draft.md
docs/ratox-successor-assessment.md
docs/recovery-and-ownership.md
docs/networks.md
docs/threat-model-draft.md
docs/testing.md
docs/roadmap.md
docs/open-questions.md
```

---

## 16. Immediate ordered work

Validation gates remain important, but unavailable gates do not forbid progress on owned code.

### 16.1 Official source-linked build

- fetch and verify the pinned archives;
- compile through canonical headers and `toxcore_static`;
- repair all real API/CMake mismatches;
- verify no runtime toxcore/libsodium dependency;
- retain corresponding-source and license evidence.

### 16.2 Two genuine native Tox peers

- request and accept friendship;
- observe actual connection callbacks;
- negotiate HELLO both directions;
- test message/receipt and finite files;
- force disconnect/reconnect and verify a new session epoch;
- exercise native direct and relay-only topology;
- measure bootstrap/reconnect timing and resource use.

### 16.3 Complete the session transcript

Implement a bounded CAPABILITIES/confirmation record that binds both canonical HELLO payloads
or digests, both nonces, selected protocol, shared feature mask, negotiated limits, and sender
role. Define timeout/retry and exact application-send barrier.

### 16.4 Independent authorization ledger

Choose and implement:

```text
stable IoTox device identity
owner and delegated controller identities
canonical signed records
roles and capabilities
ownership epoch
delegation and revocation
endpoint binding
rollback resistance
```

A compatible but unauthorized peer must remain an ordinary tested state.

### 16.5 Durable command lifecycle

Implement a bounded persistent inbox/outbox/result cache with signatures, unpredictable IDs,
correlation, replay window, issued-at/relative TTL, idempotency, cancellation, storage-full
policy, and explicit states:

```text
RECEIVED
STARTED
SUCCEEDED
FAILED
EXPIRED
```

### 16.6 RecallRoot re-entry

Connect the frozen permanent phrase contract to domain-separated owner keys, challenge-
response, controller replacement, ownership epochs, wrong-phrase behavior, and revocation—
without adding a vendor reassignment key.

### 16.7 Fuller ratox façade

Add writable compatibility paths/FIFOs over structured control, with correlated result/error
channels, safe service-manager defaults, labels/aliases, and retention policy. Do not make the
FIFO a durable queue.

### 16.8 Routes, hardware, and stewardship

After native truth is strong enough:

- build leak-tested Tox/Tor;
- research overlay-native Tox/I2P;
- benchmark named Linux-class devices;
- add sandboxing and signed update practice;
- make owner/community bootstrap and relay operation easy;
- upstream useful fixes.

---

## 17. Questions that must stay visible

- Which application signing primitive and canonical encoding become IoTox identity?
- How does a stable device identity bind and rotate Tox route endpoint keys?
- What exact CAPABILITIES transcript is minimal and sufficient?
- Should incoming Tox requests ever be durably retained, and under what redaction policy?
- Which durable store gives the clearest crash and rollback behavior?
- How are bad clocks handled without executing stale physical commands?
- How does RecallRoot derive owner/controller keys while permitting revocation?
- What ownership state survives or is destroyed by physical reset?
- Which ratox FIFO paths deserve exact compatibility?
- Can Tox/Tor be proven TCP-only and leak-free with the chosen toxcore version?
- What I2P relay/bootstrap topology is actually reproducible?
- Which first target hardware class makes toxcore's resource use acceptable?
- How will GPL corresponding source, reproducible builds, and rapid security updates operate?

`docs/open-questions.md` carries the maintained expanded list.

---

## 18. Governance and revision discipline

### 18.1 Source-of-truth order

When current records conflict, use this order:

1. observed current code and retained reproducible evidence;
2. accepted ADRs not superseded by a later ADR;
3. this BOOTSTRAP current-truth statement;
4. current architecture/protocol/testing documents;
5. roadmap and open questions;
6. historical documents and prior prose.

Do not let a confident paragraph overrule code or evidence silently. Reconcile the records.

### 18.2 BOOTSTRAP edit freedom and minimum duty

The office holder is free to reorder, compress, expand, or rewrite this file thoroughly.
Preserve neither wording nor section numbers for their own sake.

Every revision's entrance must still contain enough to recover:

```text
project identity and northstar
non-negotiable decisions
current implemented truth
current unproven claims
exact build/run/test path
one-binary operator surface
security and authority boundaries
network and recovery direction
repository/evidence map
ordered next work
open design questions
package/governance rules
```

Before replacing it, copy the previous entrance to:

```text
docs/history/BOOTSTRAPROSE-rev####.md
```

### 18.3 Decision changes

Accepted ADRs are historical records. A changed decision gets a new ADR that names what it
supersedes. Do not rewrite old ADRs into agreement.

### 18.4 Claim maturity

Every important statement should make its evidence class obvious. “Implemented” is not a
synonym for “worked on the public Tox network.” “Source-reviewed” is not “compiled.” “Mock
passed” is not “cryptography passed.”

### 18.5 Revision contents

A strong revision includes:

```text
actual product code, not only scaffolding
focused tests and process behavior
source research for external assumptions
ADRs for durable decisions
updated current docs and BOOTSTRAP
exact retained logs and checksums
historical preservation where material
an honest ordered handoff
```

### 18.6 Archive name

Required form:

```text
IoTox-rev####-YYYY.MM.DD.HH.MM-lowercase-hyphenated-summary-highlight-codename.zip
```

Use America/New_York time. The full filename is the user-visible link text.

Package from `.datacube/`:

```sh
./tools/make-revision-archive.sh \
  rev0007 \
  "$(TZ=America/New_York date +%Y.%m.%d.%H.%M)" \
  peers-speak-first-canonical-hello-live-request-inbox \
  /mnt/data
```

Then unzip into a clean directory, verify the lone entrance, build the extracted cube, run at
least the GCC debug CTest lane, inspect the archive listing, and record the archive hash.

---

## 19. rev0007 handoff

The emotional milestone in this cube is simple:

> A Tox friend comes online, and the peers speak first.

The agent now knows the difference between:

```text
this is a Tox friend
this friend is online
this online friend speaks a compatible IoTox session
this peer is authorized to do something
```

The first three states exist. The fourth deliberately does not.

The operator can also see an incoming friend request, accept it only when it really exists,
reject it, or deliberately add a known key through the lower transport operation. The surface
is becoming recognizably ratox-like while the core becomes more explicit than ratox could be.

Continue toward the actual product. Do not wait for perfect certainty. Do not erase uncertainty
either.
