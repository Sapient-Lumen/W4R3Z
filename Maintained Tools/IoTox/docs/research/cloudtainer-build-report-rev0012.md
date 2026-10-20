# Cloudtainer build report — IoTox rev0012

**Date:** 2026-08-14 America/New_York  
**Revision:** rev0012  
**Version:** 0.12.0  
**Codename:** Living Text  
**Immediate northstar:** one-binary modern ratox successor

## Result

rev0012 advances the product rather than only its proving machinery. The one `iotox` executable now
has three literal private per-peer write lanes with deliberately different truth contracts:

```text
message    live normal Tox friend text
action     live Tox action text
command    signed durable IoTox machine operation
```

The human lanes preserve ratox's ordinary-write beauty while remaining honest about their weaker
semantics. They accept bounded byte-preserving local records, call the same typed C++ text path used
by the structured client, receive c-toxcore message identifiers, and expose incoming text and read
receipts. Valid UTF-8 remains the interoperable Tox human-text contract; arbitrary machine bytes
belong to custom packets or file transfer. The lanes do not become offline queues, application
acknowledgements, authority grants, or machine commands.

The machine lane retains rev0011's stronger path: one supported operation is frozen, signed, and
committed to the durable command store before transport. It remains separately authorized and
restart-recoverable.

The final owned source passed the complete retained compiler, sanitizer, race, fuzzer,
linked-provider, process, and preservation matrix. The official pinned source-linked dependency
build still failed before compilation because shell DNS could not resolve the first archive host.
No genuine Tox network claim is made.

The narrow result is:

> The final rev0012 C++20 source gives every projected peer live byte-preserving normal/action
> ingress FIFOs and a distinct durable command FIFO. In exact consumed-ABI process tests, human writes obtain
> valid message identifiers including zero and progress through separate ingress, outgoing,
> incoming, and read-receipt evidence without hidden retry or authority; the machine write still
> receives signed durable identity, exact retry, application receipt/result, and restart continuity.

## Product work completed

### One generalized peer FIFO service

The command-only monitor was replaced with a configurable `PeerFifoServer`. The service receives an
immutable list of lanes and applies only local path and framing policy:

```text
lane name
maximum body bytes
empty-body policy
printable-ASCII or opaque-byte-line policy
```

It owns no Tox instance, durable store, authority decision, retry queue, operation registry, or
result state. Complete records are synchronously handed to the Agent, where each lane enters its
proper product path.

The concrete rev0012 configuration is:

```text
command   0..256 printable bytes by local framing policy; product parser rejects empty/unknown
message   1..1372-byte local ingress to normal Tox text
action    1..1372-byte local ingress to Tox action text
```

LF is the FIFO record delimiter. The local adapter preserves every other byte, including NUL,
carriage return, and high bytes. Current c-toxcore copies the bounded span without UTF-8 validation,
while interoperable Tox human text is UTF-8. A body containing LF uses the structured stdin or hex
command instead of the line-framed FIFO; arbitrary machine bytes use custom packets or file
transfer.

### FIFO atomicity became executable policy

A FIFO is a kernel byte stream, not a message store. Writer boundaries are not visible to readers,
and concurrent writes are only non-interleaved when one complete record is emitted in one write no
larger than `PIPE_BUF`.

rev0012 queries `_PC_PIPE_BUF` on each opened lane. It refuses to monitor that lane if its configured
maximum complete record cannot fit atomically. The maximum human record is 1372 body bytes plus one
LF delimiter. This replaces an implicit Linux-4096 assumption with an executable per-object gate.

The existing hardening remains:

```text
real peer directory, not symlink
same Unix owner
private mode requirements
mkfifo-created path
lstat before open
O_NOFOLLOW open
fstat after open
device/inode equality across path and descriptor
nonblocking reader and separate nonblocking hold writer
eventfd/poll worker
bounded rescans
bounded partial/discard timeout
clean stop notification
```

Peer-directory errors and individual-lane errors now have distinct keys. Missing or repaired paths
clear stale fingerprints so one old structural observation cannot suppress a new state.

### Live normal/action message path

