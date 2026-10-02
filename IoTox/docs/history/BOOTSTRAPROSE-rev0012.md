# BOOTSTRAPROSE — IoTox rev0012, “Living Text”

```text
Project:              IoTox
Revision:             rev0012
Version:              0.12.0
Codename:             Living Text
Immediate northstar:  one-binary modern ratox successor
Transport target:     Tox over native networking
Current evidence:      complete IoTox adapter/process path against exact c-toxcore ABI mock;
                       official source-linked provider and public network remain unproved
Current wire work:    Tox text/action plus HELLO, transcript confirmation,
                      stable-principal proof, signed authority, durable command
Current Unix work:    private per-peer message, action, and command FIFOs
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

Do not create mutable runtime state at the cube root. Tox savedata, device identities, authority ledgers, command stores, sockets, FIFOs, and journals belong in a disposable development directory or an explicit installation state directory. `Agent::start()` refuses an empty Tox savedata path before creating any dependent durable object; callers must choose the state boundary explicitly rather than inherit the current working directory.

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
rev0012
IoTox 0.12.0 rev0012
```

The public install contract contains one executable: `iotox`. Internal static libraries, exact provider doubles, unit runners, process fixtures, fuzzers, and preserved research tools may exist in build or evidence trees; they are not additional product programs.

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
sed -n '1,340p' README.md
sed -n '1,380p' MANIFEST.md
sed -n '1,480p' docs/architecture.md
sed -n '1,380p' docs/ratox-message-fifo-v1.md
sed -n '1,360p' docs/ratox-command-fifo-v1.md
sed -n '1,440p' docs/protocol-session.md
sed -n '1,440p' docs/protocol-command-v1.md
sed -n '1,440p' docs/protocol-authority-v1.md
sed -n '1,500p' docs/threat-model-draft.md
sed -n '1,420p' docs/testing.md
sed -n '1,400p' docs/roadmap.md
sed -n '1,360p' docs/open-questions.md
sed -n '1,340p' docs/decisions/README.md
sed -n '1,300p' docs/decisions/0044-connection-callbacks-own-online-epochs.md
sed -n '1,300p' docs/decisions/0045-file-receive-acknowledges-admission-not-live-residency.md
sed -n '1,380p' docs/research/c-toxcore-0.2.23-ratox-text-receipt-boundary-rev0012.md
sed -n '1,300p' docs/research/c-toxcore-0.2.23-file-admission-completion-boundary-rev0012.md
sed -n '1,400p' docs/research/cloudtainer-build-report.md
```

Then inspect the implementation being changed. Prose cannot grant a capability the code does not
implement. A deterministic mock cannot prove a public network route. A successful FIFO write cannot
prove toxcore acceptance, remote receipt, authorization, execution, or durability.

### 0.4 Run the owned tests

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

The default suite has eight CTest entries. The unit/integration executable registers 106 C++ checks. Warnings are errors.

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

This starts the real `iotox run` process and uses the same executable as the local operator. The
retained fixture crosses:

```text
one CLI/product binary
private Unix SOCK_SEQPACKET control
hardened per-peer message/action/command FIFOs
bounded agent command queue
one serialized toxcore owner thread
exact shared-library c-toxcore ABI mock
callbacks and bounded transport event queue
friend request observation and explicit rejection
peer acceptance and one callback-owned online epoch
friend inventory reconciliation that cannot manufacture reconnects
normal/action text, assigned message ids, and read receipts
canonical HELLO and mutual transcript confirmation
bidirectional transcript-bound stable-principal proof
signed local authority-ledger decision
literal per-peer command FIFO write
signed durable command-store admission
injected toxcore SENDQ and exact command retry
application RECEIVED and terminal result
ratox-style journals and typed projections
atomic savedata, stable identity, authority ledger, and command store
orderly stop, reload, and continuity
```

The exact mock is another IoTox protocol endpoint, not a packet echo. It owns a different transport
key, session nonce, sender epoch, and device principal. It asks once before authority and once
afterward, signs its proof, checks the local proof, injects selected queue pressure, and replays an
exact terminal result after duplicate delivery.

The fixture first exercises human communication through the same product:

```sh
printf '%s\n' 'ratox-writes' > "$RUNTIME/peers/$PEER/message"
```

The process test separately proves byte preservation for a body containing NUL and CR against the
exact consumed-ABI mock. That is adapter evidence, not a claim that malformed UTF-8 interoperates
with real Tox clients. The first successful text id is zero; zero is represented as data, not
“missing.” `message-events` records local ingress and exact send result, while `messages` separately
records outgoing acceptance, incoming echo, and read receipt. Human text has no hidden durable
retry.

The fixture then performs the machine operation through the literal durable-command FIFO:

```sh
printf '%s\n' device.describe > "$RUNTIME/peers/$PEER/command"
```

It passes only when `command-events` exposes a nonzero durable sender epoch and message id, an
injected first command enqueue is recorded as `send-failed`, exact retry succeeds, the remote
application commits `RECEIVED`, the terminal description is bound to the authorized principal, and
restart preserves signed command evidence.

### 0.6 Inspect the ratox-successor surface manually

Start a development node in a temporary directory:

```sh
work=$(mktemp -d)
./build/gcc-debug/iotox run \
  --library ./build/gcc-debug/libtoxcore-iotox-mock.so \
  --state "$work/tox.save" \
  --identity "$work/device.identity" \
  --authority "$work/authority.ledger" \
  --command-store "$work/commands.store" \
  --runtime "$work/run"
