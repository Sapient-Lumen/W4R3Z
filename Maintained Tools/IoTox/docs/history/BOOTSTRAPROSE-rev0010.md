# BOOTSTRAPROSE — IoTox rev0010, “Durable First Word”

```text
Project:            IoTox
Revision:           rev0010
Version:            0.10.0
Codename:           Durable First Word
Immediate north:    one-binary modern ratox successor
Current transport:  Tox over native networking
Current protocol:   HELLO, transcript confirmation, authority proof,
                    durable COMMAND receipt/result for device.describe
Current authority:  RecallRoot-derived owner principal plus signed local ledger
Owned product code: C++20
Public product:     one executable named iotox
Pinned target:      c-toxcore 0.2.23, libsodium 1.0.22, Argon2 20190702
Office timezone:    America/New_York
```

This is the lone entrance to the datacube and the office from which an amnesiac successor can
resume the work. It is not a plaque and it is not sacred text. The office holder is expected to
rewrite it thoroughly when code, evidence, decisions, hazards, or ordered work change.

The entrance has no maximum length. It has minimum duties:

```text
state what IoTox is
state what is implemented
state what is only designed
state what was actually exercised
state what cannot yet be claimed
preserve decisions in force
name hazards without euphemism
name the next executable work in order
show how to build, run, inspect, test, and package the cube
leave no hidden sovereign and no ambiguous grant of authority
```

Concision means removing duplication and vague comfort. It does not mean omitting a fact the
next office holder needs in order to make the correct change.

---

## 0. `/run` — wake from amnesia and assume the office

### 0.1 Establish the cube and the lone entrance

From the directory containing this file:

```sh
pwd
find . -mindepth 1 -maxdepth 1 -printf '%f\n' | sort
./.datacube/tools/check-lone-entrance.sh
```

The intended root is exactly:

```text
IoTox/
├── BOOTSTRAPROSE.md
├── .gitignore
└── .datacube/
```

`BOOTSTRAPROSE.md` must be the only ordinary visible object. `.datacube/` is hidden so the next
reader meets one governing entrance rather than a wall of files. Hidden does not mean secret.

Enter the repository and establish its compiled identity:

```sh
cd .datacube
cat REVISION
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
./build/gcc-debug/iotox --version
```

Expected:

```text
rev0010
IoTox 0.10.0 rev0010
```

Remove any accidental runtime state from the repository root before packaging. A developer run
belongs in a temporary working directory, not beside source.

### 0.2 Reconstruct truth in authority order

Do not trust an assistant summary, a changelog, or memory over current code and retained
results. Read in this order:

1. compiled source and exact tests;
2. accepted ADRs not explicitly superseded by later ADRs;
3. this entrance;
4. current architecture, protocol, threat, testing, and roadmap documents;
5. current research and retained build evidence;
6. historical entrances and old revision cubes.

Start here:

```sh
sed -n '1,280p' README.md
sed -n '1,360p' MANIFEST.md
sed -n '1,420p' docs/architecture.md
sed -n '1,420p' docs/protocol-session.md
sed -n '1,420p' docs/protocol-command-v1.md
sed -n '1,420p' docs/protocol-authority-v1.md
sed -n '1,420p' docs/threat-model-draft.md
sed -n '1,360p' docs/testing.md
sed -n '1,360p' docs/roadmap.md
sed -n '1,300p' docs/open-questions.md
sed -n '1,280p' docs/decisions/README.md
sed -n '1,320p' docs/research/cloudtainer-build-report.md
```

Then inspect the implementation being changed. No prose permission makes code exist, and no
exact mock makes a public Tox route network-verified.

### 0.3 Build and run the owned implementation

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

The default suite has eight CTest entries. The unit/integration executable registers 88 C++
checks. Warnings are errors.

Inspect the single product executable:

```sh
./build/gcc-debug/iotox --version
./build/gcc-debug/iotox --help
./build/gcc-debug/iotox bootstrap-seeds
```

The install surface is one public executable named `iotox`. Test doubles and test executables
exist only inside build/evidence trees.

### 0.4 Run the one-binary product fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

This starts the real `iotox run` process and uses the same executable as the local operator. It
crosses:

