# Cloudtainer build report — IoTox rev0019

**Revision:** rev0019
**Version:** 0.19.0
**Codename:** Controller Stream
**Verification date:** 2026-08-17, America/New_York
**Public product executable:** `iotox`
**Owned implementation language:** C++20
**Pinned c-toxcore target:** 0.2.23
**Outer linked revision:** rev0006

## 1. Executive result

rev0019 completes the R5 private controller-stream construction above rev0018's default-off Ratox
host. It adds a separately gated controller-side Ratox state machine, a canonical same-user local
stream, and one-binary OPEN/RESUME terminal operation without making terminal hosting, terminal
control, or Ratox advertisement default behavior.

The construction keeps five boundaries distinct:

```text
R1  pure Ratox session, replay, and quota state
R2  explicit authority-ledger v2 interactive.terminal capability
R3  sealed local terminal profiles and Linux PTY process adapter
R4  default-off Agent host dispatch over c-toxcore custom-lossless packets
R5  default-off private controller stream and one-binary terminal client
```

Host activation and controller activation are independent. `--enable-ratox-terminal` constructs the
remote process-hosting side and still requires a secure profile store, enabled bindings, and a
reviewed PTY factory/helper. `--enable-ratox-terminal-client` constructs only the controller side; it
loads no local process profile and creates no PTY. Neither flag is implied by the other, and ordinary
startup creates no `terminal.sock`.

The controller accepts one local same-user attachment through
`<runtime>/terminal.sock`, resolves one exact current Tox route to an authenticated stable principal,
and preserves immutable Ratox packets, input replay, output position, and lifecycle state under
explicit bounds. The local client writes remote output before acknowledging it, restores terminal
state, propagates window size, and distinguishes detach from remote close.

This is a substantial construction milestone, not a production remote-shell claim. rev0019 does not
preserve a remote PTY or controller replay state across Agent restart, does not support multiple local
terminal streams, does not establish two-physical-host or impaired-network terminal qualification,
does not enable Ratox by default, and does not claim namespace/cgroup/seccomp/LSM isolation.

## 2. R5 construction

### 2.1 Pure controller state

`InteractiveClient` owns controller-side Ratox state without owning toxcore, sockets, or a local
terminal. Its retained state is finite and includes:

```text
one opening/open/detached/closed lifecycle
exact peer key, friend route, online epoch, and authenticated principal
session ID, incarnation, generation, attachment token, and message correlations
unacknowledged input bytes and next input sequence
retained/delivered output position and cumulative output acknowledgement
immutable outbound Ratox packets until transport acceptance
latest coalescible resize and cumulative ACK
bounded ordered metadata events
```

OPEN requires a nonzero exact peer key and a confirmed route whose negotiated feature mask contains
Ratox. RESUME cannot retarget an established peer or principal. Route loss removes the transient
friend/epoch attachment while preserving only state safe for an exact-session resume. Conflicting
output overlap, sequence overflow, impossible gaps, stale correlations, nonadvancing generations,
and message-ID exhaustion fail closed.

RESUME_RESULT validation is transactional across every peer-controlled coordinate. Input
acknowledgement, output bounds, incarnation, generation, and session identity are validated before any
retained input is released or cursor is advanced. A contradictory reply therefore cannot partially
commit state.

### 2.2 Exact Agent route join

The Agent constructs the controller before transport startup when and only when client activation is
explicit. Once running, a local OPEN is admitted only after the Agent resolves:

```text
exact peer public key
current friend number and online epoch
confirmed bilateral application transcript
negotiated Ratox feature bit
nonzero authenticated stable remote principal
```

The friend number is only a transient route handle. Controller state stores the stable peer and
principal independently and rejects a reply whose route, epoch, principal, session, incarnation,
generation, or correlation no longer matches.

Client-only activation does not load a terminal-profile resolver and cannot call a PTY factory. Host
activation remains separately subject to the rev0018 exact-head `interactive.terminal` authority
join. Enabling a local controller therefore grants no remote process capability.

### 2.3 Private pathname socket

The local terminal entrance is Linux pathname `AF_UNIX` `SOCK_SEQPACKET`. The runtime parent must be a
real normalized absolute directory owned by the effective user and inaccessible to group/other. The
socket is owner-only, accepted peers are authenticated with `SO_PEERCRED`, and descriptors are
nonblocking and close-on-exec.

