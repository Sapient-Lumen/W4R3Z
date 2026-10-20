# BOOTSTRAPROSE — IoTox rev0014, “Ordinary Friendship”

```text
Project:              IoTox
Revision:             rev0014
Version:              0.14.0
Codename:             Ordinary Friendship
Immediate northstar:  one-binary modern ratox successor
Public product:       one executable named iotox
Owned product code:   C++20
Primary transport:    Tox over native networking
Pinned toxcore:       c-toxcore 0.2.23
Current friendship:   outgoing request; live request accept/reject; established remove
Current peer writes:  remove; message, action, command, file-send, file-receive, file-control
Current machine op:   read-only device.describe
Current authority:    permanent RecallRoot owner plus signed local authorization ledger
Current evidence:     exact consumed-ABI peer, separate processes, private filesystem, restart,
                      GCC/Clang, sanitizers, race detector, fuzzers
Unproved here:        official source-linked toxcore and two genuine Tox peers
Reserved routes:      Tox/Tor and Tox/I2P; fail closed and are not implemented
Office timezone:      America/New_York
```

This is the lone entrance to the datacube and the office from which IoTox wakes after total amnesia.
It is not sacred text. The office holder is free and expected to rewrite it thoroughly when code,
evidence, decisions, hazards, or priorities change.

There is no maximum length. There are minimum duties:

```text
state what IoTox is
state what executable code exists
state what is only designed, reserved, or unproved
state what was actually exercised
preserve accepted decisions until explicitly superseded
name hazards without euphemism
name the next executable work in order
show how to build, run, inspect, test, and package the cube
leave no hidden sovereign and no ambiguous grant of authority
```

Concision means removing repetition, ceremony, and imprecision. It does not mean omitting a fact the
next office holder needs in order to make the right change.

---

## 0. `/run` — wake, establish truth, and assume the office

### 0.1 Verify the lone entrance

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

`BOOTSTRAPROSE.md` is the only ordinary visible object. `.datacube/` is hidden to make the first
encounter one governing entrance rather than a source-tree wall. Hidden does not mean secret.

Do not create mutable runtime state at the cube root. Tox savedata, device identities, authority
ledgers, command stores, sockets, FIFOs, journals, staging files, and received files belong in a
disposable development directory or an explicit installation state directory. `Agent::start()`
refuses an empty savedata path before creating dependent durable state.

### 0.2 Establish compiled identity from a clean build

```sh
cd .datacube
cat REVISION
rm -rf build/gcc-debug
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
./build/gcc-debug/iotox --version
```

Expected:

```text
rev0014
IoTox 0.14.0 rev0014
```

The clean removal is deliberate. rev0014 construction exposed a stale-object trap: old binaries and
process fixtures could appear green until a real rebuild revealed a revision mismatch. A retained
binary, CMake cache, or timestamp is evidence only for the source from which it was actually built.

The public install contract contains one executable: `iotox`. Internal static libraries, provider
doubles, test runners, process fixtures, fuzzers, and preserved incubator programs may exist in
build/evidence trees. They are not additional product programs.

### 0.3 Reconstruct truth in authority order

Never trust an assistant summary, changelog, old cube, retained binary, or memory over current code
and fresh results. Read in this order:

1. compiled source and exact tests;
2. accepted ADRs not explicitly superseded by later ADRs;
3. this entrance;
4. current architecture, protocol, threat, testing, and roadmap documents;
5. current research and retained build evidence;
6. historical entrances and old revision cubes.

Start here:

```sh
sed -n '1,420p' README.md
sed -n '1,360p' MANIFEST.md
sed -n '1,620p' docs/architecture.md
sed -n '1,320p' docs/ratox-friend-lifecycle-v1.md
sed -n '1,460p' docs/ratox-message-fifo-v1.md
sed -n '1,420p' docs/ratox-command-fifo-v1.md
sed -n '1,520p' docs/ratox-file-fifo-v1.md
sed -n '1,460p' docs/protocol-session.md
sed -n '1,460p' docs/protocol-authority-v1.md
sed -n '1,500p' docs/protocol-command-v1.md
sed -n '1,620p' docs/threat-model-draft.md
sed -n '1,460p' docs/testing.md
sed -n '1,360p' docs/roadmap.md
sed -n '1,320p' docs/open-questions.md
sed -n '1,420p' docs/decisions/README.md
sed -n '1,260p' docs/decisions/0048-friendship-mutations-are-public-key-bound-exact-token-decisions.md
sed -n '1,320p' docs/research/c-toxcore-0.2.23-ratox-friend-lifecycle-rev0014.md
sed -n '1,620p' docs/research/cloudtainer-build-report.md
```

