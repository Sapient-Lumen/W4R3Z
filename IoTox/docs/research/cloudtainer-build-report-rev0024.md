# IoTox cloudtainer build report — rev0024

**Construction date:** 2026-08-17 America/New_York
**Version:** 0.24.0
**Revision:** rev0024
**Codename:** Procfd Quiescence Process-Guard Citadel
**Conversation handoff:** rev0011

## Outcome

rev0024 materially strengthens the Linux PTY process boundary delivered in rev0023. The revision
closes four concrete weaknesses and adds executable race evidence rather than extending the claim by
prose alone:

1. procfs process identities are now opened descriptor-relatively and bound to PID, session, state,
   and start-time witnesses across pidfd acquisition;
2. one empty `/proc` inventory can no longer release the still-waitable session leader—three
   consecutive complete empty inventories are required;
3. final baseline/strict payloads can no longer acquire or operate the reviewed pidfd/process-memory
   handles; and
4. an explicitly enabled Ratox terminal host is made non-dumpable and receives an irreversible zero
   hard/soft core limit before `Agent` construction.

A bounded fork-churn process oracle begins shutdown while descendants are still being created in
separate process groups. A second direct-process oracle proves that the first and second empty
inventories retain the zombie leader and that the third preserves and reaps its exact status.

This is still a bounded userspace Linux process boundary. It is not delegated cgroup ownership,
`cgroup.kill` atomicity, a container, a complete syscall allowlist, or a production security
certification.

## Online source review

The construction rechecked current primary Linux interface documentation online on 2026-08-17:

- kernel procfs documentation for the lifetime behavior of open `/proc/<pid>` descriptors;
- kernel cgroup-v2 documentation for the stronger concurrent-fork/migration semantics of
  `cgroup.kill` that this revision explicitly does not claim;
- Linux man-pages for `/proc/<pid>/stat` field 22, pidfds, process-memory advice/release, dumpability,
  resource limits, `openat`, and filesystem type inspection.

The retained source list is in `docs/research/sources.md`; the applied analysis is in
`docs/research/terminal-process-domain-hardening-rev0024.md`. Those references define kernel
interfaces. They do not audit IoTox or prove the implementation.

## Constructed boundary

### Verified procfs inventory

Baseline and strict startup now open `/proc` with `O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW` and verify
`PROC_SUPER_MAGIC` with `fstatfs(2)`. A substituted non-proc filesystem or unavailable inventory is a
named fail-closed startup error rather than a silent downgrade.

Every sweep enumerates the verified procfs descriptor and opens numeric process directories with
`openat(2)` plus `O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW`. `stat` is then opened through that pinned
member directory. The parser requires:

- the reported PID to equal the enumerated numeric PID;
- a valid fixed session ID;
- a live, zombie, or vanished state with zombies excluded from executable membership; and
- nonnegative field-22 process start time.

### Identity-bound pidfd signaling

For each live member of the helper-created PTY session, the supervisor records the session and start
witness, calls `pidfd_open(2)`, and re-reads `stat` through the same open process-directory descriptor.
It signals only when the reread still describes the expected live session and exact start-time
incarnation. Delivery is then performed solely with `pidfd_send_signal(2)`.

If the original process disappears and its numeric PID is reused during the sequence, the old procfs
directory does not retarget the new process. A vanished or changed witness is skipped. Sweep errors
are surfaced; last-resort direct leader/group signals do not convert an unproved complete-session
sweep into success.

### Repeated quiescence before reap

After SIGKILL teardown starts, the direct child leader remains waitable. Because its PID is also the
session ID created by the helper's `setsid(2)`, retaining that zombie prevents numeric session-ID
reuse during inventory and signaling.

The supervisor requires three consecutive complete sweeps with zero live executable session members
before `waitpid` reaps the leader. Any observed live member resets the counter. Startup-failure and
destructor cleanup use the same bounded repeated-inventory principle before last-resort direct
signals.

Three passes close the demonstrated one-empty-scan release race and give concurrently created members
multiple full inventories in which to become visible. They are not an atomic proof against every
scheduler or a substitute for a delegated cgroup-v2 lifecycle unit.

### Payload process-handle fence

The shared baseline seccomp floor now denies available build-header syscall numbers for:

```text
pidfd_open
pidfd_send_signal
process_madvise
process_mrelease
```

The final exec'd fixture issues each compiled interface with arguments chosen so `EPERM` proves
seccomp interception before normal kernel descriptor/argument validation. It emits both
`process-handle-syscalls-denied=1` and the exact compiled probe count. The parent supervisor retains
only the pidfds it opened before child filter installation.

### Enabled-host process seal

`seal_remote_terminal_host_process()` is a small idempotent, fail-closed policy unit. When the
explicit default-off terminal-host gate is enabled, `run_agent()` invokes it after argument parsing
and before signal installation or `Agent` construction. It:

1. sets `PR_SET_DUMPABLE` to zero and verifies `PR_GET_DUMPABLE`;
2. sets both `RLIMIT_CORE` values to zero; and
3. reads the limit back and requires both values to remain zero.

The hard core limit is deliberately irreversible for that process. Ordinary non-terminal and
controller-only invocations retain their previous process policy.

## Executable evidence added

rev0024 adds or extends native checks that:

- call the host seal twice in a forked child and verify non-dumpability plus zero core limits while
  confirming the parent process remains unchanged;
