# BOOTSTRAPROSE — IoTox rev0006, “One Binary Speaks”

```text
project:       IoTox
revision:      rev0006
version:       0.6.0
codename:      One Binary Speaks
northstar:     a one-binary, self-owned, modern ratox successor
current proof: C++20 adapter/process behavior against an exact c-toxcore ABI mock
not yet proof: official source-linked build or real Tox-network behavior
```

This is the lone entrance.

Every ordinary root object except this prose is intentionally absent. The complete buildable
repository is hidden under `.datacube/`. That is an entrance and governance design, not a
security boundary. Enter there only after reading enough of this file to know what you are
changing and which claims are permitted.

The office holder may—and should—rewrite this document thoroughly. Preserve decisions and
provenance in their ledgers; do not preserve stale prose merely because it is old. There is
no maximum useful length. There is a minimum duty: a competent person waking with no memory
must be able to recover the project’s purpose, state, operation, constraints, evidence, and
next work from this entrance.

The governing aesthetic is:

> Concision where a sentence will do. Precision where a mistake would lie. Enough depth that
> amnesia does not become project death.

---

## 0. `/run` — assume the office

When instructed to `/run` this file, act in this order.

### 0.1 Establish where you are

```sh
cd IoTox
find . -mindepth 1 -maxdepth 1 -printf '%f\n' | sort
cat .datacube/REVISION
```

Expected ordinary visible root object:

```text
BOOTSTRAPROSE.md
```

Expected hidden working objects:

```text
.datacube
.gitignore
```

Expected revision:

```text
rev0006
```

If those facts differ, reality wins. Investigate before repeating this document’s claims.

### 0.2 Read the governing records

```sh
cd .datacube
cat REVISION
cat MANIFEST.md
cat docs/decisions/README.md
cat docs/testing.md
cat docs/roadmap.md
cat docs/research/sources.md
```

Read individual ADRs before reversing an accepted decision. Historical decisions are not
silently rewritten. A changed decision receives a new ADR naming what it supersedes.