Then inspect the implementation being changed. Prose cannot grant a capability the code does not
implement. A deterministic mock cannot prove a public network route. A successful FIFO write cannot
prove semantic acceptance, remote receipt, authorization, execution, transfer completion, or
durability.

### 0.4 Run the owned tests

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

The default suite has eight CTest entries. The direct unit/integration runner registers 113 compiled
C++ checks. Warnings are errors.

Useful direct commands:

```sh
./build/gcc-debug/iotox --help
./build/gcc-debug/iotox bootstrap-seeds
./build/gcc-debug/iotox recall-generate
```

`recall-generate` prints a permanent owner secret. Never put a real phrase in shell history, a test
log, an issue, a datacube, or a chat transcript. Repeated words are valid and must not be normalized
away.

The CTest lane invokes `recall-generate` through a small CMake verifier. It validates one exact
LF-terminated eight-word record inside that process, erases its variables, and emits only a
`phrase suppressed` status. A test-generated RecallRoot is still sovereign material; successful
validation is not permission to retain or display it.

### 0.5 Run the one-binary product fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

This starts the real `iotox run` process and uses the same executable as the local operator. The
fixture crosses:

```text
one CLI/product binary
private Unix SOCK_SEQPACKET control
private request and per-peer FIFOs
bounded Agent command queue
one serialized toxcore owner thread
exact shared-library c-toxcore ABI peer
callbacks and bounded transport event queue
outgoing request evidence
incoming request observation and exact accept/reject
public-key-bound removal after restart
normal/action text, assigned message ids, and read receipts
canonical HELLO and mutual transcript confirmation
bidirectional transcript-bound stable-principal proof
signed local authority-ledger decision
literal durable command admission
injected toxcore SENDQ and exact retry
application RECEIVED and terminal result
finite file offer/send/receive/pause/resume/cancel
exact requested chunks and atomic destination publication
ratox-style journals and typed projections
atomic savedata, stable identity, authority ledger, and command store
orderly stop, reload, and continuity
```

The exact mock is another IoTox protocol endpoint, not a packet echo. It also deliberately fills the
lowest vacant friend-number slot so the key-bound deletion test exercises the provider contract that
numeric gaps may be reused.

The fixture distinguishes kernel admission, live projection, journal observation, and provider
success. In particular, peer-directory withdrawal and the adjacent best-effort `friend-events`
append are not one filesystem transaction. The fixture polls for exact semantic journal evidence
while requiring the node to remain alive; it never upgrades FIFO `write(2)` success or projection
disappearance into proof that the operation completed.

The fixture is adapter/process evidence. It does not prove official c-toxcore loading, DHT,
bootstrap, NAT traversal, UDP, TCP relays, public peers, Tor, I2P, or target hardware.

### 0.6 Inspect the ratox-successor surface manually

Start a disposable node:

```sh
work=$(mktemp -d)
./build/gcc-debug/iotox run \
  --library ./build/gcc-debug/libtoxcore-iotox-mock.so \
  --state "$work/tox.save" \
  --identity "$work/device.identity" \
  --authority-ledger "$work/authority.ledger" \
  --command-store "$work/commands.store" \
  --runtime "$work/run"
```

From another shell:

```sh
./build/gcc-debug/iotox --runtime "$work/run" status
./build/gcc-debug/iotox --runtime "$work/run" address
./build/gcc-debug/iotox --runtime "$work/run" profile
./build/gcc-debug/iotox --runtime "$work/run" peers
./build/gcc-debug/iotox --runtime "$work/run" requests
./build/gcc-debug/iotox --runtime "$work/run" friend-events
cat "$work/run/friendship.help"
```

The canonical outgoing request is typed because its exact record contains a full Tox address and a
bounded message:

```sh
./build/gcc-debug/iotox --runtime "$work/run" transport-peer-request \
  <76-HEX-TOX-ADDRESS> 'hello from this device'
```

For a live incoming request:

```sh
request=<64-UPPERCASE-HEX-PUBLIC-KEY>
cat "$work/run/requests/$request/request.help"
printf '%s\n' accept > "$work/run/requests/$request/accept"
# or:
printf '%s\n' reject > "$work/run/requests/$request/reject"
```

For an established peer:

```sh
peer=<64-UPPERCASE-HEX-PUBLIC-KEY>
cat "$work/run/peers/$peer/lifecycle.help"
printf '%s\n' remove > "$work/run/peers/$peer/remove"
```

The token must exactly match the lane. `REMOVE`, spaces, suffixes, partial records, and wrong-lane
words are rejected. A successful writer-side `write(2)` means only that the kernel accepted bytes.
Read `friend-events` for semantic disposition.

The public key is the destructive selector. Inside one toxcore owner-thread command, IoTox calls
`tox_friend_by_public_key` and then `tox_friend_delete`. The number returned by toxcore is evidence
for that lifecycle only. It is never persisted as the meaning of a peer.

Established peers also project:

```text
message          live normal Tox text
action           live action Tox text
command          signed durable machine operation
file-send        absolute finite local source path
file-receive     provider file number + absolute local destination
file-control     provider file number + pause|resume|cancel
```

Examples:

```sh
printf '%s\n' 'hello from the workshop' > "$work/run/peers/$peer/message"
printf '%s\n' 'waves' > "$work/run/peers/$peer/action"
printf '%s\n' device.describe > "$work/run/peers/$peer/command"
printf '%s\n' /absolute/local/source.bin > "$work/run/peers/$peer/file-send"
printf '%s\t%s\n' 65536 /absolute/local/destination.bin \
  > "$work/run/peers/$peer/file-receive"
printf '%s\t%s\n' 7 pause > "$work/run/peers/$peer/file-control"
```

These are six data/control meanings plus one lifecycle decision, not one untyped channel. Human
text is live and non-durable. Machine commands enter the signed durable engine. File FIFOs carry
path/control records, never file bytes. `remove` is exact transport administration and cannot revoke
or grant IoTox authority.

Stop and remove the disposable directory:

```sh
./build/gcc-debug/iotox --runtime "$work/run" stop
rm -rf "$work"
```

### 0.7 Run the clean compiler and analysis matrix

```sh
set -o pipefail
IOTOX_MATRIX_JOBS=2 \
IOTOX_FUZZ_LOG=/mnt/data/iotox-rev0014-fuzzer-smoke-final.log \
  ./tools/build-matrix.sh \
  |& tee /mnt/data/iotox-rev0014-final-matrix.log
printf '%s\n' "${PIPESTATUS[0]}" > /mnt/data/iotox-rev0014-final-matrix.exit
```

The matrix cleans and runs:

```text
GCC debug
GCC release
Clang debug
Clang AddressSanitizer + UndefinedBehaviorSanitizer
GCC ThreadSanitizer
five Clang libFuzzer smoke targets
GCC with host-linked Argon2
Mutorr preservation lane
```

Then run the repeated process gate:

```sh
IOTOX_AGENT_STRESS_RUNS=100 \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0014-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0014-agent-stress-final.exit \
  ./tools/agent-session-stress.sh gcc-debug
```

A matrix run owns `build/.matrix.lock`. The repeated Agent gate separately owns
`build/.agent-stress.lock`. Never run competing clean/build or evidence jobs in the same worktree;
concurrent attempts must fail closed rather than interleave retained truth.

When changing lifecycle observation or journal ordering, repeat the complete one-binary fixture from
fresh runtime directories rather than adding sleeps or treating FIFO admission as completion. The
final rev0014 correction completed ten sequential post-fix repetitions; its bounded evidence is
retained with the cube.

### 0.8 Attempt the source-linked product

```sh
set +e
./tools/build-standalone.sh \
  > /mnt/data/iotox-rev0014-standalone-attempt.log 2>&1
code=$?
printf '%s\n' "$code" > /mnt/data/iotox-rev0014-standalone-attempt.exit
set -e
```

