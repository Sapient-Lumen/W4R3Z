# Linux PTY/profile process-boundary research note — rev0017

Date: 2026-08-16
Scope: Ratox R3 local prerequisite only; no network dispatch and no feature-bit-23 advertisement

## Question

What is the smallest Linux process boundary that can launch one locally fixed terminal profile from
a future multithreaded IoTox Agent while preserving exact policy, descriptor ownership, startup
truth, nonblocking PTY semantics, deterministic shutdown, and honest confinement claims?

## Applied sources

### POSIX process creation

- POSIX `posix_spawn` specification:
  https://pubs.opengroup.org/onlinepubs/9799919799/functions/posix_spawn.html
- POSIX spawn rationale:
  https://pubs.opengroup.org/onlinepubs/007904975/xrat/xsh_chap03.html
- Linux `execve(2)` process-attribute rules:
  https://man7.org/linux/man-pages/man2/execve.2.html

Applied decision: use `posix_spawn` file actions and attributes instead of executing C++ setup in a
raw post-`fork` child. The spawned image is the same IoTox executable in an exact hidden mode. The
reviewed image then performs ordinary single-threaded setup and a descriptor-based final exec.
Spawn attributes clear the inherited signal mask and restore every catchable signal to its default
disposition. This is required because ignored dispositions otherwise survive exec and could let a
daemon's signal policy silently shape the terminal target.

Nonclaim: POSIX does not define a portable spawn-by-open-fd operation. rev0017's
`/proc/self/fd/N` helper entrance and Linux PTY ioctls make this backend Linux-specific.

### UNIX 98 pseudoterminals

- `posix_openpt(3)`:
  https://man7.org/linux/man-pages/man3/posix_openpt.3.html
- `grantpt(3)`:
  https://man7.org/linux/man-pages/man3/grantpt.3.html
- `unlockpt(3)`:
  https://man7.org/linux/man-pages/man3/unlockpt.3.html
- `ptsname(3)` / `ptsname_r`:
  https://man7.org/linux/man-pages/man3/ptsname.3.html
- PTY overview:
  https://man7.org/linux/man-pages/man7/pty.7.html

Applied decision: open the master with `O_RDWR|O_NOCTTY|O_CLOEXEC|O_NONBLOCK`, grant and unlock the
slave, prefer Linux `TIOCGPTPEER` so the slave is opened relative to the master without a pathname
race, and retain `ptsname_r` plus `O_NOFOLLOW` as the compatibility fallback. The master remains
nonblocking and all I/O reports progress, would-block, or closure explicitly.

The source documents that `ptsname_r` is the reentrant form; that matters because the product is
intended to run inside a multithreaded agent even though current R3 tests are local.

### Session, controlling terminal, foreground group, and window

- Terminal ioctls, including `TIOCSCTTY`, `TIOCGPTPEER`, and `TIOCSWINSZ`:
  https://man7.org/linux/man-pages/man2/ioctl_tty.2.html
- `tcsetpgrp(3)`:
  https://man7.org/linux/man-pages/man3/tcsetpgrp.3.html
- `setsid(2)`:
  https://man7.org/linux/man-pages/man2/setsid.2.html

Applied decision: after the helper image is entered, call `setsid`, make the already-installed PTY
slave the controlling terminal, apply the accepted initial dimensions, and set the new process group
as foreground before target exec. Native fixtures verify SID=PID, PGRP=PID, foreground=PGRP, and the
exact window.

Nonclaim: a session/process group is lifecycle organization, not a complete security container. A
target that can create a different session or process group may escape later group signaling.

### Descriptor and exec boundary

- `fexecve(3)`:
  https://man7.org/linux/man-pages/man3/fexecve.3.html
- `close_range(2)`:
  https://man7.org/linux/man-pages/man2/close_range.2.html
- `fcntl(2)` and close-on-exec descriptors:
  https://man7.org/linux/man-pages/man2/fcntl.2.html
- UNIX-domain `SO_PEERCRED`:
  https://man7.org/linux/man-pages/man7/unix.7.html

Applied decision: the parent validates and opens the target and cwd, passes those exact descriptors,
then the child uses `fchdir` and `fexecve`; it never reopens authority-bearing target paths. The
status and target descriptors are explicitly marked close-on-exec. Before accepting configuration,
the child proves that manifest and status descriptors are distinct stream sockets, that both report
the same kernel-authenticated peer PID/UID/GID, and that stdin/stdout/stderr are the same PTY character
device. `close_range(7, UINT_MAX, 0)` is the preferred descriptor sweep, with a bounded
`_SC_OPEN_MAX` close loop for older kernels.

An exec-error pipe normally treats close-on-exec EOF as success. rev0017 adds a fixed readiness
record immediately before final `fexecve`; the parent requires readiness plus EOF. This rejects a
misconfigured valid ELF helper that never entered the reviewed IoTox hidden-child path. Structured
stage/errno records cover failures both before and after readiness.

