# Cloudtainer build report — IoTox rev0017

**Revision:** rev0017
**Version:** 0.17.0
**Codename:** Sealed Profile
**Final-source verification date:** 2026-08-16, America/New_York
**Public product executable:** `iotox`
**Owned implementation language:** C++20
**Pinned c-toxcore target:** 0.2.23

## 1. Executive result

rev0017 completes Ratox prerequisite R3 as a local-only policy and Linux PTY process boundary. It
adds a strict terminal-profile store, exact principal-to-profile bindings, generation-bound policy
resolution, a transport-independent nonblocking terminal controller, and a native Linux backend that
launches one fixed executable through a real pseudoterminal. It does not connect terminal sessions to
the Agent, the local control protocol, or Tox. Ratox feature bit 23 remains unset.

The profile record owns every value that can shape a process: fixed argv, normalized executable and
working-directory paths, a generated terminal type, a small exact environment, optional exact
UID/GID, bounded window policy, resource limits, and shutdown graces. Remote bytes never become a
profile name, pathname, argv element, shell fragment, environment value, identity, or limit. The
canonical decoder rejects aliases, reordering, duplicate fields, unknown fields, noncanonical
numbers, malformed hexadecimal, and trailing data. The complete store fails closed on symlinks,
wrong ownership or modes, unexpected entries, hard-linked records, duplicate IDs, duplicate
principals, or invalid cross-references.

The Linux backend opens and validates the configured executable and working directory before spawn.
It enters the same reviewed IoTox binary through a hidden `posix_spawn` mode, passes only bounded
canonical state and already-open authority-bearing descriptors, verifies two independent
`SO_PEERCRED` observations, creates a fresh terminal session and foreground process group, applies
the exact initial window, clears inherited signal policy, disables exec-time privilege gain, clears
ambient capabilities, applies resource and identity policy, arms a parent-death kill contract, and
uses `fexecve` for the final target. A readiness record plus close-on-exec EOF distinguishes a real
final exec from a merely valid but wrong helper image. Structured stage/errno records preserve setup
failure truth.

The controller preserves binary PTY bytes, never blocks by contract, validates direct backend and
controller bounds, clamps resize requests, uses saturating counters, observes one stable exit result,
and performs HUP → TERM → KILL escalation with fresh monotonic deadlines. A separate supervisor test
kills the controller with `SIGKILL` after final exec and proves that a target intentionally ignoring
HUP and TERM still dies through the parent-death contract. This is lifecycle fencing, not a complete
sandbox or descendant container.

## 2. Final verification

The exact source state passed the clean maintained matrix:

```text
189/189 registered owned C++ checks through the fixture-aware CTest registry
9/9 CTest entries under GCC debug
9/9 CTest entries under strict GCC -O3 release
9/9 CTest entries under Clang debug
9/9 CTest entries under Clang AddressSanitizer + UndefinedBehaviorSanitizer
9/9 CTest entries under GCC ThreadSanitizer
9/9 CTest entries with host-linked Argon2
11/11 CTest entries in the Mutorr preservation configuration
8 Clang libFuzzer targets x 5,000 units = 40,000 sanitizer-backed executions
```

The matrix ended with `final-source-matrix=pass`. No fuzzer emitted a crash artifact. The eight
fuzzers cover outer frames, session payloads, local control packets, durable command codecs,
canonical terminal profile/binding records, authority records and sessions, Ratox frames, and
interactive-session/quota-directory state.

The dedicated Agent/session stress harness first completed the entire 189-check registry, discovered
the linked index of the exact mock-toxcore Agent case, and then ran only that check 100 times. All 100
numbered runs passed. Its self-validating terminal line is:

```text
agent-session-stress=100/100 passed shard=1/189
```

The native terminal process test additionally exercised:

```text
real UNIX 98 PTY binary echo and nonblocking I/O
initial and subsequent window sizes
SID, PGRP, foreground PGRP, cwd, argv, and exact environment
signal-mask and ignored-disposition reset across helper exec
RLIMIT_CORE=0 plus configured soft limits
PR_SET_NO_NEW_PRIVS set/read-back
ambient capability clearing when the fixture can raise one
exact UID/GID/supplementary-group transition when privileged
readiness/EOF startup proof and stage-specific setup failures
wrong-helper, insecure-target, and invalid-direct-backend rejection
HUP, TERM, and KILL shutdown paths
controller-SIGKILL parent-death termination after final exec
```