When providers are available:

```sh
./tools/verify-standalone.sh
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
```

A dependency-fetch failure is not an owned-code failure and is not source-linked success. A dynamic
mock pass is not a genuine-peer pass. Preserve exact negative evidence.

### 0.9 Refresh evidence and package the next cube

After final source, matrix, stress, fixture, and standalone-attempt results are fixed:

```sh
IOTOX_MATRIX_EXIT_FILE=/mnt/data/iotox-rev0014-final-matrix.exit \
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0014-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0014-standalone-attempt.exit \
IOTOX_FUZZ_LOG=/mnt/data/iotox-rev0014-fuzzer-smoke-final.log \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0014-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0014-agent-stress-final.exit \
  ./tools/refresh-retained-artifacts.sh \
    /mnt/data/iotox-rev0014-final-matrix.log

./artifacts/run-prebuilt-tests.sh
(cd artifacts && sha256sum -c SHA256SUMS)
```

Package with an America/New_York timestamp:

```sh
timestamp=$(TZ=America/New_York date +%Y.%m.%d.%H.%M)
./tools/make-revision-archive.sh \
  rev0014 \
  "$timestamp" \
  ordinary-friendship-public-key-lifecycle-just-werx \
  /mnt/data
```

Extract the archive into a fresh directory, verify the lone entrance, rebuild, run CTest, run
prebuilt smoke, verify checksums, and search for sockets, FIFOs, private state, and secrets before
handoff.

---

## 1. What IoTox is

IoTox is a self-owned C++20 device agent and modern ratox successor built around Tox.

Its public shape is intentionally small:

```text
one foreground agent
one executable for both daemon and local operator
one private Unix control socket
ordinary private files, FIFOs, and journals
one Tox identity per configured transport instance
no mandatory IoTox account or vendor cloud
```

Its internal semantics are intentionally explicit:

```text
stable device identity above transport identity
permanent owner reconstruction through RecallRoot-v1
independent signed authorization ledger
canonical session negotiation and transcript confirmation
transcript-bound principal proof
signed durable command identity and replay
bounded queues and exact error categories
finite-file staging and no-clobber publication
transport, application, authority, and completion evidence kept distinct
```

The immediate product is not a distributed object store, broad automation platform, or UI suite.
It is the ratox successor: the strongest small headless Tox agent we can construct honestly.

The phrase at the center remains:

```text
From memory, you can reach your devices.
```

The corresponding governance statement is:

```text
IoTox has no key that can reassign a customer's device.
```

The corresponding engineering aesthetic is:

```text
The outside should be ordinary.
The inside must tell the truth.
```

---

## 2. Product laws still in force

### 2.1 One public product executable

The installed product is `iotox`. `iotox run` is the agent; all other invocations are local client,
inspection, administration, or generation roles. Do not create a second daemon merely to simplify
one feature.

### 2.2 C++20 owns the product

Owned product implementation and tests are C++20. C dependencies remain behind narrow provider
boundaries. CMake, shell, and Python may build, package, or test; they do not become another runtime
product.

### 2.3 One serialized toxcore owner

No business-logic module may call toxcore directly. One thread owns each `Tox*`, its iterate cycle,
callbacks, savedata, friendship, packets, text, and file operations. Other components submit typed,
bounded work.

### 2.4 Public key selects transport friendship

A c-toxcore friend number is a process-local handle. Deleted gaps may be reused and numbers may
change after reload. Human-facing directories and destructive lifecycle operations bind to the
32-byte public key. Lookup and delete execute in one owner-thread turn.

### 2.5 Friendship is transport, never authority

A Tox friend may be unknown, untrusted, authorized, revoked, or merely conversational. Accepting a
friend does not grant ownership or capabilities. Removing a friend does not revoke an independently
bound stable principal. A future compound revoke-and-remove operation must be explicit.

### 2.6 Permanent RecallRoot stays

RecallRoot-v1 is a fixed Argon2id derivation contract over a generated permanent phrase. It
intentionally allows offline guessing, so phrase strength is structural, not optional. The owner can
return from memory or print; IoTox cannot reset or recover the phrase.

### 2.7 No vendor reassignment authority

