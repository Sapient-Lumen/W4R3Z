# ADR 0073: Fence terminal lifecycle and contain baseline PTY sessions

Status: accepted
Date: 2026-08-17

## Context

ADR 0072 established an architecture-checked classic-BPF seccomp deny floor, but its rules compared
only syscall numbers and shutdown targeted only the initial process group. That left five material gaps
inside the stated baseline boundary:

1. `ioctl(2)` could still request terminal injection, controlling-terminal detach/reassignment,
   line-discipline changes, console redirection, virtual-terminal switching, or keyboard/font mutation.
2. `clone(2)` could still request namespaces through argument bits, while `clone3(2)` hid its flags
   behind a pointer that classic BPF cannot dereference.
3. A final payload could call `setsid(2)` or clear `PR_SET_PDEATHSIG`, weakening the session and
   verified-parent lifecycle established by the helper.
4. Lowering `RLIMIT_NOFILE` did not close inherited descriptors whose numbers were already above the
   new limit.
5. A descendant could enter another process group inside the same PTY session and survive the old
   negative-PGID shutdown path.

Primary Linux references rechecked for this decision are recorded in
`docs/research/terminal-session-containment-rev0023.md`. Those references define kernel interfaces;
they do not audit IoTox, qualify arbitrary target programs, or turn this construction into a complete
sandbox.

## Decision

### Argument-aware classic-BPF helpers

The baseline filter has reusable equality and bit-mask rules over the low 32-bit word of any
`seccomp_data.args[]` entry. The offset is computed from `offsetof(seccomp_data, args)` and reviewed
native byte order. Every argument rule reloads the syscall number before later rules execute.
Architecture validation and the x86-64 x32 rejection remain first.

The filter remains a bounded deny floor. It returns `EPERM` for policy-denied operations except
`clone3(2)`, which returns `ENOSYS` to request libc's legacy-clone compatibility path.

### Terminal, namespace, and lifecycle fences

For `ioctl(2)`, baseline and strict reject the shared build-header-derived request table in
`include/iotox/terminal_seccomp_policy.hpp`. The table includes controlling-terminal detach and
assignment (`TIOCNOTTY`, `TIOCSCTTY`), input injection, line-discipline, console, keyboard/font, and
virtual-terminal mutation requests. Both filter generation and the independent exec'd payload oracle
consume the same constexpr table. It must be nonempty, bounded, unique, and exclude ordinary window
query/resize operations. The 2026-08-17 build headers expose 29 requests.

Legacy `clone(2)` rejects the reviewed namespace bits in the architecture-correct flags argument:

```text
CLONE_NEWNS, CLONE_NEWCGROUP, CLONE_NEWUTS, CLONE_NEWIPC,
CLONE_NEWUSER, CLONE_NEWPID, CLONE_NEWNET
```

`CLONE_NEWTIME` is not placed in the legacy mask because its value overlaps the traditional clone
signal field. `clone3(2)` receives `ENOSYS`; `unshare(2)` and `setns(2)` remain wholly denied. This
preserves ordinary fork/thread creation while closing the reviewed namespace entrances.

After the helper has created the PTY session and armed the verified parent-death signal, baseline and
strict also deny `setsid(2)`, deny `prctl(PR_SET_PDEATHSIG, ...)`, and deny controlling-terminal detach
or reassignment. Descendants may still create ordinary process groups for shell job control, but they
remain in the fixed PTY session.

### Descriptor closure is inventoried and proved

The final child closes every descriptor from 7 upward with `close_range(2)` when available, then
enumerates `/proc/self/fd` without trusting `RLIMIT_NOFILE` as an upper bound. A first pass closes every
unreserved descriptor except the inventory handle; a second pass proves that none remain. Failure to
open/read the inventory or satisfy the postcondition aborts before target exec. This common handoff
rule applies to compatibility, baseline, and strict modes.

### Baseline and strict require exact session-signaling primitives

Before allocating a PTY, baseline and strict require all of the following to work in the actual
supervisor environment:

```text
pidfd_open
pidfd_send_signal
readable /proc/<pid>/stat identity
readable /proc process inventory
```

