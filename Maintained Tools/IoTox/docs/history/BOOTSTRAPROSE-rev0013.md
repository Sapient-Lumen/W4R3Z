# BOOTSTRAPROSE — IoTox rev0013, “Ordinary Cargo”

```text
Project:              IoTox
Revision:             rev0013
Version:              0.13.0
Codename:             Ordinary Cargo
Immediate northstar:  one-binary modern ratox successor
Public product:       one executable named iotox
Owned product code:   C++20
Primary transport:    Tox over native networking
Pinned toxcore:       c-toxcore 0.2.23
Current Unix surface: message, action, command, file-send, file-receive, file-control
Current machine op:   read-only device.describe
Current authority:    permanent RecallRoot owner plus signed local authorization ledger
Current evidence:     exact consumed-ABI mock, separate processes, filesystem, restart, compilers,
                      sanitizers, race detector, fuzzers; genuine Tox peers remain unproved here
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
state what is only designed or reserved
state what was actually exercised
state what cannot honestly be claimed
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
refuses an empty Tox savedata path before creating dependent durable state.

### 0.2 Establish compiled identity

```sh
cd .datacube
cat REVISION
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
./build/gcc-debug/iotox --version
```

Expected:

```text
rev0013
IoTox 0.13.0 rev0013
```

The public install contract contains one executable: `iotox`. Internal static libraries, provider
doubles, test runners, process fixtures, fuzzers, and preserved incubator programs may exist in
build/evidence trees. They are not additional product programs.

### 0.3 Reconstruct truth in authority order

Never trust an assistant summary, changelog, old cube, or memory over current code and retained
results. Read in this order:

1. compiled source and exact tests;
2. accepted ADRs not explicitly superseded by later ADRs;
3. this entrance;
4. current architecture, protocol, threat, testing, and roadmap documents;
5. current research and retained build evidence;
6. historical entrances and old revision cubes.

Start here:

```sh
sed -n '1,420p' README.md
sed -n '1,420p' MANIFEST.md
sed -n '1,520p' docs/architecture.md
sed -n '1,420p' docs/ratox-message-fifo-v1.md
sed -n '1,420p' docs/ratox-command-fifo-v1.md
sed -n '1,520p' docs/ratox-file-fifo-v1.md
sed -n '1,460p' docs/protocol-session.md
sed -n '1,460p' docs/protocol-authority-v1.md
sed -n '1,500p' docs/protocol-command-v1.md
sed -n '1,560p' docs/threat-model-draft.md
sed -n '1,500p' docs/testing.md
sed -n '1,440p' docs/roadmap.md
sed -n '1,420p' docs/open-questions.md
sed -n '1,380p' docs/decisions/README.md
sed -n '1,320p' docs/decisions/0045-file-receive-acknowledges-admission-not-live-residency.md
sed -n '1,340p' docs/decisions/0046-ratox-file-fifos-name-finite-local-files.md
sed -n '1,340p' docs/decisions/0047-file-control-tracks-two-sided-pause.md
sed -n '1,420p' docs/research/c-toxcore-0.2.23-ratox-finite-file-control-rev0013.md
sed -n '1,520p' docs/research/cloudtainer-build-report.md
```

Then inspect the implementation being changed. Prose cannot grant a capability the code does not
implement. A deterministic mock cannot prove a public network route. A successful FIFO write cannot
prove toxcore acceptance, remote receipt, authorization, execution, transfer completion, or
durability.

### 0.4 Run the owned tests

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

The default suite has eight CTest entries. The unit/integration runner registers 110 compiled C++
checks. Warnings are errors.

Useful direct commands:

```sh
./build/gcc-debug/iotox --help
./build/gcc-debug/iotox bootstrap-seeds
./build/gcc-debug/iotox recall-generate
```

`recall-generate` prints a permanent owner secret. Never put a real phrase in shell history, a test
log, an issue, a datacube, or a chat transcript. Repeated words are valid and must not be normalized
away.

### 0.5 Run the one-binary product fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

This starts the real `iotox run` process and uses the same executable as the local operator. The
fixture crosses:

```text
one CLI/product binary
private Unix SOCK_SEQPACKET control
private per-peer message/action/command/file FIFOs
bounded agent command queue
one serialized toxcore owner thread
exact shared-library c-toxcore ABI mock
callbacks and bounded transport event queue
friend request observation and explicit rejection
peer acceptance and one callback-owned online epoch
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