IoTox may publish software, bootstrap lists, relay tools, directories, or convenience services. None
may contain a key capable of replacing a device's owner. Service availability and ownership
sovereignty are separate.

### 2.8 Authorization is an independent signed ledger

Roles, capability ceilings, delegation, revocation, succession, and last-owner continuity live in a
signed ledger bound to the stable device principal. Tox friendship, session confirmation, runtime
files, and command history do not silently modify it.

### 2.9 Commit before transport or effect

A durable outgoing command exists before its first send attempt. An incoming command exists before
application receipt or execution. Authority/start state exists before execution. Terminal bytes
exist before delivery. Exact duplicates replay exact committed evidence; conflicting key reuse fails.

### 2.10 Ratox simplicity is a façade over explicit semantics

A FIFO is useful because it is ordinary. It is not a transaction, queue, audit log, file stream,
receipt, authority grant, or completion proof merely because `write(2)` returned success. Every lane
states what the bytes mean and where stronger evidence appears.

### 2.11 Network and route are distinct axes

The current implemented family is:

```text
transport: Tox
route:     native
```

Reserved:

```text
Tox over Tor
Tox over I2P
```

Those are routed Tox, not direct IoTox-over-Tor/I2P transports. Reserved routes fail closed and may
not silently use native networking.

### 2.12 Mutorr is preserved, not the northstar

Small-circle replication remains in the incubator with build/test preservation. It does not compete
with the ratox successor, real Tox, owner re-entry, or safe device operations.

---

## 3. What rev0014 constructs in executable code

### 3.1 One binary crosses the product path

The same executable can:

```text
run the agent
inspect status, identity, peers, sessions, authority, commands, files, and journals
send an outgoing Tox request
accept or reject a live request
remove an established transport friend
send human text
submit a durable operation
send, admit, and control finite files
stop the agent
```

The local control protocol is private Unix `SOCK_SEQPACKET`, versioned, bounded, correlated, and
same-user checked. The ratox-style files/FIFOs converge on the same Agent operations.

### 3.2 Ordinary friendship

Runtime shape:

```text
<RUNTIME>/
├── friendship.help
├── friend-events
├── friend-events.previous
├── requests/<PUBLIC_KEY>/
│   ├── public-key
│   ├── message
│   ├── message-bytes
│   ├── received-unix-ms
│   ├── request.help
│   ├── accept
│   └── reject
└── peers/<PUBLIC_KEY>/
    ├── lifecycle.help
    └── remove
```

`accept`, `reject`, and `remove` are private mode-0600 FIFOs. Their bodies must exactly equal the
filename word. The complete word plus LF must be one atomic record.

Incoming request records are live callback projections. They are rebuilt from current process
state, not restored from a provider pending queue. Duplicate callbacks from one key currently
replace the one live record. `friend-events` is bounded, rotating, process-local evidence and may
repeat sequence values across restart.

### 3.3 Human text

`message` and `action` send 1..1372 bytes through native Tox text. LF is local framing and removed;
every other byte is preserved at the adapter boundary. Valid UTF-8 is the interoperable protocol
contract even though the exact mock can exercise arbitrary bounded bytes.

A successful send returns a per-friend message id; zero is valid. A later Tox read receipt is
separate. Disconnect abandons upstream pending-receipt correlation. IoTox records that loss instead
of promising a later receipt.

There is no hidden offline human-message spool or retry.

### 3.4 Durable machine command

`command` accepts a bounded printable operation record and enters the signed durable engine. The
only registered operation is `device.describe`, requiring `read.telemetry`.

The durable key freezes:

```text
direction
remote Tox public key
persistent sender epoch
message id
```

Canonical request, authority decision, lifecycle, application receipt, and terminal result survive
restart. The current store is signed and atomically replaced but remains plaintext and vulnerable to
replacement by an older valid snapshot.

### 3.5 Finite files

`file-send` names one absolute finite local regular file. The manager opens no-follow, retains the
descriptor, enforces size/active limits, and answers exact positional chunk requests.

`file-receive` names a live friend-scoped provider file number plus absolute destination. The offer
remains paused until destination policy and private same-directory staging succeed. Completion
requires exact size, synchronization, and no-clobber atomic publication.