### Parent death, privilege gain, limits, and identity

- `PR_SET_PDEATHSIG`:
  https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html
- `PR_SET_NO_NEW_PRIVS`:
  https://man7.org/linux/man-pages/man2/PR_SET_NO_NEW_PRIVS.2const.html
- ambient capabilities and `PR_CAP_AMBIENT_CLEAR_ALL`:
  https://man7.org/linux/man-pages/man7/capabilities.7.html
  https://man7.org/linux/man-pages/man2/PR_CAP_AMBIENT_CLEAR_ALL.2const.html
- `getrlimit(2)` / `setrlimit(2)`:
  https://man7.org/linux/man-pages/man2/getrlimit.2.html
- `setgroups(2)`:
  https://man7.org/linux/man-pages/man2/setgroups.2.html
- `setuid(2)` and `setgid(2)`:
  https://man7.org/linux/man-pages/man2/setuid.2.html
  https://man7.org/linux/man-pages/man2/setgid.2.html
- `pidfd_open(2)`:
  https://man7.org/linux/man-pages/man2/pidfd_open.2.html

Applied decision: derive the expected parent from the two agreeing `SO_PEERCRED` records, install and
read back parent-death `SIGKILL`, and reject a parent change immediately after arming. Set and read
back `PR_SET_NO_NEW_PRIVS` before any identity transition. Force `RLIMIT_CORE` soft/hard zero; apply
configured soft limits only when nonzero and never above the inherited hard limit. For exact
identity, clear supplementary groups before exact GID and UID transitions and verify real,
effective, and saved IDs plus a zero supplementary-group count. Because Linux clears the
parent-death setting after credential changes, re-arm and re-verify it after identity convergence.
Clear the complete ambient capability set and read back every capability known to the build before
identity transition. `no_new_privs` prevents a later exec from granting new set-ID or file-capability
privilege; ambient capability clearing separately prevents privilege already ambient in the daemon
from silently crossing the helper and final-target exec boundary.

The native lifecycle test launches the controller in a separate supervisor, waits until a target
that ignores HUP and TERM has completed final exec, opens a pidfd when the kernel supports it, then
kills the supervisor with `SIGKILL` so no C++ destructor can assist. The target must still terminate;
procfs start-time/state observation is the bounded fallback on older kernels.

Nonclaims:

- `no_new_privs` prevents exec-time privilege gain but does not filter syscalls or filesystem/network
  access.
- rlimits are coarse kernel limits and do not provide cgroup-style per-session ownership.
- exact identity may require root or capabilities and is not available merely because a profile asks
  for it.
- ambient clearing is inheritance hygiene, not a complete permitted/effective/inheritable or
  bounding-set policy.
- these mechanisms do not replace namespaces, seccomp, cgroups, a complete capability policy, an LSM,
  container, or VM.

### Exit observation, process-group fencing, and reap

- `waitid(2)` / `waitpid(2)`:
  https://man7.org/linux/man-pages/man2/wait.2.html
- `kill(2)` process-group semantics:
  https://man7.org/linux/man-pages/man2/kill.2.html

Applied decision: close escalation is owned by a transport-independent controller and uses HUP,
TERM, then KILL with fresh monotonic deadlines. Before each escalation the controller observes exit.
The backend uses `waitid(..., WNOWAIT)` so the leader remains waitable while a last SIGKILL fences
remaining members of the original process group; it then reaps the leader with `waitpid` and retains
one stable decoded exit result.

Nonclaim: this does not find or kill descendants that escaped the original process group. Complete
descendant containment requires a later cgroup/pidfd/supervisor decision or external confinement.

## Local profile findings

A safe process backend is insufficient if policy is ambiguous. The implemented v1 profile therefore
uses a canonical local store, exact principal binding, immutable generation-bound resolution, fixed
argv, normalized absolute paths, and an exact environment built from fixed entries plus a small
inherited allowlist. Dynamic-loader and shell startup variables are rejected, and `TERM` is generated
from policy. Every authority-bearing filesystem object is opened without symlink following before
spawn.

The profile format is not sent over Tox. It is a local policy record with a stricter grammar than a
human configuration language. Human-friendly authoring/import can be added later only if it emits
and verifies the same canonical records.

## Resulting rev0017 boundary

rev0017 can drive a fixed local ELF test target through a real PTY, preserve binary bytes, clamp and
apply resize, prove exact environment/cwd/session/limit/descriptor state, report child setup failures
by stage, reject wrong helpers and insecure executables, restore inherited ignored signals, observe
exits, clear an intentionally raised inherited ambient capability, force HUP/TERM/KILL shutdown, and
prove the parent-death kill remains effective after an exact privilege drop. A deterministic fake
proves controller races and error contracts independently of Linux.

This evidence satisfies the R3 local exit gate only. Agent dispatch, two-step input commitment to a
real PTY, attachment/revocation integration, local operator streaming, reconnect/restart behavior,
two-host latency, security review, and feature activation remain later phases.
