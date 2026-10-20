# BOOTSTRAPROSE — IoTox rev0011, “Ordinary Write”

```text
Project:              IoTox
Revision:             rev0011
Version:              0.11.0
Codename:             Ordinary Write
Immediate northstar:  one-binary modern ratox successor
Current transport:    Tox over native networking
Current wire work:    HELLO, transcript confirmation, stable-principal proof,
                      signed authority, durable device.describe command
Current Unix work:    literal private per-peer command FIFO
Current authority:    permanent RecallRoot-derived owner plus signed local ledger
Owned product code:   C++20
Public product:       one executable named iotox
Pinned dependency:    c-toxcore 0.2.23
Reserved routes:      Tox/Tor and Tox/I2P; neither is implemented
Office timezone:      America/New_York
```

This is the lone entrance to the datacube and the office from which a successor wakes after total amnesia. It is a working instrument, not a memorial and not sacred text. The office holder is free—indeed expected—to rewrite it thoroughly when code, evidence, decisions, hazards, or priorities change.

There is no maximum length. There are minimum duties:

```text
state what IoTox is
state what exists in executable code
state what exists only as design
state what was actually exercised
state what cannot honestly be claimed
preserve decisions still in force
name hazards without euphemism
name executable work in order
show how to build, run, inspect, test, and package the cube
leave no hidden sovereign and no ambiguous grant of authority
```

Concision means removing repetition, vagueness, and ceremonial prose. It does not mean omitting a fact the next office holder needs to make the right change.

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

`BOOTSTRAPROSE.md` is the only ordinary visible object. `.datacube/` is hidden so the first encounter is one governing entrance rather than a source-tree wall. Hidden does not mean secret.

Do not create mutable runtime state at the cube root. Tox savedata, device identities, authority ledgers, command stores, sockets, FIFOs, and journals belong in a disposable development directory or an explicit installation state directory.

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
rev0011
IoTox 0.11.0 rev0011
```

The public install contract contains one executable: `iotox`. Internal static libraries, exact provider doubles, unit runners, process fixtures, fuzzers, and preserved research tools may exist in build or evidence trees; they are not additional product programs.

### 0.3 Reconstruct truth in authority order

Never trust an assistant summary, changelog, old cube, or memory over current code and retained results. Read in this order:

1. compiled source and exact tests;
2. accepted ADRs not explicitly superseded by later ADRs;
3. this entrance;
4. current architecture, protocol, threat, testing, and roadmap documents;
5. current research and retained build evidence;
6. historical entrances and old revision cubes.

Start here:

```sh
sed -n '1,320p' README.md
sed -n '1,360p' MANIFEST.md
sed -n '1,440p' docs/architecture.md
sed -n '1,360p' docs/ratox-command-fifo-v1.md
sed -n '1,440p' docs/protocol-session.md
sed -n '1,440p' docs/protocol-command-v1.md
sed -n '1,440p' docs/protocol-authority-v1.md
sed -n '1,480p' docs/threat-model-draft.md
sed -n '1,380p' docs/testing.md
sed -n '1,360p' docs/roadmap.md
sed -n '1,320p' docs/open-questions.md
sed -n '1,320p' docs/decisions/README.md
sed -n '1,360p' docs/research/ratox-fifo-and-toxcore-boundary-rev0011.md
sed -n '1,360p' docs/research/cloudtainer-build-report.md
```

Then inspect the implementation being changed. Prose cannot grant a capability the code does not implement. A deterministic mock cannot prove a public network route.

### 0.4 Run the owned tests

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

The default suite has eight CTest entries. The unit/integration executable registers 98 C++ checks. Warnings are errors.

Useful direct commands:

```sh
./build/gcc-debug/iotox --help
./build/gcc-debug/iotox bootstrap-seeds
./build/gcc-debug/iotox recall-generate
```

`recall-generate` prints a permanent owner secret. Never use a real owner phrase in a shared shell history, test log, issue, cube, or chat transcript.

### 0.5 Run the one-binary product fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

This starts the real `iotox run` process and uses the same executable as the local operator. The retained fixture crosses:

```text
one CLI/product binary
private Unix SOCK_SEQPACKET control
bounded agent command queue
one serialized toxcore owner thread
exact shared-library c-toxcore ABI mock
callbacks and bounded transport event queue
friend request observation and explicit rejection
peer acceptance and connection callback
canonical HELLO and mutual transcript confirmation
bidirectional transcript-bound stable-principal proof
signed local authority ledger decision
literal per-peer command FIFO write
signed durable command-store admission
injected toxcore SENDQ and exact retry
application RECEIVED and terminal result
ratox-style journals and typed projections
atomic savedata, stable device identity, authority ledger, and command store
orderly stop, reload, and continuity
```

The exact mock is another IoTox protocol endpoint, not a packet echo. It owns a different transport key, session nonce, sender epoch, and device principal. It asks once before authority and once afterward, signs its proof, checks the local proof, deliberately injects queue pressure, and replays an exact terminal result after duplicate delivery.

The fixture now performs the operator action through the literal FIFO—not merely through a structured test call:

```sh
printf '%s\n' device.describe > "$RUNTIME/peers/$PEER/command"
```

The fixture passes only when `command-events` exposes a nonzero durable sender epoch and message id, the first transport enqueue is recorded as `send-failed`, exact retry succeeds, the remote application commits `RECEIVED`, the terminal description is bound to the authorized principal, and restart preserves the signed command evidence.

### 0.6 Inspect the ratox-successor surface manually

Start a development node in a temporary directory:

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

After a peer exists:

```sh
peer=<64-UPPERCASE-HEX-TOX-PUBLIC-KEY>
find "$work/run/peers/$peer" -maxdepth 3 -printf '%M %P\n' | sort
cat "$work/run/peers/$peer/command.help"
printf '%s\n' device.describe > "$work/run/peers/$peer/command"
tail -n 1 "$work/run/peers/$peer/command-events"
./build/gcc-debug/iotox --runtime "$work/run" peer-description "$peer"
```

Interpret the observations exactly:

```text
write returned success       bytes entered the kernel FIFO
record observed              the monitor framed one LF-terminated record
record parsed                the operation name is registered
record admitted              a signed durable command record exists
transport queued             toxcore accepted the exact packet locally
remote RECEIVED              remote IoTox committed the exact request
terminal result              the operation completed or failed terminally
```

A FIFO is not an offline mailbox, persistent queue, reply channel, authority grant, or execution receipt.

### 0.7 Run the quality matrix

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh \
  |& tee /mnt/data/iotox-rev0011-final-matrix.log
```