`file-control` sends pause, resume, or cancel. Local and peer pause are independent; a local resume
cannot erase peer pause. File numbers are ephemeral live handles and may be reused after terminal
cleanup. Transfer maps do not survive disconnect or restart.

### 3.6 Capability session and authority

Each true offline-to-online transition creates a fresh session nonce and frozen HELLO. Compatible
peers mutually confirm one canonical transcript before application records are admitted. A stable
principal then proves itself against that transcript and the local signed ledger decides capability.

Tox transport authentication and IoTox application authorization are intentionally layered. A
transport compromise should not automatically manufacture a valid signed operation.

### 3.7 Persistence

Current durable files:

```text
Tox savedata                 private atomic replacement + file/directory sync
stable device identity       fixed-size private seed/public record
authority ledger             signed bounded complete-history replacement
command store                signed bounded v2 snapshot
```

Current runtime projections are intentionally disposable. Do not infer durable audit from `/run`.

---

## 4. Evidence maturity and honest claims

Use these terms narrowly:

```text
specified              prose or frozen bytes define intended behavior
compiled               one toolchain built the path
unit-verified          in-process deterministic checks passed
process-verified       separate iotox process and local OS boundary passed
adapter-verified       exact consumed provider ABI double passed
source-linked          official pinned provider headers/sources compiled and linked
network-verified       two genuine peers crossed the stated route and lifecycle
target-verified        representative hardware/network/power behavior measured
production             security, update, operations, and support duties satisfied
```

rev0014 can honestly claim process- and adapter-verification for the owned friendship, text,
session, authority, durable-read, and finite-file paths. The retained final-source matrix in
`docs/research/cloudtainer-build-report.md` is green across GCC, Clang, sanitizers, ThreadSanitizer,
five bounded fuzz targets, host-linked Argon2, and the Mutorr preservation lane; the exclusive Agent
stress gate records 100/100 fresh-process passes.

It cannot honestly claim here:

```text
real c-toxcore ABI/load success
public Tox connectivity
bootstrap, DHT, NAT traversal, UDP, or TCP relay behavior
remote friend-request/deletion interoperability
Tox/Tor or Tox/I2P containment
mobile background operation
constrained-target power suitability
production security or independent audit
```

A static source reading is useful design evidence. It is not runtime evidence. An exact mock is
useful adapter evidence. It is not a network.

---

## 5. Hazards that must remain visible

### 5.1 Permanent phrase strength is security

RecallRoot-v1 intentionally supports deterministic re-entry and therefore offline password
guessing. Generated entropy is the defense. Do not add normalization, password hints, vendor reset,
or low-entropy convenience phrases.

### 5.2 Tox key is not the whole product identity

The Tox key addresses one route endpoint. Stable device identity and application authority exist
above it. Future native/Tor/I2P endpoint rotation must not erase device continuity or silently link
routes beyond owner policy.

### 5.3 Friend number reuse is destructive-risk material

Never persist friend-number meaning. Never resolve a key in one asynchronous operation and delete
the number in another. Every public destructive lifecycle operation must remain key-bound through
the owner-thread mutation.

### 5.4 Rejection and deletion are local

c-toxcore exposes an incoming callback, not a pending request object. Reject means IoTox discards its
live record. Delete means this profile removes the friend; toxcore does not notify the remote peer.
Do not write prose or UI that claims more.

### 5.5 Friendship is not authority

Removing a route without revoking an application principal may be intentional. Revoking a principal
without deleting every route may also be intentional. An operation that does both needs an explicit
compound commit/failure contract.

### 5.6 FIFO write success is weak evidence

A writer may return successfully before IoTox parses, rejects, persists, sends, or completes
anything. Request withdrawal, peer-directory withdrawal, and a journal append are also separate
observable effects rather than one cross-file transaction. Poll the exact semantic fact required; do
not turn an adjacent projection into an invented commit boundary. Journals are later local evidence.
Signed stores and published destinations are stronger boundaries for their respective meanings.

### 5.7 Runtime journals are not audit stores

They are bounded, rotating, unsigned, and not fsync-committed after each line. `friend-events`
sequence is process-local. A durable friendship history requires its own retention, privacy,
signature, rollback, and capacity decision.