### 0.3 Build the owned code

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel
ctest --preset gcc-debug --output-on-failure
```

Then run the operator fixture:

```sh
./tools/run-mock-node.sh gcc-debug
```

The fixture launches the actual product executable as an agent and uses the same executable
for control. It is not a simulated CLI transcript. It crosses a real Unix socket and a real
loadable C ABI boundary. The network behind that ABI is still a deterministic mock.

### 0.4 Inspect the product, not only the tests

```sh
./build/gcc-debug/iotox --version
./build/gcc-debug/iotox --help
```

Read these implementation seams:

```text
include/iotox/transport.hpp
src/toxcore/transport.cpp
src/agent.cpp
src/cli.cpp
include/iotox/local/control_protocol.hpp
src/local/runtime_tree.cpp
include/iotox/protocol/frame.hpp
src/file_transfer.cpp
```

Tests can prove that an existing implementation behaves as asserted. They cannot substitute
for constructing missing product behavior. This office is explicitly authorized to write the
best plausible implementation before real toxcore/network access exists, provided every
claim retains its correct evidence label.

### 0.5 Preserve evidence classes

Use the strongest honest label, never the most flattering label:

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

A source reading is not a runtime test. A mock pass is not a Tox-network pass. A linked build
is not NAT traversal. A successful packet queue is not physical execution.

### 0.6 Leave a complete cube

Before packaging a new revision:

1. advance actual product code, not only harnesses;
2. update this entrance and the decision/research ledgers;
3. run the strongest available matrix;
4. retain exact reports and convenience artifacts;
5. update checksums;
6. enforce the lone-entrance shape;
7. archive with the required revision filename;
8. inspect the archive after creation.

---

## 1. The thing being made

IoTox is a self-owned Tox device agent and a stronger ratox successor.

It is not a vendor cloud. It is not a new peer network pretending Tox does not exist. It is
not a distributed-storage research project with a small client attached. The immediate
product is one executable that turns Tox into an ordinary, scriptable local surface and then
adds the semantics physical devices require above transport friendship.

The long product sentence is:

> From memory, you can reach your devices; from an ordinary shell, you can understand and
> operate them.

The outside should be simple:

```text
run
show identity and connection
request or accept a peer
name a peer by public key
message or act
watch a journal
send or receive a file
send structured device traffic
stop and restart without losing identity
```

The inside must be explicit:

```text
one toxcore owner thread
versioned local requests
bounded queues and decoders
atomic state
independent authorization
ownership epochs and revocation
durable command lifecycle
expiry, replay handling, and idempotency
safe files and signed updates
explicit route policy
```

The purpose of internal rigor is to let the surface remain ordinary without lying about what
happened.

---

## 2. Decisions in force

These are not casual preferences. Their full records live in `.datacube/docs/decisions/`.

### 2.1 Tox stays primary

Tox is the connection fabric. It supplies long-term transport identities, encrypted peer
sessions, NAT traversal, bootstrap discovery, TCP relays, friendship, human messages,
reliable custom packets, and file transfer.

Sentiment alone is not proof, but the project values Tox because it works, composes, and has a
real network. IoTox should contribute fixes, server capacity, deployment tooling, and
transparent infrastructure governance where practical.

Tox is not the entire root of product authority. IoTox adds that above it.

### 2.2 The installed product is one executable

```text
iotox run ...
iotox status
iotox message ...
iotox file-send ...
```

Internal static libraries, mocks, fuzzers, and test executables are allowed. A second public
daemon/client binary is not the intended product shape.

### 2.3 C++20 owns the product

IoTox-owned product and test code is C++20. External C remains behind narrow ABI adapters.
GCC and Clang are first-class build lanes. Warnings are errors.

### 2.4 One thread owns each `Tox*`

No service calls toxcore directly. One owner thread serializes lifecycle, friendship,
profile, messaging, packets, files, savedata, bootstrap, and relay operations. Callbacks are
normalized into bounded C++ events.

### 2.5 Source-linked standalone is the product direction

The intended final product links a pinned c-toxcore and its required dependencies into the
one executable’s dependency graph. Runtime loading remains useful for exact ABI mocks,
diagnostic overrides, and integration research.

Dynamic loading is an engineering seam, not a substitute for shipping a coherent product or
meeting c-toxcore’s license obligations.

### 2.6 Permanent RecallRoot remains

A fixed Argon2id derivation contract allows a strong generated phrase to reconstruct owner
root material.

This intentionally permits offline password guessing. Therefore phrase entropy, generated
word count, ceremony, and domain separation are structural security requirements, not
optional advice.

The joy is deliberate:

> From memory, you can reach your devices.

Do not replace the permanent generated phrase with an expiring factory token merely because
that would simplify one threat model.

### 2.7 No IoTox/vendor reassignment sovereign

The project must not possess a key capable of reassigning customer devices. Infrastructure,
software updates, bootstrap lists, or support services must not secretly become ownership.

### 2.8 Authorization is independent of Tox friendship

A Tox friend is a transport peer. Friendship, public key, nickname, status, text, typing,
receipt, relay use, or bootstrap service grants no owner role, actuator capability, firmware
authority, or factory-reset power.

IoTox needs an independent ledger containing roles, capabilities, epochs, delegation, and
revocation.

### 2.9 Native Tox first; routed alternatives reserved

```text
Tox/native     current enabled route
Tox/Tor        future Tox route, reserved, fail closed
Tox/I2P        future Tox route, reserved, fail closed
Tor-direct     separate future transport
I2P-direct     separate future transport
```

A requested reserved route must never silently fall back to native networking.

### 2.10 Ratox successor is the immediate northstar

Mutorr remains preserved as optional namespace-replication research. It is disabled by
default and must not pull focus from identity, peers, profile, text, files, protocol,
authorization, recovery, and durable device commands.

### 2.11 Structured core; ratox façade

The primary local write contract is a bounded versioned `SOCK_SEQPACKET` protocol. The
runtime filesystem is a private read projection. Exact stdin forms provide ordinary Unix
composition today.

Writable ratox-compatible FIFOs may be added later as a façade that translates into explicit
requests and results. A FIFO must not become the authority or durable queue simply because it
is elegant.

### 2.12 Public-key-first peer selection

The Tox public key is the stable current operator handle. c-toxcore friend numbers are local
indices. Commands accept either, but documentation and durable scripts should prefer the
64-hex public key.

The public key is still a transport identity, not the future stable IoTox device identity.

### 2.13 Human text and IoTox device frames are separate lanes

Native Tox profile, presence, typing, normal text, action text, and read receipts form the
human/ratox lane.

IoTox reliable custom frames form the device-protocol lane.

A Tox read receipt says the peer received a Tox text message. It does not say a physical
command was authorized, durably accepted, executed once, or completed.

---

## 3. Current truth — rev0006

### 3.1 What is implemented

The repository contains C++20 implementations for:

- status/result vocabulary;
- network transport/route model;
- current c-toxcore 0.2.23 consumed ABI declarations;
- runtime-loaded and source-linked provider tables;
- exclusive toxcore owner thread;
- bounded command and event queues;
- startup options, savedata, bootstrap, and TCP-relay configuration;
- transport friendship request/accept/list/remove;
- self and peer profile/presence/typing behavior;
- normal/action text and read receipts;
- reliable raw custom-packet send/callback;
- strict IoTox frame encode/decode;
- finite native Tox file-transfer manager;
- private same-user local control;
- private ratox-inspired runtime projection;
- event, human-message, and decoded-protocol journals;
- one-binary CLI and foreground agent;
- RecallRoot-v1 research implementation and exact Argon2 ABI mock;
- compiler, sanitizer, process, fuzz, and preservation facilities.

### 3.2 What is process-tested

Against the exact loadable toxcore mock, the actual product executable has demonstrated:

```text
start and local socket admission
create and persist a Tox identity
stop and restart with the same address
accept, list, persist, and remove a friend
select that friend by public key
set and persist self name, status message, and presence
preserve embedded NUL in a profile field
pipe an action containing NUL and newline through stdin
observe outgoing, echoed incoming, and receipt text records
set typing state
encode, queue, echo, decode, and journal an IoTox HELLO
send and receive finite files by public-key selector
project and retire transfer state
keep global event payloads private
```

### 3.3 What is not proven

This cube has not:

- compiled the official c-toxcore release source;
- started a real c-toxcore peer;
- used DHT/public bootstrap, NAT traversal, or a real TCP relay;
- proven Tox cryptography or upstream memory safety;
- exchanged real text, packets, or files;
- tested reconnect/congestion/malicious timing;
- routed Tox through Tor or I2P;
- implemented the authorization ledger;
- implemented RecallRoot network re-entry;
- implemented durable physical-command semantics;
- qualified target hardware.

The strongest honest transport claim is **adapter-verified and process-tested against an
exact consumed-ABI mock**.

### 3.4 Why implementation continues anyway

The absence of real toxcore in this cloudtainer is not a command to stop coding. Primary
source contracts, exact ABI boundaries, deterministic process tests, and clear module seams
let the project construct the likely-correct program now. Later command-line work must
compile, debug, and correct it against upstream reality.

Do not confuse humility about evidence with passivity about construction.

---

## 4. The one-binary surface

Run:

```sh
.datacube/build/gcc-debug/iotox --help
```

The current main groups are below.

### 4.1 Agent

```sh
iotox run \
  --library /path/to/libtoxcore.so \
  --state /private/path/device.toxsave \
  --runtime /private/path/run
