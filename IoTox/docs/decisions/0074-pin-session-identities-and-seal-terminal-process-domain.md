# ADR 0074 — Pin session identities and seal the terminal process domain

- Status: accepted
- Date: 2026-08-17
- Revision: rev0024
- Supersedes: no earlier ADR; strengthens ADRs 0064, 0072, and 0073

## Context

ADR 0073 changed baseline and strict PTY teardown from process-group-only signaling to repeated
session inventories and pidfd signaling. That closed a demonstrated escape in which a descendant
created another process group but remained in the helper-created session. Three narrower gaps
remained:

1. a numeric `/proc/<pid>/stat` path was read before and after `pidfd_open(2)`, but the pathname itself
   was not pinned while PID reuse was being excluded;
2. one empty session inventory was sufficient to reap the waitable leader, even though `/proc`
   iteration and concurrent forks are not an atomic cgroup operation; and
3. a confined payload could still request new pidfds or process-memory release/advice interfaces,
   while the long-lived terminal host retained ordinary same-UID dumpability and core limits.

The Linux procfs documentation states that an open `/proc/<pid>` descriptor does not prevent PID
reuse, but operations through a descriptor for a dead process do not switch to a later process that
receives the same numeric PID. `/proc/<pid>/stat` additionally exposes the process start time in field
22. The cgroup v2 documentation explicitly gives `cgroup.kill` stronger concurrent-fork and migration
semantics; IoTox does not own a delegated cgroup tree today and must not claim that property for a
procfs sweep.

## Decision

### Pin the procfs inventory and each candidate directory

Baseline and strict startup must open `/proc` with `O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC` and verify
its filesystem type is `PROC_SUPER_MAGIC`. Every session sweep must enumerate through that open
directory, open each numeric member directory with descriptor-relative `openat(2)`, and read `stat`
through the pinned member descriptor.

The parsed identity must include:

- the reported PID;
- the fixed PTY session ID;
- the live/zombie state; and
- field 22 start time in clock ticks.

After `pidfd_open(2)`, IoTox must re-read `stat` through the same pinned process-directory descriptor
and require the session plus start-time witness to match before `pidfd_send_signal(2)`. A vanished or
changed identity is not signaled.

### Require repeated quiescent inventories before leader reap

Once SIGKILL teardown begins, the still-waitable leader continues to pin the numeric session ID.
IoTox must observe three consecutive complete inventories with zero live executable session members
before reaping the leader. Any observed live member resets the quiescence count. Startup-failure and
destructor cleanup use the same bounded repeated-inventory principle before last-resort group and
leader signals.

Three inventories are a bounded race-hardening rule, not an atomic proof. They prevent one empty scan
from immediately releasing the session-ID pin and give newly forked members multiple complete
inventories in which to become visible. A future delegated cgroup-v2 design may supersede this rule
with `cgroup.kill` and cgroup lifecycle ownership.

### Deny process-handle acquisition inside confined payloads

The baseline seccomp floor must deny, when present in the build headers:

- `pidfd_open`;
- `pidfd_send_signal`;
- `process_madvise`; and
- `process_mrelease`.

The parent supervisor retains its pre-filter pidfds and performs all authorized process-domain work.
The exec'd payload oracle must prove interception with `EPERM` before ordinary descriptor or argument
validation.

### Seal the long-lived remote-terminal host before Agent construction

When and only when the explicit Ratox terminal-host gate is enabled, the one-binary agent entrance
must, before constructing `Agent` or loading device state:

1. set `PR_SET_DUMPABLE` to zero and verify `PR_GET_DUMPABLE`;
2. set both soft and hard `RLIMIT_CORE` to zero and verify them; and
3. fail closed if either property cannot be established.

The operation is idempotent. The hard core limit is deliberately irreversible for that process. The
controller-only and ordinary non-terminal agent paths retain their existing process policy.

## Consequences

- PID reuse is checked through three independent witnesses: a pinned procfs process directory, field
  22 start time, and a pidfd used for signaling.
- A single empty `/proc` pass can no longer trigger leader reap.
- Confined payloads cannot create their own pidfd/process-memory management channel through the
  reviewed interfaces.
- An enabled terminal host no longer exposes ordinary dumpable/core-file behavior while it holds
  device secrets and supervises same-UID children.
- Baseline and strict now depend on a genuine readable procfs mount in addition to pidfd support.
- Compatibility mode remains intentionally weaker for canonical-v1 migration.
- IoTox still does not own a cgroup tree, provide atomic fork/migration kill semantics, or claim a
  complete sandbox.

## Executable evidence

The native process fixture and owned registry must prove:

- procfs-backed baseline startup and final-payload process-handle syscall denial;
- first and second empty inventories leave an exited leader waitable;
- the third consecutive empty inventory reaps it without changing status;
- bounded concurrent fork churn in separate process groups converges under session shutdown;
- observed descendants are gone after shutdown;
- terminal-host sealing is idempotent, sets dumpability and core limits as specified, and does not
  mutate the parent test process; and
- all earlier capability, seccomp, strict-confinement, descriptor, parent-death, restart-fence, and
  authority oracles remain passing.

## References

- `docs/research/terminal-process-domain-hardening-rev0024.md`
- `docs/research/terminal-session-containment-rev0023.md`
- `docs/terminal-profile-v2.md`
- Linux procfs documentation: <https://docs.kernel.org/filesystems/proc.html>
- Linux cgroup v2 documentation: <https://docs.kernel.org/admin-guide/cgroup-v2.html>
- Linux `proc_pid_stat(5)`: <https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html>
- Linux `pidfd_open(2)`: <https://man7.org/linux/man-pages/man2/pidfd_open.2.html>
- Linux `pidfd_send_signal(2)`: <https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html>
- Linux `process_madvise(2)`: <https://man7.org/linux/man-pages/man2/process_madvise.2.html>
- Linux `process_mrelease(2)`: <https://man7.org/linux/man-pages/man2/process_mrelease.2.html>
- Linux `PR_SET_DUMPABLE(2const)`: <https://man7.org/linux/man-pages/man2/PR_SET_DUMPABLE.2const.html>
- Linux `getrlimit(2)`: <https://man7.org/linux/man-pages/man2/getrlimit.2.html>
