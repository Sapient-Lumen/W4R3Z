# Cloudtainer build report — IoTox rev0015

**Revision:** rev0015  
**Version:** 0.15.0  
**Codename:** Ordinary Request  
**Final-source verification date:** 2026-08-14, America/New_York  
**Public product executable:** `iotox`  
**Owned implementation language:** C++20  
**Pinned c-toxcore target:** 0.2.23

## 1. Executive result

rev0015 closes the missing first step in the ratox-style friendship loop. The one `iotox` product
can now initiate an outgoing Tox friend request by one ordinary write to a private root FIFO, while
retaining the typed local control operation and one serialized toxcore implementation underneath.
The new local record carries the complete c-toxcore input rather than inventing a public-key-only or
whitespace-shaped shortcut:

```text
76 hexadecimal complete-address bytes
1 literal TAB
1..921 request-message bytes
1 LF record delimiter
```

The complete 38-byte Tox address reaches `tox_friend_add` unchanged after exact hexadecimal decode.
The message field preserves every non-LF byte, including TAB, NUL, CR, spaces, and high bytes. The
ordinary façade owns framing and path hardening only. It does not own a second friendship state
machine, retry queue, authority model, or provider policy.

The final owned source passed:

```text
121/121 compiled C++ checks in the retained direct run
8/8 CTest entries under GCC debug
8/8 CTest entries under GCC release
8/8 CTest entries under Clang debug
8/8 CTest entries under Clang ASan + UBSan
8/8 CTest entries under GCC ThreadSanitizer
5 Clang libFuzzer targets x 5,000 units
8/8 CTest entries with host-linked Argon2
10/10 Mutorr preservation CTest entries
100/100 exclusive fresh-process Agent/session repetitions
the separate-process one-binary lifecycle fixture
the one-binary mock-node lifecycle fixture
the lone-entrance root-layout check
```

The retained full matrix terminates with:

```text
final-source-matrix=pass
```

A source-linked standalone build was attempted again. It stopped before compilation because this
shell could not resolve `download.libsodium.org` while fetching the first pinned archive. The exact
curl retries and exit status 6 are retained. No official c-toxcore object, public DHT bootstrap,
NAT traversal, TCP relay, genuine remote peer, Tor route, or I2P route ran in this cloudtainer.

The strongest honest claim is therefore:

> IoTox rev0015 is a cleanly built and heavily exercised C++20 ratox-successor construction whose
> exact outgoing-request FIFO converges on the same bounded, serialized provider operation as its
> structured local API. It is not yet evidence of a real Tox-network friend request.

## 2. Environment and source size

The final evidence used:

```text
Kernel:  Linux 6.18.35 x86_64 GNU/Linux
CMake:   3.31.6
Ninja:   1.12.1
GCC:     g++ (Debian 14.2.0-19) 14.2.0
Clang:   17.0.0
```

Warnings are errors in all owned product lanes. The matrix removes and recreates its lane build
directories, so current evidence is not inherited from stale objects.

The default owned C++ tree contains:

```text
89 implementation/header/test files
45,965 lines across include/, src/, and tests/
121 registered owned C++ checks
```

The preserved Mutorr incubator brings the combined C++ tree to 101 files and 47,501 lines, but it is
not linked into the default product and did not determine the rev0015 direction.

## 3. Research contract applied

The primary review for this revision is recorded in:

```text
docs/research/c-toxcore-0.2.23-ratox-outgoing-request-ingress-rev0015.md
docs/decisions/0049-root-request-fifo-is-an-exact-complete-address-adapter.md
```

The binding facts from pinned c-toxcore 0.2.23 are:

```text
Tox address size:                   38 bytes
long-term public key:               32 bytes
nospam field:                        4 bytes
checksum:                            2 bytes
maximum friend-request message:    921 bytes
minimum friend-request message:      1 byte
provider operation:                tox_friend_add
accepted address input:            complete Tox address, not public key alone
accept-incoming operation:          tox_friend_add_norequest(public key)
Tox object concurrency rule:        serialized access
friend-number stability:            process/savedata-local and reusable
```

The upstream header also gives the provider—not IoTox's line parser—authority over checksum, own-key,
already-sent/already-friend, changed-nospam, allocation, and other friend-add outcomes.

Ratox proved the human-interface proposition: beginning a secure peer relationship can feel like
writing one ordinary object. IoTox retains that quality but does not copy ratox's first-whitespace
search, hidden default request message, C-string discovery, or implication that a local file write is
remote acceptance.

