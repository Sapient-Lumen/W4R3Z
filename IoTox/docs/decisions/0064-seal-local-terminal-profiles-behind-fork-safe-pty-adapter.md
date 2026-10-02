# ADR 0064: Seal local terminal profiles behind a fork-safe PTY process adapter

Status: accepted
Date: 2026-08-16

## Context

Ratox R1 provides a transport-independent session engine and R2 provides an explicit
`interactive.terminal` authority bit, but neither is allowed to create a process. R3 needs a real
local process boundary before Agent dispatch is attempted. That boundary must not turn a remote
OPEN into a command line, inherit ambient loader state, run non-async-signal-safe product code after
a multithreaded `fork`, confuse process exit with PTY EOF, or leave child ownership and shutdown
semantics implicit.

A profile is operator policy, not peer input. The first implementation therefore needs one exact
local profile per proven principal, immutable for one OPEN attempt. The profile must freeze argv,
working directory, environment selection, terminal type, dimensions, identity, limits, and close
graces. Missing, disabled, ambiguous, malformed, or insecure policy must deny creation before any
process side effect.

Linux PTY creation also crosses several subtle boundaries: master/slave allocation, session and
controlling-terminal setup, descriptor remapping, child-setup error reporting, final `exec`,
nonblocking I/O, process-group signaling, exit observation, and reap. A plain `fork` followed by C++
work in the child is not acceptable in the future multithreaded Agent. A successful `posix_spawn`
alone is insufficient evidence that the reviewed IoTox internal child completed its second exec into
the locally selected target.

R3 must remain unreachable from the network. Ratox feature bit 23 stays absent, Agent has no Ratox
dispatcher, and no CLI terminal client is added.

## Decision

Introduce three independent product layers:

1. `terminal_profile` owns the canonical local profile/binding format, secure tree loader,
   generation-bound registry, environment resolution, and dimensions policy.
2. `terminal_process` owns a narrow nonblocking `PtyProcess` interface plus a deterministic
   `TerminalController` lifecycle state machine. Tests use a fake backend.
3. `terminal_posix` implements the Linux PTY backend and the one-binary hidden child entrance.

### Local-only profile selection

The store is exactly:

```text
ROOT/
├── profiles/<profile-id>.profile
└── bindings/<64-lowercase-hex-principal>.binding
```

`ROOT`, `profiles`, and `bindings` are opened component by component from `/` with no symlink
following. They must be owner-only directories owned by the configured daemon UID. Every record
must be an owner-only, single-link regular file with a bounded size; hidden names, unexpected names,
extra root entries, symlinks, and hard links reject the complete load.

Records are strict canonical text. Decoding requires exact field order, lowercase hex, one trailing
LF, no unknown fields, bounded counts and bytes, and byte-for-byte canonical re-encoding. A profile
ID is a bounded lowercase token. A binding maps one nonzero stable principal to one profile. The
registry sorts and validates a candidate replacement before changing authority; invalid replacement
leaves the prior generation intact. Every successful replacement increments a nonzero generation,
and each resolved profile carries that generation.

The wire never names a profile and never supplies argv, shell text, paths, environment, UID/GID, or
limits. R4 may ask the registry to resolve the already proven principal and requested dimensions,
but it may not append remote bytes to the fixed local argv.

### Exact environment and executable policy

A profile contains a fixed environment plus an explicit inherited-name allowlist. Inherited names
are limited to `LANG`, `TZ`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `PATH`, and `LC_*`. Loader and
runtime hazard names are rejected whether fixed or inherited, including `LD_*`, `DYLD_*`,
`MALLOC_*`, `IFS`, `ENV`, `BASH_ENV`, `SHELLOPTS`, `PS4`, `GCONV_PATH`, `LOCPATH`, `NLSPATH`, and
`GLIBC_TUNABLES`. `TERM` is generated only from the profile. Ambient duplicates, NULs, invalid
names, and oversize values fail closed. The final child receives only the sorted resolved vector;
the internal-helper marker is not forwarded.

The target and helper paths are normalized absolute paths opened component by component with
`O_NOFOLLOW`. The final object must be a regular ELF executable, have at least one execute bit, be
owned by root or the effective daemon UID, be neither group/other writable nor set-ID, and remain
authoritative through its already-open descriptor. V1 deliberately rejects interpreter scripts.
The working directory is also opened without following symlinks and entered by descriptor.

This does not defend against an attacker who can already replace daemon-owned executable content or
control the daemon process. The equal-UID boundary remains explicit.

### Fork-safe one-binary handoff

The parent opens all authority-bearing objects and allocates the PTY. It then uses `posix_spawn` to
execute the already-open IoTox binary through a high-numbered `/proc/self/fd/N` path. High duplicate
source descriptors prevent the ordered `dup2` file actions from overwriting the helper descriptor.
The spawned helper starts with only:

```text
0,1,2  PTY slave
3      canonical resolved-profile manifest
4      close-on-exec startup/status channel
5      close-on-exec target executable
6      working-directory descriptor
```

The parent closes every child-side and high handoff duplicate immediately after spawn. Spawn
attributes empty the inherited signal mask and restore every catchable signal to default. In the
hidden child, IoTox requires an exact private marker; proves that fds 3 and 4 are distinct stream
sockets whose `SO_PEERCRED` PID/UID/GID agree; proves fds 0/1/2 are one PTY; derives the exact parent
PID from those kernel credentials; and installs and verifies parent-death `SIGKILL`. It then decodes
and canonicalizes the bounded manifest, creates a new session, claims the controlling terminal,
applies the initial window and foreground process group, revalidates the target descriptor, enters
the working directory, applies limits, installs and verifies `PR_SET_NO_NEW_PRIVS`, applies and
verifies complete ambient-capability clearing, applies and verifies identity, re-arms parent death
after any credential change, sets `umask(077)`, and closes
every unreserved descriptor.

