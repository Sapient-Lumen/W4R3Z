# IoTox cloudtainer build report — rev0023

**Construction date:** 2026-08-17 America/New_York
**Version:** 0.23.0
**Revision:** rev0023
**Codename:** Session-Swept Argument-Fence Citadel
**Conversation handoff:** rev0010

## Outcome

rev0023 materially strengthens the native Linux PTY boundary introduced in rev0022. The final source
closes five concrete classes of escape or lifecycle ambiguity that remained after the earlier
syscall-number-only seccomp floor:

1. terminal mutation requests hidden inside `ioctl(2)` arguments;
2. namespace creation bits hidden inside legacy `clone(2)` arguments and uninspectable `clone3(2)`
   flags;
3. payload attempts to detach from the helper-created session or weaken the verified-parent contract;
4. inherited descriptors above a lowered `RLIMIT_NOFILE` ceiling; and
5. descendants in a different process group but the same PTY session surviving group-only shutdown.

The construction is fail closed in baseline and strict modes when the exact pidfd/procfs primitives
needed to prove session signaling are unavailable. Compatibility mode remains intentionally weaker and
retains its historical process-group lifecycle for canonical-v1 migration.

This is a bounded Linux process boundary, not a container, cgroup, namespace, virtual machine, complete
syscall allowlist, or production security certification.

## Constructed boundary

### Shared argument-aware terminal policy

`include/iotox/terminal_seccomp_policy.hpp` owns one compile-time terminal/console ioctl request table.
The classic-BPF builder and the independent exec'd payload oracle consume that same table, preventing
policy/test drift caused by duplicate names or indirect header inclusion.

On the qualification host, the reviewed Linux headers expose 29 unique requests covering:

- controlling-terminal detach and assignment;
- terminal input injection and line-discipline mutation;
- console redirection and virtual hangup;
- keyboard, font, console-mode, and virtual-terminal mutation.

Compile-time assertions require the table to be nonempty, bounded, unique, and to exclude ordinary
window query and resize requests. The native oracle proves every compiled request is intercepted with
`EPERM`, while ordinary `TIOCGWINSZ` validation still reaches the kernel.

### Namespace and lifecycle argument fences

The legacy clone filter inspects the architecture-correct flags argument and rejects the reviewed
namespace bits:

```text
CLONE_NEWNS, CLONE_NEWCGROUP, CLONE_NEWUTS, CLONE_NEWIPC,
CLONE_NEWUSER, CLONE_NEWPID, CLONE_NEWNET
```

`CLONE_NEWTIME` is deliberately excluded from the legacy mask because its numeric bit overlaps the
traditional clone exit-signal field. Time-namespace creation remains blocked through the existing
whole-syscall `unshare(2)`/`setns(2)` denials and the `clone3(2)` fallback boundary.

Classic BPF cannot dereference `struct clone_args`; therefore `clone3(2)` returns `ENOSYS`, allowing
libc to retry the inspected legacy clone path. The process oracle proves real `fork()` and
`std::thread` creation still work after the filter is installed.

After helper setup, baseline and strict also deny:

- `setsid(2)`;
- `prctl(PR_SET_PDEATHSIG, ...)`;
- `TIOCNOTTY`; and
- `TIOCSCTTY`.

This freezes the reviewed PTY session and verified-parent properties while preserving ordinary
same-session job-control process groups.

### Descriptor closure based on inventory, not limits

Lowering `RLIMIT_NOFILE` does not close already-open descriptors above the new soft limit. The final
handoff therefore treats `close_range(2)` only as an acceleration. It then inventories
`/proc/self/fd`, closes every unreserved descriptor except the inventory handle, and performs a second
inventory pass to prove the postcondition before target exec.

The native fixture duplicates a non-CLOEXEC descriptor above 255 and proves it is absent in the final
payload. The rule applies to compatibility, baseline, and strict modes.

### Required pidfd/procfs primitives

Before allocating a PTY, baseline and strict verify that the actual supervisor environment supports:

```text
pidfd_open
pidfd_send_signal
readable /proc/<pid>/stat identity
readable /proc process inventory
```

Immediately after `posix_spawn`, the parent retains a close-on-exec pidfd for the child leader. Any
failure is a named startup error; baseline and strict do not silently degrade to numeric-PID or
process-group-only claims.