### 5.8 Local same-user malware remains powerful

Private permissions and peer credentials reduce accidental/foreign-user access. They do not protect
against malicious code running as the same effective user. Product hardening still needs service
accounts, sandboxing, privilege separation, and target policy.

### 5.9 Command persistence is not rollback-resistant

A valid older signed snapshot remains valid. Physical effects must not rely on the current store
until rollback consequences and a monotonic witness are solved.

### 5.10 Time may be wrong

Many devices boot without trusted wall time. Absolute expiry alone is unsafe. Mutable operations
need relative lifetime, session/epoch evidence, or another freshness model.

### 5.11 File transfer is not object durability

Provider file numbers and live maps disappear across restart/disconnect. Restart-resumable cargo
needs stable object ids, hashes, checkpoints, quotas, and explicit publication records above Tox.

### 5.12 Transferred content has no execution authority

A Tox friend or authorized file sender does not automatically authorize import, firmware install,
configuration activation, or execution. OTA requires signed manifests, anti-rollback, staging,
health confirmation, and recovery.

### 5.13 Tox remains a network-facing native dependency

Pin current source, compile official headers, fuzz owned boundaries, sandbox where possible, monitor
upstream security work, and retain a rapid patch path. Sentiment is a reason to steward Tox, not a
reason to hide dependency risk.

### 5.14 Licensing is architecture

c-toxcore distribution obligations affect linking, appliance delivery, source provision, and update
strategy. Resolve the precise legal model before product distribution; runtime loading is not a
magic exemption.

### 5.15 Physical effects remain out of scope

No GPIO, lock, valve, motor, heat, power, medication, or safety-system operation is registered.
Before any such operation: freeze idempotency, maximum effect, interlocks, cancellation, power-loss
behavior, local override, quotas, and auditable terminal evidence.

---

## 6. Immediate executable direction

### Gate 1 — ordinary outgoing friend request

Add one private root-level request entrance that converges on the existing typed operation carrying a
complete 38-byte Tox address and a 1..921-byte message. Freeze one unambiguous bounded record format,
transactional FIFO publication, exact local evidence, replacement behavior, shutdown behavior, and
clear separation from any durable/offline application outbox. Do not parse shell syntax and do not
make a successful FIFO write mean remote receipt or acceptance.

The structured `transport-peer-request` command remains the normative operation. The ordinary
entrance is an adapter to it, just as request accept/reject and peer removal are adapters to their
typed Agent operations.

### Gate 2 — one useful harmless read

Choose one read that makes the ratox successor more operable, such as `transport.describe`,
`capabilities.describe`, or `health.snapshot`. Freeze exact fields, bounds, capability, expiry,
restart, and unknown/degraded semantics. Enter it through the same operation registry, signed durable
engine, wire protocol, structured client, and ordinary command FIFO. Keep the executor
transport/storage blind by passing an immutable bounded snapshot if necessary.

### Gate 3 — official source-linked providers

On a networked CLI, verify pinned archives/hashes, build libsodium, Argon2, and c-toxcore 0.2.23,
compile the linked provider against official headers, install one `iotox`, and correct real API/build
defects without creating a second product.

### Gate 4 — two genuine native Tox peers

Cross request/accept/reject/remove, text/receipts, HELLO/confirmation, stable-principal proof,
authorized durable reads, finite files, restart, disconnect/reconnect, and TCP relay. Record exact
versions, topology, timings, failures, and resource behavior.

Only this gate permits `Tox/native=network-verified` language.

### Gate 5 — owner re-entry and delegation

Implement the challenge/transition ceremony by which a phrase-reconstructed owner returns without
sending phrase, root, seed, or secret key to the daemon. Freeze discovery, freshness, ownership
epoch, ledger mutation, phrase-compromise handling, rollback, and evidence.

### Gate 6 — durable lifecycle and offline queues

Decide whether friend requests and lifecycle history remain live-only or become durable. Define
application outbox/inbox identity, expiry, quotas, priority, acknowledgements, duplicate handling,
and shutdown semantics. Do not promote runtime files silently.

### Gate 7 — safe mutable state