Immediately after `posix_spawn`, the parent must retain a close-on-exec pidfd for the child leader.
Failure is a named, fail-closed startup result. Compatibility mode retains its historical process-group
lifecycle and may run without pidfds.

Exit observation prefers `waitid(P_PIDFD, ..., WNOWAIT)`. On the narrow kernel/libc boundary where a
pidfd exists but pidfd waiting returns `EINVAL` or `ENOSYS`, IoTox keeps the pidfd and observes the
still-waitable direct child with `waitid(P_PID, ..., WNOWAIT)` before exact `waitpid` reap.

### Session-wide, PID-identity-aware teardown

The helper's successful `setsid(2)` makes the child PID the fixed session ID. For baseline and strict,
HUP, TERM, and KILL stages inventory `/proc`, select live processes whose parsed session ID equals that
fixed value, open a pidfd for each candidate, re-read its session after pidfd acquisition, and signal
through `pidfd_send_signal`. Revalidation prevents a PID that disappeared and was reused during the
inventory/open race from entering the target set.

Once KILL begins, every poll repeats the SIGKILL sweep until no live executable session member remains.
If the leader exits naturally, it remains waitable while IoTox kills and drains the remaining session;
the leader's original exit status is then reaped and preserved. Keeping the leader waitable pins the
numeric session ID across inventory, signaling, convergence, and reap. The destructor and startup
failure paths use the same bounded best-effort sweep before final group/leader kill fences.

A failed procfs or pidfd sweep is surfaced as an error rather than reported as complete session
signaling. Last-resort direct group/leader signals are still attempted for safety, but they do not
convert the failed proof into success.

## Evidence

The native payload and parent-side process oracle prove:

```text
every shared terminal-mutation ioctl is denied while ordinary window ioctl validation remains reachable
namespace-bearing legacy clone is denied and a nonnamespace invalid clone reaches kernel validation
clone3 requests legacy fallback; real fork and std::thread creation remain operational
setsid, controlling-terminal detach, and PR_SET_PDEATHSIG mutation are denied after final exec
a non-CLOEXEC descriptor duplicated above 255 is absent in the final payload
a live baseline supervisor retains its child pidfd
a child in a separate process group does not survive HUP -> TERM -> KILL shutdown
a separate-process-group child does not survive natural leader exit, while leader status 0 is preserved
```

The optimized native process oracle is additionally repeated as a stress gate. Sanitizer helper lanes
omit only the test profile's finite `RLIMIT_AS`, because ASan and TSan reserve large virtual shadow
mappings before the re-executed helper reaches `main`; ordinary debug/release lanes retain the limit
and the final payload remains native.

## Consequences

Baseline and strict now provide session-wide lifecycle containment for the reviewed Linux boundary,
including ordinary shell process groups. They fail closed when exact pidfd/procfs signaling cannot be
established. Compatibility remains explicitly weaker for canonical v1 migration and fixed payloads
that cannot operate under baseline.

The construction does not provide cgroup accounting or quotas, a created PID/user/mount namespace,
read/execute confinement, mount isolation, a complete syscall allowlist, VM isolation, or proof
against an unknown future session-escape interface. The ioctl list and syscall boundary require
continued review as Linux evolves.

## Rejected alternatives

- **Deny all `ioctl(2)` or all `clone(2)`.** Ordinary terminal, process, and thread behavior require
  bounded argument-aware rules instead.
- **Allow `clone3(2)` without inspecting `struct clone_args`.** Classic BPF cannot safely prove the
  pointed-to flags.
- **Return `EPERM` for `clone3(2)`.** `ENOSYS` is the compatibility signal that lets libc retry the
  inspected legacy path.
- **Keep a pidfd only as optional evidence.** Baseline/strict teardown depends on pidfd-backed identity;
  silently falling back would overstate session containment.
- **Signal only the original process group.** Legitimate shell job-control groups share the session and
  must be included in shutdown.
- **Reap the leader before draining descendants.** That would permit its numeric session ID to recycle
  during the proof boundary.
- **Call this cgroup or whole-machine containment.** The decision owns one reviewed PTY session
  lifecycle, not resource accounting or every possible kernel isolation mechanism.