Pathname checks are performed on both sides of `connect(2)`. The client rejects relative paths and
embedded NUL bytes, records the pre-connect socket device/inode, authenticates the connected peer, and
then rechecks type, owner, mode, device, and inode. A path replacement or alias cannot be silently
accepted after connection.

Server startup and cleanup are inode transactions:

- a non-socket path is never replaced;
- a socket owned by another UID is never removed;
- a reachable listener is never stolen;
- a stale owned socket is removed only after an unchanged device/inode recheck; and
- shutdown unlinks only the exact device/inode bound by that server instance.

Only one local attachment is admitted. The server does not publish an attachment or invoke disconnect
cleanup until the first OPEN handler commits successfully. A rejected OPEN therefore cannot create a
phantom stream or trigger teardown of state that never existed.

### 2.4 Canonical local terminal protocol

Every local record has one canonical 32-byte header:

```text
offset  size  field
0       4     magic "ITTS"
4       1     major = 1
5       1     minor = 0
6       1     packet type
7       1     flags = 0
8       8     nonzero stream ID, big endian
16      8     sequence or cumulative acknowledgement, big endian
24      2     typed IoTox status, big endian
26      2     payload length, big endian
28      4     reserved = 0
```

Payloads are bounded to 16,384 bytes. The implementation and specification are frozen by an exact
32-byte golden vector. OPEN is mandatory as the first packet; later packets retain the same stream ID
and obey exact direction, payload, status, and sequence rules.

Because the local carrier is reliable and message preserving, network replay tolerance is not reused
at this boundary. Duplicate OPENED, inconsistent pre-open gaps, duplicate or out-of-position OUTPUT,
and other impossible local transitions are protocol failures rather than silent retries.

### 2.5 One-binary terminal operation

The public executable exposes:

```text
iotox --runtime RUNTIME terminal PEER_PUBLIC_KEY_HEX
iotox --runtime RUNTIME terminal-resume SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]
```

The interactive client uses scoped terminal-mode and signal ownership. It enters raw mode only after
OPENED, restores prior state on ordinary exits, sends initial and `SIGWINCH` dimensions, writes OUTPUT
to stdout before sending a cumulative OUTPUT_ACK, detaches on stdin EOF, and recognizes beginning-of-
line `~.`, `~d`, `~~`, and `~?` escapes. Error metadata is bounded and printable-sanitized; terminal
bytes are not written to ordinary runtime journals.

## 3. Additional hardening completed during qualification

### 3.1 Optimized packet construction

A clean GCC Release build with warnings-as-errors found that direct insertion of a header into an
initially empty vector could trigger GCC's optimized null-dereference diagnostic. Packet encoding now
constructs the fixed header in `std::array`, reserves the final bounded size, and appends header and
payload. The fix removes the Release blocker without weakening diagnostics.

### 3.2 Deterministic PTY helper startup failure

The PTY adapter uses independent configuration and status sockets. An executable that does not
implement the hidden IoTox child role can close both immediately; depending on scheduling, the parent
could previously observe either configuration-socket `EPIPE`/`ECONNRESET` or status-channel EOF.
Both outcomes rejected the helper, but the typed result was race-dependent.

After any manifest-send failure, the parent now consults the status channel before classifying the
startup. A structured child setup record is preserved, while a closed or malformed helper is
consistently reported at the protocol/readiness boundary. The regression performs eight immediate
wrong-helper attempts per process-suite run, and the optimized process suite passed 100 consecutive
runs after the fix.

### 3.3 Complete fuzz-enabled build graph

The fuzz configuration instruments the static product archive with
`-fsanitize=fuzzer-no-link,address,undefined`. Before rev0019 qualification, only dedicated fuzzer
targets linked the sanitizer runtimes; building every target in the same tree could therefore leave
ordinary executables with unresolved ASan/UBSan symbols.

The product archive now exports the address/undefined-sanitizer runtime link requirement to every
consumer while keeping the libFuzzer main private to dedicated fuzzer targets. A complete
fuzz-enabled all-target build now succeeds, as does the ten-target smoke run.

### 3.4 Release provenance and count accuracy

The governing source identity, package contract, active report, and executable evidence are all
rev0019/0.19.0. The final linked registry contains 269 checks, not the earlier intermediate count of
260. Active documentation and retained validation use the final count; historical revision reports
remain unchanged.

### 3.5 Scheduler-independent concurrent-registry evidence

