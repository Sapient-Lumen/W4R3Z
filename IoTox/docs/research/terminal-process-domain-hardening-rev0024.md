# Terminal process-domain hardening — rev0024

**Research date:** 2026-08-17 America/New_York
**Applied revision:** rev0024
**Decision:** ADR 0074

## Question

How can IoTox narrow the remaining Linux PTY process-domain races without pretending that a procfs
scan is equivalent to owning a delegated cgroup, and how can the host/payload boundary expose less
same-UID process-control surface?

## Primary-source findings

### Open procfs descriptors are stable against PID retargeting, not PID reuse

The Linux procfs documentation says that keeping `/proc/<pid>` open does not reserve the numeric PID.
If that process exits and the PID is later reused, operations through the old procfs descriptor do not
operate on the new process and usually fail with `ESRCH`. This makes a descriptor-relative re-read a
useful anti-retargeting witness, provided IoTox does not claim that it prevents reuse.

`/proc/<pid>/stat` field 6 is the session ID and field 22 is the process start time after boot. Reading
both before and after pidfd acquisition through the same process-directory descriptor supplies a
bounded incarnation check independent from the numeric pathname.

Applied rule:

```text
open genuine /proc inventory
  -> openat numeric member directory without following links
  -> read PID/session/state/starttime through that directory
  -> pidfd_open numeric PID
  -> re-read through the same directory
  -> require session and starttime equality
  -> pidfd_send_signal
```

A disappeared descriptor or changed witness produces `vanished`; it never redirects the signal.

### A procfs sweep is not `cgroup.kill`

The cgroup-v2 documentation states that writing `1` to `cgroup.kill` kills a cgroup subtree with
protection for concurrent forks and migrations. That is a materially stronger kernel-owned lifecycle
primitive than a userspace `/proc` iteration.

IoTox does not currently create and own a delegated cgroup subtree. rev0024 therefore applies a
bounded quiescence rule: the leader remains waitable, SIGKILL sweeps continue, and the leader is reaped
only after three consecutive complete inventories report no live executable member of its fixed
session. Seeing any member resets the count.

This closes the immediate one-empty-scan release and is tested during bounded fork churn. It remains
possible for a sufficiently adversarial schedule or hostile outer procfs policy to defeat a userspace
inventory. The document and implementation intentionally retain cgroup ownership as future work.

### Pidfds are supervisor capabilities, not payload capabilities

`pidfd_open(2)` creates a stable process handle and `pidfd_send_signal(2)` operates through it.
`process_madvise(2)` and `process_mrelease(2)` also consume pidfds to affect another process's memory
management or release. Even where ordinary Linux permission checks would reject a target, the
confined terminal payload does not need these interfaces.

rev0024 leaves the parent supervisor's already-open leader/member pidfds outside the payload seccomp
filter and returns `EPERM` for all four reviewed process-handle interfaces inside baseline and strict.
The executable fixture intentionally uses invalid descriptors for the latter calls so `EPERM`, rather
than `EBADF`/`EINVAL`, proves that seccomp intercepted the call before ordinary kernel validation.

### Disable terminal-host dumpability and core files before secrets

`PR_SET_DUMPABLE` controls whether a process is dumpable and also affects ptrace/procfs access checks.
`RLIMIT_CORE` controls core-file size; lowering both its soft and hard values to zero prevents the
process from later raising the limit without a new privilege boundary.

The terminal-host gate is the point where one process may hold device identity/authority state while
supervising same-UID PTY descendants. rev0024 therefore performs both operations before constructing
`Agent`. It verifies each postcondition and exits with a named error if either operation fails.
Controller-only and non-terminal agent runs are not silently changed.

This reduces ordinary debugging and crash-artifact exposure. It does not erase secrets from live
memory, prevent a privileged administrator or kernel compromise, replace memory locking, or prove
that every platform crash mechanism honors `RLIMIT_CORE`.

## Construction

### Procfs and signaling

- `/proc` is opened with `O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW`.
- `fstatfs` must report `PROC_SUPER_MAGIC`.
- each numeric member directory is opened with descriptor-relative `openat` and `O_NOFOLLOW`;
- `stat` is read through that directory and must report the enumerated PID;
- session ID, live state, and field-22 start time are parsed;
- post-`pidfd_open` revalidation must match session and start time;
- signaling occurs only through `pidfd_send_signal`;
- three empty full inventories are required before leader reap after KILL starts.

### Payload process-handle fence

The shared baseline filter denies available syscall numbers for `pidfd_open`,
`pidfd_send_signal`, `process_madvise`, and `process_mrelease`. The final payload report records both a
boolean and the number of syscall probes compiled for the qualification architecture.

### Host process seal

`seal_remote_terminal_host_process()` is a small idempotent Linux policy unit. It sets and verifies
non-dumpability, lowers and verifies the hard and soft core limits, and fails closed. `run_agent()`
invokes it only after argument validation confirms the explicit host gate and before `Agent` is
constructed.

## Executable oracles

rev0024 adds or extends tests that:

1. call the host seal twice in a child and verify dumpability/core limits while confirming the parent
   retains its original process policy;
2. call all compiled process-handle interfaces after final exec and require `EPERM`;
3. let a direct PTY leader exit, observe it as a zombie, and prove the first and second empty session
   inventories do not reap it while the third does;
4. create a bounded 48-descendant fork-churn tree in separate process groups, begin shutdown during
   churn, and verify convergence plus death of captured process incarnations; and
5. retain all earlier native session-tree, natural-leader, parent-death, descriptor, capability,
   strict Landlock/MDWE, and argument-fence probes.

The churn fixture is explicitly bounded by profile process limits, a finite descendant count, finite
observation windows, and the existing three-second shutdown deadline. It is a race oracle, not a load
generator or fork bomb.

## Nonclaims

rev0024 does not claim:

- cgroup-v2 ownership, `cgroup.kill` atomicity, migration protection, accounting, or quotas;
- immunity to every theoretical fork/procfs enumeration schedule;
- a complete syscall allowlist or complete process-handle inventory;
- protection from root, kernel compromise, hostile hypervisors, or physical memory capture;
- secret memory locking, crash-system qualification, or target-fleet kernel qualification;
- public-network or two-physical-host Ratox qualification; or
- production security certification.

## Sources rechecked online

```text
https://docs.kernel.org/filesystems/proc.html
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html
https://man7.org/linux/man-pages/man2/process_madvise.2.html
https://man7.org/linux/man-pages/man2/process_mrelease.2.html
https://man7.org/linux/man-pages/man2/PR_SET_DUMPABLE.2const.html
https://man7.org/linux/man-pages/man2/getrlimit.2.html
https://man7.org/linux/man-pages/man2/prctl.2.html
https://man7.org/linux/man-pages/man2/openat.2.html
https://man7.org/linux/man-pages/man2/statfs.2.html
```

These sources define Linux interface semantics. They do not audit IoTox or prove the implementation's
security claims; the executable evidence establishes only the bounded behavior described above.