The exact mock is another IoTox protocol endpoint, not a packet echo. It owns another transport key,
session nonce, sender epoch, and stable principal. It signs its proof, verifies the local proof,
injects selected queue pressure, and replays exact terminal command evidence.

The mock does not implement the Tox network. It cannot prove bootstrap, DHT, NAT traversal, UDP,
TCP relay reachability, client interoperability, Tor routing, or I2P routing.

### 0.6 Inspect the ratox-successor surface manually

Start a development node in a disposable directory:

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

From another terminal:

```sh
./build/gcc-debug/iotox --runtime "$work/run" status
./build/gcc-debug/iotox --runtime "$work/run" address
./build/gcc-debug/iotox --runtime "$work/run" identity
./build/gcc-debug/iotox --runtime "$work/run" authority
./build/gcc-debug/iotox --runtime "$work/run" peers
./build/gcc-debug/iotox --runtime "$work/run" sessions
./build/gcc-debug/iotox --runtime "$work/run" files
./build/gcc-debug/iotox --runtime "$work/run" command-store
```

After a peer exists:

```sh
peer=<64-UPPERCASE-HEX-TOX-PUBLIC-KEY>
find "$work/run/peers/$peer" -maxdepth 3 -printf '%M %P\n' | sort

cat "$work/run/peers/$peer/message.help"
printf '%s\n' 'hello from the workshop' > "$work/run/peers/$peer/message"
printf '%s\n' 'waves'                   > "$work/run/peers/$peer/action"
./build/gcc-debug/iotox --runtime "$work/run" peer-message-events "$peer"
./build/gcc-debug/iotox --runtime "$work/run" peer-messages "$peer"

cat "$work/run/peers/$peer/command.help"
printf '%s\n' device.describe > "$work/run/peers/$peer/command"
cat "$work/run/peers/$peer/command-events"
./build/gcc-debug/iotox --runtime "$work/run" peer-description "$peer"

cat "$work/run/peers/$peer/file.help"
printf '%s\n' /absolute/source.bin > "$work/run/peers/$peer/file-send"
printf '%s\t%s\n' 65536 /absolute/destination.bin \
  > "$work/run/peers/$peer/file-receive"
printf '%s\t%s\n' 7 pause > "$work/run/peers/$peer/file-control"
./build/gcc-debug/iotox --runtime "$work/run" peer-file-events "$peer"
find "$work/run/peers/$peer/files" -maxdepth 3 -type f -print -exec cat {} \;
```

The example file numbers are illustrative. Use the complete provider-assigned value shown by live
evidence. A file number is scoped to one friend, identifies one live provider transfer, and may be
reused after terminal cleanup.

### 0.7 Run the full retained-evidence matrix

```sh
set -o pipefail
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh \
  |& tee /mnt/data/iotox-rev0013-final-matrix.log
printf '%s\n' "${PIPESTATUS[0]}" > /mnt/data/iotox-rev0013-final-matrix.exit

IOTOX_AGENT_STRESS_RUNS=100 \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0013-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0013-agent-stress-final.exit \
  ./tools/agent-session-stress.sh gcc-debug
```

The matrix takes an exclusive `flock` before cleaning shared build trees. A concurrent invocation
exits with status 75 rather than deleting another verifier's active work. Use separate worktree
copies for genuinely independent parallel runs.

Required lanes are:

```text
GCC debug
GCC release
Clang debug
Clang AddressSanitizer plus UndefinedBehaviorSanitizer
GCC ThreadSanitizer
five Clang libFuzzer smoke targets
GCC linked to host Argon2
Mutorr preservation build/tests
one-binary process lifecycle
one-binary mock-node lifecycle
release install surface
retained artifact checksums and offline prebuilt smoke
```

A failed or absent lane remains failed or absent in retained evidence. Do not soften flags, edit a
log, or broaden a claim to make it disappear.

### 0.8 Attempt the source-linked product

On a networked command line:

```sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
./dist/standalone/iotox --version
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
```

The intended product build compiles pinned official c-toxcore 0.2.23, libsodium 1.0.22, and Argon2
20190702 and still installs one `iotox` executable. The runtime-loaded provider exists for research
and exact ABI doubles; the source-linked provider requires official upstream headers and links the
provider into the product.