The Agent already had structured normal/action text commands. rev0012 extracted one shared typed
send helper and connected both structured and FIFO ingress to it. The helper resolves the current
public-key peer, performs the send through the serialized toxcore owner thread, and retains the
provider's exact result class.

c-toxcore v0.2.23's text contract is reflected directly:

```text
friend absent          not_found
friend disconnected    unavailable
local send queue full  resource_exhausted
empty/too long/null    invalid_argument
unknown provider code  library_error
```

A successful send returns a per-friend message id. The first valid id is zero. rev0012 therefore
stores `has_message_id` separately from the numeric value. Failed sends do not consume an id in the
exact mock, and tests prove the first later success still receives zero.

No hidden human-message retry was added. A disconnected peer or full c-toxcore send queue yields an
exact rejected ingress event. A future durable human outbox, if ever desired, must define its own
identity, expiry, duplicate, privacy, cancellation, and reconnect contract rather than inheriting
kernel FIFO buffering.

Official v0.2.23 source review also found that c-toxcore clears a friend's pending text-receipt list
when that friend disconnects. IoTox now mirrors this lifetime: the disconnect callback erases every
pending local normal/action correlation for that friend and emits the abandoned count. The exact
mock can deterministically disconnect after message delivery but before receipt; the regression
proves that no stale receipt event appears.

### Evidence layers for ordinary writes

Each peer now projects:

```text
message              normal-message FIFO
action               action-message FIFO
message.help         exact framing and evidence contract
message-events       bounded local ingress acceptance/rejection journal
messages             bounded transport lifecycle journal
```

These observations mean different things:

```text
successful shell write       kernel accepted bytes
accepted message-events row  IoTox framed and submitted the body; toxcore returned an id
outgoing messages row         local transport acceptance was journaled
incoming messages row         a text callback arrived from the peer
receipt messages row          c-toxcore reported friend receipt for that id
```

None means an IoTox machine operation was authorized or executed. Human text never enters the
`COMMAND` decoder and cannot grant capabilities.

The one binary also exposes `peer-message-events` and `peer-message-events-watch`. Existing
`peer-messages` and `peer-watch` remain the transport journal. Structured `message-stdin`,
`action-stdin`, `message-hex`, and `action-hex` support embedded LF and synchronous typed results.

### Durable machine command remains separate

The `command` FIFO continues to converge with `iotox command` before durable identity reservation.
The path remains:

```text
bounded operation record
current peer resolution
persistent nonzero sender epoch and message id
canonical request/frame freeze
stable-device signature
atomic durable store commit
c-toxcore lossless custom-packet attempt
application RECEIVED
capability decision and execution
canonical terminal result
exact duplicate replay
restart recovery
```

Only read-only `device.describe` is registered. The operation executor remains transport- and
storage-blind. No human message is parsed as an operation.

### Runtime and status surface

`RuntimeSnapshot` gained explicit human-lane state:

```text
text-fifo-running
message-fifo-count
action-fifo-count
text-fifo-record-count
text-fifo-rejected-count
```

Command FIFO counts remain separately named. Peer ingress events include timestamp, ingress
sequence, message kind, disposition, stable error code, explicit message-id presence/value, escaped
body bytes, and detail.

Regular runtime projections still use temporary-file replacement so readers do not see partial
content. They are private same-user views, not `fsync`-durable authority.

## Primary-source research applied

### c-toxcore v0.2.23

The pinned public `tox.h` was re-read for normal/action message kinds, the 1372-byte maximum,
`tox_friend_send_message`, `Tox_Err_Friend_Send_Message`, per-friend message ids, read-receipt
callbacks, and serialized `Tox*` access.

The applied boundary is:

```text
successful send = accepted into the local c-toxcore send queue
message id zero = valid first id
read receipt = friend received that message id
application result = not defined by Tox text
```

The FIFO worker never calls toxcore. Every text operation crosses the existing owner-thread command
queue.

### ratox

Ratox's source and README were re-read for the essential experience: one can write ordinary text to
a per-friend FIFO and compose the network with shell tools. Ratox appends local feedback immediately
after its send call; that is useful but is not a remote receipt.