The script takes an exclusive `flock` before any clean step. A concurrent matrix exits with status 75 rather than deleting another verifier's active tree. Use a copied worktree for genuinely independent concurrent runs.

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

The final rev0011 source passed GCC 14.2 debug and release, Clang 17 debug, Clang AddressSanitizer plus UndefinedBehaviorSanitizer, GCC ThreadSanitizer, five Clang libFuzzer targets at 5,000 units each, the system-linked Argon2 lane, and the Mutorr preservation lane. Ordinary lanes passed 8/8 CTest entries; Mutorr passed 10/10; the direct runner passed 98/98 compiled checks. The separate-process literal-FIFO lifecycle, one-binary mock-node lifecycle, release install surface, retained checksums, and offline prebuilt smoke also pass.

ThreadSanitizer found and forced correction of a real startup race between the event pump and publication of the FIFO service pointer. Final evidence is from the corrected source. Exact state is recorded in `artifacts/reports/validation-summary.txt`, `artifacts/reports/build-matrix.log`, and `docs/research/cloudtainer-build-report.md`. Do not summarize a compiler, sanitizer, race, or fuzzer failure away. Correct the program, narrow the claim, or retain the exact platform limitation.

### 0.8 Attempt the product-shaped dependency build

On a networked command line:

```sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
./dist/standalone/iotox --version
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
```

That path verifies immutable source archives from `dependencies.lock`, builds pinned libsodium, Argon2, and c-toxcore, compiles the linked provider against official toxcore headers, installs one product executable, and prepares two genuine Tox peers.

This cloudtainer has not completed the official source-linked or genuine-peer lane because the shell dependency fetch reaches a DNS boundary before compilation. This is an evidence limit, not permission to stop writing the product. The exact failure is retained under `artifacts/reports/standalone-attempt.*`.

### 0.9 Refresh evidence and package only after verification