```text
one CLI/product binary
Unix SOCK_SEQPACKET control
bounded agent command queue
one toxcore owner thread
exact shared-library C ABI mock
callbacks and bounded event queue
canonical HELLO and mutual transcript confirmation
bidirectional transcript-bound stable-principal proof
signed local authority ledger decision
persistent signed command journal
ratox-style journals and transactional projections
atomic savedata, stable device identity, authority ledger, and command store
orderly stop, reload, and identity/command continuity
```

The exact mock is another signed IoTox peer, not an echo. The fixture deliberately injects
c-toxcore `SENDQ` pressure. A successful run requires exact frozen retry, receipt/result
correlation, restart-stable sender epoch, and replay of already committed terminal evidence.

### 0.5 Run the quality matrix

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh |& tee /tmp/iotox-rev0010-matrix.log
```

The script takes an exclusive `flock` on `build/.matrix.lock` before any clean step. A second
matrix exits with status 75 instead of deleting or rebuilding another verifier's active tree. Do
not bypass the lock; use a copied worktree when two independent matrices are genuinely required.

The matrix covers:

```text
GCC debug
GCC release
Clang debug
Clang AddressSanitizer + UndefinedBehaviorSanitizer
GCC ThreadSanitizer
five Clang libFuzzer smoke targets
system-linked Argon2 provider lane
Mutorr preservation build and tests
```

Retained rev0010 result in this cloudtainer:

```text
GCC debug/release:             8/8 + 8/8 CTest entries passed
Clang debug/ASan+UBSan:        8/8 + 8/8 CTest entries passed
GCC ThreadSanitizer:           8/8 CTest entries passed
five Clang fuzz targets:       25,000 total units completed
system-linked Argon2:          8/8 CTest entries passed
Mutorr preservation:          10/10 CTest entries passed
matrix exit:                   0
```

The Clang fuzzer links emitted a host `.eh_frame_hdr` warning for the packaged fuzzer runtime;
each target still linked and completed its bounded run. Preserve the exact log rather than
rewriting that platform fact as either silence or a product failure.

Do not suppress a compiler, sanitizer, race, or fuzzer finding merely to make a lane green.
Correct the program, narrow the claim, or retain the exact platform limitation.

### 0.6 Attempt the product-shaped dependency build

On a networked command line:

```sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
./dist/standalone/iotox --version
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
```

That path verifies immutable source archives in `dependencies.lock`, builds pinned libsodium,
Argon2, and c-toxcore, compiles the linked provider against official toxcore headers, installs
one product executable, and prepares two genuine Tox peers.

This cloudtainer has not completed the official source-linked or real-peer lane because its
shell cannot resolve the required archive hosts. That is an evidence boundary, not a reason to
stop constructing the program.

### 0.7 Inspect a running node

Use a temporary working directory:

```sh
work=$(mktemp -d)
./build/gcc-debug/iotox run \
  --state "$work/tox.save" \
  --identity "$work/device.identity" \
  --authority "$work/authority.ledger" \
  --command-store "$work/commands.store" \
  --runtime "$work/run"
```

From another terminal:

```sh
./build/gcc-debug/iotox --runtime "$work/run" status
./build/gcc-debug/iotox --runtime "$work/run" address
./build/gcc-debug/iotox --runtime "$work/run" identity
./build/gcc-debug/iotox --runtime "$work/run" authority
./build/gcc-debug/iotox --runtime "$work/run" sessions
./build/gcc-debug/iotox --runtime "$work/run" command-store
```

Peer-facing examples:

```sh
./build/gcc-debug/iotox --runtime "$work/run" peers
./build/gcc-debug/iotox --runtime "$work/run" authority-session FRIEND
./build/gcc-debug/iotox --runtime "$work/run" command FRIEND device.describe
./build/gcc-debug/iotox --runtime "$work/run" peer-description FRIEND
./build/gcc-debug/iotox --runtime "$work/run" \
  command-record outgoing PEER_PUBLIC_KEY_HEX SENDER_EPOCH MESSAGE_ID
