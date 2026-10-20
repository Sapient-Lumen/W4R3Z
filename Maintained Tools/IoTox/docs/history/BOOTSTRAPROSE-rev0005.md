# BOOTSTRAPROSE — The Lone Entrance

**Project:** IoTox  
**Revision:** rev0005  
**Codename:** One Binary, File Road  
**Immediate northstar:** a standalone, one-binary, C++20 ratox successor built around c-toxcore  
**Evidence state:** mock-binary-verified; real c-toxcore source-link path prepared but not executed here  
**Office:** held by whoever is presently responsible for making the cube more truthful

This is the lone ordinary entrance to the IoTox datacube.

Everything else is intentionally hidden under `.datacube/`. That hiding is interface
discipline, not security. A future office holder—human or machine—must be able to wake
without conversational memory, read one object, learn the governing decisions, reproduce
the retained evidence, and enter the working repository without guessing which old README
won an argument.

Read this file completely before changing the project.

This file is not a shrine. It is living operational governance. The office holder is free
to rewrite it thoroughly and is obligated to do so when code, evidence, decisions, or
priorities change. Preserve superseded entrances under `.datacube/docs/history/`; do not
preserve stale claims in the active entrance.

The standard is a **wake-from-amnesia Rolls-Royce**: unusually good orientation, precise
claims, decisive ordering, reproducible commands, and enough context to resume difficult
work without the prior conversation.

---

## 0. `/run` — assume the office

When instructed to `/run: BOOTSTRAPROSE.md`, perform this sequence. Do not merely summarize
it.

1. Read this entire file.
2. Confirm that it is the only ordinary visible root object:

   ```sh
   cd IoTox/.datacube
   ./tools/check-lone-entrance.sh
   ```

3. Read, in order:

   ```text
   REVISION
   CHANGELOG.md
   README.md
   BUILDING.md
   docs/architecture.md
   docs/ratox-successor-assessment.md
   docs/protocol-draft.md
   docs/threat-model-draft.md
   docs/roadmap.md
   docs/open-questions.md
   docs/decisions/README.md
   ```

4. Build and test the default product before trusting prose:

   ```sh
   cmake --preset gcc-debug
   cmake --build --preset gcc-debug --parallel
   ctest --preset gcc-debug --output-on-failure
   ```

5. Inspect the current executable surface:

   ```sh
   ./build/gcc-debug/iotox --version
   ./build/gcc-debug/iotox --help
   ./build/gcc-debug/iotox bootstrap-seeds
   ```

6. Inspect evidence retained under `.datacube/artifacts/` and research notes under
   `.datacube/docs/research/`. Distinguish evidence produced in this environment from plans
   intended for a later command line.
7. Work the first unresolved gate in §15 unless new evidence justifies changing the order.
8. Before delivery, update this file, archive the superseded entrance, run the available
   matrix, refresh artifacts and checksums, increment the revision, package a clean cube,
   extract it elsewhere, and rerun the retained smoke facility.

The office holder may alter architecture, priorities, prose, tests, or code. Material
reversals require an ADR that says what changed, why, and what evidence displaced the old
decision. Governance exists to preserve reasoning, not to prevent correction.

---

## 1. The thing being made

IoTox is a self-owned, peer-to-peer device agent whose primary network is Tox.

The immediate product is a modern ratox successor. It is not presently a distributed
database, a mandatory cloud, a GUI framework, an OTA appliance, or an abstraction over
every anonymity network. It is the small, strong base from which those things could be
built without surrendering ownership.

The product should make encrypted peer networking feel like ordinary local machinery:

```text
start one binary
see its persistent Tox address
observe connection and peer state
receive and deliberately accept transport requests
send framed lossless packets
send and receive finite files
watch a private local surface
restart without losing identity
script all of it without embedding toxcore
```

The internal system must earn that simplicity with:

```text
one toxcore owner thread
bounded queues and datagrams
explicit errors and request correlation
private atomic state persistence
strict packet decoding
safe file descriptors and no-clobber publication
transport friendship separated from authority
route policy that fails closed
reproducible source-linked dependencies
hostile tests, sanitizers, and fuzzers
```

The governing product sentence is:

> **From memory, you can reach your devices.**

The governing implementation sentence is:

> **Make the simple operation truly simple without lying about what occurred.**

The ratox inheritance is philosophical and practical: Unix composability, a small surface,
local ownership, and the feeling that it “just werx.” IoTox does not inherit ambiguity as
the price of that elegance.

---

## 2. Decisions in force