Exit observation prefers `waitid(P_PIDFD, ..., WNOWAIT)`. Where a retained pidfd exists but pidfd
waiting returns the narrow compatibility errors `EINVAL` or `ENOSYS`, IoTox observes the still-waitable
direct child through `waitid(P_PID, ..., WNOWAIT)` and performs exact `waitpid` reap. The pidfd remains
available for identity-bound session signaling.

### Session-wide, PID-identity-aware teardown

The helper's successful `setsid(2)` makes the child PID the fixed PTY session ID. Baseline and strict
shutdown now use that session—not merely the initial process group—as the lifecycle unit.

For HUP, TERM, and KILL stages, the supervisor:

1. inventories `/proc`;
2. parses each candidate's session ID from `/proc/<pid>/stat`;
3. selects live members of the fixed PTY session;
4. opens a pidfd for each candidate;
5. re-reads and revalidates session identity after pidfd acquisition; and
6. signals with `pidfd_send_signal(2)`.

Revalidation prevents a PID that disappeared and was reused during inventory/open from entering the
signal set. Once KILL begins, each poll repeats the SIGKILL sweep until no live executable session
member remains.

If the leader exits naturally while descendants remain, the leader stays waitable while IoTox drains
the session. Keeping it waitable pins the numeric PID that is also the session ID. The exact natural
leader status is then reaped and preserved. Startup failure and destructor paths use the same bounded
best-effort sweep before last-resort group/leader fences.

A failed procfs or pidfd sweep is surfaced as an error. Last-resort direct signals are still attempted
for safety but do not convert an unproved sweep into success.

## Construction defects found and closed

The build process exposed and corrected several defects rather than merely documenting them:

1. **Syscall-number-only filtering.** Dangerous terminal and namespace operations remained reachable
   through arguments. The final filter has reviewed exact and masked argument rules.
2. **Oracle drift.** The first test duplicated ioctl names and could silently shrink through indirect
   includes. Enforcement and verification now share one constexpr policy table.
3. **Legacy time-namespace mask error.** An intermediate mask included `CLONE_NEWTIME` despite its
   overlap with the legacy signal field. The final mask excludes it.
4. **Group-only shutdown.** Retaining a leader pidfd did not contain a descendant in another process
   group. The final lifecycle unit is the fixed PTY session.
5. **Limit-bounded descriptor scan.** A lowered `RLIMIT_NOFILE` was mistaken for closure. The final
   child inventories and proves the actual descriptor table.
6. **Payload lifecycle mutation.** A final payload could attempt `setsid`, terminal detach/reassignment,
   or clearing `PR_SET_PDEATHSIG`. Those reviewed transitions are now denied after setup.
7. **Release identity drift.** Textual version fields were advanced while numeric minor/revision
   constants remained stale in an intermediate tree. An owned coherence check now binds all fields.
8. **Sanitizer helper startup.** TSan, like ASan, reserves a large shadow mapping before the helper
   reaches `main`; inheriting the test profile's finite `RLIMIT_AS` prevented readiness. Sanitizer-only
   helper lanes omit that test limit while ordinary debug/release and final payload lanes retain it.
9. **Evidence overclaim risk.** Late session-containment work invalidated earlier broad sanitizer logs.
   Those attempts were discarded. The final source was rebuilt from empty roots and all 29 unique
   ASan/UBSan tests plus all 29 unique TSan tests were re-run in bounded groups.
10. **Abandoned-run interference.** A detached validation command from the discarded attempt later
    re-entered standard build/log paths. Its processes were terminated, affected logs were rejected,
    and the final TSan lane used a unique build root with the exact preset-equivalent cache settings.
    Retained evidence was reconstructed only from controlled final-source commands.

## Online source review

Primary Linux references were rechecked online on 2026-08-17 and are retained in
`docs/research/sources.md` and `docs/research/terminal-session-containment-rev0023.md`. They cover:

- seccomp filter architecture and argument semantics;
- terminal ioctl families and `TIOCSTI`;
- legacy clone/clone3 flags;
- `setsid`, `prctl`, and parent-death signals;
- `pidfd_open`, `pidfd_send_signal`, `waitid`, and Linux pidfd UAPI values;
- `/proc/<pid>/stat` session identity; and
- `close_range` descriptor semantics.

The sources establish kernel interface semantics. They do not audit IoTox, qualify every target
kernel, establish physical-host truth, or certify a complete sandbox.

## Final-source qualification

### Complete non-sanitized builds and suites

The final source was built from empty roots with warnings treated as errors in three independent
configurations:

| Lane | Build status | CTest status |
|---|---:|---:|
| GCC 14 Debug | complete target graph | 14/14 passed |
| Clang 17 Debug | complete target graph | 14/14 passed |
| GCC 14 Release | complete target graph | 14/14 passed |

The direct GCC Debug owned registry passed `294/294` checks. The optimized native PTY process oracle
passed 100 consecutive repetitions.

### Sanitizer and analyzer lanes

Both sanitizer configurations built the complete final target graph. Their 29-test CTest surfaces
were executed in bounded groups: 16 owned-registry shards, 11 supporting process/CLI/analyzer tests,
one native terminal process test, and one binary lifecycle process test.

| Lane | Final-source scope | Result |
|---|---|---:|
| Clang 17 ASan/UBSan | complete target graph; all 29 unique tests | 29/29 passed; no retained diagnostic |
| GCC 14 TSan | complete target graph in isolated preset-equivalent root; all 29 unique tests | 29/29 passed; no retained diagnostic |
| Clang static analyzer | `src/terminal_posix.cpp` with the warning policy | no findings |

The sanitizer log scan covers configure, build, shard, supporting-process, terminal-process, and
binary-process logs. It found no AddressSanitizer, UndefinedBehaviorSanitizer, LeakSanitizer, or
ThreadSanitizer diagnostic.

### Identity and support gates

```text
product identity: IoTox 0.23.0 rev0023
codename: Session-Swept Argument-Fence Citadel
owned registry: 294/294
compiled terminal ioctl request count: 29
Python bytecode compilation: pass
Ratox R7 analyzer self-test: pass
release PTY process stress: 100/100
```

The native process oracle covers all shared terminal mutation requests, ordinary window ioctls,
namespace-bearing and ordinary clone behavior, clone3 fallback, real fork/thread creation, lifecycle
mutation denials, high inherited descriptor closure, retained child pidfd, forced separate-process-
group teardown, and natural leader-status preservation while the remaining session is drained.

## Retained evidence

The revision-owned evidence set is under `artifacts/rev0023/`:

```text
gcc-debug-configure.log
gcc-debug-build.log
gcc-debug-ctest.log
gcc-debug-owned-registry.log
clang-debug-configure.log
clang-debug-build.log
clang-debug-ctest.log
gcc-release-configure.log
gcc-release-build.log
gcc-release-ctest.log
gcc-release-terminal-process-repeat100.log
clang-asan-ubsan-configure.log
clang-asan-ubsan-build.log
clang-asan-ubsan-owned-shards-ctest.log
clang-asan-ubsan-supporting-processes-ctest.log
clang-asan-ubsan-terminal-process-ctest.log
clang-asan-ubsan-binary-process-ctest.log
gcc-tsan-configure.log
gcc-tsan-build.log
gcc-tsan-owned-shards-ctest.log
gcc-tsan-supporting-processes-ctest.log
gcc-tsan-terminal-process-ctest.log
gcc-tsan-binary-process-ctest.log
clang-static-analyzer-terminal-posix.log
sanitizer-diagnostics-scan.log
product-identity.log
terminal-policy-compile-oracle.log
python-py-compile.log
ratox-r7-analyzer-self-test.log
toolchain-and-identity.txt
source-integrity.log
validation-summary.txt
SHA256SUMS
```

Every executable gate has an adjacent `.exit` file. `SHA256SUMS` covers all other files in the
revision evidence directory and is verified before packaging.

## Security boundary and nonclaims

rev0023 claims session-wide lifecycle containment only for the reviewed Linux baseline/strict PTY
boundary when the required pidfd/procfs primitives are established. It includes ordinary separate
process groups that remain in the helper-created session.

rev0023 does **not** prove or provide:

```text
cgroup accounting, quotas, or an independent cgroup kill boundary
a created PID, user, mount, network, or time namespace sandbox
mount graph, filesystem read, or executable-content isolation
a complete syscall allowlist or complete ioctl audit
virtual-machine or hardware isolation
proof against unknown future session-escape interfaces
qualification on every kernel, libc, architecture, or terminal payload
public Tox route qualification or a two-physical-host Ratox R7 result
remote hardware attestation or hardware power-cut durability
production readiness or a third-party security audit
```

The next engineering steps are deployment-kernel qualification, real-payload syscall/ioctl inventory,
continued Linux interface review, and evaluation of cgroup v2 as a separate resource and lifecycle
boundary rather than an inferred property of this PTY session construction.