```

That command is deliberately mock-backed so the entrance is executable in this datacube. On a
networked system with the pinned source-linked product, omit `--library` or point it at the intended
real provider and retain the resulting provider/network evidence separately.

From another terminal:

```sh
./build/gcc-debug/iotox --runtime "$work/run" status
./build/gcc-debug/iotox --runtime "$work/run" address
./build/gcc-debug/iotox --runtime "$work/run" identity
./build/gcc-debug/iotox --runtime "$work/run" authority
./build/gcc-debug/iotox --runtime "$work/run" peers
./build/gcc-debug/iotox --runtime "$work/run" sessions
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
./build/gcc-debug/iotox --runtime "$work/run" peer-command-events "$peer"
./build/gcc-debug/iotox --runtime "$work/run" peer-description "$peer"
```

For human text, interpret the observations exactly:

```text
write returned success        bytes entered the kernel FIFO
message-events accepted       IoTox framed the record and toxcore returned an id
messages outgoing             local send acceptance entered the transport journal
messages receipt              c-toxcore reported remote friend receipt
machine effect                none; human text grants no command authority
```

For machine commands:

```text
write returned success        bytes entered the kernel FIFO
record observed               the monitor framed one LF-terminated record
record parsed                 the operation name is registered
record admitted               a signed durable command record exists
transport queued              toxcore accepted the exact packet locally
remote RECEIVED               remote IoTox committed the exact request
terminal result               the operation completed or failed terminally
```

A FIFO is not an offline mailbox, persistent queue, reply channel, authority grant, or execution
receipt. Use `message-stdin`/`action-stdin` or hex variants when a text body contains LF or when the
caller needs a synchronous typed result.

### 0.7 Run the quality matrix

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh \
  |& tee /mnt/data/iotox-rev0012-final-matrix.log
```

The script takes an exclusive `flock` before any clean step. A concurrent matrix exits with status 75 rather than deleting another verifier's active tree. Use a copied worktree for genuinely independent concurrent runs. This cloudtainer may terminate one shell invocation before the entire clean matrix finishes; rev0012's retained final evidence therefore uses independently fresh, non-overlapping lane invocations and concatenates only their exact successful logs. On an ordinary command line, prefer the single script above.

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

