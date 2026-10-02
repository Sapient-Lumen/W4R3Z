# Linux terminal session containment review — rev0023

Date: 2026-08-17 America/New_York
Revision: rev0023
Version: 0.23.0
Codename: Session-Swept Argument-Fence Citadel

## Question

Which Linux interfaces could let a final PTY payload mutate terminal state, create isolation contexts,
weaken its parent/session contract, retain unexpected descriptors, or outlive process-group shutdown;
and which bounded changes close those paths without claiming a complete sandbox?

## Findings

### Terminal and namespace controls are often syscall arguments

`TIOCSTI`, controlling-terminal detach/reassignment, line-discipline changes, console operations,
keyboard/font operations, and virtual-terminal switching are `ioctl(2)` requests, not distinct
syscalls. A syscall-number-only filter therefore leaves them reachable. Denying every ioctl would
break ordinary termios and window behavior, so the request argument is the bounded control point.

Likewise, legacy `clone(2)` places namespace selection in its flags word. The flags argument is first
on the reviewed architectures except s390x, where it is second. `clone3(2)` places flags behind a user
pointer that classic BPF cannot dereference; returning `ENOSYS` asks libc to retry the inspectable
legacy path. `CLONE_NEWTIME` is excluded from the legacy mask because its value overlaps the legacy
signal field. `unshare(2)` and `setns(2)` remain denied.

### Process groups are not a PTY session

A shell may create multiple process groups while remaining inside one terminal session. Signaling only
`-leader_pid` therefore does not cover a background group. After helper setup, denying `setsid(2)`,
`TIOCNOTTY`, `TIOCSCTTY`, and `prctl(PR_SET_PDEATHSIG, ...)` freezes the reviewed session and verified-
parent properties while leaving ordinary job-control groups available.

Linux `/proc/<pid>/stat` exposes process state and session ID. A session inventory can select every
live process with the helper-created session ID, but numeric PIDs can disappear and be reused between
inventory and signaling. Opening a pidfd for each candidate and re-reading its session after pidfd
acquisition binds the signal to the revalidated kernel process identity. `pidfd_send_signal(2)` then
avoids a second numeric-PID signal race.

The leader should remain waitable until the session is empty. That pins its PID, which is also the
session ID after `setsid(2)`, across the inventory/signal/reap boundary. Natural leader exit must start
the same cleanup while preserving the leader's original wait status.

### Pidfd availability and pidfd waiting are separate boundaries

Baseline/strict session signaling requires `pidfd_open(2)` and `pidfd_send_signal(2)`. Exit observation
can prefer `waitid(P_PIDFD, ..., WNOWAIT)`, but Linux exposed pidfd creation before pidfd waiting. A
narrow `EINVAL`/`ENOSYS` fallback to `waitid(P_PID, ..., WNOWAIT)` remains safe for the still-waitable
direct child and does not discard the retained pidfd used by session signaling.

### `RLIMIT_NOFILE` is not descriptor closure

Lowering the soft descriptor limit does not close descriptors already open above the new ceiling.
The final helper therefore cannot use that limit as a scan bound. `close_range(2)` is an acceleration,
not the proof: `/proc/self/fd` inventory closes all unreserved descriptors and a second pass verifies
the postcondition.

## Implemented boundary

`src/terminal_posix.cpp` now:

1. computes endian-correct seccomp argument offsets and supports exact/masked argument denials;
2. derives one shared, compile-time-checked terminal/console ioctl deny table for enforcement and test;
3. denies reviewed namespace flags in legacy clone and returns `ENOSYS` for clone3;
4. denies post-setup `setsid`, parent-death-signal mutation, terminal detach, and terminal assignment;
5. closes and independently inventories every descriptor above the reserved handoff floor;
6. requires pidfd/procfs signaling support for baseline and strict before PTY allocation;
7. retains a close-on-exec child-leader pidfd immediately after spawn;
8. inventories the fixed PTY session, pidfd-opens and revalidates each member, then signals by pidfd;
9. repeats SIGKILL sweeps until the executable session is empty;
10. keeps the leader waitable until descendants are gone and preserves its exact exit status;
11. retains compatibility mode's historical process-group behavior rather than silently changing v1.