```

A source-linked build omits `--library`. Useful agent controls include:

```text
--network tox/native
--bootstrap HOST:PORT:PUBLIC_KEY
--tcp-relay HOST:PORT:PUBLIC_KEY
--no-default-bootstrap
--no-default-relays
--bootstrap-retry-ms N
--owner-command-timeout-ms N
--max-pending-commands N
--max-pending-events N
--max-file-bytes N
--max-active-sends N
--max-active-receives N
--max-pending-file-offers N
--run-ms N
```

Agent mode stays foreground. A service manager may supervise it.

### 4.2 Basic inspection

```sh
iotox --runtime RUN ping
iotox --runtime RUN status
iotox --runtime RUN address
iotox --runtime RUN profile
iotox --runtime RUN peers
iotox --runtime RUN files
iotox --runtime RUN stop
```

### 4.3 Profile and presence

```sh
iotox --runtime RUN profile-name IoTox Device
iotox --runtime RUN profile-name-hex 496F546F78
printf '%s' 'IoTox Device' | iotox --runtime RUN profile-name-stdin

iotox --runtime RUN profile-status-message at home
iotox --runtime RUN profile-status-message-hex HEX
cat status.bin | iotox --runtime RUN profile-status-message-stdin

iotox --runtime RUN profile-status available|away|busy
```

Profile byte fields are bounded by the reviewed c-toxcore 0.2.23 maxima. They are Tox
presentation only.

### 4.4 Friendship

```sh
iotox --runtime RUN transport-peer-request TOX_ADDRESS_HEX MESSAGE
iotox --runtime RUN transport-peer-accept PUBLIC_KEY_HEX
iotox --runtime RUN transport-peer-remove PUBLIC_KEY_HEX
iotox --runtime RUN peers
```

`transport-peer-add` remains an accept compatibility alias. Acceptance establishes a Tox
friendship only.

Incoming requests are projected under `RUN/requests/<PUBLIC_KEY>/` for current inspection.
Full one-binary list/read/reject ergonomics remain an immediate ratox-surface task.

### 4.5 Human text and typing

```sh
iotox --runtime RUN message PUBLIC_KEY hello there
iotox --runtime RUN action PUBLIC_KEY waves
iotox --runtime RUN message-hex PUBLIC_KEY HEX
printf 'hello\0world\n' | iotox --runtime RUN action-stdin PUBLIC_KEY
iotox --runtime RUN typing PUBLIC_KEY on|off
```

The command returns the c-toxcore per-friend message ID for outgoing text. Incoming Tox text
does not carry the sender’s local outgoing ID. Receipts are transport receipts.

Read or follow the private peer journal:

```sh
iotox --runtime RUN peer-messages PUBLIC_KEY
iotox --runtime RUN --from-start --watch-ms 5000 peer-watch PUBLIC_KEY
```

### 4.6 IoTox lossless frames

Raw packet experiment:

```sh
iotox --runtime RUN transport-send PUBLIC_KEY PACKET_HEX
```

Current typed convenience:

```sh
iotox --runtime RUN transport-hello PUBLIC_KEY [TEXT]
```

The HELLO payload is still experimental text. The frame header is structured; the capability
payload contract is not yet frozen.

Read or follow valid decoded frames:

```sh
iotox --runtime RUN peer-protocol PUBLIC_KEY
iotox --runtime RUN --from-start --watch-ms 5000 \
  peer-protocol-watch PUBLIC_KEY