FIFO/POSIX review binds the local transport contract. A FIFO is a byte stream; read boundaries are
not writer boundaries. The complete maximum record is 999 bytes including LF. The service queries
the opened FIFO's actual `_PC_PIPE_BUF`, refuses a lane below 999, and requires producers to perform
one complete write for atomic multi-writer framing.

## 4. What changed in executable code

### 4.1 Exact finite request decoder

New files:

```text
include/iotox/local/friend_request_fifo.hpp
src/local/friend_request_fifo.cpp
```

The decoder accepts one record excluding LF:

```text
<76 hex complete Tox address><TAB><1..921 message bytes>
```

Properties frozen in code:

- uppercase and lowercase address hex are accepted;
- exactly 76 address characters are required;
- the separator exists at exactly byte 76 and must be TAB;
- the message must contain 1..921 bytes;
- no trimming, token search, Unicode normalization, shell parsing, default message, or C-string
  discovery occurs;
- the message owns every non-LF byte after TAB;
- embedded LF is outside this line adapter's representable set and requires a future framed local
  operation rather than ambiguous escaping.

The parser may know no peer, a trustworthy 32-byte public-key prefix, or a complete decoded address.
Those states are represented distinctly.

### 4.2 The root `request` inode is now alive

The private runtime root now publishes:

```text
request                 mode-0600 FIFO
request.help            exact grammar and evidence limits
friendship.help
friend-events
```

The established friendship surface remains:

```text
requests/<PUBLIC_KEY>/accept
requests/<PUBLIC_KEY>/reject
peers/<PUBLIC_KEY>/remove
```

The entire ordinary lifecycle is therefore writable without introducing another daemon:

```text
send outgoing request
accept incoming request
reject incoming request
remove established transport friend
```

All four paths remain transport friendship operations. None grants, revokes, or substitutes for
IoTox application authority.

### 4.3 One hardened FIFO implementation now supports two layouts

`PeerFifoServer` now has explicit layouts:

```text
public_key_directories
root_lanes
```

The same implementation performs:

```text
O_NOFOLLOW open
lstat/fstat opened-inode agreement
FIFO type check
daemon owner check
mode-0600 check
actual _PC_PIPE_BUF query
bounded buffer
LF framing
partial-record expiry
overflow recovery
replacement rescan
finite statistics
```

An unknown layout enum fails closed.

The semantic difference is explicit. Public-key directory lanes are dynamic projections. A
configured process-wide root lane is a promised entrance. Startup fails if it is absent or invalid,
and live status becomes unready if the monitored root request FIFO disappears. Merely leaving a FIFO
inode in the runtime tree is not treated as a running service.

### 4.4 Ordinary and structured ingress converge

The existing local protocol operation and the new FIFO call one Agent method under one friendship
lifecycle mutex. That method queues one `tox_friend_add` operation onto the exclusive toxcore owner
thread.

The data path is:

```text
ordinary FIFO or structured SOCK_SEQPACKET request
        -> exact typed request object
        -> Agent friendship serialization
        -> ToxTransport owner-thread command
        -> tox_friend_add
        -> normalized provider result
        -> peer/runtime reconciliation
        -> bounded friendship lifecycle evidence
```

No FIFO worker calls toxcore directly. No separate retry policy or shadow friend database was added.

### 4.5 Evidence is deliberately layered

A successful root write establishes only this first fact:

```text
write(2) success = kernel admitted the bytes
```

Subsequent facts are separate:

```text
parser accepted record
local tox_friend_add accepted state
a public-key peer projection became visible
the packet traversed a network
the remote Tox client received it
the remote person accepted it
an IoTox session became compatible
a stable principal proved identity
the authority ledger granted capability
```

`request-send disposition=requested` means local c-toxcore admission only. It does not claim remote
receipt, remote acceptance, connectivity, IoTox protocol confirmation, ownership, or authorization.

### 4.6 No fabricated peer for malformed input

A malformed record may fail before any identity is trustworthy. The historical friendship event
shape expected a public key, which made an all-zero placeholder tempting. rev0015 adds an explicit
keyless lifecycle state rendered as:

```text
public-key=unknown
```

A canonical 64-hex prefix may be retained as a diagnostic public-key hint only when that prefix was
actually decoded. IoTox never manufactures a plausible peer merely to fill an event field.

### 4.7 Successful admission joins the existing lifecycle