Immediately before final `fexecve`, the reviewed hidden child writes a fixed readiness record on fd
4. The parent accepts startup only after receiving that record and then observing close-on-exec EOF.
A structured 12-byte stage/errno record replaces EOF on child setup or final-exec failure. EOF before
readiness rejects a wrong or prematurely exiting helper. A bounded monotonic startup deadline
covers manifest transfer and final-exec confirmation; timeout kills and reaps the child.

No general C++ application work runs between a raw `fork` and `exec`; `posix_spawn` owns that
implementation boundary. The internal argument is intercepted before public CLI parsing and is not
an advertised command.

### PTY ownership and lifecycle truth

The native backend uses `posix_openpt`, `grantpt`, `unlockpt`, and `TIOCGPTPEER` when available,
falling back to `ptsname_r`. The master is nonblocking. Read/write results distinguish progress,
would-block, and closure. Each controller call is bounded to 64 KiB, and backend contract
violations become terminal controller failure.

The controller owns one immutable resolved profile and one process. It accepts input and resize only
while running; output may continue to drain after close begins. Close first observes exit to avoid
signaling a completed process, then escalates with fresh profile-defined windows:

```text
SIGHUP -> grace -> SIGTERM -> grace -> SIGKILL -> reap grace
```

The backend signals the original process group. `waitid(..., WNOWAIT)` observes the leader without
reaping it; while that leader remains waitable, the backend sends a final group `SIGKILL` and then
reaps the leader. Exit status is stable and idempotent after observation. Destructor cleanup kills
both the original group and leader and waits for the leader when no exit has been observed.
Controller snapshots retain profile ID, policy generation, dimensions, close reason, exact exit,
I/O counters, resize/signal counts, output-closed state, and typed failure.

### Test-only target

The PTY target fixture is a separate test executable, not a public mode in `iotox`. It reports exact
environment, cwd, window, session/group/foreground state, signal dispositions, `no_new_privs`,
ambient-capability count, parent-death signal, identities/groups, limits, and closed descriptors;
echoes binary bytes including NUL and high bytes; exits on HUP; or deliberately ignores HUP and TERM so KILL escalation is
exercised. A separate-supervisor test kills the controller process without running destructors and
uses pidfd/procfs exit observation to prove the ignoring target still dies through parent death,
including after exact root-to-unprivileged identity transition when available. Native tests also
raise a capability into a separate root supervisor's ambient set and prove the final target observes
zero ambient capabilities. They reject symlinked and writable targets, impossible child limits, and
a valid ELF that is not the reviewed IoTox helper.

## Consequences

R3 now has a real, locally testable PTY/process boundary without making a remote shell reachable.
Canonical policy and generation binding exist before Agent integration. Process creation has an
explicit startup proof, exact child setup error stage, descriptor ownership, output/input contract,
and deterministic close/reap model. The pure controller can be exhaustively tested without creating
processes, while native tests cover the Linux boundary end to end.

The design intentionally does **not** provide a complete sandbox. UID/GID transition and rlimits do
not replace namespaces, seccomp, cgroups, mount isolation, complete capabilities policy, an LSM, a container,
or a VM. `PR_SET_NO_NEW_PRIVS` prevents later exec privilege gain but does not restrict ordinary
syscalls. The child clears ambient capabilities, but does not claim to erase every inherited
permitted/effective/inheritable or bounding-set capability. Exact identity normally requires root or
the relevant `CAP_SETUID`/`CAP_SETGID` powers.
`RLIMIT_NPROC` has Linux/user-wide semantics and is not a per-session descendant counter.

Process-group signaling fences members that remain in the original group. A target able to fork and
escape with a new session or process group is not fully contained. The production backend has no
pidfd/cgroup-based descendant ownership, no daemon-restart survival, no durable PTY supervisor, no
local operator terminal client, no remote dispatch, and no advertised feature bit 23. These remain
R4–R8 work or separate deployment confinement. Test-only pidfds observe one leader's exit; they do
not change that production limitation.

The `/proc/self/fd` helper entrance makes this backend Linux-specific and requires a mounted procfs
that permits execution of the open helper descriptor. Other operating systems require a separately
reviewed backend rather than silently weakening the handoff.

## Rejected alternatives

- **Let the peer send a command line or profile name.** This collapses local policy into remote
  command selection and makes authorization much harder to audit.
- **Use `system`, a shell, or `execvp`.** Search paths, shell parsing, and ambient environment would
  create unnecessary interpretation and injection surfaces.
- **Run C++ setup after a raw `fork`.** The future Agent is multithreaded; allocator, lock, and
  library state make that child path unsafe.
- **Treat `posix_spawn` return as final-target success.** It proves the helper image was entered, not
  that reviewed setup and final `fexecve` completed.
- **Treat status-channel EOF alone as proof.** A wrong helper can simply exit and close inherited
  descriptors. The explicit readiness record binds EOF to the reviewed internal child path.
- **Pass paths to the child and reopen them.** That reintroduces replacement and symlink races after
  parent validation. Open descriptors remain authoritative instead.
- **Inherit the daemon environment and delete a few names.** Denylisting is incomplete. V1 builds an
  exact environment from fixed entries, a small inherited allowlist, and generated `TERM`.
- **Make the test fixture a public product mode.** Test behavior must not enlarge the installed
  one-binary command surface.
- **Claim process groups are a sandbox.** A cooperating tree is manageable, but escaped descendants
  require cgroup/pidfd or stronger external confinement.