IoTox keeps the ordinary write and splits the evidence more precisely. It also exposes actions as a
distinct lane rather than inventing a chat command prefix.

The original `text_in`/`text_out` names were not adopted. `message`, `action`, `message-events`, and
`messages` name semantic kind and evidence strength explicitly. A later compatibility view must not
weaken those meanings.

### FIFO, pipe, write, and fpathconf contracts

Linux `fifo(7)`/`pipe(7)` and POSIX `write`/`fpathconf` material were rechecked. The implementation
uses the actual opened FIFO's `_PC_PIPE_BUF`, treats LF as an adapter delimiter rather than a body
encoding rule, and keeps partial-record timeout necessary because the hold writer means writer close
cannot delimit a record.

The research note is retained at:

```text
docs/research/c-toxcore-0.2.23-ratox-text-receipt-boundary-rev0012.md
```

The accepted decision is ADR 0043.

## Final-source build and verification evidence

### Environment

```text
kernel: Linux 6.18.35 x86_64 GNU/Linux
CMake: 3.31.6
Ninja: 1.12.1
GCC/G++: Debian 14.2.0-19
Clang/Clang++: 17.0.0
owned C++ source/test files: 86
owned C++ source/test lines: 42219
registered direct C++ checks: 106
public installed product executables: 1
```

### Full matrix

The final source was rebuilt and tested through the same lanes required by
`tools/build-matrix.sh`. Because this cloudtainer terminates a single shell invocation before the
complete clean matrix can finish, each lane ran as an independently fresh, non-overlapping
invocation in the same final-source worktree. The retained aggregate log concatenates those exact
successful lane logs and ends with `final-source-matrix=pass`:

| Lane | Result |
|---|---|
| GCC debug | 8/8 CTest entries passed |
| GCC release | 8/8 passed |
| Clang debug | 8/8 passed |
| Clang AddressSanitizer + UndefinedBehaviorSanitizer | 8/8 passed |
| GCC ThreadSanitizer | 8/8 passed |
| system-linked host Argon2 | 8/8 passed |
| Mutorr preservation | 10/10 passed |
| direct owned runner | 106/106 passed |
| frame libFuzzer | 5,000 units completed |
| session libFuzzer | 5,000 units completed |
| local-control libFuzzer | 5,000 units completed |
| command libFuzzer | 5,000 units completed |
| authority libFuzzer | 5,000 units completed |

The default CTest entries remain:

```text
unit-and-integration
binary-process-lifecycle
client-version
client-help
bootstrap-seeds
recall-generate
client-absent-daemon
lone-entrance-layout
```

### One-binary process evidence

The separate-process test starts `iotox run`, operates it through the same executable, and uses the
exact c-toxcore shared-library mock as a second IoTox peer.

rev0012 added these assertions to the existing session/authority/command/restart path:

```text
structured binary action accepted as first successful id zero
literal message FIFO preserves NUL and CR
normal message receives id one
message-events exposes escaped binary body and explicit id presence
messages exposes outgoing, incoming echo, and friend read receipt separately
unit transport fault abandons pending receipt correlation on disconnect
live text never creates a durable command record
command FIFO still produces durable identity and terminal result
stop/restart preserves savedata, stable identity, authority, and command evidence
```

`tools/run-mock-node.sh` repeats the product-shaped path without rebuilding and passed with a literal
normal-message FIFO write plus durable command operation.

### Retained evidence tooling

rev0012 corrected a mismatch in the evidence tools: the artifact refresher required a standalone
fuzzer log and a `final-source-matrix=pass` marker, but the matrix previously emitted neither.
`build-matrix.sh` now tees the fuzz lane to the revision-derived log and prints the completion marker
only after every required lane passes.

The cloudtainer imposes a hard lifetime on individual shell commands that is shorter than the full
clean matrix. Interrupted aggregate attempts and overlapping verifier processes were discarded; no
partial lane was promoted. Final evidence therefore comes from independently clean lane invocations
with distinct build directories and exact logs. Each required CTest tree retains its own
`Testing/Temporary/LastTest.log`; all five fuzzer executables retain their 5,000-run output; the
100-run Agent shard has an exact line-per-run log and zero exit record. The aggregate
`build-matrix.log` is a deterministic concatenation of those completed logs plus the final marker,
not a reconstruction from prose or memory.