```sh
# Preferred after every required lane completes:
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0011-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0011-standalone-attempt.exit \
  ./tools/refresh-retained-artifacts.sh \
  /mnt/data/iotox-rev0011-final-matrix.log

# Only when packaging an explicitly incomplete environment record:
IOTOX_ALLOW_PARTIAL_EVIDENCE=1 \
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0011-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0011-standalone-attempt.exit \
  ./tools/refresh-retained-artifacts.sh \
  /mnt/data/iotox-rev0011-final-matrix.log

./artifacts/run-prebuilt-tests.sh
(cd artifacts && sha256sum -c SHA256SUMS)
./tools/check-lone-entrance.sh
```

Package from the cube root:

```sh
./.datacube/tools/make-revision-archive.sh \
  rev0011 \
  "$(TZ=America/New_York date +%Y.%m.%d.%H.%M)" \
  ordinary-write-ratox-command-durable-admission \
  /mnt/data
```

Unpack the result into a fresh directory, rerun the lone-entrance check, verify retained checksums, and run the retained prebuilt smoke before handing off.

---

## 1. What IoTox is

IoTox is a self-owned device agent and modern ratox successor built around Tox.

It is not a cloud account system. It is not an MQTT broker with peer-to-peer branding. It is not a shell exposed over the Internet. It is not a new Tox implementation. It is not primarily Mutorr.

Its intended product claim is:

> A physical thing owns a stable identity, belongs to its owner rather than a vendor, speaks to authorized peers over Tox, and exposes useful local behavior through ordinary Unix composition.

The sentence at the center is:

> From memory, you can reach your devices.

The permanent generated phrase is a feature, not a regrettable emergency credential. RecallRoot-v1 uses a fixed Argon2id derivation contract so a strong phrase can reconstruct owner authority without an IoTox server. This necessarily permits offline guessing. Phrase strength is structural, not optional, and Argon2id cannot rescue weak or leaked words.

IoTox itself must never possess a key that can reassign a customer's device. There is no vendor recovery sovereign. A manufacturer may someday attest hardware provenance; it must not thereby acquire ownership authority.

Tox remains the primary network. We keep it because it is operationally valuable and because ratox demonstrates the kind of composable peer experience we want. Sentiment does not replace measurement, so native Tox still has to pass source-linked, real-peer, target-network, resource, and security gates.

---

## 2. Decisions in force

### 2.1 Tox stays; IoTox owns product semantics

Tox provides transport identity, encrypted peer sessions, bootstrap discovery, NAT traversal, relays, lossless custom packets, messages, and file transfer. IoTox provides stable application identity, owner reconstruction, authorization, protocol negotiation, command identity, persistence, receipts, replay, effects, and route policy.

A Tox friend is a transport peer. Friendship alone is never ownership and never actuator authority.

### 2.2 One product binary

The installed product is `iotox`. It can run the daemon and act as its local operator client through subcommands. There is no separate required `iotoxd` or ratox helper binary. Internal libraries are encouraged when they improve boundaries; they do not broaden the public program surface.

### 2.3 C++20 owns the product

IoTox-owned product and test code is C++20. c-toxcore and cryptographic dependencies remain their upstream implementation languages behind narrow adapters. GCC and Clang are both first-class build gates.

### 2.4 One toxcore owner thread

No business module calls toxcore directly. One thread exclusively owns each `Tox*`, performs iteration and every consumed API call, and turns callbacks into bounded internal events. This is stricter and easier to reason about than a giant cross-cutting mutex.

### 2.5 The outside is ordinary; the inside is explicit

Ratox's essential beauty is composability: network behavior appears as files, FIFOs, and ordinary I/O. IoTox preserves that simplicity as a façade over typed operations, signed authority, durable state, and explicit acknowledgements.

A simple surface must not lie. `write(2)` success is not remote execution. A journal projection is not durable truth. An online peer is not authorized. A transport receipt is not an application result.

### 2.6 Permanent RecallRoot stays

A generated permanent phrase may reconstruct owner authority. The derivation contract must be fixed, domain-separated, versioned, and documented. No vendor escrow or reassignment key exists.

The authorization ledger remains independent. It records owner and delegated principals, roles, capabilities, ownership epochs, sequence, grant, revocation, and later quorum/re-entry transitions.

### 2.7 Network and route are distinct axes

The intended first family is:

```text
Tox/native
Tox/Tor
Tox/I2P
```

Tox still provides peer/session semantics; native, Tor, and I2P describe how Tox reaches the network. Future direct transports are a separate family:

```text
Tor-direct
I2P-direct
```

Only Tox/native is under active construction. Reserved routes fail closed; selecting Tox/Tor or Tox/I2P must never silently leak onto native networking.