During strict Clang validation, the new supervisor fixture exposed a warning-as-error defect: a
report-descriptor constant was compiled but not used consistently. The test was corrected to use the
sealed supervisor descriptor everywhere, then the focused GCC and ASan/UBSan PTY tests and the full
clean matrix passed. Earlier sanitizer investigation also reinforced that the PTY payload itself must
remain unsanitized: the profile deliberately applies a finite address-space limit that is incompatible
with ASan's multi-terabyte shadow reservation, while the controller and helper remain sanitized.

## 3. Compiler and source environment

```text
Kernel:  Linux 6.18.35 x86_64 GNU/Linux
CMake:   3.31.6
Ninja:   1.12.1
GCC:     g++ (Debian 14.2.0-19) 14.2.0
Clang:   17.0.0
```

Warnings are errors in maintained compiler lanes. The final owned `include/`, `src/`, and `tests/`
C/C++ surface contains:

```text
116 implementation/header/test files
66,052 lines
189 registered owned C++ checks
```

Including the preserved Mutorr incubator yields 128 C/C++ files and 67,588 lines. Mutorr remains
buildable but is not linked into the default product and did not determine the terminal boundary.

## 4. Source-linked standalone result

The exact pinned source archives were verified before extraction:

```text
c-toxcore 0.2.23  b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe
cmp 52bfcfa17d2e    4abfd641dd5ccba04b6e0ced04a79755fa70709290b3ba15dbd4b4a2de345ed0
libsodium 1.0.22   adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349
Argon2 20190702    daf972a89577f8772602bf2eb38b6a3dd3d922bf5724d45e7f9589b5e830442c
```

The first standalone attempt could not resolve the upstream libsodium host from the isolated build
shell. Construction did not stop. The exact immutable archives retained by the immediately prior
IoTox workspace were copied into rev0017's dependency cache, independently hashed against
`dependencies.lock`, and accepted only because all four digests matched. The build then compiled
c-toxcore, libsodium, and Argon2 into the `iotox` executable and passed
`tools/verify-standalone.sh` with:

```text
standalone-linked-toxcore-libsodium-argon2=pass
```

The resulting executable identified itself as `IoTox 0.17.0 rev0017`. Its final pre-packaging digest
was:

```text
36155962548f09a0b332f7824351310b50391a4272b931b011ff856faec1366f
```

It is a source-linked Linux x86-64 product binary, not a universally portable static executable. It
still uses the host loader, libc, libstdc++, libgcc_s, and libm. Opus and libvpx were absent; the
pinned c-toxcore build therefore omitted optional audio/video support, which the current IoTox
product does not expose.

No public DHT bootstrap, NAT traversal, TCP relay qualification, genuine remote peer, two-host PTY
session, or hostile-host sandbox escape test was exercised by this standalone build.

## 5. Research contract applied

Primary references reviewed for the rev0017 process boundary include:

```text
https://pubs.opengroup.org/onlinepubs/9799919799/functions/posix_spawn.html
https://man7.org/linux/man-pages/man2/execve.2.html
https://man7.org/linux/man-pages/man3/posix_openpt.3.html
https://man7.org/linux/man-pages/man7/pty.7.html
https://man7.org/linux/man-pages/man2/ioctl_tty.2.html
https://man7.org/linux/man-pages/man3/tcsetpgrp.3.html
https://man7.org/linux/man-pages/man2/setsid.2.html
https://man7.org/linux/man-pages/man3/fexecve.3.html
https://man7.org/linux/man-pages/man2/close_range.2.html
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html
https://man7.org/linux/man-pages/man2/PR_SET_NO_NEW_PRIVS.2const.html
https://man7.org/linux/man-pages/man7/capabilities.7.html
https://man7.org/linux/man-pages/man2/getrlimit.2.html
https://man7.org/linux/man-pages/man2/setgroups.2.html
https://man7.org/linux/man-pages/man2/setuid.2.html
https://man7.org/linux/man-pages/man2/setgid.2.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://man7.org/linux/man-pages/man2/wait.2.html
https://man7.org/linux/man-pages/man2/kill.2.html
```