## Defects found and corrected during rev0012

### Pre-start per-lane statistics storage

Rapid repeated process starts found an out-of-bounds read. The event/status path could observe the
new peer FIFO service before `start()` completed, while per-lane counter storage was allocated only
inside `start()`.

The correction establishes:

```text
configured lane shape exists at construction
pre-start counts are defined as zero
start resets values but does not create the shape
all per-lane lookups are bounds checked
```

A regression test queries aggregate and lane statistics before start. Twenty consecutive GCC
start/ping/stop runs and the final full matrix passed after the correction.

This is distinct from rev0011's earlier TSan-detected FIFO service-pointer publication race, which
remains fixed.

### Implicit current-working-directory durability

A packaging rehearsal ran the retained direct unit binary from the datacube source directory and
found newly created `device.identity` and `commands.store` files. Several transient `Agent` tests had
omitted `transport.state_path`; dependent default-path helpers consequently derived durable names
from an empty path and the process current directory. Archive exclusion would have hidden the symptom
without correcting the product boundary.

The final source refuses an empty Tox savedata path in `Agent::start()` before runtime publication,
identity loading, authority loading, or command-store loading. Empty dependent defaults remain empty,
transient tests use explicit temporary savedata paths, the direct retained runner changes into a
disposable directory, and refresh/offline scripts assert that no durable sidecar appeared at the
source root. A dedicated regression verifies the typed `invalid_argument` result and zero created
state.

### Stale compiled numeric version

The process fixture detected that revision strings said rev0012 while `kVersionMinor` still encoded
11. The compiled version now consistently reports 0.12.0/rev0012, and the process/version CTest gates
cover it.

### Stale inventory manufactured a false online epoch

Repeated execution of the canonical Agent fixture found an intermittent `online-epoch=2` after the
mock had emitted only one friend-online callback. The injected first HELLO `SENDQ` occurred in the
real first epoch, but a stale copied offline friend-list snapshot could be applied afterward by a
concurrent refresh. The next online handling then discarded the first transcript and opened a false
second epoch.

The correction makes ordered required friend-connection events the sole authority for online/offline
session transitions. Inventory refresh now reconciles friend existence, public-key mapping, and
presentation only, and its complete collect/apply phase is serialized. Unit and separate-process
fixtures require epoch one together with the exact failed-then-successful HELLO attempt count. The
final Agent integration shard was then repeated 100 consecutive times, each preserving
`online-epoch=1` and `hello-send-attempts=2`. This is evidence for the owned scheduling contract,
not a substitute for real c-toxcore reconnect testing.

A final typed-error audit also found that the Agent's redundant pre-provider length check classified an over-1372-byte human body as `resource_exhausted`, even though the transport boundary and c-toxcore `TOO_LONG` mapping classify it as invalid input. The Agent now returns `invalid_argument`; only genuine c-toxcore `SENDQ` pressure uses `resource_exhausted`, and the transport regression includes an explicit oversized body.

The same audit found an overbroad assertion: the exact peer may independently send a valid
`device.describe` while the test sends a malformed raw command. The negative check now correlates
the exact malformed message id instead of forbidding all unrelated incoming command records.

### Successful incoming file completed before its admission reply

Release-scheduled separate-process verification found an intermittent `file-receive` failure. The
exact mock accepts RESUME and immediately queues a four-byte body plus the zero-length completion
callback. The Agent event pump could write, fsync, publish, and remove that transfer before the local
control thread performed its final live-map lookup. The command then returned `not_found` despite a
safely published destination.

c-toxcore v0.2.23 defines RESUME as acceptance and defines the zero-length receive callback as
terminal completion; it does not promise a minimum delay between them. IoTox now freezes the
accepted record before RESUME and returns it after successful toxcore admission without requiring
continued live-map residency. Publication remains separate asynchronous evidence. The process
fixture reports exact command output on failure and repeated release lifecycles preserve the fixed
boundary. ADR 0045 records the contract.

### Saturation test confused queue scheduling with lifecycle order