After provider admission, IoTox reconciles the canonical uppercase public-key peer projection. The
same peer can then be removed through its existing exact `remove\n` FIFO. Lookup and deletion remain
bound to public key in one owner-thread operation; current numeric friend numbers are evidence only.

The authorization ledger sequence, head, principals, roles, and capabilities remain unchanged across
request send, accept, reject, and transport removal.

## 5. Test evidence

### 5.1 Direct owned C++ registry

The retained direct runner reports:

```text
tests=121 selected=121 shard=0/1 failures=0
```

rev0015 adds or strengthens coverage for:

```text
minimum and maximum outgoing-request records
uppercase/lowercase complete-address hex
complete 38-byte decode
TAB/NUL/CR/space/high-byte message preservation
short/long/empty/malformed-hex/wrong-separator rejection
root-lane startup and direct monitoring
maximum record plus LF against actual PIPE_BUF
symlink, regular-file, mode, owner, and opened-inode rejection where host permits
partial-record expiry and overflow recovery
lane replacement and rescan
required-root readiness behavior
invalid layout rejection
shared typed/FIFO Agent operation
explicit keyless malformed evidence
trustworthy-prefix-only diagnostics
provider admission and public-key projection
unchanged authorization ledger
status failure when the promised lane disappears
narrow success language that does not claim remote acceptance
```

All earlier identity, RecallRoot, authority, session, durable command, text, file, state-store, local
IPC, runtime-tree, and transport checks remain in the same registry and passed.

### 5.2 Separate-process one-binary fixture

`iotox.binary-process-lifecycle` starts the actual `iotox run` process and then uses the same binary
as the operator client. It crosses the process, socket/FIFO, filesystem, queue, owner-thread,
callback, store, and restart boundaries.

rev0015 extends it through:

```text
root request FIFO existence/help/status
malformed root write -> explicit keyless rejection evidence
exact complete-address root write -> local requested evidence
canonical public-key peer projection
literal public-key-bound removal of that temporary peer
continued incoming accept/reject, session, authority, text, command, and file paths
orderly shutdown and restart
```

The fixture polls asynchronous projections separately. FIFO write completion is never used as proof
that provider mutation or journal publication has completed.

### 5.3 Compiler and dynamic-analysis matrix

The final matrix passed:

```text
GCC debug                  8/8 CTest entries
GCC release                8/8 CTest entries
Clang debug                8/8 CTest entries
Clang ASan + UBSan         8/8 CTest entries
GCC TSan                   8/8 CTest entries
GCC host-linked Argon2     8/8 CTest entries
Mutorr preservation       10/10 CTest entries
Clang libFuzzer             5/5 targets x 5,000 units
```

The fuzz targets cover the outer frame, session payload, local control packet, durable command, and
authority record/session decoders. The fixed request grammar is covered by exhaustive finite
boundary/unit cases and the actual process path; it does not receive a ceremonial fuzzer target
merely to increase the target count.

### 5.4 Repeated Agent/session proof

The exclusive stress harness discovered the linked Agent test shard and ran it in 100 fresh
processes. Its atomic published transcript contains exactly runs 001 through 100 once and ends with:

```text
agent-session-stress=100/100 passed shard=1/121
```

A foreground orchestration wrapper first expired before the harness could publish. Because the
harness stages privately and publishes only after self-validation, that interrupted attempt created
no partial green evidence. The final detached run acquired the same exclusive lock and published one
canonical transcript with exit zero.

### 5.5 Mock-node lifecycle

The one-binary mock-node script passed after exercising:

```text
private runtime and stable savedata-backed address
root request lane health
owner/device authority bootstrap
profile name/status mutation
canonical HELLO and transcript confirmation
application-ready session state
normal/action text and read receipts
ordinary ratox-style text write
durable device.describe request/result path
finite file lifecycle
shutdown and restart
```

This is exact adapter/process evidence against a controlled c-toxcore ABI double. It is not network
evidence.

## 6. Construction defects found and retained

### 6.1 Process-global mock fault was consumed by an unrelated new peer

The fixture armed a one-shot “next lossless send fails” hook and assumed one intended session would
consume it. The new request-created peer changed send ordering. The fixture now removes the temporary
peer before deliberate session fault injection. The remaining design debt is explicit: future mock
fault plans should be peer- and operation-bound rather than process-global.

### 6.2 Malformed records initially lacked an honest identity state

The lifecycle event type expected a public key even when parsing failed before one existed. A fake
zero key would have made evidence structurally convenient and semantically false. An explicit keyless
state now carries that truth.