The retained rev0013 standalone attempt exited before compilation because this shell could not
resolve `download.libsodium.org` while fetching the first pinned archive. This cloudtainer has not
yet supplied a successful pinned source-linked toxcore build or two genuine Tox peers. Continue
implementing the reviewed program without pretending that the external gate already passed.

### 0.9 Refresh evidence and package the next cube

After final source and documents are frozen:

```sh
set +e
./tools/build-standalone.sh \
  > /mnt/data/iotox-rev0013-standalone-attempt.log 2>&1
printf '%s\n' "$?" > /mnt/data/iotox-rev0013-standalone-attempt.exit
set -e

IOTOX_MATRIX_EXIT_FILE=/mnt/data/iotox-rev0013-final-matrix.exit \
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0013-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0013-standalone-attempt.exit \
IOTOX_FUZZ_LOG=/mnt/data/iotox-rev0013-fuzzer-smoke-final.log \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0013-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0013-agent-stress-final.exit \
  ./tools/refresh-retained-artifacts.sh \
  /mnt/data/iotox-rev0013-final-matrix.log

stamp=$(TZ=America/New_York date +%Y.%m.%d.%H.%M)
./tools/make-revision-archive.sh \
  rev0013 \
  "$stamp" \
  ordinary-cargo-ratox-finite-file-fifos-two-sided-control \
  /mnt/data
```

Extract the produced ZIP into a fresh directory. Re-run lone-entrance, clean GCC build, CTest,
prebuilt smoke, and checksum verification from the extracted copy. The archive itself is not proof
until the extracted object passes.

---

## 1. What IoTox is

IoTox is a self-owned, one-binary C++20 device agent and modern ratox successor.

Its core promise is:

```text
From memory, you can reach your devices.
The outside should be ordinary; the inside must tell the truth.
```

A physical device owns a Tox endpoint and a stable IoTox identity. An owner may reconstruct their
root authority from a permanent generated phrase under a fixed Argon2id contract. No IoTox vendor
key can reassign the device. A signed local authorization ledger decides roles and capabilities.
Tox supplies reachability, encrypted peer sessions, friendship, lossless packets, text, receipts,
and file transfer. IoTox supplies ownership, authorization, application protocol, durable command
truth, recovery policy, and an ordinary Unix operator surface.

IoTox is not:

```text
a mandatory vendor cloud
a Tox fork
a second chat network
a claim that friendship means ownership
a shell exposed to remote peers
a FIFO mistaken for a durable queue
a file-transfer callback mistaken for safe publication
a mock mistaken for the public Tox network
```

---

## 2. Product laws still in force

### 2.1 One public product executable

`iotox` is daemon, local client, inspection tool, recall tool, and fixture subject. Internal
libraries are encouraged when they sharpen boundaries. They do not widen the installed executable
surface.

### 2.2 C++20 owns the product

IoTox-owned product and test code is C++20. c-toxcore and cryptographic dependencies remain their
upstream implementation languages behind narrow adapters. GCC and Clang are first-class gates.

### 2.3 One serialized toxcore owner

No business module calls toxcore directly. One thread exclusively owns each `Tox*`, performs
iteration and every consumed API call, and converts callbacks into bounded internal events.

Required connection edges may not be silently dropped. `friend_connection_status` is the sole clock
for an IoTox online epoch. Friend-list snapshots reconcile existence and presentation; they do not
manufacture online/offline transitions.

### 2.4 Friendship is transport, never authority

A Tox friend is a reachable cryptographic peer. Friendship alone grants no IoTox ownership, role,
capability, command execution, firmware authority, file destination choice, or actuator authority.

Mutual HELLO/transcript confirmation establishes protocol compatibility. Stable-principal proof
binds a principal to that transcript. The local signed authorization ledger alone decides active
authority.

### 2.5 Permanent RecallRoot stays

A generated phrase may reconstruct owner authority through a fixed, versioned, domain-separated
Argon2id derivation contract. This deliberately permits offline guessing. Phrase strength is
structural, not optional.

No vendor escrow, reassignment key, or account service exists. IoTox cannot recover a forgotten
phrase, and the project must not silently add a sovereign substitute.

### 2.6 The authorization ledger is independent

The ledger records stable principals, issuer, role, capability mask, ownership epoch, sequence,
grants, revocations, and succession. Tox savedata and friendship are not the authorization database.

### 2.7 Commit before transport or effect

A durable machine command is authoritative only after its exact canonical request, identity,
authority context, and state are signed and durably committed. Incoming work commits before
application receipt or execution. Terminal result bytes commit before transmission.