```

The operator surface is intentionally ordinary. The persistent semantics beneath it are not.

### 0.8 Refresh evidence and package only after verification

```sh
./tools/refresh-retained-artifacts.sh /tmp/iotox-rev0010-matrix.log
./artifacts/run-prebuilt-tests.sh
(cd artifacts && sha256sum -c SHA256SUMS)
./tools/check-lone-entrance.sh
```

Package from the repository root:

```sh
./.datacube/tools/make-revision-archive.sh \
  rev0010 \
  "$(TZ=America/New_York date +%Y.%m.%d.%H.%M)" \
  durable-first-word-exact-receipts-restart-journal
```

The archive name is part of the handoff contract:

```text
IoTox-rev####-YYYY.MM.DD.HH.MM-summary-highlight-codename.zip
```

---

## 1. What IoTox is

IoTox is a C++20, one-binary, self-owned device agent and modern ratox successor built with Tox
as its primary connection fabric.

The product thesis is:

> A physical thing should own its network identity, obey an owner-defined authorization ledger,
> remain locally useful without a vendor cloud, and be operable through an interface as ordinary
> as files, streams, and one command-line executable.

The permanent recovery thesis is:

> From memory, you can reach your devices.

The permanent generated phrase is intentionally reproducible. The fixed Argon2id derivation
contract therefore permits offline guessing. Phrase strength is structural, not optional. There
is no IoTox vendor key capable of assigning or reassigning a customer's device.

Tox is kept because it already supplies difficult connection machinery: long-term peer keys,
encrypted sessions, bootstrap discovery, DHT behavior, NAT traversal, TCP relays, lossless
custom packets, and file transfer. IoTox does not ask Tox friendship to define ownership.

## 2. Product axioms in force

```text
One public product executable: iotox.
Tox is the primary connection fabric.
Tox friendship is transport, never authority.
IoTox authority lives in an independent signed ledger.
RecallRoot-v1 remains permanent and reproducible.
No IoTox-controlled key may reassign a customer device.
The ratox successor is the immediate northstar.
The outside should be ordinary; the inside must tell the truth.
No physical effect may rely on transport enqueue alone.
An explicitly selected privacy route must fail closed rather than leak natively.
```

These are decisions, not marketing suggestions. Changing one requires a new ADR that states what
is superseded and why.

## 3. What rev0010 actually constructs

### 3.1 One product, one toxcore owner

All IoTox-owned implementation and tests are C++20. `iotox run` and every local operator command
live in the same executable. One thread owns each `Tox*`; other product code submits bounded
operations and receives normalized events.

The runtime provider can load c-toxcore dynamically for research and exact ABI testing. The
product-shaped path builds and links the pinned source. Both routes share one internal API table
so the rest of IoTox does not depend on toxcore call sites.

### 3.2 Ratox inheritance

IoTox keeps ratox's best idea: make peer networking feel like ordinary Unix I/O.

Current local surfaces include:

```text
one private SOCK_SEQPACKET control socket
one CLI executable for daemon and operator work
private status and peer projections
byte-preserving message/protocol journals
transactional request, transfer, authority, session, and command records
public-key-first peer selection
standard input for pipeline-friendly writes
```

The structured socket is constitutional. The runtime tree is a replaceable projection. Future
FIFO/watch compatibility should translate into the same typed operations; a FIFO must never be
mistaken for a durable queue or authorization boundary.

### 3.3 Identity and authority

IoTox separates:

```text
RecallRoot-v1
    permanent generated phrase -> deterministic owner Ed25519 principal

stable device identity
    random Ed25519 principal stored independently of Tox savedata

Tox route identity
    current c-toxcore profile/address/session identity