```

### 4.7 Finite files

```sh
iotox --runtime RUN file-send PUBLIC_KEY /absolute/or/normalized/path
iotox --runtime RUN file-receive PUBLIC_KEY FILE_NUMBER DESTINATION
iotox --runtime RUN file-cancel PUBLIC_KEY FILE_NUMBER
iotox --runtime RUN files
```

Files use c-toxcore’s file-transfer API, not custom-packet fragmentation. Current safe policy
supports finite regular files only.

### 4.8 Journals

```sh
iotox --runtime RUN events
iotox --runtime RUN --from-start --watch-ms 5000 watch
```

The global event journal contains lifecycle metadata and does not copy message or packet
bodies. Human text and valid IoTox frames live in separate per-peer journals.

---

## 5. Runtime tree

Default roots follow local/XDG conventions where possible. An explicit absolute `--runtime`
path is recommended for tests and appliances.

A running tree resembles:

```text
RUN/
├── control.sock
├── status
├── address
├── events
├── events.previous
├── self/
│   ├── name
│   ├── name-bytes
│   ├── status-message
│   ├── status-message-bytes
│   └── status
├── peers/
│   └── <64-HEX-PUBLIC-KEY>/
│       ├── number
│       ├── public-key
│       ├── connection
│       ├── online
│       ├── name
│       ├── name-bytes
│       ├── status-message
│       ├── status-message-bytes
│       ├── status
│       ├── typing
│       ├── messages
│       ├── messages.previous
│       ├── protocol
│       └── protocol.previous
├── requests/
│   └── <PUBLIC-KEY>/
│       ├── public-key
│       ├── message
│       └── message-bytes
└── transfers/
    └── <direction>-<friend>-<file>/
        └── structured fields
```

### 5.1 Security properties

- root and directories are owner-only;
- regular projection files are private;
- runtime roots must be absolute and owned by the effective user;
- symlink substitution is rejected at critical openings;
- multi-file request/transfer records publish by complete-directory rename;
- journals are bounded and rotate to one previous segment;
- bytes are escaped so control characters cannot inject records;
- packet/message bodies are not copied into global events.

### 5.2 Semantics

The tree is observational. It is not the durable authorization ledger, device command queue,
or source of truth for delivery.

Messages and protocol journals are useful and sensitive. Future deployments need explicit
retention, redaction, and disablement policy.

### 5.3 Why no writable FIFO yet

A FIFO write cannot inherently answer:

```text
which request is this?
who authorized it?
when does it expire?
may it execute after the writer timed out?
was it persisted?
was it executed once?
where is the result?
```

Stdin already gives scripts an exact-byte pipe into the structured local request. Writable
ratox compatibility paths can arrive after the core can answer those questions.

---

## 6. Toxcore boundary

### 6.1 External API isolation

The adapter resolves or links only the consumed API. Product modules use C++ types such as:

```text
SelfProfile
TransportPeer
TransportEvent
ToxTransport
FileTransferRecord
```

They do not manipulate `Tox*` or raw callback registrations.

### 6.2 Current upstream target

```text
c-toxcore: 0.2.23
libsodium:  1.0.22
```

Pinned URLs and SHA-256 values live in:

```text
.datacube/dependencies.lock
.datacube/third_party/README.md
.datacube/docs/research/sources.md
```

The tagged c-toxcore release was source-reviewed again for rev0006. It was not compiled here.

### 6.3 Provider modes

```text
linked provider
    compile with IOTOX_TOXCORE_SOURCE_DIR
    populate the internal API table with direct function addresses
    intended product/standalone direction