These are project decisions, not passing preferences. Reverse one only with an explicit
replacement decision record.

### 2.1 Tox stays primary

Tox remains the primary connection fabric. It supplies endpoint identity, encrypted peer
sessions, NAT traversal, bootstrap discovery, TCP relays, reliable custom packets, and file
transfer. IoTox supplies durable device identity, ownership, authorization, re-entry,
command semantics, local policy, and route policy above it.

A Tox public key is a transport endpoint. It is not automatically an owner, administrator,
firmware signer, storage custodian, or actuator authority.

IoTox intends to contribute useful bootstrap and relay capacity, deployment instructions,
measurements, and fixes to the Tox commons. A bootstrap or relay operator never receives
IoTox ownership authority.

### 2.2 One product executable

The product command is **`iotox`**.

```text
iotox run ...       foreground agent and toxcore owner
iotox status        same binary acting as a local client
iotox peers         same binary acting as a local client
iotox file-send ... same binary acting as a local client
```

There is no `iotoxd` product target in rev0005. Internal static libraries, test binaries,
mock libraries, fuzzers, and optional research executables may exist, but ordinary product
installation exposes one executable.

### 2.3 Standalone means source-linked toxcore by default

The intended distributable `iotox` binary contains the pinned c-toxcore and libsodium code
needed for Tox operation. Ordinary platform runtime libraries may remain shared; toxcore
and libsodium must not be required as separately installed runtime libraries in the
standalone build.

Runtime `dlopen` remains a valuable research and testing provider. It allows the exact ABI
mock and can diagnose a separately installed toxcore. It is not the preferred owner
experience.

The provider rule is:

```text
source-linked build + no override  -> linked c-toxcore
source-linked build + --library    -> explicit dynamic diagnostic override
research build                      -> runtime-loaded compatible c-toxcore
```

Both providers populate the same narrow function table and feed the same owner-thread
implementation.

### 2.4 Permanent recall remains

IoTox keeps a fixed Argon2id derivation contract for owner re-entry. A strong generated
phrase may be memorized, printed, or both. The same phrase reproduces the same RecallRoot
without stored per-owner salt or vendor lookup.

This intentionally permits offline guessing. Phrase strength is therefore structural,
not optional. RecallRoot-v1 currently fixes:

```text
word list:       pinned EFF 7776-word long list
phrase:          8 independently uniform generated words
entropy:         approximately 103.4 bits under uniform generation
normalization:   canonical single ASCII spaces and exact listed words
algorithm:       Argon2id version 19
memory:          65536 KiB
iterations:      3
lanes/threads:   4
public salt:     IoToxRecallRoot1
output:          32 bytes
```

Human-invented passwords are unacceptable. The phrase and RecallRoot must never be sent to
a peer or placed in ordinary process arguments. Domain-separated delegated keys will
perform daily work. The owner-key hierarchy and live re-entry handshake remain unfinished.

### 2.5 No vendor reassignment sovereign

No IoTox maintainer, company, app publisher, bootstrap operator, relay operator, update
service, or manufacturer possesses a key capable of silently reassigning an owner’s device.

A manufacturer key may attest hardware or sign software. It may not replace the owner.

### 2.6 Authorization is independent of Tox friendship

IoTox needs an application authorization ledger with owners, delegated controllers, roles,
capabilities, ownership epochs, endpoint bindings, temporary grants, and revocation.

Transport friendship creates only a Tox relationship. The current commands deliberately say
`transport-peer-*`.

No physical actuation operation belongs in the trusted product surface until application
signatures, authorization, expiry, replay rules, durable execution state, idempotency, and
cancellation semantics exist.

### 2.7 Native Tox first; other routes reserved and fail closed

The route model is two-dimensional:

```text
transport: Tox
route:     native | Tor-reserved | I2P-reserved
```

That is separate from possible future direct IoTox transports over Tor or I2P.

Only `Tox/native` is enabled. `Tox/Tor` and `Tox/I2P` are deliberate future spaces through
which Tox itself may run. Selecting either today returns an explicit unsupported error.
It may never silently leak through native networking.

### 2.8 Mutorr is preserved, not pursued

The Milehigh/Mutorr small-circle research is retained under
`.datacube/incubator/mutorr/`. It is excluded from the default build and is not the current
northstar. Core product code must not acquire an accidental dependency on it.

### 2.9 Structured local core; ratox-style projection

The authoritative local API is a bounded, versioned Unix `SOCK_SEQPACKET` protocol. It has
whole-message framing, operation types, request IDs, response correlation, and explicit
status codes.

