# Cloudtainer build report — IoTox rev0018

**Revision:** rev0018
**Version:** 0.18.0
**Codename:** Bounded Dispatcher
**Final-source verification date:** 2026-08-17, America/New_York
**Public product executable:** `iotox`
**Owned implementation language:** C++20
**Pinned c-toxcore target:** 0.2.23

## 1. Executive result

rev0018 crosses the first live Ratox boundary. It joins the previously separate authenticated
session transcript, authority-ledger v2 capability, sealed local terminal-profile registry, and
Linux PTY controller into an Agent-owned, bounded interactive service carried on c-toxcore
custom-lossless packet ID `0xA2`.

The service is deliberately **disabled by default**. A normal Agent still omits Ratox feature bit 23.
Explicit activation must complete before toxcore starts and fails closed unless the profile store,
principal bindings, process factory or helper path, startup timeout, and every service bound are
valid. Only a successfully constructed service may add bit 23 to the immutable local HELLO feature
mask. A peer's unilateral advertisement is not negotiation and cannot reach process admission.

Every inbound Ratox packet is admitted under a fresh join of:

```text
application-ready transcript
mutually confirmed feature bit 23
current friend online epoch
authenticated stable principal
exact current authority-ledger head
interactive.terminal grant
canonical Ratox frame and route-scoped replay state
```

The resulting `RatoxService` owns the bounded coordinator between a resolved local profile, one PTY
controller, the pure interactive session state, replay records, retained output, outbound packets,
and lifecycle evidence. It handles OPEN, ATTACH, RESUME, DETACH, INPUT, output ACK/replay/gap,
RESIZE, PING, CLOSE, EXIT, duplicate admission replay, shutdown, and exact stale-route fencing.
Whole INPUT frames are acknowledged only after complete nonblocking PTY commitment. If a process
accepts only a prefix and the next write fails, rev0018 emits no misleading ACK, discards the
uncertain process, and leaves a bounded terminal tombstone with an explicit failure result.

Outbound packets remain service-owned until c-toxcore accepts them. A retryable SENDQ failure
retains the exact front packet and does not reorder or regenerate terminal traffic. Every retained
packet records whether it depends on terminal authority and is revalidated against the exact
friend/epoch/principal/head immediately before a later send. A signed revocation therefore purges a
previously queued authority-bound OPEN_RESULT before another transport attempt. The only
no-terminal-authority exception is a canonical denial produced for an authenticated but unauthorized
admission request; it contains no terminal data or accepted attachment identity.

The transport crossings shorten sensitive-byte lifetime. Outbound Ratox traffic uses one shared
owner-thread payload allocation whose final release securely wipes its storage after success,
rejection, cancellation, or failure. Inbound Ratox custom-packet storage remains alive through the
metadata-only journal update and is then wiped on normal and exceptional exits. Service replay,
outbound, PTY, and queue-compaction paths have their own explicit wipe points. These controls reduce
retention; they do not claim control over copies inside c-toxcore, the kernel, allocators, swap, crash
dumps, or a compromised process.

The live service is a substantial construction, not a production-completeness claim. rev0018 has no
operator-side streaming terminal client, no daemon-restart PTY supervisor, no two-physical-host
full-service qualification, and no complete namespace/cgroup/seccomp/Landlock sandbox. Public or
default advertisement remains prohibited.

## 2. Security and lifecycle construction

### 2.1 Fail-closed activation before network startup

The Ratox construction gate runs before the Agent starts toxcore. Explicit enablement requires:

1. a normalized absolute profile-store root;
2. a secure owner-only store load for the expected daemon UID;
3. at least one enabled profile and enabled stable-principal binding;
4. either an injected `PtyProcessFactory` or an absolute reviewed helper path;
5. a finite helper startup timeout;
6. validated global session, admission, replay, packet, byte, PTY I/O, event, and shutdown bounds; and
7. successful coordinator construction.

Any failure aborts Agent startup rather than advertising a service that cannot enforce its local
policy. Runtime feature selection is separated into local supported, local required, peer supported,
peer required, and negotiated masks. The local masks become immutable after peer admission. Tests
freeze the default-off, failed-construction, one-sided-offer, and bilateral-negotiation cases.