Exact duplicates replay exact committed evidence. Reuse of the same durable key with different
bytes is a conflict.

### 2.8 Ratox simplicity is a façade over explicit semantics

The outside should allow ordinary files, FIFOs, command-line composition, and supervised processes.
The inside must distinguish:

```text
kernel write acceptance
local parse/admission
provider queue acceptance
remote transport receipt
application receipt
execution start
terminal application result
safe file publication
```

A simple surface must not lie about which boundary has been crossed.

### 2.9 Network and route are distinct axes

The intended first family is:

```text
Tox/native
Tox/Tor
Tox/I2P
```

Tox still provides peer/session semantics; native, Tor, and I2P describe how Tox reaches the
network. Future direct transports are a different family:

```text
Tor-direct
I2P-direct
```

Only Tox/native is under active construction. Reserved routes fail closed. Selecting Tox/Tor or
Tox/I2P must never silently leak onto native networking.

### 2.10 Mutorr is preserved, not the northstar

Small-circle replication remains useful research for owner-operated durable state. It is preserved
under the incubator and build lanes. It must not delay the working ratox successor.

---

## 3. What rev0013 constructs in executable code

### 3.1 One executable crosses the product path

The same `iotox` executable can:

```text
run the long-lived agent
create/load Tox savedata
create/load stable device identity
create/load signed authorization ledger
create/load signed durable command store
serve private Unix SOCK_SEQPACKET control
project private ratox-style state
send normal/action Tox text through CLI or FIFO ingress
observe outgoing ids, incoming text, and read receipts
accept literal per-peer durable command FIFO writes
negotiate and confirm an IoTox session
prove stable application principals
make a capability decision
commit, transport, retry, and recover a read-only command
send, accept, pause, resume, cancel, and complete finite files
stop and restart while preserving durable identity and command evidence
```

The development path dynamically loads exact provider ABIs. The standalone path is designed to
build the same product with pinned linked providers.

### 3.2 One peer directory, six write meanings

Every current peer is projected under its uppercase Tox public key:

```text
<RUNTIME>/peers/<PUBLIC_KEY>/
├── message              FIFO: live normal Tox text
├── action               FIFO: live Tox action text
├── command              FIFO: signed durable machine intent
├── file-send            FIFO: absolute finite local source path
├── file-receive         FIFO: file number, TAB, absolute local destination
├── file-control         FIFO: file number, TAB, pause|resume|cancel
├── message.help
├── command.help
├── file.help
├── message-events
├── messages
├── command-events
├── file-events
├── files/
│   ├── incoming/<FILE_NUMBER>/...
│   └── outgoing/<FILE_NUMBER>/...
└── iotox/description/...
```

The product law is:

```text
message/action   live human communication; no durable retry and no command authority
command          machine intent; signed durable admission precedes transport or effect
file-*           finite local-file transfer controls; no FIFO carries file bytes
```

### 3.3 Hardened generalized FIFO service

`PeerFifoServer` owns path validation and record framing for all six lanes. It uses Linux `eventfd`,
`poll`, nonblocking readers, separate nonblocking hold-writers, bounded rescans, and bounded
partial-record expiry. It does not depend on Linux-only `O_RDWR` FIFO behavior.

It verifies real same-user directories and mode-0600 FIFOs with `lstat`, `O_NOFOLLOW`, `fstat`,
ownership/mode checks, and device/inode equality. It rejects symlinks, regular-file substitution,
wrong mode/owner, path replacement, invalid records, and abandoned fragments. Directory-scan and
per-lane errors remain distinct.

Lane policy is configured rather than hard-coded:

```text
command       printable ASCII, at most 256 body bytes, LF delimiter
message       byte-preserving, 1..1372 body bytes, LF delimiter
action        byte-preserving, 1..1372 body bytes, LF delimiter
file-send     byte-line path record, at most 4095 body bytes, LF delimiter
file-receive  byte-line handle/path record, at most 4095 body bytes, LF delimiter
file-control  byte-line handle/action record, at most 17 body bytes, LF delimiter
```

For every opened FIFO, IoTox queries `_PC_PIPE_BUF`. It refuses a lane if its maximum complete
record cannot be emitted atomically. The service owns no Tox object, authority, durable queue,
retry, file descriptor for payload data, or operation meaning.

### 3.4 Live normal/action text