The final rev0012 source passed GCC 14.2 debug and release, Clang 17 debug, Clang AddressSanitizer plus UndefinedBehaviorSanitizer, GCC ThreadSanitizer, five Clang libFuzzer targets at 5,000 units each, the system-linked Argon2 lane, and the Mutorr preservation lane. Ordinary lanes passed 8/8 CTest entries; Mutorr passed 10/10; the direct runner passed 106/106 compiled checks. The separate-process literal message/action/command FIFO lifecycle, one-binary mock-node lifecycle, release install surface, retained checksums, and offline prebuilt smoke also pass.

Repeated process runs found and forced correction of a real pre-start statistics defect in the generalized FIFO service: status publication could observe configured lanes before counter storage was shaped. Final evidence is from the constructor-shaped, bounds-checked correction. Packaging verification then found that direct tests with an omitted savedata path could derive identity, authority, and command-store names from the caller's current directory, allowing an offline retained smoke to dirty the cube root. The product now refuses an empty savedata path before side effects, transient tests select explicit temporary state, retained direct tests run from a disposable working directory, and both retained paths assert that the source root remains clean. A scheduling audit exposed a third semantic defect: an older friend-list snapshot could be applied after a newer online callback, manufacture online epoch two, and erase the real epoch's failed-then-retried HELLO evidence. Required ordered friend-connection callbacks now exclusively open and close protocol epochs; inventory refresh projects friend existence, public-key mapping, and presentation only. Direct and process assertions require `online-epoch=1` and `hello-send-attempts=2` after one injected `SENDQ`; the exact Agent integration shard then passed 100 consecutive executions while preserving that contract. Release scheduling exposed a fourth defect: a tiny incoming file could complete and leave the live transfer map after successful RESUME but before the local `file-receive` reply lookup, producing false `not_found` after safe publication. The reply now acknowledges frozen admission; completion remains asynchronous truth. A separate saturation-test correction permits already-published observational events while still requiring the callback-owned connection edge before any later required friend event. The earlier rev0011 TSan service-publication race remains fixed. Exact state is recorded in `artifacts/reports/validation-summary.txt`, `artifacts/reports/build-matrix.log`, `artifacts/reports/agent-session-stress.log`, and `docs/research/cloudtainer-build-report.md`. Do not summarize a compiler, sanitizer, race, or fuzzer failure away. Correct the program, narrow the claim, or retain the exact platform limitation.

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
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0012-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0012-standalone-attempt.exit \
  ./tools/refresh-retained-artifacts.sh \
  /mnt/data/iotox-rev0012-final-matrix.log

# Only when packaging an explicitly incomplete environment record:
IOTOX_ALLOW_PARTIAL_EVIDENCE=1 \
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0012-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0012-standalone-attempt.exit \
  ./tools/refresh-retained-artifacts.sh \
  /mnt/data/iotox-rev0012-final-matrix.log

./artifacts/run-prebuilt-tests.sh
(cd artifacts && sha256sum -c SHA256SUMS)
./tools/check-lone-entrance.sh
```

Package from the cube root:

```sh
./.datacube/tools/make-revision-archive.sh \
  rev0012 \
  "$(TZ=America/New_York date +%Y.%m.%d.%H.%M)" \
  living-text-ratox-message-action-file-admission \
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

Not every event has equal evidentiary weight. Diagnostic/bootstrap presentation may be discarded
with an explicit loss counter under pressure. Friendship edges, especially
`friend_connection_status`, are required: they may evict older observational records or apply
bounded backpressure, but they may not disappear. The connection callback is the sole clock for an
IoTox peer online epoch.

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