### 2.2 Exact route, transcript, principal, and authority join

Friend numbers are transient route handles, not identities. A live control is scoped by local replay
domain, friend number, online epoch, authenticated stable principal, session ID, incarnation,
generation, and attachment token as applicable. Delayed controls from an old epoch cannot collide
with or consume the owning route's message IDs.

The Agent serializes accepted signed authority-head mutation with Ratox receive, bounded PTY service,
and retained transport admission. This establishes a deliberate order across otherwise independent
thread-safe components:

```text
old head + bounded Ratox effect
or
new signed head + reconciliation before the next Ratox effect
```

The authority ledger still does not own PTYs or toxcore, and the ordering lock does not make network
or process execution transactional. It closes the local check/effect window between an exact-head
decision and the immediately bounded process or send operation.

Exact-route proof loss and durable principal revocation remain separate transitions. Losing the
current proof fences sessions whose last successful authority route was that friend/epoch. A signed
principal revocation closes all live or detached sessions for that stable principal. A rejected route
cannot retarget the stored revocation owner. Unauthorized absent ATTACH or RESUME requests receive a
retained denial before the service reveals whether the session ID exists.

### 2.3 Bounded PTY coordinator

The coordinator validates all limits at construction and maintains finite ownership of:

```text
live sessions and process controllers
admission replay entries and canonical result bytes
session replay/tombstone state
retained output history and explicit gap state
outbound packet count and total bytes
lifecycle event count
per-cycle PTY writes, reads, generated frames, and transport sends
shutdown progress and deadlines
```

OPEN reserves admission before profile lookup or spawn. ATTACH and RESUME reserve the route before
changing the current attachment. Control replay reservations are committed only after a valid route
and effect; an invalid route cancels rather than burning the message ID. Exact committed duplicates
replay the canonical result, while a different packet under the same scoped ID is rejected as a
conflict.

INPUT is staged as a whole frame. Partial nonblocking writes retain unsent bytes and consume no ACK.
A complete commit advances the accepted sequence exactly once and emits the cumulative ACK. A hard
failure after an uncertain prefix cannot safely retry or claim acceptance, so the controller is
discarded and the session transitions to a bounded failure tombstone.

Output is read under finite byte and frame budgets, assigned monotonic sequence positions, retained
for replay within the configured history bound, and removed only after a valid cumulative ACK. A
resume request before retained history receives an explicit gap rather than invented data. Resize is
clamped through the sealed local profile policy. Close and shutdown use the existing bounded
HUP → TERM → KILL process lifecycle and publish one stable exit result.

Round-robin session cursors are retained across service cycles. Global write/read/frame budgets
therefore cannot let a permanently busy low-index PTY starve later sessions indefinitely.

### 2.4 Transport ownership and sensitive-byte lifetime

Ratox stays on c-toxcore's lossless custom-packet path. IoTox treats c-toxcore enqueue acceptance as
a distinct boundary from peer receipt or application acknowledgement.

```text
encode canonical frame
retain exact packet in bounded service storage
revalidate exact route and terminal-authority dependency
call owner-thread send_sensitive_lossless
accepted: wipe and pop exactly one packet
SENDQ/retryable unavailable: retain identical front packet
stale/nonretryable route: detach and wipe route-owned traffic
```

The ordinary transport adapter copies general packet vectors by value for owner-thread lifetime.
rev0018 adds a sensitive-lossless path specifically for terminal traffic. One shared payload object
owns the copy; closures retain only the shared pointer, and the final release securely wipes the
allocation. Queue rejection and shutdown paths release it as deliberately as the success path.

Inbound packet dispatch uses an exception-safe wipe guard around the transport event vector after
metadata journaling. Runtime lifecycle records may contain bounded route, epoch, principal, session,
frame-type, generation, incarnation, sequence, and typed-error metadata. They exclude terminal
input/output, argv, environment, cwd, filesystem paths, profile IDs, and diagnostic strings.

## 3. Final verification

The exact implementation state passed the maintained clean source matrix:

```text
223/223 registered owned C++ checks through the fixture-aware registry
9/9 CTest entries under GCC debug
9/9 CTest entries under strict GCC -O3 release
9/9 CTest entries under Clang debug
9/9 CTest entries under Clang AddressSanitizer + UndefinedBehaviorSanitizer
9/9 CTest entries under GCC ThreadSanitizer
9/9 CTest entries with host-linked Argon2
11/11 CTest entries in the Mutorr preservation configuration
9 Clang libFuzzer targets x 5,000 units = 45,000 sanitizer-backed executions
```

The final matrix ended with `final-source-matrix=pass`. Warnings are errors in maintained compiler
lanes. The ASan/UBSan registry also passed as four deterministic shards during focused diagnosis,
then passed as one complete CTest lane. No fuzzer emitted a crash artifact.

The nine sanitizer-backed parser/state fuzzers cover:

```text
outer protocol frames
session payloads and transcript state
local control packets
durable command codecs
canonical terminal profile and binding records
authority records and authority sessions
Ratox frames
interactive session, replay, and quota-directory state
complete RatoxService coordination with injected PTY behavior
```

The new service fuzzer mutates authenticated and stale routes, canonical and malformed packets,
duplicate/conflicting replay, outbound retention, disconnect/revocation/shutdown transitions, and an
injected PTY that can partially write, block, close, fail, misreport bounds, emit output, or exit.
After every operation it checks snapshot, event, principal, packet, sequence, replay, tombstone, and
queue invariants.

The dedicated Agent/session stress harness first discovers the linked position of the exact
mock-toxcore Agent case, then starts a distinct process for each repetition. All 100 ordered runs
passed, and the retained log terminates with:

```text
agent-session-stress=100/100 passed shard=1/223
```

The live exact-mock coverage includes:

```text
default-off feature advertisement
fail-closed activation before transport construction
one-sided feature advertisement rejected as not negotiated
bilateral transcript-confirmed negotiation
same-epoch stable-principal proof
v1 authority authentication without interactive.terminal admission
real OPEN dispatch through the Agent and returned canonical denial/result
no-profile-lookup and no-spawn assertions on rejected gates
retained authority-bound OPEN_RESULT across repeated SENDQ
signed revocation followed by purge before another transport attempt
round-robin service fairness
runtime journal privacy and rotation
```

The existing native terminal process suite continues to exercise real Linux PTYs, binary I/O,
window changes, session/process-group/foreground-terminal state, cwd/argv/environment policy,
signal reset, rlimits, `PR_SET_NO_NEW_PRIVS`, ambient-capability clearing, optional UID/GID/group
transition, startup readiness/exec proof, typed setup failures, HUP/TERM/KILL shutdown, and
parent-death termination after final exec.

A sanitizer-sensitive pause/resume regression was made scheduler-independent while retaining a
finite deadline and separate bulk-transfer coverage. The affected ASan/UBSan shard passed 20 fresh
repetitions before the final complete sanitizer lane.

Unavailable optional analyzers in this environment were `clang-tidy`, cppcheck, and shellcheck.
Shell scripts were nevertheless syntax-checked with `bash -n`. Their absence is not described as a
pass and does not broaden the matrix evidence.

## 4. Compiler and source environment

```text
Kernel:  Linux 6.18.35 x86_64 GNU/Linux
CMake:   3.31.6
Ninja:   1.12.1
GCC:     g++ (Debian 14.2.0-19) 14.2.0
Clang:   17.0.0
```

The final owned `include/`, `src/`, and `tests/` C++ surface contains:

```text
120 implementation/header/test files
73,383 lines
223 registered owned C++ checks
```

Including the preserved Mutorr incubator yields 132 C/C++ files and 74,919 lines. Mutorr remains
buildable and independently tested but is not linked into the default product and did not determine
the Ratox service design.

## 5. Source-linked standalone result

The four immutable source archives were recovered from the prior verified offline source package and
independently rehashed against the current lockfile before extraction:

```text
c-toxcore 0.2.23
b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe

c-toxcore cmp 52bfcfa17d2eb4322da2037ad625f5575129cece
4abfd641dd5ccba04b6e0ced04a79755fa70709290b3ba15dbd4b4a2de345ed0

libsodium 1.0.22
adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349

Argon2 20190702
daf972a89577f8772602bf2eb38b6a3dd3d922bf5724d45e7f9589b5e830442c
```