The process also projects private ratox-inspired files under its runtime root. These are
inspectable local views, not the authority database and not a durable command queue.
Future FIFOs may be added only as façades over explicit structured semantics.

### 2.10 C++20 is the owned implementation language

IoTox-owned product code, tests, mocks, fuzzers, and retained research code are C++20.
External libraries may be C but remain behind narrow exact boundaries. GCC and Clang are
both first-class. Warnings are errors in checked configurations.

---

## 3. Claim vocabulary

Use these labels precisely:

```text
idea                 described only
planned              ordered work with acceptance criteria
compiled             compiler and linker accepted it
unit-verified         deterministic direct tests passed
adapter-verified      boundary passed against an exact test double
binary-verified       separate built processes passed an end-to-end fixture
source-linked         compiled against and linked with the named upstream source
network-verified      real peers crossed a named real or controlled network
route-verified        route behavior and leak properties were measured
target-verified       measured on intended hardware and operating conditions
production            reviewed, supportable, updateable, and accepted for deployment
```

Do not use “implemented” as a solvent that dissolves these distinctions.

The current project is:

```text
one-binary product shape:          compiled and binary-verified
runtime-loaded toxcore boundary:   adapter-verified against exact mock
source-linked toxcore provider:    compiled as IoTox code, upstream link not run here
Tox identity persistence:          binary-verified against exact mock
friend lifecycle:                  binary-verified against exact mock
lossless packet path:              binary-verified against exact mock
finite file transfer manager:      binary-verified against exact mock
Tox/native Internet operation:     not network-verified
standalone pinned binary:          planned path with scripts; not produced here
Tox/Tor and Tox/I2P:               reserved and fail-closed
IoTox authorization ledger:        planned
RecallRoot derivation:             adapter-verified against exact Argon2 ABI mock
RecallRoot live re-entry:          planned
physical device actuation:         deliberately absent
```

---

## 4. Current executable surface — rev0005

### 4.1 Agent mode

```sh
iotox run [options]
```

Important options:

```text
--library PATH                 dynamic c-toxcore override/research provider
--state PATH                   private toxcore savedata file
--runtime PATH                 private ratox-style runtime root
--network tox/native           only enabled route
--bootstrap HOST:PORT:KEY      replace default bootstrap set; repeatable
--tcp-relay HOST:PORT:KEY      replace default relay set; repeatable
--no-default-bootstrap         use no compiled bootstrap nodes
--no-default-relays            use no compiled relay nodes
--bootstrap-retry-ms N         retry cadence while disconnected
--owner-command-timeout-ms N   owner-queue admission/start deadline
--max-pending-commands N       bounded owner-thread command queue
--max-pending-events N         bounded transport event queue
--max-file-bytes N             finite file ceiling, default 1 GiB
--max-active-sends N           concurrent outgoing finite-file limit
--max-active-receives N        accepted incoming finite-file limit
--max-pending-file-offers N    paused incoming offer limit; zero rejects all
--run-ms N                     deterministic fixture lifetime
```

Defaults are intended for research, not all device classes. Product deployments must set
limits according to storage, memory, trust, and workload.

### 4.2 Local control mode

The same executable talks to the running process:

```text
ping
status
address
stop
peers
transport-peer-request TOX_ADDRESS_HEX MESSAGE
transport-peer-accept PUBLIC_KEY_HEX
transport-peer-remove FRIEND_NUMBER
transport-send FRIEND_NUMBER PACKET_HEX
transport-hello FRIEND_NUMBER [TEXT]
file-send FRIEND_NUMBER ABSOLUTE_PATH
file-receive FRIEND_NUMBER FILE_NUMBER ABSOLUTE_PATH
file-cancel FRIEND_NUMBER FILE_NUMBER
files
bootstrap-seeds
```

`transport-peer-add` remains only as a compatibility alias for explicit no-request peer
acceptance. New prose and scripts use `transport-peer-accept`.

The low-level send and hello commands are research tools. They are not an authorization API.

### 4.3 Runtime projection

The default root is platform-derived under `/run/user/$UID/iotox` where available, otherwise
an owner-specific temporary runtime location. A configured root must be absolute. Important
entries include:

```text
status
control.sock
self/address
self/connection
peers/<64-hex-public-key>/number
peers/<64-hex-public-key>/connection
peers/<64-hex-public-key>/online
requests/<64-hex-public-key>/public-key
requests/<64-hex-public-key>/message
requests/<64-hex-public-key>/message-bytes
transfers/<direction>-<friend>-<file>/direction
transfers/<direction>-<friend>-<file>/state
transfers/<direction>-<friend>-<file>/friend-number
transfers/<direction>-<friend>-<file>/file-number
transfers/<direction>-<friend>-<file>/kind
transfers/<direction>-<friend>-<file>/size
transfers/<direction>-<friend>-<file>/position
transfers/<direction>-<friend>-<file>/file-id
transfers/<direction>-<friend>-<file>/filename
transfers/<direction>-<friend>-<file>/filename-bytes
transfers/<direction>-<friend>-<file>/local-path
transfers/<direction>-<friend>-<file>/detail
events
events.previous
```

Directories are owner-only (`0700`); files and the control socket are owner-only (`0600`).
Peer, request, and transfer directories are prepared completely in private temporary
directories and published by rename. Observers must not see half a request or half a
transfer record.

The event journal records metadata and sizes, not lossless-packet or file contents.

---

## 5. Architecture that exists

```text
                         one installed executable
                                iotox
                                  |
              +-------------------+-------------------+
              |                                       |
          iotox run                             local subcommands
              |                                       |
              |                              Unix SOCK_SEQPACKET
              |                                       |
              +--------------- Agent ----------------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
        RuntimeTree       FileTransferManager   protocol framing
              |                   |                   |
              +-------------------+-------------------+
                                  |
                           ToxTransport API
                                  |
                   bounded command/event queues
                                  |
                       one toxcore owner thread
                                  |
              +-------------------+-------------------+
              |                                       |
       linked function table                    dlopen function table
     intended standalone mode                 exact mock/research mode
              |                                       |
        c-toxcore static                         c-toxcore shared
              |
          libsodium
```

No business-logic component owns or calls `Tox*`. The owner thread serializes all toxcore
operations and callbacks. Public calls submit bounded commands and wait for a result. A
command that times out before beginning is explicitly removed and cannot later execute.
Work that has begun is not falsely reported as cancelled.

The event queue distinguishes required events from observational events:

- friendship mutations, requests, custom packets, and file-transfer protocol events cannot
  be silently discarded; they apply backpressure;
- observational diagnostics may be evicted when bounded capacity is exhausted;
- every later event carries the cumulative evidence-loss count, and status exposes it.

Mutation persistence and shutdown persistence are separate configuration decisions. A
friend addition or deletion can be durably saved without depending on a graceful process
exit.

---

## 6. Toxcore boundary and standalone plan

### 6.1 Target

rev0005 targets official c-toxcore **0.2.23**, released June 3, 2026. The dependency lock
also pins libsodium **1.0.22**. Release URLs and SHA-256 digests are in
`.datacube/dependencies.lock`.

The source-linked path adds the pinned c-toxcore source tree as a CMake subdirectory, turns
off toxav, bootstrap daemons, utilities, and upstream tests, enables `toxcore_static`, and
links it into `iotox`. The linked provider uses official headers when that source tree is
present.

The dynamic provider validates:

```text
version compatibility with 0.2.23
public key size
Tox address size
file-id length
maximum filename length
maximum friend-request length
maximum custom-packet size
all required function symbols
```

c-toxcore does not promise numeric constants as ABI; runtime constant functions are checked
rather than assumed.

### 6.2 Reproduce the normal mock-backed build

```sh
cd IoTox/.datacube
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel
ctest --preset gcc-debug --output-on-failure
```

### 6.3 Build the intended standalone binary on a connected command line

```sh
cd IoTox/.datacube
./tools/build-standalone.sh
```

That script:

1. downloads only the pinned release archives;
2. verifies exact SHA-256 digests before extraction;
3. builds static libsodium into a private prefix;
4. configures IoTox against pinned c-toxcore source;
5. builds only the `iotox` product executable;
6. verifies that no unresolved toxcore symbols remain;
7. rejects a runtime dependency on `libtoxcore` or `libsodium`;
8. records dependency and binary hashes.

This environment could not retrieve the upstream archives through the shell, so the final
source-linked build remains an external gate. Do not claim it passed until its retained
verification report exists.

### 6.4 Why retain dynamic loading

The mock is a loadable shared object implementing exactly the subset consumed by IoTox. It
lets the full C++ path exercise symbol resolution, options, lifecycle, callbacks, friendship,
savedata, packets, and transfers deterministically. Dynamic loading also supports diagnostic
comparison with a system toxcore.

It does not prove packet compatibility, NAT traversal, relay behavior, DHT behavior, power
cost, or Internet reachability.

---

## 7. Friendship and packet behavior