The POSIX spawn contract led to a two-exec design rather than running non-async-signal-safe C++ setup
inside a raw post-`fork` child. Linux PTY documentation led to `posix_openpt`, grant/unlock, a
nonblocking close-on-exec master, preferred `TIOCGPTPEER`, and a bounded `ptsname_r`/`O_NOFOLLOW`
fallback. Session and tty documentation led to an explicit `setsid`, `TIOCSCTTY`, foreground group,
and window-size sequence that the fixture verifies rather than assumes.

`fexecve`, close-on-exec, and `close_range` documentation shaped descriptor-based authority and a
minimal final descriptor set. UNIX-domain peer credentials supplied a kernel-authenticated parent
identity on two separate sockets. Parent-death, no-new-privileges, capability, identity, and rlimit
documentation led to explicit set-and-read-back checks and to re-arming `PR_SET_PDEATHSIG` after a
credential transition because Linux clears that setting on such transitions.

`waitid(..., WNOWAIT)` and `waitpid` permit the leader to remain observable while the controller
issues a last process-group kill before reap. That ordering narrows one lifecycle race but does not
contain descendants that have escaped the original group.

Upstream documentation guided local requirements; it does not prove IoTox correct. The applied
research, precise nonclaims, and implementation mapping are retained in:

```text
docs/research/linux-pty-profile-process-boundary-rev0017.md
docs/decisions/0064-seal-local-terminal-profiles-behind-fork-safe-pty-adapter.md
docs/terminal-profile-v1.md
```

## 6. Construction details

### Canonical local policy

A profile is an exact local record, not a shell command or remotely supplied request. V1 permits at
most 64 profiles, 256 bindings, 32 arguments, 64 resolved environment entries, a 64 KiB record, 4
KiB individual argument/value fields, and 32 KiB of final environment material. Profile IDs,
principal filenames, field order, numeric spelling, hexadecimal case, sorting, and the single final
LF are canonical.

`arguments[0]` and the working directory are normalized absolute paths with no `.` or `..`
components or lexical aliases. The executable path may not name a script; the native backend accepts
an already-open regular ELF object with safe ownership/mode properties. No shell is inserted. The
remaining arguments are fixed policy bytes. The environment starts empty, imports only a small
allowlist explicitly named by policy, adds fixed entries, generates `TERM`, rejects duplicate names
and dynamic-loader/shell-startup variables, sorts deterministically, and passes no other daemon
environment.

The store root, `profiles/`, and `bindings/` are opened without following symlinks and must be private
directories owned by the configured user. Records must be private, single-link regular files with
exact names. A complete load is transactional: one bad or unexpected entry rejects the complete
candidate. `ProfileRegistry::replace` validates profiles, bindings, uniqueness, references, and
generation advance before atomically publishing a new immutable value set under a shared mutex.
Every resolution returns a value copy carrying the generation that authorized it.

### One-binary spawn and descriptor handoff

The parent validates the resolved profile, opens the target and cwd, creates the PTY and two
`SOCK_STREAM|SOCK_CLOEXEC` UNIX socket pairs, encodes one bounded manifest, and spawns the same
already-open IoTox executable through `/proc/self/fd` in an exact hidden mode. Spawn file actions
place stdin/stdout/stderr on the PTY slave and install fixed manifest, status, target, and cwd
descriptors. Spawn attributes clear the inherited signal mask and restore every catchable signal to
default so ignored daemon dispositions cannot silently survive into the final executable.

The hidden child verifies descriptor types and identities before trusting the manifest. Manifest and
status sockets must be distinct stream sockets, and both `SO_PEERCRED` records must agree on PID,
UID, and GID. Standard input, output, and error must identify the same PTY character device. The child
requires one exact canonical manifest, rejects trailing bytes, closes unrelated descriptors, changes
directory through the already-open directory, and never reopens either authority-bearing path.

Immediately before final `fexecve`, the child emits a fixed readiness record. The target and status
descriptors are close-on-exec. The parent accepts startup only after receiving the readiness record
and then EOF. A wrong executable that happens to be valid ELF cannot impersonate successful helper
setup merely by exiting or closing a pipe. Failures before or after readiness carry a fixed stage and
errno record, and timeout cleanup kills and reaps the incomplete child.