`message` and `action` remove only the LF delimiter and preserve every other byte at the local
adapter boundary, including NUL, CR, and high bytes. Current c-toxcore 0.2.23 forwards the bounded
span without validating UTF-8, while interoperable Tox human text is UTF-8. Emit valid UTF-8 for
ordinary communication. Use IoTox custom packets or Tox file transfer for arbitrary machine bytes.
Bodies containing LF use structured stdin/hex commands.

Exact c-toxcore failures map to stable IoTox results:

```text
friend absent        not_found
friend disconnected  unavailable
local send queue full resource_exhausted
empty/too long/null  invalid_argument
unknown provider code library_error
```

The first successful Tox text message id may be zero. IoTox therefore represents id presence
separately from numeric value. No hidden live-text spool or reconnect retry exists. When toxcore
clears pending receipts on disconnect, IoTox abandons matching message-kind correlations and records
the count rather than carrying stale ids into a future epoch.

`message-events` records local ingress and immediate send result. `messages` records outgoing
acceptance, incoming text, and read receipt. Both are bounded disposable projections.

### 3.5 Durable machine command

A complete supported command enters one durable path:

```text
parse operation
resolve peer/public-key identity
reserve persistent sender epoch and message id
freeze canonical request and frame
sign and atomically commit outgoing record
attempt toxcore send
record exact delivery transition
commit application receipt and terminal result
```

The FIFO monitor is a framing adapter, not a queue. If the store cannot commit, the operation is
rejected and no transport attempt becomes an authoritative command.

The only executable operation remains:

```text
device.describe
```

It is read-only and reports revision, semantic version, negotiated protocol version, stable device
principal, supported feature mask, and offered operation mask. No GPIO, lock, camera, settings
mutation, firmware install, arbitrary file read, or shell execution is implemented or advertised.

The operation executor receives an already-decoded request and immutable execution context. It has
no transport, filesystem, journal, authority, or command-store handles. Admission, authorization,
durability, retry, and result commit remain Agent responsibilities.

### 3.6 Finite-file send

`file-send` grammar is:

```text
<absolute-source-path><LF>
```

File bytes never cross the FIFO. IoTox opens the source using no-follow read-only semantics, requires
a finite regular file within configured limits, records identity/size/modification evidence, retains
the descriptor, and offers the basename through toxcore. Chunk requests are served at exact
positions from the retained descriptor. Source mutation is detected and fails the transfer.

Accepted ingress means the source was admitted and toxcore accepted the offer. It does not mean the
peer accepted or received the file.

### 3.7 Finite-file receive

`file-receive` grammar is:

```text
<decimal-file-number><TAB><absolute-destination-path><LF>
```

An incoming toxcore offer starts paused. IoTox does not allow generic resume before a destination is
admitted. It validates an absolute local path, an owned real parent directory, no existing target,
size/capacity policy, and a matching live offer. It creates a private same-directory temporary file,
retains the descriptor, and only then sends local RESUME.

Successful receive admission means a safe local destination resource exists and toxcore accepted
RESUME. A tiny transfer may complete before the caller renders that response, so the manager returns
a frozen admission snapshot instead of converting success into `not_found`.

On terminal zero-length input, IoTox validates final size, synchronizes the file, and publishes
without clobbering an existing destination. Destination appearance is completion truth. A journal
line and a vanished live projection are not substitutes.

### 3.8 Two-sided pause and cancellation

`file-control` grammar is:

```text
<decimal-file-number><TAB><pause|resume|cancel><LF>
```

Tox file pause is two-sided. IoTox stores independent `local_paused` and `peer_paused` facts. The
transfer is active only when neither bit is true. Local RESUME clears only local pause; it cannot
erase a peer-owned pause. If both sides paused, both sides must resume.

The toxcore `file_recv_control` callback is peer-originated evidence. A successful local
`tox_file_control()` call is not synthesized into that callback.

Local cancellation releases retained descriptors and temporary files even when the provider can no
longer queue the control packet. The caller still receives the provider failure. The live local
resource decision and the transport-send result are separate facts.

### 3.9 File handles and transfer lifetime

The complete toxcore file number is preserved as an opaque `uint32_t`. It is scoped to one friend,
may distinguish direction by implementation convention, and may be reused after terminal cleanup.
IoTox does not truncate it to 16 bits and does not treat it as a durable object id.