### 2.8 Mutorr is preserved, not the northstar

Small-circle replication remains useful research for owner-operated durable state. It is retained under the incubator and preservation lanes. It must not delay the working ratox successor.

---

## 3. What rev0011 constructs in code

### 3.1 One executable crosses the product path

The same `iotox` executable can:

```text
run the long-lived agent
create/load Tox savedata
create/load stable device identity
create/load the signed authority ledger
create/load the signed durable command store
serve a private local control socket
project private ratox-style state
accept a literal per-peer FIFO command
negotiate and confirm an IoTox session
prove stable application principals
make a capability decision
commit and transport a command
commit receipt and result evidence
stop and restart
```

The default development path dynamically loads exact provider ABIs. The standalone path is designed to build the same product with pinned linked providers.

### 3.2 Literal private per-peer command FIFO

Every current Tox peer is projected under its uppercase public key:

```text
<RUNTIME>/peers/<PUBLIC_KEY>/
├── command              FIFO, mode 0600
├── command.help         exact local grammar and meaning
├── command-events       bounded ingress observation journal
└── iotox/description/   typed terminal device.describe projection
```

The implemented record is:

```text
device.describe\n
```

v1 accepts printable ASCII, at most 256 body bytes, terminated by LF. It has no shell expansion, quoting, NUL, CR, binary frame, JSON, or arguments. A producer should write the complete record in one at-most-257-byte `write(2)`, below the POSIX minimum `PIPE_BUF` of 512 bytes. Reads may still split the bytes because a FIFO is a byte stream.

The monitor uses Linux `eventfd` and `poll`, a nonblocking read descriptor, a separate nonblocking hold-writer descriptor, bounded rescans, and bounded partial-record expiry. It does not use Linux-only `O_RDWR` FIFO behavior. It verifies real same-user directories and mode-0600 FIFOs with `lstat`, `O_NOFOLLOW`, `fstat`, ownership/mode checks, and device/inode equality. It rejects symlinks, regular-file substitution, wrong mode/owner, non-printable bytes, oversized records, and abandoned fragments.

The FIFO monitor does not call toxcore and owns no persistence.

### 3.3 Durable admission remains the first truth

A complete supported FIFO record enters the same `send_device_describe_request` path as the structured local client:

```text
parse operation
resolve current public key to current friend number
reserve sender epoch and message id
freeze canonical request and frame
sign and atomically commit durable outgoing record
attempt toxcore send
record exact state transition
```

An admitted `command-events` line names the nonzero durable sender epoch and message id. If the store cannot commit, the FIFO record is rejected and no transport attempt becomes an authoritative command.

`command-events` is bounded disposable evidence. The signed command store is authoritative. Terminal `device.describe` state is additionally projected under the peer's `iotox/description/` tree.

### 3.4 Transport/storage-blind command executor

`device.describe` execution is extracted into a typed command engine. It receives an already-decoded request and immutable execution context. It has no transport, filesystem, journal, authority, or command-store handles.

Admission, authorization, durability, transport, retry, and result commit remain Agent responsibilities. This separation is required before adding more operations; an operation implementation should not be able to smuggle network or storage behavior into its effect.

### 3.5 Implemented machine operation

The only executable operation is read-only:

```text
device.describe
```

Its result reports:

```text
IoTox revision number
semantic version
negotiated protocol version
stable device principal
supported feature mask
offered operation mask
```

No GPIO, lock, camera, settings mutation, firmware install, arbitrary file read, or shell execution is implemented or advertised.

### 3.6 IoTox session and authority path

The current peer protocol includes:

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

Transport identity and stable application principal are distinct. Each direction proves its principal after transcript confirmation. Authorization is evaluated against the local ledger and required capability. A command sent before the remote principal is authorized is denied.

### 3.7 Durable command store

The signed command store persists incoming and outgoing command identity, exact canonical bytes, authority context, state transitions, receipts, results, attempts, and terminal evidence. It supports exact duplicate replay and restart recovery for the read-only operation policy.

Integrity does not imply confidentiality or freshness. The current store is plaintext and an attacker able to restore an older valid snapshot can roll it back. These limits remain explicit.

### 3.8 Runtime projections

Runtime files are private same-user operator views. Regular projections are published by temporary file plus rename so readers do not observe partial contents. They are not `fsync`-durable and must be reconstructible from authoritative state or live process state.