IoTox supports both Tox friendship ceremonies:

```text
request_friend(address, message)    full Tox address and nonempty bounded message
accept_friend(public_key)           no-request acceptance of an observed/verified key
remove_friend(friend_number)
list_friends()
```

Friend requests are projected privately and remain until explicit acceptance. Acceptance
updates the persisted friend list and the runtime projection before the local response is
returned.

The current application-frame lane uses Tox reliable custom packets. Its envelope includes:

```text
protocol major and minor
message type
flags
message ID
correlation ID
sequence number
expiry field
payload length
bounded payload
```

The decoder rejects malformed identifiers, unsupported message types, version mismatch,
truncation, length mismatch, and packets above the Tox custom-packet ceiling.

This envelope is scaffolding. Version negotiation, message-ID generation, clock/TTL rules,
application signatures, durable acknowledgements, and replay state are not yet frozen.

---

## 8. File-transfer behavior — rev0005

c-toxcore’s file-transfer API is used rather than inventing a bulk-data protocol over
custom packets.

### 8.1 Exact low-level seam

The transport exposes:

```text
offer_file
control_file: resume | pause | cancel
seek_file
get_file_id
find_file by stable file id
send_file_chunk
file offer callback
file control callback
file chunk-request callback
file receive-chunk callback
```

Public Tox file numbers are treated as opaque `uint32_t` handles. Current c-toxcore encodes
incoming handles separately from outgoing handles; IoTox does not decode or depend on that
pattern for policy.

### 8.2 High-level manager scope

rev0005 supports finite regular files only.

Outgoing behavior:

- path must be absolute;
- file is opened with `O_NOFOLLOW | O_CLOEXEC`;
- it must be a finite regular file;
- size and filename are bounded before offer;
- device, inode, size, and nanosecond modification time are frozen;
- each requested chunk is read from a duplicated descriptor at the exact requested offset;
- metadata is verified before and after reading;
- mutation fails closed and cancels the Tox transfer;
- zero-byte files follow toxcore terminal-callback semantics;
- completed live records are removed from the active projection.

Incoming behavior:

- offers begin paused, as required by c-toxcore;
- pending offers are bounded and overflow is explicitly cancelled;
- unknown-size streams and non-data kinds are rejected by the safe path receiver;
- a destination must be absolute and its immediate parent must be a real directory owned by
  the IoTox user;
- an existing destination is never replaced;
- acceptance first acquires a `0600`, close-on-exec temporary file in the destination
  directory;
- chunks must be ordered and remain inside the advertised size;
- completion requires the exact advertised final position;
- data and directory metadata are `fsync`ed;
- publication uses same-directory `link` plus `unlink`, so an appearing destination cannot
  be clobbered;
- cancellation, disconnect, or failure removes the temporary file.

Known limits:

- ancestor symlinks above the immediate destination parent are not yet comprehensively
  forbidden;
- there is no content digest, application authorization, durable restart/resume ledger, or
  terminal-history database;
- the live list intentionally contains only pending/active state;
- streaming transfers are not accepted;
- the mock models the consumed callback contract, not a full remote toxcore peer.

Do not use this path for firmware until independent signatures, target binding, rollback
protection, staging, and boot-health confirmation exist.

---

## 9. What the retained tests prove

The default GCC debug facility currently contains **44 registered C++ tests** and **seven
CTest lanes**.

The tests cover:

- exact fallback ABI type compatibility;
- one owner thread and lifecycle ordering;
- runtime constant validation;
- bounded command admission and pre-start cancellation;
- bounded event behavior and required-event backpressure;
- Tox savedata identity persistence;
- friend request, accept, list, remove, and persistence;
- bootstrap and TCP-relay parsing and attempts;
- custom packet encoding, transport, callback, and decoding;
- local control framing, correlation, bounds, credentials, and stale-socket defense;
- private ratox-style runtime status, peers, requests, transfers, and journal rotation;
- transactional projection with no partially visible request/transfer directories;
- finite outgoing and incoming file transfer;
- exact chunk positions and stable file IDs;
- destination no-clobber;
- source mutation rejection;
- zero-byte transfer completion;
- pending-offer overflow rejection;
- private atomic state replacement;
- RecallRoot phrase and Argon2 ABI contract;
- explicit failure of reserved Tox/Tor and Tox/I2P routes.

The separate process fixture starts `iotox run`, uses the same built `iotox` as the local
client, accepts a peer, sends a packet, sends a local file through toxcore chunk requests,
receives a paused file into an explicit path, checks the runtime tree, stops, restarts with
the same address and friend list, removes the peer, and stops again.