Repeated optimized qualification exposed a test-harness assumption rather than a registry data race:
the publisher could finish all 512 replacements before the operating system scheduled any reader,
leaving the observer count at zero even though every published generation was mutex-coherent. The
regression now waits until every reader is ready and until the released reader set has completed a
minimum observation before the publisher loop begins. The coherence checks remain unchanged; only the
scheduler-timing shortcut was removed.

## 4. Final-source verification

### 4.1 GCC Debug and direct registry

Toolchain:

```text
g++ (Debian 14.2.0-19) 14.2.0
CMAKE_BUILD_TYPE=Debug
warnings-as-errors enabled
```

Results:

```text
269/269 fixture-aware owned C++ checks
11/11 default CTest targets
```

The direct registry uses the exact mock c-toxcore and Argon2 providers and the pinned embedded EFF
word-list input. It covers protocol, authority, durable state, file transfer, interactive host and
controller state, terminal profile/process abstractions, local control and terminal sockets, runtime
projection, Agent integration, and toxcore owner-thread behavior.

### 4.2 GCC optimized Release

Toolchain:

```text
g++ (Debian 14.2.0-19) 14.2.0
CMAKE_BUILD_TYPE=Release (-O3 -DNDEBUG)
warnings-as-errors enabled
```

After the packet-construction and helper-startup fixes:

```text
11/11 CTest targets passed in three successive parallel suite runs
100/100 standalone optimized terminal POSIX process-suite runs passed
```

The repeated process suite includes real Linux PTY creation, raw binary I/O, window changes,
session/process-group/foreground-terminal checks, cwd/argv/environment policy, signal reset, resource
limits, `PR_SET_NO_NEW_PRIVS`, ambient-capability clearing, optional identity transition, startup
readiness plus exec proof, typed setup failures, HUP/TERM/KILL escalation, and parent-death behavior.

### 4.3 Clang Debug

Toolchain:

```text
clang version 17.0.0
CMAKE_BUILD_TYPE=Debug
warnings-as-errors enabled
```

Result on the final source:

```text
11/11 default CTest targets passed
```

This independent compiler lane includes the complete 269-check registry, the Linux PTY process
fixture, the one-binary lifecycle, authority ceremony, and terminal CLI error boundaries.

### 4.4 GCC ThreadSanitizer

Toolchain:

```text
g++ (Debian 14.2.0-19) 14.2.0
CMAKE_BUILD_TYPE=Debug
ThreadSanitizer enabled
warnings-as-errors enabled
TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1
```

Results on the final source:

```text
16/16 deterministic registry shards passed
269/269 registry checks selected exactly once
no ThreadSanitizer diagnostic was reported
```

The scheduler-independent profile-registry regression is included in these shards together with the
controller state machine, socket callback shutdown, replay reservations, Agent synchronization, and
other owned concurrent boundaries. Process-level TSan qualification is not promoted beyond the
retained registry evidence stated here.

### 4.5 Clang ASan + UBSan

Toolchain:

```text
clang version 17.0.0
CMAKE_BUILD_TYPE=Debug
AddressSanitizer enabled
UndefinedBehaviorSanitizer enabled
warnings-as-errors enabled
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1:abort_on_error=1
UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1
```

Results on the final source:

```text
16/16 deterministic registry shards passed
269/269 registry checks selected exactly once
no ASan, leak, or UBSan finding was reported
```

The monolithic sanitizer registry is intentionally not promoted as evidence because its aggregate
runtime exceeded the execution wrapper used for this build session. The same complete registry was
run as 16 bounded leak-enabled shards; every registered index was selected exactly once.

### 4.6 Sanitizer-backed fuzzing

The complete Clang fuzz-enabled build graph succeeded. Ten libFuzzer targets then completed 1,000
units each:

```text
outer IoTox frame
session payload/transcript
local control protocol
local terminal protocol
command codecs
terminal profile/binding records
authority records and authority sessions
Ratox frame
interactive session and quota-directory state
complete RatoxService coordination with injected PTY behavior
```

Result:

```text
10 targets x 1,000 units = 10,000 sanitizer-backed executions
10/10 targets reached Done 1000 runs
no ASan/UBSan/crash artifact marker
```

The new local-terminal target uses a maximum input length of 16,417 bytes, enough for the full 32-byte
header, maximum payload, and one extra byte beyond the canonical packet ceiling.

### 4.7 One-binary mock lifecycle

The retained fixture-aware node lifecycle completed with:

```text
mock-node-lifecycle=pass
```

This crosses actual executable startup, private runtime creation, mock toxcore loading, local control,
controller activation boundaries, and clean shutdown. It is a deterministic provider-backed process
fixture, not a genuine c-toxcore network or two-host terminal test.

### 4.8 Pinned standalone attempt

The final clean-source qualification also invoked `tools/build-standalone.sh` with source-input
packaging enabled. The script reached the first immutable dependency fetch, retried the pinned
libsodium 1.0.22 URL, and exited with curl status 6 because this container could not resolve
`download.libsodium.org`. Compilation did not begin, no standalone binary was produced, and the
official-source provider lane remains unverified. The exact attempt output and exit code are retained
under `artifacts/reports/standalone-attempt.*`.

## 5. Evidence not run in this revision

The following lanes were not executed against the final rev0019 source in this build session and are
not claimed:

```text
linked system Argon2 lane
Mutorr preservation lane
coverage threshold run
verified official-source standalone c-toxcore build (attempt blocked at DNS before compilation)
genuine Tox bootstrap and two-peer network exchange
two-physical-host terminal stream
UDP/TCP impairment, reconnect, queue-pressure, and long-soak laboratory
daemon-restart PTY/controller persistence
namespace/cgroup/seccomp/Landlock production sandbox qualification
```

The repository retains tools and prior historical evidence for several of these lanes. Historical
passes are not silently promoted to final-source rev0019 qualification.

## 6. Research boundary

Primary platform and provider sources rechecked for this revision include:

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/accept.2.html
https://man7.org/linux/man-pages/man3/termios.3.html
https://man7.org/linux/man-pages/man2/ioctl_tty.2.html
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/blob/master/INSTALL.md
https://docs.kernel.org/userspace-api/landlock.html
https://docs.kernel.org/filesystems/proc.html
```

These sources define relevant provider, pathname socket, peer-credential, terminal, process, and
kernel behavior. They do not audit, endorse, or approve IoTox. The project continues to pin
c-toxcore 0.2.23 because that release contains the currently targeted critical security fix; a source
pin remains distinct from a successful genuine-provider build in this environment.

## 7. Retained evidence map

Tracked evidence:

```text
artifacts/reports/validation-summary.txt
docs/research/cloudtainer-build-report.md
docs/research/cloudtainer-build-report-rev0019.md
docs/research/ratox-controller-stream-rev0019.md
docs/decisions/0066-separate-private-terminal-controller-stream.md
docs/terminal-client-v1.md
```

External build-session logs used to derive the compact tracked summary:

```text
/mnt/data/iotox-rev0019-validation/gcc-debug-direct-final.log
/mnt/data/iotox-rev0019-validation/gcc-debug-ctest-final.log
/mnt/data/iotox-rev0019-validation/clang-debug-ctest-final.log
/mnt/data/iotox-rev0019-validation/gcc-release-three-runs-bounded.log
/mnt/data/iotox-rev0019-validation/gcc-release-terminal-posix-100.log
/mnt/data/iotox-rev0019-validation/tsan-16-testbarrier-final/shard-0.log ... shard-15.log
/mnt/data/iotox-rev0019-validation/asan-16-testbarrier-final/shard-0.log ... shard-15.log
/mnt/data/iotox-rev0019-fuzzer-smoke-final-1000.log
/mnt/data/iotox-rev0019-mock-node-final.log
```

The repository-datacube is generated only from a clean committed tree. Its metadata records the exact
commit and checksums every retained file. Renaming the verified outer artifact to the requested
linked-revision filename does not change its embedded rev0019 source identity.

## 8. Final claim

The supported claim is narrow and evidence-backed: IoTox rev0019 constructs a default-off,
controller-side Ratox stream with exact route/principal fencing, bounded replay, a canonical
owner-private same-user local protocol, inode-safe pathname handling, and one-binary OPEN/RESUME
terminal operation. The final owned registry, GCC and Clang Debug suites, repeated optimized Release
suites, GCC ThreadSanitizer shards, leak-enabled Clang ASan/UBSan shards, real PTY process stress,
complete fuzz-enabled build, ten fuzzer smoke targets, and mock lifecycle passed on the source
described here.

Production-default enablement remains prohibited until restart recovery, genuine two-peer networking,
physical-host latency/impairment qualification, longer sanitizer/race/soak evidence, and an explicit
support and sandbox policy are completed.