- execute every compiled reviewed process-handle syscall after final exec and require `EPERM`;
- hold an exited PTY leader as a zombie, prove two empty inventories do not reap it, and prove the
  third preserves exact exit status and idempotent later polling;
- create a finite churn tree of at most 48 descendants, move descendants into separate process
  groups, start close while churn is active, and verify shutdown convergence plus death of captured
  process incarnations; and
- retain every earlier capability, descriptor, seccomp-argument, parent-death, strict
  Landlock/MDWE, separate-process-group, natural-leader, controller, restart-fence, and authority
  oracle.

The churn test uses cumulative identity capture rather than requiring a scheduler-specific snapshot.
The sanitizer whole-binary lifecycle test is marked `RUN_SERIAL`, so `ctest -j` does not turn CPU
contention from unrelated shadow-instrumented registries into a false queue-coalescing failure.

## Construction defects found and closed

1. **Mutable proc pathname re-resolution.** The rev0023 sweep reread numeric paths. rev0024 pins the
   proc inventory and candidate process directory and adds the independent start-time witness.
2. **One-empty-scan leader release.** One empty inventory could immediately release the session-ID
   pin. rev0024 requires three consecutive complete empty inventories.
3. **Payload process-handle acquisition.** The final payload could still call reviewed pidfd and
   process-memory release/advice interfaces. The baseline/strict filter and exec oracle now cover
   them.
4. **Host dump/core exposure.** Enabling a terminal host did not change the long-lived Agent's
   same-UID dumpability/core policy. The explicit host path now seals and verifies both properties.
5. **Scheduler-sensitive churn evidence.** An intermediate test expected several descendants to be
   visible in one narrow observation instant. The final oracle accumulates stable PID/start-time
   identities over a bounded window.
6. **Parallel sanitizer test interference.** A four-way TSan validation run caused the timing-sensitive
   whole-binary queue oracle to compete with multiple instrumented registries. The test passed alone;
   sanitizer configurations now declare it serial, and the final parallel grouped lanes pass.

## Final-source qualification

### Native builds and suites

| Lane | Compiler mode | Build | CTest |
|---|---|---:|---:|
| GCC 14 Debug | warnings as errors | complete current target graph | 14/14 passed |
| Clang 17 Debug | warnings as errors | complete current target graph | 14/14 passed |
| GCC 14 Release | optimized, warnings as errors | clean full target graph | 14/14 passed |

The direct GCC Debug owned registry passed **295/295** checks. The GCC Release native PTY process
suite passed 30 consecutive repetitions after the final process implementation was in place.

### Sanitizer and analyzer lanes

| Lane | Scope | Result |
|---|---|---:|
| Clang 17 ASan + UBSan | complete target graph; 16 registry shards plus 13 process/CLI/analyzer tests | 29/29 passed |
| GCC 14 TSan | complete target graph; 16 registry shards plus 13 process/CLI/analyzer tests | 29/29 passed |
| Clang static analyzer | `src/terminal_posix.cpp` under project warning flags | no finding emitted |
| Python bytecode compile | all `tools/*.py` | passed |
| Ratox R7 analyzer self-test | canonical self-test corpus | passed |

A retained log scan found no AddressSanitizer, LeakSanitizer, UndefinedBehaviorSanitizer, or
ThreadSanitizer diagnostic in the final passing logs.

### Identity and boundary gates

```text
product identity: IoTox 0.24.0 rev0024
codename: Procfd Quiescence Process-Guard Citadel
owned registry: 295/295
native CTest: 14/14 in GCC Debug, Clang Debug, and GCC Release
ASan/UBSan CTest surface: 29/29
TSan CTest surface: 29/29
release PTY process repetition: 30/30
procfs inventory type verification: implemented and exercised
PID/session/start-time revalidation: implemented and exercised
three-empty-inventory reap gate: implemented and exercised
reviewed process-handle filter: implemented and exercised
terminal-host dump/core seal: implemented and exercised
```

## Retained evidence

The revision-owned evidence set is under `artifacts/rev0024/` and includes configuration/build logs,
all native CTest logs, the verbose 295-check registry, sanitizer shard/process logs, the PTY repetition
log, static-analyzer output, Python/analyzer checks, product identity, source-integrity metadata,
validation summary, and `SHA256SUMS`. Every executable gate has an adjacent `.exit` file.

## Security boundary and nonclaims

rev0024 claims only the reviewed behavior of baseline and strict PTY sessions on a Linux host where
required procfs, pidfd, seccomp, and optional strict-tier primitives are established. It does not
prove or provide:

```text
delegated cgroup-v2 ownership, cgroup.kill atomicity, migration control, accounting, or quotas
a created PID, user, mount, network, time, or cgroup namespace sandbox
filesystem read/execute confinement beyond the documented strict Landlock rules
a complete syscall, ioctl, prctl, or process-handle allowlist
proof against every possible fork/procfs enumeration schedule
protection from root, kernel compromise, a hostile hypervisor, or physical memory capture
secret-page locking, crash-system qualification, or target-fleet kernel qualification
public Tox route qualification or a two-physical-host Ratox R7 result
remote hardware attestation, hardware power-cut durability, or production readiness
an independent third-party security audit or certification
```

The next stronger lifecycle boundary is explicit delegated cgroup-v2 ownership with separately proven
creation, migration prevention, accounting, and `cgroup.kill` semantics—not an overclaim that repeated
procfs inventories already provide those properties.