runtime provider
    dlopen an explicit library
    populate the same API table with resolved symbols
    exact mock and integration-research direction
```

A linked build may still accept an explicit dynamic diagnostic override. This must not cause
two competing `Tox*` owners.

### 6.4 ABI caution

Use runtime size functions and official accessors. Do not assume copied constants or public
struct layouts are permanent ABI. Keep deprecated toxcore names hidden at compile time where
supported.

### 6.5 Upstream security posture

The current upstream project describes c-toxcore as experimental and not independently
formally audited. Its 0.2.23 release fixed a critical issue found during manual review and
other memory-safety defects.

Consequences:

- pin and monitor the dependency;
- retain a narrow boundary;
- fuzz all IoTox parsers;
- sandbox the product where possible;
- ship updates quickly;
- require application-level command authorization even inside Tox;
- do not market toxcore as a complete formal security proof.

---

## 7. Profile, human text, and receipts

### 7.1 Upstream limits reviewed for 0.2.23

```text
name:               128 bytes
status message:     1007 bytes
friend request:     921 bytes
normal/action text: 1372 bytes
custom packet:      1373 bytes total
```

IoTox validates the relevant runtime functions at transport startup and enforces the bounds
again at local control/CLI boundaries.

### 7.2 Byte preservation

Tox APIs carry bounded byte strings with explicit lengths. IoTox does not rely on C-string
termination. Hex and stdin forms may carry NUL and newline. Runtime raw files preserve bytes;
line journals escape them.

### 7.3 Message IDs

Outgoing c-toxcore text returns a per-friend `uint32_t` ID. The first may be zero; IDs
increment and can wrap. It is not a global IoTox command ID.

Journal directions are:

```text
outgoing  local message ID available
incoming  sender's local ID unavailable
receipt   local outgoing ID available
```

### 7.4 Authority boundary

A malicious friend may send text such as `unlock`. It remains human text. No actuator adapter
may parse ordinary Tox messages as authoritative device commands.

---

## 8. IoTox over-Tox protocol lane

### 8.1 Frame

IoTox currently reserves custom lossless discriminator `0xA0` and uses a 41-byte header:

```text
discriminator
protocol major / minor
message type
flags
payload length
message ID
correlation ID
sequence
expiry Unix milliseconds
payload
```

At the reviewed total packet maximum, payload is at most 1332 bytes.

### 8.2 Reserved semantic types

```text
HELLO
CAPABILITIES
COMMAND
COMMAND_RESULT
STATE_SNAPSHOT
STATE_EVENT
ACKNOWLEDGEMENT
ERROR
PAIR_REQUEST
PAIR_RESULT
REVOKE
OTA_MANIFEST
Mutorr incubator types
```

The frame codec knows these numbers. Most state machines do not yet exist.

### 8.3 Current observation behavior

- outgoing valid IoTox frames are journaled after toxcore accepts them for queueing;
- incoming `0xA0` packets are strictly decoded before protocol journaling;
- malformed candidates are not presented as valid IoTox messages;
- non-IoTox custom packets remain raw integration traffic;
- protocol journals are per peer and private;
- global events record only packet metadata.

### 8.4 What must come next

HELLO must stop being arbitrary text and become a compact canonical capability record. The
agent must negotiate once per online epoch, project compatibility, reject required-feature
mismatch, and defend against stale/downgrade transcripts.

Then device commands need:

```text
stable application identity
independent signatures/authorization
ownership epoch
durable inbox/outbox
unpredictable message ID
correlation
expiry or relative TTL
replay window
idempotency
RECEIVED / STARTED / SUCCEEDED / FAILED / EXPIRED
```

Reliable Tox delivery is necessary. It is not sufficient.

---

## 9. Finite file-transfer policy

The low-level adapter exposes c-toxcore offer, control, seek, file ID, chunk request, and
chunk send/receive behavior. The high-level manager adds local filesystem policy.

### 9.1 Outgoing

- finite regular file only;
- open without following the final symlink;
- freeze device, inode, size, and modification time;
- bound total size and active transfers;
- serve exact requested positions/lengths;
- cancel if the source changes;
- preserve full opaque file handles.

### 9.2 Incoming

- offer stays paused;
- explicit operator chooses a destination;
- destination parent must pass current ownership/type checks;
- create a private same-directory temporary file;
- enforce ordered bounded writes and exact final size;
- synchronize file and directory;
- publish without replacing an existing destination;
- clean up on failure/cancel.

### 9.3 Limits of current safety

- finite known-size data only;
- no restart-resume contract;
- no complete ancestor traversal with `openat2`/disciplined `openat` yet;
- no content hash/signature policy;
- no OTA authority or anti-rollback;
- no real peer/congestion testing.

Bulk IoTox objects and firmware should build on this transport only after manifests,
authorization, integrity, storage reservation, and safe activation exist.

---

## 10. Local control protocol

Current version:

```text
1.3
```

Transport:

```text
Unix SOCK_SEQPACKET
one packet = one request or response
same-user admission
24-byte fixed header
60 KiB maximum payload
```

Properties:

- explicit protocol version and operation;
- request ID and response correlation;
- exact payload length;
- structured status code and error text;
- bounded decode;
- no stream framing ambiguity;
- no direct toxcore access by the client process.

Current operations cover lifecycle, profile, friendship, text, typing, packets, and finite
files. The protocol is local and private, not the over-Tox IoTox protocol.

Before physical commands use it, re-audit:

- whether a local timeout can ever leave executable work behind;
- cancellation state;
- queue capacity/backpressure;
- shutdown draining;
- authorization context for multiple local principals;
- durable acceptance.

---

## 11. Ownership and recovery direction

### 11.1 Separate identities

The intended hierarchy distinguishes:

```text
RecallRoot / owner root
stable IoTox device identity
owner and delegated controller principals
Tox route endpoint identity or identities
local data-encryption keys
```

A Tox endpoint should eventually be replaceable without making the physical device a new
owned object.

### 11.2 Permanent phrase

The fixed RecallRoot-v1 Argon2id contract is preserved. It is not yet connected to the
running agent.

The eventual work must freeze:

- generated phrase policy;
- normalization and salt/domain contract;
- domain-separated key hierarchy;
- owner challenge-response;
- ownership epoch transition;
- replay and rollback protection;
- wrong-phrase behavior;
- controller replacement;
- physical destructive reset.

### 11.3 No vendor key

No design may smuggle an IoTox-controlled reassignment key into attestation, updates,
bootstrap service, password reset, or support tooling.

### 11.4 Recovery categories

Keep distinct:

```text
transport recovery      rotate/recreate a Tox endpoint
controller recovery     authorize a replacement controller
owner re-entry          reconstruct authority from RecallRoot
physical reset          return hardware to unowned state, erasing old private domain
```

A physical reset may restore use of hardware. It must not reveal the prior owner’s secrets.

---

## 12. Network direction

### 12.1 Tox/native

Immediate route. The next real gate is official source-linking and a controlled two-peer
fixture, including TCP-relay-only behavior.

### 12.2 Tox/Tor

Likely requires TCP-only toxcore operation, explicit proxy/tunnel behavior, known reachable
Tox relays/bootstrap endpoints, UDP/local-discovery disablement, and DNS/native-fallback leak
tests. It is not “set one proxy flag and trust.”

### 12.3 Tox/I2P

Likely requires explicit stream tunnels and Tox bootstrap/relay infrastructure reachable
inside I2P. Connection time, endpoint distribution, restart, memory, and leak behavior must
be measured.

### 12.4 Route identity

Reusing one Tox public key across native, Tor, and I2P improves continuity but links the
routes. Separate endpoint keys improve unlinkability but require an IoTox device identity to
bind them. This remains an explicit design question.

### 12.5 Owner-operated infrastructure

Owners should be able to operate bootstrap nodes, TCP relays, and later durable home hubs.
Infrastructure may improve reachability and offline queues without becoming authority.

---

## 13. Security invariants

Do not merge code that knowingly violates these without a new decision and explicit threat
analysis.

1. One thread owns one `Tox*`.
2. Tox friendship is never application authorization.
3. Human text is never silently interpreted as a device command.
4. A Tox receipt is never called command completion.
5. A reserved route never silently falls back.
6. No IoTox/vendor reassignment sovereign exists.
7. RecallRoot phrase strength is a product invariant because offline guessing is possible.
8. Local packets, network frames, paths, queues, transfers, and journals are bounded.
9. Persistent identity replacement is atomic and private.
10. Required semantic events do not disappear silently.
11. Observational event loss is counted.
12. Incoming files do not overwrite existing destinations.
13. Runtime projections are private and observational.
14. Global diagnostics do not copy human/protocol payloads by default.
15. Public keys identify Tox peers; friend numbers remain local details.
16. Evidence labels never exceed the test actually performed.

Future invariants must cover application signatures, ownership epochs, rollback resistance,
replay, durable acceptance, idempotency, signed OTA, and secure hardware use.

---

## 14. Verification facility

### 14.1 Current count

```text
48 registered C++ tests
7 default CTest entries
```

### 14.2 Retained lanes

```text
GCC debug
GCC release
Clang debug
Clang AddressSanitizer + UndefinedBehaviorSanitizer
GCC ThreadSanitizer
Clang frame libFuzzer
Clang local-control libFuzzer
Mutorr preservation build
one-binary process lifecycle
prebuilt artifact smoke
```

### 14.3 Important defects previously found by the facility

The test/sanitizer culture has already exposed real errors, including:

- an incorrect C++ function-pointer boundary in an earlier mock ABI;
- weaker temporary savedata naming/writing discipline;
- startup visibility ordering;
- mock environment races under ThreadSanitizer;
- an end-to-end observer deadline that was shorter than a loaded owner/callback/projection
  path, exposing the need to measure and batch transient runtime publication separately from
  durable saved identity;
- an operator fixture that configured by absolute source path but built a preset relative to
  the caller's directory; it now builds the known directory and works from arbitrary cwd.

Keep tests as instruments that find defects. Do not let “all green” become the product goal
when whole state machines remain unwritten.

### 14.4 Run everything available

```sh
./tools/build-matrix.sh
```

Fuzzers are built separately as documented in `.datacube/BUILDING.md`.

### 14.5 Prebuilt evidence

```sh
./artifacts/run-prebuilt-tests.sh
```

Prebuilt binaries are Linux x86-64 convenience evidence only. They are not portable or
production releases.

---

## 15. Repository map

All paths below are relative to `.datacube/`.

```text
CMakeLists.txt                 product/test build graph
CMakePresets.json              compiler/sanitizer lanes
REVISION                       machine-readable revision
include/iotox/                 public/internal C++ contracts
src/                           product implementation
tests/                         tests, exact ABI mocks, fuzz corpora
tools/                         build, fixture, dependency, packaging scripts
docs/decisions/                immutable decision ledger
docs/research/                 primary-source readings and evidence
docs/history/                  superseded lone entrances
docs/provenance/               imported branch provenance
incubator/mutorr/              optional preserved research
third_party/                   retained word list/licenses and source notes
artifacts/                     retained binaries, reports, checksums
MANIFEST.md                    exact current contents and claim boundary
CHANGELOG.md                   revision deltas
BUILDING.md                    build/operator commands
PACKAGE.md                     archive/distribution contract
LICENSE.md                     project-license status
```

The original rev0005 entrance is preserved at:

```text
docs/history/BOOTSTRAPROSE-rev0005.md
```

---

## 16. Immediate ordered work

Do not reorder these merely because a later feature is more exciting.

### Gate 1 — official source-linked c-toxcore

1. fetch and verify pinned archives;
2. compile upstream 0.2.23 with the prepared CMake path;
3. fix real header, target, and link mismatches;
4. verify `iotox` starts without `--library`;
5. record hashes, tools, link dependencies, and license/source-delivery obligations.

### Gate 2 — controlled two-real-peer native fixture

Exercise friendship, profile, text, receipts, HELLO, files, restart, disconnect/reconnect, and
TCP-relay-only mode. Keep public bootstrap/NAT claims separate from local controlled claims.

### Gate 3 — HELLO/capability session

Freeze a compact canonical payload. Send/receive it per online epoch. Project compatible
protocol range, features, and limits. Reject downgrade and required-feature mismatch.

### Gate 4 — independent authorization ledger

Choose signing/canonicalization. Implement stable device and principal identities, roles,
capabilities, ownership epochs, delegation, revocation, and rollback-resistant storage.
Connected-but-unauthorized must be a normal tested state.

### Gate 5 — durable command lifecycle

Persistent bounded queues, unpredictable IDs, correlation, TTL, replay protection,
idempotency, cancellation, and RECEIVED/STARTED/SUCCEEDED/FAILED/EXPIRED results.

No physical actuator integration is allowed to outrun this gate.

### Gate 6 — RecallRoot re-entry

Connect the frozen Argon2id contract to domain-separated owner authority and a tested
challenge/epoch transition. Preserve the permanent generated phrase and no-vendor-key rules.

### Gate 7 — fuller ratox surface

Incoming request commands, aliases, service files, FIFO compatibility with explicit result
channels, retention controls, and polished shell workflows.

### Later

Tox/Tor, Tox/I2P, owner-operated hub, signed OTA, target-device qualification, and optional
Mutorr namespace replication.

---

## 17. Questions that must remain visible

- Will official c-toxcore compile against the exact adapter as guessed?
- What canonical HELLO/capability payload is compact and downgrade resistant?
- Which signing primitive and ledger encoding should the product freeze?
- How does RecallRoot re-entry locate and authenticate existing devices without a vendor?
- How is ledger rollback resisted on ordinary Linux hardware?
- What clock model gives safe expiry after an RTC-less boot?
- Can timed-out local work ever execute later, and how will that be made impossible/visible?
- Which ratox FIFOs can honestly map to structured semantics?
- Should journals default to body, metadata-only, or disabled on privacy-critical devices?
- How will file path ancestors and restart resume be hardened?
- Can Tox/Tor and Tox/I2P be made provably fail-closed?
- Should route-specific Tox identities be bound to one stable IoTox device identity?
- Which target hardware class is first?
- What IoTox-owned license and GPL compliance model will be used?

Detailed form: `.datacube/docs/open-questions.md`.

---

## 18. Governance and revision discipline

### 18.1 Source of truth order

When sources conflict, use this order:

1. observed current code/build behavior;
2. accepted ADRs and exact pinned primary sources;
3. current manifest/testing reports;
4. this entrance;
5. older prose and historical plans.

Then repair the stale higher-level record. Do not leave contradiction knowingly.

### 18.2 BOOTSTRAP edit freedom

The office holder may compress, reorganize, or replace this prose. Required content is
functional, not ceremonial:

- project identity and northstar;
- decisions in force;
- exact current implementation;
- evidence boundary;
- build/run/operate path;
- security invariants;
- unresolved hazards;
- ordered next work;
- governance/provenance.

Archive the previous entrance before a substantial rewrite.

### 18.3 Revision contents

A meaningful new cube should include some combination of:

- product implementation;
- a newly frozen decision;
- corrected research;
- tests that exercise new behavior;
- retained reports/artifacts;
- an entrance that matches reality.

A revision that only changes the number is invalid.

### 18.4 Required archive name

```text
IoTox-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