The runtime tree itself is not a security boundary against another malicious process under the same Unix account. Product deployment should use a dedicated service account and narrow filesystem permissions.

---

## 4. Source map

```text
src/main.cpp
    one executable entry point

src/cli.cpp
    daemon mode and structured local operator subcommands

src/agent.cpp
    current coordinator for state, local surfaces, sessions, authority,
    durable commands, retries, results, and shutdown

include/iotox/local/command_fifo.hpp
src/local/command_fifo.cpp
    literal private peer FIFO monitor and framing

include/iotox/local/runtime_tree.hpp
src/local/runtime_tree.cpp
    private files, FIFOs, journals, typed projections, rotation

include/iotox/command_engine.hpp
src/command_engine.cpp
    transport/storage-blind operation execution

include/iotox/command_store.hpp
src/command_store.cpp
    signed durable command-store v2

include/iotox/protocol/
src/protocol/
    bounded canonical frame, session, authority, command codecs

include/iotox/security/
src/security/
    random, RecallRoot, stable device identity, signed authority ledger/proof

include/iotox/toxcore/
src/toxcore/
    narrow c-toxcore ABI/provider, options, bootstrap, owner thread, callbacks

tests/mock_toxcore.cpp
    exact consumed ABI plus deterministic second IoTox endpoint

tests/test_cli_process.cpp
    separate-process one-binary lifecycle and literal FIFO proof
```

The Agent is still too large. New feature code should continue moving behind typed boundaries rather than making `agent.cpp` the permanent architecture.

---

## 5. Evidence maturity

Use these words precisely:

```text
reserved               named in architecture; selecting it fails closed
compiled               owned source builds in one lane
adapter-verified        exact consumed provider ABI was exercised
integration-verified    owned modules crossed a process/lifecycle fixture
network-verified        genuine peers crossed the intended network path
target-verified         measured on intended hardware/OS/network conditions
production              security, operations, update, packaging, and support gates passed
```

rev0011 is compiled and integration-verified across retained GCC, Clang, sanitizer, race, fuzzer, linked-Argon2, and Mutorr-preservation lanes against the exact provider doubles. The c-toxcore adapter is adapter-verified against the consumed ABI mock. Native public Tox is not network-verified in this cloudtainer. Tor and I2P routes are reserved only.

The completed local matrix is strong evidence against ordinary owned-code regressions and caught a genuine startup race. It is not a cryptographic audit, public-network test, power-failure campaign, or target-hardware qualification.

The pinned c-toxcore project itself describes the library as experimental and not independently formally audited. Its 0.2.23 release includes a critical fix found during manual review. IoTox must pin, monitor, sandbox where possible, fuzz its boundaries, and remain able to ship security updates. High-consequence physical effects will require defense in depth above the Tox session.

---

## 6. Identity, ownership, and recovery

### 6.1 Key classes must remain distinct

The design separates:

```text
stable device signing identity
owner RecallRoot-derived authority
signed authorization ledger
replaceable Tox transport identity
future route-specific transport identities
future local-data encryption keys
```

A Tox profile is not the owner constitution. Losing or rotating a transport identity must not redefine who owns the physical device.

### 6.2 Permanent phrase contract

The owner phrase is intentionally permanent and exportable. A fixed Argon2id contract makes re-entry reproducible. This creates an offline guessing surface by design.

Therefore:

```text
generated entropy is mandatory
human-invented weak phrases are unacceptable
normalization and domain separation must be frozen
parameters and version must be explicit
no vendor copy exists
no silent derivation change is allowed
```

The current local ceremonies keep the phrase, RecallRoot, and owner signing seed out of the daemon process. Continue that property.

### 6.3 Authorization ledger

The independent signed ledger must remain the sole product authority for roles and capabilities. Planned capabilities include read state, change selected settings, actuate specific effects, administer principals, install firmware, export diagnostics, and transfer ownership. A friend list is not the ledger.

### 6.4 Recovery remains policy, not a secret vendor override

Ordinary recovery should add a replacement controller through an existing owner or configured owner-controlled quorum. Total re-entry from the permanent phrase must be explicit, epoch-changing, replay-resistant, and observable. Physical destructive reset may make hardware reusable without revealing the prior ownership domain.

The exact owner re-entry handshake to already-owned devices is still designed rather than implemented. Do not claim otherwise.

---

## 7. Tox, Tor, I2P, and network stewardship