That is **binary verification against a mock**, not real-network verification.

Sanitizer and fuzz configurations exist for:

```text
Clang AddressSanitizer + UndefinedBehaviorSanitizer
GCC ThreadSanitizer
Clang libFuzzer for application frames
Clang libFuzzer for local control packets
```

The office holder must retain exact commands and results for each delivered revision rather
than merely saying “sanitizers were used.”

---

## 10. Security invariants

These are minimum invariants, not a complete threat model.

1. **Friendship is not authority.** A Tox peer never gains IoTox ownership or actuation by
   friendship alone.
2. **No vendor reassignment key.** Infrastructure or software publishers cannot replace the
   owner.
3. **RecallRoot remains local.** Phrase and root never cross the network or ordinary argv.
4. **Phrase strength is mandatory.** Fixed derivation intentionally enables offline
   verification of guesses.
5. **One toxcore owner thread.** No business component calls `Tox*` directly.
6. **Routes fail closed.** An unavailable requested overlay may not fall back to native.
7. **Bound before allocation.** Frames, paths, messages, files, queues, and offer sets have
   explicit ceilings.
8. **Required protocol events do not disappear.** Backpressure is preferable to silent
   semantic loss.
9. **Timeout is not retroactive cancellation.** Only not-yet-started owner work may be
   removed by the current deadline mechanism.
10. **Transport delivery is not execution.** Future device operations require durable
    application states and terminal results.
11. **Retry is not repetition.** Hardware-affecting work requires idempotency and duplicate
    result handling.
12. **State is private and atomically replaced.** A routine power interruption should not
    destroy the Tox identity.
13. **Incoming files do not clobber.** Existing destinations survive, and incomplete data is
    never published as final.
14. **Outgoing files are immutable for the transfer.** Mutation aborts rather than mixing
    versions.
15. **Status surfaces do not copy payload secrets.** Journals record metadata, not packet or
    file bodies.
16. **Firmware trust is independent of transport.** A Tox channel alone cannot authorize
    executable installation.
17. **Mocks remain labeled.** Deterministic test doubles never count as network evidence.
18. **Dependency provenance is explicit.** Standalone inputs are version- and digest-pinned.

---

## 11. Ownership and recovery direction

The intended key separation is:

```text
RecallRoot
   |
   +-- domain-separated owner authority
   +-- controller delegation authority
   +-- local-data/recovery keys as separately specified

stable IoTox device identity
   |
   +-- current ownership epoch and authorization ledger
   +-- replaceable Tox/native endpoint binding
   +-- future replaceable Tox/Tor endpoint binding
   +-- future replaceable Tox/I2P endpoint binding
```

The permanent phrase is not a vendor master password. It is owner-held root material. A
printed copy may be permanent by design. The system must make this joy real without letting
the phrase become a daily bearer token.

Still unresolved:

- exact signing primitive and deterministic key derivation;
- device identity creation and storage;
- physical initial claim;
- fresh re-entry challenge transcript;
- ownership epoch transition;
- delegated controller enrollment;
- phrase compromise response;
- authorization record encoding and canonicalization;
- high-consequence device policy.

Until these are implemented and reviewed, IoTox remains a transport agent and research
system, not an authorization-complete appliance.

---

## 12. Network direction

### Tox/native

This is the current route and the next real-network gate. It should use as much c-toxcore as
makes sense: native UDP/DHT behavior, TCP relays, bootstrap discovery, toxcore savedata,
lossless packets, and file transfer.

### Tox/Tor

Reserved. Likely constraints include TCP-only toxcore behavior, disabled UDP, local
discovery, announcements, and hole punching, an explicit proxy path, reachable Tox TCP
relays, and leak tests proving no native DNS or socket fallback. These are hypotheses until
measured.

### Tox/I2P

Reserved and more experimental. A plausible fixture uses local stream tunnels and Tox TCP
bootstrap/relay endpoints reachable inside I2P. It requires reproducible endpoints,
reconnect measurements, and leak tests.

### Direct Tor or I2P

Separate future transports. They must not be confused with routing Tox over those networks.
The current enums and architecture reserve that distinction; no direct overlay transport is
implemented.

Identity linkability across routes remains an open design question. A stable IoTox device
identity may eventually bind separate route-specific Tox identities.

---

## 13. Ratox inheritance and deliberate departures

Ratox’s source demonstrates why the idea is worth preserving:

- peer state appears as ordinary files;
- input can be written through FIFOs;
- output can be tailed;
- a Tox identity becomes scriptable Unix I/O;
- the program is small enough to understand.

IoTox preserves:

```text
local-first operation
persistent self-owned Tox identity
small foreground service
private inspectable filesystem projection
scriptability
file transfer as a first-class Tox feature
few conceptual steps for ordinary work
```

IoTox deliberately replaces:

```text
one monolithic global-state source file
FIFOs as the authoritative application protocol
friendship as a tempting proxy for authority
unbounded or implicit queues
in-place state truncation
single/conflated transfer state
ambiguous command completion
permissive filesystem creation dependent on umask
build-time-only network policy
```

A future compatibility façade should feel like ratox while translating every operation into
the structured local core. The façade must not claim durable acceptance merely because a
writer successfully opened a FIFO.

---

## 14. Repository map

From `IoTox/.datacube/`:

```text
CMakeLists.txt                    product and test build graph
CMakePresets.json                 checked compiler/sanitizer configurations
include/iotox/                    public C++ boundaries
src/main.cpp                      one executable entry
src/cli.cpp                       agent and local-client command surface
src/agent.cpp                     runtime orchestration and event pump
src/toxcore/transport.cpp         one-owner-thread toxcore integration
src/toxcore/dynamic_library.cpp   runtime provider
src/toxcore/linked_api.cpp        source-linked provider
src/file_transfer.cpp             finite safe-path transfer manager
src/local/                        seqpacket protocol/socket and runtime tree
src/protocol/                     IoTox-over-Tox frame codec
src/security/                     RecallRoot research implementation
src/state_store.cpp               private atomic savedata replacement
tests/mock_toxcore.cpp            exact consumed ABI test double
tests/                            unit/integration/process/fuzz facilities
tools/build-standalone.sh         pinned source-linked product build
tools/build-matrix.sh             compiler and sanitizer matrix
tools/make-revision-archive.sh    clean timestamped datacube package
dependencies.lock                 immutable upstream input contract
docs/decisions/                   architecture decision records
docs/research/                    source-linked findings and retained evidence
docs/history/                     superseded lone entrances
incubator/mutorr/                 preserved non-default research
artifacts/                        retained binaries/reports/checksums
```

---

## 15. Immediate ordered work

Work from the top unless new evidence changes the order.

### Gate 1 — source-link official c-toxcore

On a connected command line:

- fetch the exact locked c-toxcore and libsodium archives;
- verify hashes;
- compile the source-linked provider against official headers;
- confirm the result contains no runtime `libtoxcore` or `libsodium` dependency;
- run `iotox --version` and `bootstrap-seeds`;
- retain build logs, compiler versions, dependency list, binary hash, and failures;
- repair assumptions exposed by official headers or linker behavior.

Acceptance: the named `iotox` binary is source-linked and independently verified by the
retained script.

### Gate 2 — real local two-peer native fixture

- run two isolated IoTox state/runtime roots;
- provide a controlled bootstrap and TCP relay or reproducible local Tox fixture;
- perform an explicit friend ceremony;
- exchange HELLO frames both ways;
- transfer finite files both ways;
- stop, restart, reconnect, and preserve identities;
- test UDP-enabled and relay-only modes separately;
- measure connection and recovery timing.

Acceptance: `Tox/native` becomes network-verified in the named fixture.

### Gate 3 — harden the ratox successor surface

- define stable multi-instance runtime naming;
- add a bounded watch/subscription facility rather than polling files;
- specify a minimal FIFO compatibility façade, if still valuable;
- make peer and transfer projections resilient to full disk and crash interruption;
- add explicit terminal transfer history or event IDs;
- add restart/resume policy for stable file IDs;
- test stale runtime occupants, abrupt clients, disk exhaustion, path races, and shutdown
  during each operation.

Acceptance: ordinary shell tools can use IoTox naturally while every failure remains
observable and correctly scoped.

### Gate 4 — authorization ledger skeleton

- choose application signing primitives;
- define stable device identity and endpoint bindings;
- define canonical owner/delegation/capability/epoch/revocation records;
- implement verification before any protected operation;
- fuzz all record decoders and transition rules.

Acceptance: an unprivileged Tox friend may connect but cannot perform a protected action.

### Gate 5 — durable command semantics

- bounded durable inbox/outbox;
- received, started, succeeded, failed, rejected, expired, and cancelled states;
- stable message IDs and duplicate-result cache;
- explicit deadline and clock/boot-epoch rules;
- power-loss and queue-full tests.

Acceptance: retrying a completed hardware command cannot accidentally repeat it.