## Runtime oracle design

The final payload and parent process test distinguish policy interception from ordinary kernel errors:

| Probe | Expected result | Meaning |
|---|---|---|
| every shared mutation `ioctl(-1, request, ...)` | `EPERM` | request argument intercepted before fd validation |
| `ioctl(-1, TIOCGWINSZ, ...)` | `EBADF` | ordinary request reached the kernel |
| invalid legacy clone plus namespace flag | `EPERM` | namespace bit intercepted |
| invalid legacy clone without namespace flag | `EINVAL` | ordinary clone reached kernel validation |
| `clone3(NULL, 0)` | `ENOSYS` | inspected legacy fallback requested |
| real `fork()` and one `std::thread` | success | ordinary process/thread creation preserved |
| descendant `setsid()` | `EPERM` | session escape denied |
| `TIOCNOTTY` | `EPERM` | controlling-terminal detach denied |
| `PR_SET_PDEATHSIG` mutation | `EPERM` | verified parent contract frozen |
| inherited descriptor duplicated above 255 | `EBADF` after exec | closure is not RLIMIT-bounded |
| separate process-group child during forced close | exits | session-wide HUP/TERM/KILL converges |
| separate process-group child after leader exits 0 | exits; leader remains 0 | orphan cleanup preserves leader truth |

The test also counts `/proc/self/fd` links named `anon_inode:[pidfd]` and requires one additional live
child pidfd in baseline. Release stress repeats the complete native process oracle.

## Construction defects found and closed

1. The first argument-fence oracle duplicated ioctl names and depended on indirect header inclusion.
   Production and test now consume the same constexpr table.
2. The first merged policy accidentally included `CLONE_NEWTIME` in the legacy mask despite its signal-
   field overlap. The final source excludes it and blocks time namespaces through clone3/unshare paths.
3. The earlier supervisor retained a leader pidfd but still killed only the original process group.
   The final design treats the fixed PTY session as the lifecycle unit and revalidates every member.
4. The earlier descriptor fallback trusted a lowered `RLIMIT_NOFILE`. The final handoff inventories and
   proves the actual descriptor table.
5. TSan initially failed before payload readiness because the instrumented helper inherited the test
   profile's 512 MiB address-space limit. The sanitizer harness now omits only that test limit for ASan
   and TSan helper lanes; production and ordinary build lanes are unchanged.

## Applied source review

Primary references rechecked online on 2026-08-17:

```text
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://man7.org/linux/man-pages/man2/TIOCSTI.2const.html
https://man7.org/linux/man-pages/man4/tty_ioctl.4.html
https://man7.org/linux/man-pages/man2/ioctl.2.html
https://man7.org/linux/man-pages/man2/clone.2.html
https://man7.org/linux/man-pages/man2/setsid.2.html
https://man7.org/linux/man-pages/man2/prctl.2.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html
https://man7.org/linux/man-pages/man2/wait.2.html
https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
https://man7.org/linux/man-pages/man2/close_range.2.html
https://raw.githubusercontent.com/torvalds/linux/v6.18/include/uapi/linux/sched.h
https://raw.githubusercontent.com/torvalds/linux/v6.18/include/uapi/linux/wait.h
```

These references establish interface semantics. They do not qualify every kernel configuration,
audit the complete ioctl/syscall surface, or prove resistance to unknown future session-escape paths.

## Remaining work and nonclaims

- Qualify baseline and strict on named deployment kernels and outer service sandboxes.
- Inventory real payload syscall/ioctl needs before claiming broad baseline compatibility.
- Decide whether cgroup v2 is appropriate for descendant resource accounting, quotas, and a second
  lifecycle boundary independent of procfs.
- Revisit the ioctl and lifecycle request set as Linux evolves.
- Retain explicit nonclaims: no read allowlist, mount graph isolation, created namespace sandbox,
  cgroup accounting, virtual-machine boundary, production security audit, or physical-host R7 result.