Require effect identity, relative expiry, idempotency, cancellation, indeterminate state, resource
reservation, disk-full handling, power-cut fault injection, hardware isolation, and local override.

### Gate 8 — signed bulk and OTA

Use Tox file transfer as carrier only. Add signed manifests, immutable content ids, target
constraints, anti-rollback, staged install, boot health, and recovery.

### Gate 9 — Tox stewardship and routed Tox

Create owner-contributable bootstrap/TCP relay tooling and documentation. Then research Tox/Tor and
Tox/I2P with explicit no-native-leak policy, DNS/UDP analysis, identity-linkability policy, resource
measurement, and fail-closed fallback. Direct Tor/I2P transport remains separate future work.

---

## 7. Code-shaping rules for the next office holder

```text
keep one installed iotox executable
keep one serialized owner per Tox instance
make provider handles evidence, not durable identity
bind destructive friendship decisions to public key
keep friendship and authority independent
reuse typed Agent operations across socket and FIFO entrances
keep FIFO services framing/path-only
commit durable command state before send or effect
keep human text out of machine authority
keep remote filenames out of local path selection
keep incoming files paused until resources/policy exist
make every parser bounded and fail closed
add a regression for every discovered defect
run clean builds before retaining evidence
preserve exact negative results
update BOOTSTRAPROSE and history when truth changes
```

When a module becomes large, split by semantic ownership rather than by arbitrary file size. The
likely next split remains incoming/outgoing durable command state machines and bounded immutable
operation snapshots—not another product process.

Do not create generic extension machinery before a concrete operation requires it. IoTox should
stay strong because its meanings are few and exact.

---

## 8. Governance of the office

The office holder may rewrite this entrance, reorder work, supersede an ADR with a later ADR, remove
failed experiments, and compress repetitive prose. The office holder may not silently change an
accepted security contract or inflate evidence maturity.

Every revision should:

```text
advance executable product construction or remove real debt
research the exact upstream seam being changed
record source date/version and inference boundary
add or strengthen tests around the changed semantics
retain failures that constrain claims
update current docs and preserve the old entrance in docs/history
refresh retained artifacts only from final source
package with the required revision timestamp filename
leave the root lone entrance intact
```

A good revision can be small if it closes one real semantic gap. A large revision is not good merely
because it adds machinery.

If the full product never ships, leave behind a usable ratox successor, disciplined toxcore adapter,
real-peer fixture, bootstrap/relay tooling, authority experiment, strict protocol library, or
upstream fixes. Partial value is still value when the evidence is honest and the cube is resumable.

---

## 9. Handoff truth for rev0014

This handoff section is synchronized to the retained rev0014 report. A future office holder must
verify and update it from fresh evidence rather than memory.

Current source truth:

```text
version/revision:          0.14.0 / rev0014
codename:                  Ordinary Friendship
public executable:         iotox
owned language:            C++20
registered C++ checks:     113, all passed
CTest entries:             8, all passed in every required product lane
full source matrix:        passed
Agent stress:              100/100 exclusive fresh-process runs passed
fuzzer smoke:              five targets x 5,000 units passed
local protocol:            major 1, minor 15
machine protocol:          major 1, minor 0
implemented route:         Tox/native adapter path
reserved routes:           Tox/Tor, Tox/I2P
implemented machine op:    device.describe only
friendship selection:      Tox public key
friend-number role:        process-local lifecycle evidence only
request retention:         live process projection, not durable
friend-events retention:   bounded/rotating/process-local, not signed audit
real toxcore here:          unproved until standalone/source-linked gate passes
genuine peers here:        unproved until real-peer gate passes
physical effects:          none
vendor reassignment key:   none
```

rev0014's central construction is:

> The ratox successor can now send a friend request, expose an incoming request as ordinary private
> state, accept or reject it with one exact write, and remove an established transport peer with one
> exact write—while binding destructive mutation to the public key and leaving ownership authority
> untouched.

The next office holder should first read the final build report, rerun a clean owned build, and then
construct the ordinary root-level outgoing-request entrance already named as Gate 1. After that,
advance one useful harmless read or the official source-linked native Tox gate. Do not reopen Mutorr,
Tor, I2P, OTA, GPIO, or physical effects merely because those dreams are interesting.