The 32-byte toxcore file id is exposed as transfer identity evidence when available. rev0013 does
not persist enough live-transfer state to promise restart-resume. Disconnect purges provider live
transfers. A future resumable object protocol must sit above ephemeral file handles.

### 3.10 Session, authority, and durable store

The current machine protocol includes:

```text
canonical HELLO
CAPABILITIES
mutual transcript confirmation
transcript-bound authority challenge
stable-principal proof
local signed ledger decision
COMMAND
COMMAND_ACK with RECEIVED
COMMAND_RESULT
```

The signed command store persists exact canonical bytes, durable identities, authority context,
state transitions, receipts, results, attempts, and terminal evidence. It supports exact duplicate
replay and restart recovery for the current read-only policy.

Integrity does not imply confidentiality or freshness. The store is plaintext, rewrites a bounded
snapshot, and cannot detect replacement by an older valid signed snapshot without an external
monotonic witness.

### 3.11 Runtime projections

Runtime regular files are private same-user operator views. They use temporary file plus rename so
readers do not observe partial content. They are not `fsync`-durable and must be reconstructible
from authoritative durable state or live process state.

Journals are bounded and rotate one previous generation. File journals record metadata and payload
length, not transferred file bytes.

---

## 4. Evidence maturity and honest claims

Use these words precisely:

```text
reserved               type/name exists; selecting it may fail closed
compiled               owned source builds
adapter-verified       exact consumed ABI double exercises the boundary
integration-verified   separate owned components/processes cross the path
source-linked          official pinned provider compiled and linked
network-verified       two genuine peers crossed the claimed route
platform-verified      measured on named target hardware/OS/network
production             externally reviewed and operated under defined policy
```

rev0013 is compiled and integration-verified across the owned process/filesystem path and
adapter-verified against exact consumed provider ABIs. The final clean wrapper completed GCC debug,
GCC release, Clang debug, Clang ASan+UBSan, GCC TSan, host-linked Argon2, all five 5,000-run fuzz
smokes, and the Mutorr preservation configuration. The default suite passed 8/8 in every normal
lane; Mutorr preservation passed 10/10; the direct registry contains 110 checks; and the principal
Agent/session shard passed 100/100 repeated runs. It is not source-linked or network-verified for
c-toxcore in this cloudtainer. Tox/Tor and Tox/I2P are reserved only.

Implemented and exercised here:

```text
C++20 one-binary product and local client
runtime-loaded exact c-toxcore ABI adapter and one owner thread
savedata continuity and stable IoTox device identity
RecallRoot derivation and signed authorization ledger
HELLO, callback-owned epochs, transcript confirmation, stable-principal proof
canonical command/receipt/result codecs
signed durable command store and restart recovery
read-only device.describe executor
private normal/action text FIFOs, typed errors, ids, incoming text, receipts
private durable command FIFO and admission journal
finite file manager, send/receive/control FIFOs, exact chunks, atomic publication
independent local/peer pause ownership
compiler, sanitizer, race, fuzzer, process, artifact, and restart facilities
```

Not yet claimed:

```text
official source-linked c-toxcore success in this cloudtainer
two genuine peers crossing bootstrap, NAT, UDP, or TCP relay
cross-client text/file interoperability
resume of a live file after process restart or disconnect
leak-free Tox/Tor or Tox/I2P
durable offline human-message delivery
trusted command expiry on an untrusted clock
rollback-resistant or encrypted persistent stores
safe mutable settings, physical actuation, or OTA
production security audit or target-hardware fitness
```

---

## 5. Hazards that must remain visible

### 5.1 A Tox key is not the whole product identity

Tox endpoint keys provide route/session identity. Stable IoTox identity, owner authority, roles,
capabilities, and recovery sit above them. Endpoint rotation must not silently redefine ownership.

### 5.2 The permanent phrase is intentionally guessable offline

RecallRoot-v1 has a fixed Argon2id derivation contract. Anyone with a verifier may guess offline.
Generated entropy, exact phrase preservation, domain separation, and owner handling are security
requirements. A convenient human-chosen password is not an acceptable substitute.

### 5.3 No vendor recovery authority

A vendor master key would make the vendor sovereign over every device. It is prohibited. Any future
re-entry or succession mechanism must be owner-controlled and explicit in the signed ledger.

### 5.4 FIFO write success is weak evidence

`write(2)` success proves only kernel acceptance. The record may later fail framing, path policy,
authority, durable admission, provider queueing, peer receipt, execution, or publication.