The one-slot required-event regression originally required the friend-connection callback to be the
literal next value returned after `friend_added`. A consumer can legitimately dequeue an
observational self/backend event after that event is published but before the same toxcore iteration
reaches the required friend callback. That does not lose or reorder the lifecycle edge.

The test now permits only such observational events while waiting, then requires the connection
edge before any later required friend event. Required-event delivery and callback-owned epoch order
remain unchanged; the correction removes an invalid scheduler assumption from the proof.

### Error-key collision during rescans

Peer-directory structural errors previously shared one lane's reporting key. The scanner now uses a
distinct directory key, and stale fingerprints are cleared when paths disappear or are repaired.
This prevents one observation from suppressing a different lane fault.

### Evidence contract mismatch

As noted above, the matrix and artifact refresh requirements were made mutually executable. A full
artifact refresh can now verify the exact fuzzer log and final completion marker rather than relying
on manual file preparation.

## Source-linked standalone attempt

The product-shaped path was attempted with:

```sh
./tools/build-standalone.sh
```

It exited 6 before compilation. `curl` could not resolve `download.libsodium.org` while fetching the
first pinned archive, including after configured retries.

Therefore this revision does **not** establish:

```text
pinned archive retrieval and SHA-256 verification
official c-toxcore header compilation
source-linked libsodium/Argon2/c-toxcore product
one linked standalone installation
two genuine native Tox peers
real bootstrap, NAT traversal, TCP relay, reconnect, message receipt, or file transfer
```

The exact attempt log and exit status are retained. The successful host-linked Argon2 matrix lane is
useful provider evidence but does not promote the fully pinned standalone build.

## Current evidence boundary

Established for final rev0012 source in this cloudtainer:

```text
one C++20 product executable
GCC and Clang warning-clean compilation
ASan/UBSan and TSan matrix completion
five bounded parser fuzz-smoke lanes
exact consumed c-toxcore ABI loading and callbacks
one serialized toxcore owner thread
binary-preserving normal/action local ingress
valid message id zero handling
exact absent/offline/SENDQ/invalid text status mapping
separate ingress/outgoing/incoming/read-receipt evidence
signed stable device identity and authority ledger
transcript-bound principal proof against exact mock peer
signed durable command admission before transport
application receipt/result and exact duplicate replay
restart continuity for savedata, identity, authority, and command store
private hardened per-peer FIFO/runtime projection
```

Not established:

```text
real c-toxcore ABI/link success
public Tox bootstrap/DHT/NAT/relay behavior
real remote read receipts or queue pressure
security or cryptographic audit
malicious same-UID containment
durable human-message outbox
trusted-clock expiry and cancellation
rollback-resistant or confidential durable stores
safe physical effects
OTA execution
Tox/Tor or Tox/I2P routing
resource/power behavior on target hardware
production readiness
```

The exact mock validates the API surface IoTox consumes and deterministic product semantics. It does
not implement Tox cryptography, DHT, NAT traversal, public bootstrap, relays, congestion, or hostile
network timing.

## Next executable work

The immediate ratox-successor order is:

1. project the existing finite-file manager into a bounded peer-local send/offer/progress/control
   surface with independent transfer identities and no shell parsing;
2. expose explicit friend-request accept/reject and peer removal without granting authority;
3. add more bounded read-only operations behind the existing durable registry;
4. on a networked CLI, build the pinned linked product and cross two genuine native peers through
   binary text/read receipts, session/authority, durable command, restart, relay/reconnect, and file
   transfer;
5. then implement owner re-entry and only later a carefully specified reversible mutable effect.

Tor-routed Tox, I2P-routed Tox, direct overlay transports, Mutorr integration, and physical-device
control remain later gates.

## Decision

Keep Tox. Keep one binary. Keep C++20. Keep the permanent RecallRoot and independent signed
authorization ledger. Keep ratox's ordinary Unix feeling.

Also keep the semantics separate:

```text
human text may be live and simple
machine intent must be durable and authorized
transport receipt is not application completion
friendship is not ownership
local write success is not remote truth
```

rev0012 makes that distinction executable rather than merely aspirational.