### 7.1 Native Tox is first

The immediate product should build and ship a pinned c-toxcore inside the one `iotox` installation, then prove two genuine IoTox peers over native networking. Required measurements include bootstrap, relay-only behavior, reconnect, NAT variety, long offline periods, idle memory/CPU/network, suspend/resume, and target power behavior.

### 7.2 Tox over Tor

This is a future route for Tox, not direct Tor transport. It likely requires UDP and local discovery disabled, TCP relay/bootstrap reachability through an explicit proxy/tunnel, DNS-leak controls, and tests proving no native fallback. A toxcore proxy option alone is not route proof.

### 7.3 Tox over I2P

This is also a future Tox route, likely using stream tunnels and reachable Tox TCP bootstrap/relay infrastructure inside the overlay. It requires reproducible end-to-end experiments and explicit leak/failure policy.

### 7.4 Multiple route identities

Reusing one Tox identity across native, Tor, and I2P improves continuity but links the routes. Separate route identities improve separation but require stable IoTox identity binding, rotation, revocation, and deduplication. This remains an explicit design question.

### 7.5 Contribute to the Tox commons

IoTox should eventually make it easy for willing owners to operate bootstrap and TCP relay capacity, with clear consent, resource limits, upgrade guidance, observability, and no accidental public service. We should contribute fixes upstream where practical. IoTox should strengthen the network it depends on rather than merely consume it.

---

## 8. Hazards that must stay visible

### 8.1 No genuine c-toxcore run here yet

The source-linked build and real-peer fixture exist but have not completed in this cloudtainer. The network fetch fails before compilation at DNS resolution. All claims about bootstrap, DHT, NAT traversal, relays, public peers, and real c-toxcore timing remain unproven here.

### 8.2 FIFO semantics are easy to overclaim

A FIFO pathname does not store bytes. Unread data is kernel memory and disappears when descriptors close. It is a byte stream without message boundaries. Concurrent writers are only safely contiguous under the atomic-write bound. The current hold-writer means writer close is not a record delimiter; timeout policy prevents abandoned fragments from joining later writers.

Never use FIFO buffer capacity as a queue. Never return success from a shell write as operation success. Never add arbitrary shell evaluation.

### 8.3 Same-UID local processes are trusted together

Mode 0600 prevents other Unix users, not another malicious process under the daemon account. The same account can write FIFOs, use the control socket, inspect plaintext projections, and attempt path interference. Use a dedicated account. A stronger multi-tenant local security model would require explicit credentials/peer credentials and probably a different surface policy.

### 8.4 Command timeout and cancellation semantics remain sensitive

A caller timing out while an agent command is queued must not leave ambiguity about later physical execution. The current only operation is read-only. Before effects exist, every queued operation needs deadline, cancellation, admission, execution, shutdown, retry, and idempotency rules that survive restart.

### 8.5 Wall clock is not trustworthy by default

Absolute expiry exists in protocol records, but embedded clocks may start wrong or move backward. Replay windows, relative TTL, sender epoch, durable monotonic sequencing, and clock-estimation policy still need a complete design.

### 8.6 Durable stores are not yet confidential or rollback-resistant

Signed identity, authority, and command records detect unauthorized modification. They do not hide metadata or stop restoration of an older valid snapshot. Product storage requires encryption policy, backup/recovery semantics, rollback strategy, full-disk behavior, atomic power-loss tests, and possibly hardware monotonic state.

### 8.7 Source-linked licensing is a product requirement

c-toxcore's license and the licenses of all dependencies affect distribution. Runtime loading is an engineering seam, not a licensing bypass. Keep source availability, notices, reproducible inputs, and legal review in the product plan.

### 8.8 Target hardware may split the architecture

The full agent naturally fits Linux-class devices. Tiny microcontrollers may require an owner-controlled local gateway. Do not pretend a cloud-container build proves RAM, flash, wakeup, battery, or real-time suitability.

### 8.9 Physical effects raise the bar

`device.describe` is deliberately harmless. Before any lock, valve, motor, heater, camera, or firmware effect, require typed parameters, capability granularity, application signatures, expiry/replay protection, exact idempotency, durable execution state, safe startup/shutdown policy, hardware interlocks, and destructive tests.

---

## 9. Immediate executable work, in order

The northstar is not more generalized framework. It is a useful ratox successor.

### 9.1 Human text/action surface