### 5.5 FIFO paths are names, not file streams

The finite-file lanes carry bounded path/control records. They do not stream payload bytes, evaluate
shell syntax, expand environment variables, follow remote path choices, or overwrite existing local
files. Paths containing LF require structured local control; the FIFO grammar cannot represent them.

### 5.6 Admission and completion are different

An incoming file is admitted after safe local staging exists and toxcore accepts RESUME. Completion
is the successful atomic appearance of the requested destination after exact-size verification and
synchronization. A transfer may complete before an admission reply is rendered; the frozen admitted
snapshot remains valid evidence.

### 5.7 Pause has two owners

Local pause and peer pause are independent. Local resume cannot override peer pause. Tests and UI
must not flatten them into one mutable boolean.

### 5.8 File handles are ephemeral and reusable

Friend file numbers are live provider handles. Never persist a durable historical object keyed only
by file number. Include peer, direction, stable application identity, and epoch where durability is
needed.

### 5.9 Disconnect destroys live transfer state

c-toxcore purges live transfers on disconnect. rev0013 does not claim restart or disconnect resume.
A resumable artifact protocol needs immutable ids, checkpoints, hashes, and explicit negotiation
above Tox file transfer.

### 5.10 Runtime projections are not authoritative durable state

A file under the runtime tree may be stale, rotated, or reconstructed. Signed ledger/command state
and completed destination files carry stronger semantics. Never derive ownership or execution truth
from a disposable journal alone.

### 5.11 Persistence is signed but not rollback-resistant

An attacker who can replace a store with an older valid signed snapshot may roll it back. Physical
products need a monotonic anchor, owner witness, secure element, or another explicit rollback policy.

### 5.12 Time is untrusted on many devices

Wall-clock expiry is unsafe when a device boots without trusted time. Mutable commands require
relative freshness, session evidence, monotonic counters, or explicit indeterminate handling before
physical effects are added.

### 5.13 Tox remains an external security dependency

c-toxcore should be pinned, monitored, sandboxed, fuzzed, updated, and treated as network-facing
native code. Application-level signatures, authorization epochs, replay protection, and effect
identity remain necessary defense in depth.

### 5.14 Licensing is architecture

The final distribution model must satisfy c-toxcore and dependency licenses. Runtime loading is an
engineering boundary, not a promise that distribution obligations disappear.

---

## 6. Immediate executable direction

The ratox successor—not Mutorr—is the northstar.

### Gate 1 — ordinary friend lifecycle

Construct the remaining first-class peer management surface through the one binary and runtime tree:

```text
outgoing friend request by Tox address
incoming request inbox with exact message/public key
explicit accept and reject
friend removal with durable/local evidence
stable public-key-first peer selection
clear offline/online/pending presentation
no authority grant implied by any friend operation
```

Prefer ordinary files/FIFOs only where their semantics remain finite and truthful. Keep structured
SOCK_SEQPACKET control as the canonical typed path.

### Gate 2 — useful harmless reads

Add one or more read-only operations after `device.describe`, chosen for real ratox value and narrow
attack surface. Candidates include bounded device status, named capability inventory, and explicit
runtime health. Do not add generic shell, arbitrary filesystem read, mutable settings, or actuator
control.

Every operation must define:

```text
canonical request and result
capability required
maximum input/output size
retry and duplicate semantics
restart policy
privacy exposure
journal projection
failure mapping
```

### Gate 3 — official source-linked providers

On a networked CLI:

```text
fetch and verify pinned archives
compile official c-toxcore/libsodium/Argon2
compile the linked adapter against official headers
install exactly one iotox executable
retain compiler, dependency, symbol, license, and failure evidence
fix real API/build defects without creating a second product
```

### Gate 4 — two genuine native Tox peers

```text
bootstrap both peers
request and accept friendship
exchange valid UTF-8 normal/action text and observe ids/receipts
confirm IoTox transcript in both directions
prove stable principals in both directions
perform durable device.describe through CLI and FIFO
send, receive, pause, resume, cancel, and complete simultaneous finite files
restart sender and receiver at hostile points
exercise TCP relay and disconnect/reconnect
retain exact versions, records, timings, topology, and failures
```

Only this gate permits `Tox/native=network-verified` language.

### Gate 5 — owner re-entry and delegation