```

A confirmed IoTox session proves protocol agreement. Directional challenge/proof binds a stable
principal to that exact transcript and online epoch. The local signed authority ledger decides
roles and capabilities. Friendship, transcript confirmation, and authority are separate states.

### 3.4 Durable first word

rev0010 turns the first harmless machine operation, `device.describe`, from a transient exchange
into a restart-stable command transaction.

The durable command identity is:

```text
direction
remote Tox public key
persistent nonzero sender epoch
sender-chosen message id
```

The local sender epoch survives process restart. Tox friend numbers and online epochs do not
form command identity.

For an outgoing durable request, IoTox now performs:

```text
reserve one canonical COMMAND frame
commit the exact bytes to the signed command store
record the send attempt
ask toxcore to enqueue those exact bytes
on retryable SENDQ, retry the same frame and logical id
commit peer receipt and final result as they arrive
resume unfinished work after restart or reconnect
```

For an incoming durable request, IoTox performs:

```text
validate session, framing, sender epoch, and operation
commit the canonical request before acknowledging it
freeze and commit an exact RECEIVED receipt
apply the current authority decision and freeze its ledger head
commit STARTED before execution
execute only the harmless read-only device.describe operation
commit the exact terminal result before sending it
on an exact duplicate, replay the frozen receipt/result
on conflicting reuse of the same durable key, reject it
```

`RECEIVED` means the request is in the local durable store. It does not mean authorized, started,
or succeeded. Tox queue acceptance means only that toxcore accepted a packet into its local send
queue. It does not mean the peer persisted or executed the command.

### 3.5 Persistent command store

`commands.store` is:

```text
private regular file, current user only
bounded by record count and total bytes
atomically replaced and fsynced
signed by the stable device identity
strictly decoded with duplicate and transition checks
keyed independently of process-local toxcore friend numbers
projected read-only into the ratox-style runtime tree
```

The current defaults are 1,024 records and 8 MiB. When full, only the oldest terminal records
are eligible for pruning. If no terminal record can be removed, admission fails rather than
silently losing unfinished work.

Lifecycle is monotonic:

```text
outgoing: reserved -> locally-queued -> succeeded|failed|expired
incoming: received -> admitted -> started -> succeeded|failed|expired
```

Receipt and result delivery state is separately monotonic. Terminal command outcome cannot be
rewritten into another outcome.

The store is signed, not encrypted. It protects integrity against undetected ordinary file
modification but does not hide metadata or payloads from a local reader. Whole-file rollback by
an attacker able to replace old valid state is not yet prevented.

The current implementation rewrites and fsyncs the complete bounded snapshot on every mutation.
That is an intentionally simple correctness baseline, not the final flash-wear or high-throughput
format.

### 3.6 Current wire operation

The only machine operation is still:

```text
device.describe
```

It requires `read.telemetry`, has fixed bounded encodings, and returns one principal-bound device
description. It cannot change a setting, move an actuator, install firmware, delete data, or
transfer ownership.

That restriction is deliberate. rev0010 establishes durable identity, admission order,
deduplication, receipts, result retention, and restart recovery. Cancellation, trustworthy
expiry, effect-specific idempotency, storage reservation, and safety policy remain prerequisites
for physical effects.

## 4. Evidence maturity

Use the narrowest claim supported by retained evidence.

```text
C++ source and GCC/Clang build:                    compiled
command protocol/store direct tests:              unit-verified
runtime c-toxcore boundary against exact mock:    adapter-verified
one-binary durable process lifecycle:             binary-verified
sanitizer, race, and bounded fuzz matrix:          retained-green
system-linked Argon2 provider lane:                provider-verified
Tox/native on genuine c-toxcore peers:            not yet network-verified
Tox/Tor and Tox/I2P:                              reserved, fail-closed
physical effects, OTA, production hardening:      not claimed
```

The exact-mock fixture proves owned process semantics and the c-toxcore API boundary it models.
It does not prove DHT bootstrap, NAT traversal, relay behavior, public-network availability,
route containment, or compatibility with the official source build.

A passing sanitizer lane is evidence about executed paths, not proof of memory safety. A fuzzer
smoke run is evidence that its generated inputs did not find a crash, not proof that the parser
is complete or secure.

## 5. Current network model

```text
built first:                  IoTox protocol -> Tox -> native networking
reserved route:              IoTox protocol -> Tox -> Tor
reserved route:              IoTox protocol -> Tox -> I2P
separate possible future:    IoTox protocol -> direct Tor transport
separate possible future:    IoTox protocol -> direct I2P transport
```

Transport and route are distinct types. Tor or I2P as a route for Tox is not the same thing as
replacing Tox with a direct overlay transport.

Native Tox comes first. Future Tor likely requires explicit TCP-only/proxy policy, disabled
native fallback, DNS containment, and route-leak tests. I2P likely requires explicit stream
fixtures and reachable bootstrap/relay infrastructure inside the overlay. Neither route may be
advertised merely because toxcore exposes proxy or TCP options.

IoTox should make it straightforward for owners and the project to operate and contribute Tox
bootstrap and relay infrastructure. Operating a road never grants ownership authority over the
traffic using it.

## 6. Security and recovery boundary

### 6.1 Permanent phrase

The permanent phrase is a feature, not a temporary enrollment secret. A fixed Argon2id contract
reconstructs the same RecallRoot and stable owner principal. Offline guessing is therefore
possible by design. Generated entropy, word-list provenance, normalization, parameters, domain
separation, and test vectors are constitutional protocol material.

The daemon must not receive the phrase, RecallRoot, owner seed, or owner secret. Recall and
signing remain explicit local ceremonies.

### 6.2 No vendor sovereign

IoTox must not possess a key, account, or service capable of silently reassigning customer
devices. Manufacturer attestation may prove hardware provenance; it must not become ownership
recovery authority.

### 6.3 Independent ledger

The signed authorization ledger owns roles, capability grants, revocation, ownership epochs, and
future delegation. The transport friend list is not the authorization database.

### 6.4 Remaining recovery work

Re-entry from a phrase derives authority but does not by itself solve discovery, remote challenge,
ownership transfer, phrase compromise, ledger rollback, or a device whose local state is gone.
Those ceremonies require explicit protocol and storage decisions. Do not smuggle a vendor master
key into them.

## 7. Hazards that remain open

### Real toxcore

The official c-toxcore 0.2.23 source has not yet compiled or run inside this cloudtainer. The
source-linked tools are prepared. A networked CLI must execute them and correct any real API,
link, bootstrap, timing, or relay defects found.

c-toxcore 0.2.23 is retained because the June 2026 release fixes a remotely triggerable stack
buffer overflow in affected earlier versions. Dependency pinning and rapid update capability are
product requirements, not clerical work.

### Durable store rollback and confidentiality

A valid old signed snapshot can presently be substituted by a local attacker with file-replacement
ability. The journal is plaintext. Device-specific rollback anchors, hardware monotonic counters,
append-only checkpoints, encryption policy, backup, and recovery remain unresolved.

### Whole-snapshot writes

Every command transition replaces and fsyncs the complete bounded store. This makes the current
contract easy to audit but may be unsuitable for flash wear, high command volume, or large
payloads. A future append/checkpoint format must preserve exact duplicate and crash semantics.

### Time

Wall-clock timestamps are made nondecreasing inside a record, but command expiry is not safe on a
device with an untrusted clock. No physical command may depend on current expiry behavior until
issued-at, relative TTL, clock evidence, restart epochs, and replay windows are settled.

### Cancellation and physical effects

There is no mature cancellation protocol, effect reservation, compensation model, or per-operation
idempotency contract. A local API timeout must not mean an operation cannot later run. Physical
operations remain forbidden until their exact crash and retry semantics are specified and tested.

### Store and queue denial of service

Bounded storage prevents unbounded growth but creates admission pressure. Per-peer quotas,
priorities, authenticated rate limits, terminal retention, operator alerts, and disk-full behavior
need stronger policy.

### Source size and decomposition

`agent.cpp` remains large. It now contains enough proven behavior to justify extraction of a
command engine, session coordinator, and projection adapters without changing public semantics.
Refactor by preserved tests and narrow ownership boundaries, not aesthetic churn.

## 8. Code map

```text
include/iotox/, src/
    owned C++20 product implementation