## 3. What rev0012 constructs in code

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
send normal/action Tox text through structured or FIFO ingress
observe outgoing ids, incoming text, and read receipts
accept a literal per-peer durable command FIFO write
negotiate and confirm an IoTox session
prove stable application principals
make a capability decision
commit and transport a command
commit receipt and result evidence
stop and restart
```

The default development path dynamically loads exact provider ABIs. The standalone path is designed
to build the same product with pinned linked providers.

### 3.2 Three ordinary peer write lanes

Every current Tox peer is projected under its uppercase public key:

```text
<RUNTIME>/peers/<PUBLIC_KEY>/
├── message              FIFO, mode 0600: normal Tox text
├── action               FIFO, mode 0600: Tox action text
├── message.help         exact live-text grammar and evidence
├── message-events       bounded local ingress journal
├── messages             bounded transport lifecycle journal
├── command              FIFO, mode 0600: durable machine operation
├── command.help         exact machine-operation grammar
├── command-events       bounded durable-admission journal
└── iotox/description/   typed terminal device.describe projection
```

The product law is:

```text
message/action   live human communication; no durable queue and no command authority
command          machine intent; signed durable admission precedes transport or effect
```

### 3.3 Generalized hardened peer FIFO service

`PeerFifoServer` owns path validation and record framing for all three lanes. It uses Linux `eventfd`
and `poll`, nonblocking readers, separate nonblocking hold-writers, bounded rescans, and bounded
partial-record expiry. It does not use Linux-only `O_RDWR` FIFO behavior.

It verifies real same-user directories and mode-0600 FIFOs with `lstat`, `O_NOFOLLOW`, `fstat`,
ownership/mode checks, and device/inode equality. It rejects symlinks, regular-file substitution,
wrong mode/owner, path replacement, invalid records, and abandoned fragments. Directory-scan errors
and per-lane errors have distinct keys.

Lane policy is configured rather than hard-coded:

```text
command   printable ASCII, at most 256 body bytes, LF delimiter
message   byte-preserving local record, 1..1372 body bytes, LF delimiter
action    byte-preserving local record, 1..1372 body bytes, LF delimiter
```

For every opened FIFO, IoTox queries `_PC_PIPE_BUF`. It refuses a lane if its maximum complete
record cannot be emitted atomically. The service owns no durable queue, Tox object, authorization,
retry, or operation meaning and never calls toxcore directly.

### 3.4 Live text semantics

`message` and `action` remove only the LF delimiter and preserve every other byte at the local
adapter boundary, including NUL, CR, and high bytes. Current c-toxcore 0.2.23 forwards the bounded
span without validating UTF-8, but native Tox human-message semantics are UTF-8. Emit valid UTF-8
for interoperability; use IoTox custom packets or Tox file transfer for arbitrary machine bytes.
Bodies containing LF use structured stdin/hex commands for exact adapter access.

The same typed C++ send path serves structured and FIFO callers. Exact c-toxcore text failures map
to stable IoTox results:

```text
friend absent        not_found
friend disconnected  unavailable
local send queue full resource_exhausted
empty/too long/null  invalid_argument
unknown provider code library_error
```

A successful c-toxcore call yields a per-friend message id. The first valid id is zero, so ingress
evidence has an explicit `has_message_id` field. No live-text retry or offline spool is invented.
c-toxcore clears pending text-receipt entries when a friend disconnects. IoTox now clears the
matching local message-kind correlations at the same callback boundary and emits the abandoned
count, preventing stale receipt metadata from surviving reconnect or message-id reuse.

`message-events` records local framing and send acceptance/rejection. `messages` records outgoing
transport acceptance, incoming text, and read receipt. Both are bounded disposable projections.

### 3.5 Durable admission remains the first machine truth

A complete supported command record enters the same durable path as the structured local client:

```text
parse operation
resolve current public key to current friend number
reserve sender epoch and message id
freeze canonical request and frame
sign and atomically commit durable outgoing record
attempt toxcore send
record exact state transition
```

An admitted `command-events` line names the nonzero durable sender epoch and message id. If the store
cannot commit, the record is rejected and no transport attempt becomes an authoritative command.

### 3.6 Transport/storage-blind command executor

`device.describe` execution remains behind a typed command engine. It receives an already-decoded
request and immutable execution context. It has no transport, filesystem, journal, authority, or
command-store handles.

Admission, authorization, durability, transport, retry, and result commit remain Agent
responsibilities. This boundary must hold before adding more operations.

### 3.7 Implemented machine operation

The only executable operation is read-only:

```text
device.describe
```

Its result reports revision, semantic version, negotiated protocol version, stable device principal,
supported feature mask, and offered operation mask. No GPIO, lock, camera, settings mutation,
firmware install, arbitrary file read, or shell execution is implemented or advertised.

### 3.8 IoTox session, authority, and durable store

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

The signed command store persists incoming and outgoing command identity, exact canonical bytes,
authority context, state transitions, receipts, results, attempts, and terminal evidence. It
supports exact duplicate replay and restart recovery for the read-only operation policy.

One required friend-connection callback owns each online/offline transition and therefore each
protocol epoch. Friend inventory refresh may reconcile existence, public-key mapping, and
presentation, but it may not open or close a session. A copied level snapshot can be stale by the
time another worker applies it; treating it as an edge manufactured a false reconnect during this
revision. ADR 0044 freezes callback evidence above inventory evidence.

Integrity does not imply confidentiality or freshness. The store is plaintext and an attacker able
to restore an older valid snapshot can roll it back.

### 3.9 Runtime projections

Runtime files are private same-user operator views. Regular projections use temporary file plus
rename so readers do not observe partial contents. They are not `fsync`-durable and must be
reconstructible from authoritative state or live process state.

The runtime tree is not a security boundary against another malicious process under the same Unix
account. Product deployment should use a dedicated service account and narrow permissions.

## 4. Source map

```text
src/main.cpp
    one executable entry point