### Gate 6 — RecallRoot re-entry

- domain-separated owner and delegation keys;
- no-argv phrase entry;
- device-bound fresh challenge;
- ownership epoch and revocation rules;
- physical initial claim;
- compromise and transition story;
- independent cryptographic review before consequential use.

Acceptance: the exact generated phrase can authorize a new delegated controller without
revealing the phrase/root and without a vendor service.

### Later

- signed OTA over Tox file transfer;
- owner-operated bootstrap/relay packaging and contribution tooling;
- target-hardware power, memory, traffic, and fault measurements;
- leak-tested Tox/Tor;
- experimental Tox/I2P;
- direct overlay transports only under separate ADRs;
- Mutorr reconsideration only after the ratox successor is strong.

---

## 16. Open questions that must remain visible

- Does c-toxcore 0.2.23 compile source-linked exactly as the current CMake provider assumes?
- Does the official release archive contain all vendored source expected by its CMake graph?
- What changes when two real peers, not the deterministic mock, drive file-control timing?
- Should outgoing transfers be projected as offered until peer resume rather than active?
- How should stable file IDs support restart/resume without exposing partial files?
- What terminal transfer history is useful without turning `/run` into a database?
- What is the smallest ratox FIFO façade that does not lie about acceptance or completion?
- How are multiple local users, containers, or service accounts admitted safely?
- What persistent store is small, inspectable, bounded, and power-loss-safe for commands?
- Which first hardware class can afford toxcore’s memory, descriptors, wakeups, and traffic?
- How are bootstrap lists updated without creating silent vendor sovereignty?
- Should route-specific Tox identities be distinct to reduce native/Tor/I2P linkability?
- What is the exact no-leak definition for Tox/Tor and Tox/I2P?
- What GPL-3.0 source-delivery process accompanies a shipped source-linked product?
- Which IoTox changes belong upstream rather than in a permanent private patch set?
- Which device classes are too consequential for this transport/application stack without
  independent security review?

Convert questions into experiments. Do not answer them with confidence theater.

---

## 17. Revision discipline

A good revision makes at least one difficult thing more truthful. More prose or a higher test
count is not automatically progress.

Before packaging:

```text
[ ] archive the previous BOOTSTRAPROSE under docs/history
[ ] rewrite this entrance to current truth
[ ] update REVISION, version, changelog, package, manifest, ADR index, and open questions
[ ] research current upstream primary sources and retain exact URLs/findings
[ ] run default GCC and Clang builds
[ ] run available sanitizer lanes
[ ] run the separate one-binary process fixture
[ ] run retained fuzz smoke lanes
[ ] build Mutorr preservation once if its files or shared boundaries changed
[ ] refresh prebuilt artifacts, reports, and SHA-256 checksums
[ ] prove only BOOTSTRAPROSE is ordinarily visible at the cube root
[ ] ensure no stale iotoxd product artifact survives
[ ] create the timestamped archive from a clean staging tree
[ ] extract the archive elsewhere and rerun its retained smoke facility
```

Archive filename contract, using America/New_York local package time:

```text
IoTox-rev####-YYYY.MM.DD.HH.MM-lowercase-hyphenated-summary-highlight-codename.zip
```

The archive contains one `IoTox/` root, this entrance, optional hidden root metadata such as
`.gitignore`, and `.datacube/`. It excludes Git metadata, build trees, dependency caches,
temporary identities, and editor debris. The delivered link text is the complete filename.

---

## 18. rev0005 amendment

rev0005 converts the product from two public executables into one `iotox` executable with
agent and local-client roles. It expands the toxcore seam to friendship lifecycle and the
official file-transfer API, adds bounded owner/event semantics, separates mutation saves
from shutdown saves, introduces source-linked and dynamic toxcore providers, and prepares a
pinned standalone build path.

It adds a finite regular-file transfer manager with paused incoming offers, bounded offer
capacity, immutable outgoing snapshots, exact chunk handling, private temporary files,
no-clobber publication, empty-file behavior, live runtime projection, and process-level
coverage in both directions.

The retained matrix passes GCC debug and release, Clang debug, Clang ASan/UBSan,
GCC ThreadSanitizer, both 5,000-run Clang fuzzer smokes, and the Mutorr preservation
lane. ThreadSanitizer first found a fixture race caused by concurrent environment access;
the mock now freezes its configuration at `tox_new`, and the repaired lane passes.

It does **not** claim a real c-toxcore build or a real Tox network connection in this
container. Those remain the first external gates.