### Session, privilege, and parent-death contract

The child creates a new session, acquires the PTY slave as controlling terminal, sets itself as the
foreground process group, and applies the accepted initial dimensions. It sets and reads back
`PR_SET_NO_NEW_PRIVS`, clears the complete ambient capability set and verifies each capability known
to the build, forces both `RLIMIT_CORE` values to zero, and applies each nonzero configured soft limit
only when it does not exceed the inherited hard limit.

Exact identity mode clears supplementary groups, sets real/effective/saved GID and UID to the exact
configured values, and reads all of them back. It fails closed when the caller lacks the required
privilege. The parent PID is derived from the agreeing peer credentials rather than accepted from
manifest bytes. The child installs and verifies `PR_SET_PDEATHSIG=SIGKILL`, confirms the parent did
not change, performs any identity transition, then re-arms and re-verifies the setting because Linux
clears it after credential changes.

The supervisor test is intentionally independent of normal C++ cleanup. It waits until the fixture
reports final-exec state, opens a pidfd where available, kills the supervising controller with
`SIGKILL`, and requires the target to terminate. A bounded procfs start-time/state fallback avoids PID
reuse ambiguity on kernels without the needed pidfd operation.

### Nonblocking control and deterministic shutdown

`PtyProcess` exposes typed nonblocking read, write, resize, signal, and exit observation. Results
separate progress, would-block, and closure. Calls reject oversized requests before touching the
backend, retain no caller buffers, and make exit observation idempotent. `TerminalController`
accounts bytes and operations with saturation, rejects writes and resize after closure begins,
preserves a stable failure status, and never extends a shutdown deadline because of repeated calls.

Close first observes exit, then sends HUP and starts the configured hangup grace. A later poll observes
again before TERM, and again before KILL. The Linux backend signals the original process group.
`waitid(..., WNOWAIT)` keeps the leader waitable long enough for a final group fence, then `waitpid`
performs exactly one reap and decodes an exit or signal result. Output EOF and process exit remain
separate observations.

## 7. Honest boundary and next work

rev0017 proves a local, compiler-clean, sanitizer-clean, fuzzed profile and Linux PTY construction. It
does not prove complete host confinement. `no_new_privs` blocks privilege gain through later exec but
does not filter system calls. Rlimits are coarse and not per-session ownership controls. Clearing
ambient capabilities is inheritance hygiene, not a complete capability-bounding policy. A process
group is not a descendant container. The backend does not install namespaces, seccomp, cgroups, an
LSM policy, a container, or a VM, and it does not prevent a sufficiently capable target from creating
an escaped session or process group.

The profile store is local filesystem policy. It is not a remote protocol object and has no signed
network distribution format. The implementation is Linux-specific because it uses `/proc/self/fd`,
UNIX 98 PTYs, Linux tty ioctls, peer credentials, prctl operations, pidfds/procfs observation, and
Linux close-range behavior. Exact identity transition depends on local privilege. Secure time,
hardware anti-rollback, multi-writer shared storage, and host compromise resistance remain outside
this evidence.

The strongest supportable claim is:

> IoTox rev0017 has a strict local principal-bound terminal-profile store, a generation-bound policy
> resolver, a nonblocking terminal controller, and a Linux one-binary PTY process boundary with
> descriptor-based target/cwd authority, verified session and privilege setup, structured startup
> truth, deterministic escalation, and a tested parent-death kill contract. No terminal service is
> advertised or reachable over Tox.

The next independent Ratox gate is R4: connect the existing negotiated interactive session engine to
this local controller through the Agent without allowing remote profile/path/argv selection. That
work must preserve two-step input commitment, attachment/revocation semantics, output replay and
quota accounting, process-exit truth, and terminal-byte non-logging. Feature bit 23 must remain unset
until genuine two-host authorization, reconnect, revocation, backpressure, resize, exit, and teardown
evidence passes. Stronger confinement should be a separate explicit cgroup/namespace/seccomp or
external supervisor decision rather than an accidental claim attached to the PTY adapter.