src/cli.cpp
    daemon mode and structured local operator subcommands

src/agent.cpp
    current coordinator for state, local surfaces, sessions, authority,
    live text, durable commands, retries, results, and shutdown

include/iotox/local/peer_fifo.hpp
src/local/peer_fifo.cpp
    configurable private peer FIFO service and bounded framing

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
    bounded canonical frame, session, authority, and command codecs

include/iotox/security/
src/security/
    random, RecallRoot, stable device identity, signed authority ledger/proof

include/iotox/toxcore/
src/toxcore/
    narrow c-toxcore ABI/provider, options, bootstrap, owner thread, callbacks

tests/mock_toxcore.cpp
    exact consumed ABI plus deterministic second IoTox endpoint

tests/test_peer_fifo.cpp
    multi-lane framing, hardening, recovery, atomicity, and lifecycle

tests/test_cli_process.cpp
    separate-process one-binary text/receipt/command/restart proof
```

The Agent is still too large. New feature code should continue moving behind typed boundaries rather
than making `agent.cpp` the permanent architecture.

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

rev0012 is compiled and integration-verified across retained GCC, Clang, sanitizer, race, fuzzer, linked-Argon2, and Mutorr-preservation lanes against the exact provider doubles. The c-toxcore adapter is adapter-verified against the consumed ABI mock, including typed text failures and disconnect-before-receipt cleanup. Native public Tox is not network-verified in this cloudtainer. Tor and I2P routes are reserved only.

The completed local matrix is strong evidence against ordinary owned-code regressions and caught genuine lifecycle defects. After repairing the stale-inventory session race, the exact Agent integration shard passed 100 consecutive runs while preserving `online-epoch=1` and the injected failed-then-successful HELLO attempt history. A final queue audit then found that this authoritative callback was still classified as disposable under saturation; it is now a required backpressured event, with a one-slot regression proving the online edge survives behind `friend_added` even when an observational self/backend event wins a consumer scheduling race. Release scheduling also forced the finite-file admission boundary: successful RESUME returns a frozen accepted record even when a tiny transfer has already completed and left the live map. This is scheduling evidence for the owned mock boundary, not a substitute for genuine c-toxcore reconnect or file-transfer behavior. The matrix is not a cryptographic audit, public-network test, power-failure campaign, or target-hardware qualification.

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

The human-text adapter preserves bytes, but that does not make native Tox text a binary protocol.
Valid UTF-8 is the interoperable contract. A pending text read receipt also dies with the friend
connection because c-toxcore clears its receipt list on disconnect; neither IoTox nor an operator
may promise that it will arrive after reconnect.

### 8.3 Same-UID local processes are trusted together

Mode 0600 prevents other Unix users, not another malicious process under the daemon account. The same account can write FIFOs, use the control socket, inspect plaintext projections, and attempt path interference. Use a dedicated account. A stronger multi-tenant local security model would require explicit credentials/peer credentials and probably a different surface policy.

### 8.4 Command timeout and cancellation semantics remain sensitive

A caller timing out while an agent command is queued must not leave ambiguity about later physical execution. The current only machine operation is read-only; live human text has no effect authority. Before effects exist, every queued operation needs deadline, cancellation, admission, execution, shutdown, retry, and idempotency rules that survive restart.

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

### 9.1 Finite file transfer as an ordinary peer surface

The finite-file manager and structured one-binary commands already exist. Give them a peer-local
ratox-style entrance without treating arbitrary FIFO bytes as an unbounded stream.

Preserve ADR 0045: local receive acceptance means destination policy passed, a private temporary
file exists, and toxcore accepted RESUME. It is not a completion receipt and must not require the
transfer to remain in the live map. A tiny transfer may already be safely published when the
operator receives the admission response.

Candidate surface:

```text
peers/<KEY>/file-send          private bounded path-record FIFO
peers/<KEY>/file-events        offer/send/receive/control journal
peers/<KEY>/files/<ID>/...     typed per-transfer state and controls
```

One absolute local source path must identify a regular no-follow file. There is no shell parsing,
globbing, remote-selected local path, overwrite-by-default, or execution. Independent transfer
identity must survive simultaneous offers, cancellation, pause/resume, completion, and error
ordering.

### 9.2 Friend lifecycle as ordinary files

Expose incoming request observation and explicit accept/reject/remove through small
request/peer-local paths. Friendship remains transport only and must never rewrite the independent
authorization ledger or grant ownership.

### 9.3 More typed read-only operations

Freeze a bounded argument codec and operation metadata registry, then add harmless reads such as
transport description, capability description, health, and selected sensor values. Keep execution
transport/storage-blind.

### 9.4 Real source-linked native Tox

On the first networked CLI:

```text
fetch and hash pinned archives
build one linked iotox
compile against official headers
run two genuine peers
exchange valid UTF-8 normal/action text and adversarial byte cases; observe real ids/receipts
cross HELLO/confirmation/authority
write the literal command FIFO
cross durable COMMAND/ACK/RESULT
restart both sides
exercise finite file transfer
retain logs and measured timings
```

Fix the program based on real behavior rather than protecting mock assumptions.

### 9.5 Owner re-entry

Implement the exact challenge/transition by which a RecallRoot-reconstructed owner re-enters an
existing ownership domain, rotates authority safely, revokes lost controllers, and resists
replay/rollback without a vendor key.

### 9.6 First mutable operation only after the safety substrate

Before any physical effect, complete deadlines, cancellation, idempotency, execution journal,
restart policy, capability granularity, local hardware abstraction, and destructive fault tests.
The first mutation should be low consequence and reversible.

### 9.7 Later, not now

```text
Tox/Tor route experiment
Tox/I2P route experiment
direct Tor/I2P transports
owner-operated mailbox/automation hub
Mutorr replication integration
mobile UI and consumer polish
```

These remain important. They do not outrank a working native-Tox ratox successor.

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

IoTox rev0012 is a compiled C++20, one-binary ratox-successor foundation in which ordinary private
per-peer `message` and `action` FIFO writes enter the same typed c-toxcore owner-thread path as the
structured client, preserve local bytes while keeping UTF-8 interoperability and disconnect-scoped
receipt truth explicit, without pretending text is a durable command; the separate `command` FIFO
still enters signed durable admission and restart-stable result truth against an exact consumed-ABI
peer mock. Official source-linked c-toxcore, genuine native-network peers, practical file/friend
surfaces, physical effects, and Tox/Tor or Tox/I2P remain future evidence gates.