A fresh clean standalone build compiled all four pinned inputs and IoTox from source. The verifier
confirmed that the resulting product contains the source-linked toxcore, libsodium, and Argon2
providers and does not depend on separate runtime copies of those libraries. It remains a normal
Linux PIE executable dynamically linked to the platform C/C++ runtime; “one binary” does not mean a
fully static or cross-distribution portable executable.

```text
IoTox 0.18.0 rev0018
standalone-linked-toxcore-libsodium-argon2=pass
SHA-256 d06272bd015f8afcc1da527d95ced51214e4e624d10d45ad29aacfd4ffd7b56c
```

This proves the local source-link and verifier contract for the recorded host. It does not prove a
genuine two-peer Tox exchange, public bootstrap, NAT traversal, relay behavior, network loss and
reconnect handling, cross-host interoperability, portability, or production hardening.

## 6. Research contract applied

Primary upstream sources reviewed for rev0018 include:

```text
TokTok c-toxcore v0.2.23 release and source
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h

TokTok protocol specification
https://toktok.ltd/spec.html

c-toxcore security advisory referenced by v0.2.23
https://github.com/TokTok/c-toxcore/security/advisories/GHSA-42vg-9mg3-399f

Linux path, privilege, and confinement contracts
https://man7.org/linux/man-pages/man2/openat2.2.html
https://docs.kernel.org/userspace-api/no_new_privs.html
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://docs.kernel.org/userspace-api/landlock.html
```

The v0.2.23 release asset publishes the same c-toxcore SHA-256 pinned by IoTox. Upstream describes
c-toxcore itself as experimental and not independently audited as a complete cryptographic system;
IoTox therefore does not transform successful local integration tests into a broad network-security
claim.

The Tox protocol specifies ordered, retransmitted lossless packet delivery and duplicate handling
inside the transport. IoTox still retains its own application packet until the local toxcore enqueue
call accepts it, because transport reliability does not make a rejected local enqueue successful and
does not replace application acknowledgements, replay windows, authority checks, or terminal byte
commit semantics.

`openat2`-style beneath/root/no-symlink/no-magic-link controls reinforce the descriptor-oriented path
principle already used by the sealed profile and PTY boundary. They address path resolution, not an
attacker who controls the daemon UID, target content, or running process.

The kernel defines `no_new_privs` as a one-way rule preventing `execve` from granting new privilege.
It does not remove existing privilege or restrict ordinary syscalls and filesystem access. Seccomp
can restrict syscalls, and Landlock can restrict filesystem access for a task and descendants within
its supported ABI, but each requires a deliberately tested policy. rev0018 records them as future
R8 confinement work rather than adding an opportunistic filter and mislabeling it a sandbox.

The applied source review and decision mapping are retained in:

```text
docs/research/ratox-agent-dispatch-rev0018.md
docs/decisions/0065-gate-live-ratox-dispatch-before-network.md
docs/protocol-ratox-v1.md
docs/security-ratox-v1.md
```

## 7. Evidence and claim boundary

The exact toxcore mock validates the consumed C ABI and deterministic IoTox Agent, transport,
authority, protocol, filesystem, and process lifecycle behavior. It does not implement Tox
cryptography, DHT, NAT traversal, public bootstrap, relays, congestion, or hostile-network timing.
The source-linked standalone binary establishes local linkage, not two-peer operation.

rev0018 specifically does **not** claim:

```text
an operator-ready local streaming terminal client
PTY survival or recovery after daemon restart
two physical hosts completing the entire Ratox service protocol
public-network reliability or performance
production-default feature advertisement
complete namespace, cgroup, seccomp, or LSM confinement
protection after daemon-UID or process compromise
formal verification or a third-party security audit
```

The next credible construction gates remain independent:

```text
R5  bounded operator-side client and local attachment UX
R6  explicit restart/recovery policy and supervisor ownership
R7  two-host laboratory qualification under loss, reconnect, revocation, and failure
R8  reviewed deployment confinement, support policy, and production enablement criteria
```

This report describes only the exact rev0018 source, retained logs, and verified standalone artifact.
Earlier revision evidence cannot override or broaden a current-source claim.