Use America/New_York local time. Summary/codename words are lowercase and hyphenated. The
final response containing the cube uses the complete filename as its only link and provides
no other links.

### 18.5 Package command

From `.datacube/`:

```sh
./tools/make-revision-archive.sh \
  rev0006 \
  "$(TZ=America/New_York date +%Y.%m.%d.%H.%M)" \
  one-binary-speaks-public-key-protocol-journals \
  /mnt/data
```

Inspect the resulting ZIP before delivery.

---

## 19. rev0006 amendment — One Binary Speaks

The important change is not that more tests exist. The important change is that the product
now performs a coherent ratox-style human workflow and exposes the beginning of its device
protocol through the same executable.

Today the one binary can:

```text
own and preserve a Tox identity
own a presentation profile
accept and name transport peers by public key
send human normal/action messages
carry exact bytes from stdin
observe incoming text and receipts
project typing and peer presentation
send and receive finite files
encode and decode an IoTox HELLO
separate human and protocol journals
stop and restart without losing identity/profile/friends
```

That is implementation progress. It is still not the full product.

The next decisive step is not another mock abstraction. It is to compile the official pinned
c-toxcore source, correct every wrong guess, and run two real native peers. Immediately after
that, the structured HELLO must become a real capability session so the authorization and
durable-command layers have a trustworthy place to begin.

Keep the ratox beauty:

```text
one process
ordinary files
simple commands
public-key peer directories
pipes that just work
```

Strengthen the inside:

```text
explicit identity
explicit authority
explicit durability
explicit results
explicit failure
```

That is IoTox.