### 6.3 A promised root FIFO could disappear while aggregate status stayed green

Dynamic peer lanes and required root entrances were initially generalized without distinct readiness
semantics. The service now requires every root lane at startup and includes current monitored-root
count in live readiness.

### 6.4 An unfinished ephemeral worktree was reclaimed

An early green rev0015 branch disappeared from an ephemeral workspace. The released rev0014 cube was
immutable, so the validated changes were replayed from that base and rebuilt. Unreleased workspace
state is not evidence; the self-contained datacube and final logs are.

### 6.5 Clean GCC Release found an implicit packet precondition

The first clean full-matrix attempt stopped because GCC's null-dereference analysis proved that the
lossless-send path could call `packet.front()` without an explicit non-empty source precondition.
Existing debug callers supplied non-empty packets, but caller habit was not a sufficient contract.
The path now checks `!packet.empty()` before reading the discriminator. The failed transcript was not
converted into success; the complete matrix was regenerated from corrected source and passed.

### 6.6 Foreground stress orchestration expired without publishing evidence

The first 100-run invocation exceeded an external foreground wrapper limit. The stress tool behaved
correctly: its staged transcript was removed and no exit-zero evidence file appeared. A detached run
then completed under the exclusive lock and atomically published the validated 100/100 transcript.

### 6.7 Retained binaries and retained prose briefly named different revisions

Artifact refresh replaced the executable evidence and reports but left the manually maintained
`artifacts/README.md` describing rev0014. Checksums remained internally valid, yet the human entrance
to the evidence set was stale. The refresh tool now generates that README from current revision,
codename, and registered-check metadata before freezing `SHA256SUMS`. A future revision cannot obtain
a green refreshed artifact set while preserving the previous revision's artifact prose unnoticed.

## 7. Standalone and real-provider gate

The intended standalone tool remains:

```text
tools/build-standalone.sh
```

It pins and verifies source archives for:

```text
c-toxcore 0.2.23
libsodium 1.0.22
Argon2 20190702
```

The final attempt failed at the first archive fetch:

```text
host:    download.libsodium.org
failure: DNS resolution
curl:    exit 6 after retained retries
stage:   before provider compilation
```

Therefore these claims remain prohibited:

```text
official c-toxcore linked and executed
real savedata compatibility proved
real outgoing request delivered
real incoming request accepted
DHT bootstrap proved
NAT traversal proved
TCP relay fallback proved
Tox/Tor proved or leak-contained
Tox/I2P proved or leak-contained
genuine remote text receipt proved
genuine file transfer proved
```

The next networked-CLI gate should build the pinned providers, run two genuine local/remote IoTox
nodes, and drive request/accept/remove, session confirmation, text/receipt, durable command, and
finite-file paths through real callbacks before making public-network maturity claims.

## 8. Governance and architecture result

rev0015 reinforces these accepted rules:

```text
one installed product executable: iotox
one exclusive toxcore owner thread
one typed semantic implementation per operation
ordinary files/FIFOs are compatibility façades, never shadow state machines
complete provider inputs remain complete through local adapters
Tox friendship is not IoTox authority
public-key selection is stable; friend numbers are evidence
write success, provider admission, remote receipt, and execution are distinct
required runtime entrances fail closed
no fabricated identity in evidence
reserved Tor/I2P routes do not silently fall back to native
BOOTSTRAPROSE.md remains the lone ordinary root entrance
```

This is the correct shape for a stronger ratox successor: ordinary at the surface, explicit and
bounded underneath.

## 9. Immediate next construction

The next ratox-successor gap is ordinary self-profile mutation. Typed operations already exist for
self name, status message, and presence, and the runtime tree already projects their current values.
The next revision should decide and implement exact write lanes—likely under `self/`—that converge on
those same typed Agent/owner-thread operations.

That work must decide:

```text
which inodes are writable FIFOs versus read-only projections
whether name/status-message use LF-delimited bytes or exact length-bearing local frames
how an empty value is represented without an ambiguous empty FIFO record
whether presence uses exact finite tokens
how provider success, savedata persistence, and runtime publication are ordered
what survives restart and what evidence proves it
how replacement/mode/owner/PIPE_BUF checks reuse the existing service
```

It should not create another product process, generic plugin system, Mutorr dependency, Tor/I2P
implementation, OTA path, GPIO layer, or physical effect. The immediate northstar remains literal
construction of the one-binary ratox successor.