src/main.cpp, src/cli.cpp
    the single public executable and local operator surface

src/agent.cpp
    current one-process coordinator; extraction target, not an excuse to fork products

include/iotox/command_store.hpp, src/command_store.cpp
    signed bounded durable command state

include/iotox/protocol/, src/protocol/
    bounded canonical wire records

include/iotox/security/, src/security/
    RecallRoot, device identity, authority ledger, transcript proof

include/iotox/toxcore/, src/toxcore/
    narrow owner-thread c-toxcore boundary and bootstrap policy

include/iotox/local/, src/local/
    SOCK_SEQPACKET control and replaceable ratox-style projections

tests/mock_toxcore.cpp
    exact in-process c-toxcore ABI peer fixture, not a network implementation

tests/test_cli_process.cpp
    one-binary lifecycle and restart evidence

tools/build-standalone.sh, tools/run-real-peer-smoke.sh
    official source-linked and genuine-peer gates for a networked CLI

incubator/mutorr/
    preserved optional research; not the immediate product path

artifacts/
    retained binaries and exact evidence from the most recent verified matrix
```

## 9. Ordered executable work

The immediate northstar remains the ratox successor. rev0010 now has the first generic writable
one-binary entrance:

```text
iotox command FRIEND device.describe
```

It resolves a registered operation, reserves one durable identity, commits exact bytes, and returns
its inspectable record. `device-describe` remains a compatibility alias. This is real product
surface, but only one harmless operation is registered and the filesystem side is still read-only.

### Gate A — extract the durable command engine from the coordinator

The operation registry is present. The next step is to make it own protocol mechanics rather than
leaving those mechanics spread through `agent.cpp`.

Acceptance:

```text
one incoming admission/replay state machine serves every operation
one outgoing reservation/retry/result state machine serves every operation
operation handlers receive validated bounded inputs and return typed terminal evidence
per-operation capability, read/write class, expiry, idempotency, and restart policy are explicit
request identity and exact bytes remain frozen across restart
no second product binary appears
existing device.describe and generic command evidence remain green
```

### Gate B — make the ratox-style write side ordinary

Add a filesystem/FIFO adapter over the same structured local-control operation, not a second queue:

```text
/run/iotox/peers/<public-key>/command
/run/iotox/commands/outgoing/<durable-key>/...
```

Acceptance:

```text
one local write produces or reports one durable key
status is followable through CLI and the runtime-tree record
partial, malformed, oversized, and unauthorized writes fail before transport
reconnect/restart does not create a second logical command
projection deletion or corruption cannot mutate the signed store
backpressure and abandoned writers have explicit behavior
```

The first new operation should remain harmless or purely local—bounded device metadata or test
state—not GPIO.

### Gate C — compile and cross two genuine native Tox peers

On a networked CLI:

```text
build pinned official dependencies
run two source-linked iotox nodes
request and accept friendship
confirm transcript both ways
prove stable principals both ways
complete durable device.describe and restart replay
exercise TCP relay and disconnect/reconnect
retain logs and exact versions
```

Correct real API and timing defects in the same architecture. Do not replace work with a note that
the container could not fetch sources.

### Gate D — owner re-entry and delegation protocol

Build a complete challenge/proof ceremony by which a phrase-reconstructed owner principal can
return without sending the phrase or owner secret to the daemon. Define discovery, freshness,
ledger mutation, revocation, ownership epoch, phrase compromise, and audit evidence.

### Gate E — safe mutable device state

Only after cancellation, relative expiry, replay, disk-full, effect idempotency, and power-cut
semantics are specified should IoTox admit a setting change. Physical actuation and OTA come later
still.

### Later — routed Tox and stewardship

Native Tox remains first. Add bootstrap/relay operation and contribution tooling. Treat Tox/Tor and
Tox/I2P as explicit leak-tested routes. Direct overlay transports remain separate future work.

Mutorr stays preserved in the incubator until the ratox successor earns a reason to pull it into the
product.

## 10. Governance rules for the office holder

```text
Do not claim more maturity than the evidence supports.
Do not make friendship authority.
Do not let the vendor become sovereign.
Do not weaken permanent RecallRoot because offline guessing is uncomfortable.
Do not expose a physical effect because a mock packet round-trip is green.
Do not silently fall back from a requested private route.
Do not add another public product binary to avoid integrating the one product.
Do not delete failed evidence; explain it and fix or narrow the claim.
Do not preserve this prose when it becomes stale; rewrite it.
```

A change is complete only when code, tests, active docs, ADRs, retained evidence, and this
entrance agree.

## 11. Current handoff sentence

IoTox rev0010 is a compiled C++20, one-binary ratox successor whose first authorized machine
operation now has persistent sender identity, signed bounded admission state, exact receipts,
terminal result retention, duplicate replay, and restart recovery across the full exact-mock
process fixture. It is not yet a genuine Tox-network result or a safe actuator platform. The
next correct move is to extract the working generic `command` path into a reusable durable engine
and complete its ordinary ratox-style filesystem/FIFO write adapter, while preserving the
one-binary, commit-before-transport, and no-hidden-sovereign rules.