Build the remote challenge/transition ceremony by which a phrase-reconstructed owner returns without
sending the phrase, RecallRoot, seed, or private key to the daemon. Define discovery, freshness,
ledger mutation, revocation, ownership epoch, phrase compromise, rollback, and evidence.

### Gate 6 — safe mutable device state

Before any setting or physical effect:

```text
relative expiry and clock evidence
per-operation effect identity
idempotency across retry and restart
durable cancellation and indeterminate state
resource reservation and full-disk behavior
power-cut fault injection
hardware adapter isolation
operator-visible recovery
```

A mutable operation is not ready merely because its packet and journal are correct.

### Gate 7 — signed bulk and OTA

Build signed manifests, immutable artifact ids, content hashes, target constraints, storage
reservation, anti-rollback, staged activation, boot health, and recovery independently of Tox
friendship. Tox file transfer is a carrier, never execution authority.

### Gate 8 — Tox stewardship and routed Tox

Operate and document owner-contributable bootstrap and TCP relay infrastructure. Then research:

```text
Tox/native
Tox/Tor with native leakage prohibited
Tox/I2P with native leakage prohibited
```

Route policy, identity linkability, DNS behavior, UDP disabling, relay/bootstrap topology, resource
cost, and fail-closed fallback must be measured. Direct IoTox-over-Tor/I2P remains a separate future
transport question.

---

## 7. Code-shaping rules for the next office holder

1. Keep one installed executable.
2. Keep all toxcore calls behind the serialized transport adapter.
3. Keep local control typed and bounded; a filesystem façade may translate into it.
4. Never add a FIFO that silently becomes an unbounded queue.
5. Never make remote text a shell language.
6. Never let a remote filename choose a local destination.
7. Commit machine truth before transport or effect.
8. Preserve exact duplicate replay and reject conflicting identity reuse.
9. Keep authority independent from friendship and session compatibility.
10. Add parser limits before adding parser expressiveness.
11. Treat process restart, disconnect, full disk, stale clocks, and cancellation as normal states.
12. Record defects discovered by tools and the semantic repair, not only green summaries.
13. Preserve old entrances and accepted ADRs as history; supersede explicitly rather than rewriting
    the past.
14. Change this entrance whenever current executable truth changes.

---

## 8. Governance of the office

The office holder may modify every current document and implementation file. Freedom to modify does
not mean freedom to obscure provenance or rewrite retained evidence.

For every material revision:

```text
archive the previous BOOTSTRAPROSE under docs/history
increment REVISION and compiled version coherently
write a changelog entry describing product progress and defects found
add or supersede ADRs for durable decisions
record primary-source research that materially shaped code
run the strongest available compiler/test/evidence matrix
retain failures and environmental limits honestly
refresh checksums and prebuilt evidence
package one datacube with the lone entrance intact
extract and verify the packaged object before release
```

Claims follow evidence, not intention. A feature may be beautiful, promising, or strongly designed
and still remain `reserved`, `compiled`, or `adapter-verified` rather than `network-verified`.

---

## 9. Handoff truth for rev0013

IoTox rev0013 is a compiled C++20 one-binary ratox-successor foundation. It now gives each projected
peer six ordinary write meanings: live normal text, live action text, signed durable machine intent,
finite source-file offer, finite destination admission, and two-sided transfer control. The file
FIFOs carry path/control records rather than payload streams; exact file bytes travel through
c-toxcore chunk callbacks and complete only when a no-clobber synchronized destination appears.

The owned C++ path, private local runtime, separate-process fixture, exact consumed-ABI mock, savedata
continuity, session proof, authority decision, durable read-only command, finite files, restart,
GCC/Clang facilities, sanitizers, race detector, and fuzzers are real. The final retained matrix is
complete, the direct registry has 110 passing checks, the principal Agent/session path passed
100/100 fresh-process repetitions through its in-repo stress tool, and copied artifact checksums plus
offline prebuilt smoke pass. Official source-linked c-toxcore and genuine public-network peers remain
unproved in this cloudtainer. Tox/Tor and Tox/I2P
remain fail-closed reserved routes. Mutable device effects and OTA remain prohibited by absence, not
merely by prose.

The immediate next code is ordinary friend lifecycle and another useful read-only ratox operation,
while the first networked CLI should compile the pinned providers and drive two genuine IoTox peers
through text, authority, durable command, and finite-file paths.

Wake from here. Read the code. Preserve the truths. Build the product.