Add an ordinary private peer write surface for Tox text/action traffic and a clear message/receipt journal. Preserve ratox's composition while reusing one typed internal message path. Decide explicit grammar, length, newline/binary behavior, receipt meaning, rotation, and same-UID security. Do not force human text through the durable machine-command store unless its semantics require persistence.

Candidate surface:

```text
peers/<KEY>/message
peers/<KEY>/message.help
peers/<KEY>/messages
```

The implementation should use existing structured text/action operations and toxcore owner-thread calls, not a second protocol.

### 9.2 Friend lifecycle as ordinary files

Expose incoming request observation and explicit accept/reject/remove through small capability-shaped surfaces. Preserve the rule that a friend request and friendship do not grant authority. Never recreate a generic command parser.

### 9.3 Finite file transfer surface

Turn the existing file-transfer machinery into a practical ratox-style interface for send, offer, accept, progress, cancel, and final integrity. Separate finite files from unknown-length streams. Multiple simultaneous transfers must be keyed independently and survive adversarial cancellation/error ordering.

### 9.4 More typed read-only operations

Freeze a bounded argument codec and operation registry, then add harmless reads such as health, network state, capability description, and selected sensor values. Keep execution transport/storage-blind. This grows the machine product without risking physical mutation.

### 9.5 Real source-linked native Tox

On the first networked CLI:

```text
fetch and hash pinned archives
build one linked iotox
compile against official headers
run two genuine peers
cross HELLO/confirmation/authority
write the literal FIFO
cross durable COMMAND/ACK/RESULT
restart both sides
retain logs and measured timings
```

Fix the code based on real behavior rather than protecting mock assumptions.

### 9.6 Owner re-entry

Implement the exact challenge/transition by which a RecallRoot-reconstructed owner re-enters an existing ownership domain, rotates authority safely, revokes lost controllers, and resists replay/rollback without a vendor key.

### 9.7 First mutable operation only after the safety substrate

Before any physical effect, complete deadlines, cancellation, idempotency, execution journal, restart policy, capability granularity, local hardware abstraction, and destructive fault tests. The first mutation should be low consequence and reversible.

### 9.8 Later, not now

```text
Tox/Tor route experiment
Tox/I2P route experiment
direct Tor/I2P transports
owner-operated mailbox/automation hub
Mutorr replication integration
mobile UI and consumer polish
```

These remain important. They do not outrank a working native-Tox ratox successor.

---

## 10. Governance of the cube and the office

### 10.1 BOOTSTRAPROSE is controlled but editable

The office holder may compress, expand, reorder, correct, or replace this file. No sentence is immutable merely because an earlier office holder wrote it. The duties at the top are the constraint.

When changing it:

```text
remove stale claims
retain unresolved hazards
point to exact code and evidence
name superseded decisions explicitly
keep the first run path executable
preserve the one-binary and no-vendor-sovereign decisions unless consciously reversed
archive the prior entrance under docs/history/
```

### 10.2 Claims follow evidence

Every revision must distinguish:

```text
implemented
exercised
retained as design
reserved
known broken or blocked
```

A failed test is evidence. A missing dependency is evidence. A mock pass is evidence. None may be relabeled as a different kind of evidence.

### 10.3 Decisions are append-only history

Do not silently edit an accepted architectural decision into its opposite. Add a superseding ADR that states what changed and why. Source code remains authoritative for behavior; ADRs remain authoritative for the intended decision history.

### 10.4 One cube per handoff

Each handoff archive uses:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

The root keeps one visible entrance. The archive excludes live identities and mutable runtime state. Retained binaries/logs are evidence, not promises of portability.

### 10.5 “Just werx” is a product requirement

A power user should eventually be able to install one binary, start one service, inspect ordinary files, write a small FIFO, and compose IoTox with shell/C++/automation tools. The internal discipline exists to make that simplicity honest and durable—not to replace it with ceremony.

---

## 11. Revision handoff sentence

IoTox rev0011 is a compiled C++20, one-binary ratox-successor foundation in which one literal private per-peer FIFO write of `device.describe` enters the same signed durable command path as the structured client, survives exact toxcore queue-pressure retry, receives principal-bound application evidence, and remains inspectable after restart against an exact c-toxcore ABI peer mock; it is not yet a genuine-network or physical-actuator product, and the next northstar is useful human text/friend/file Unix surfaces while the pinned real-toxcore gate remains mandatory.
