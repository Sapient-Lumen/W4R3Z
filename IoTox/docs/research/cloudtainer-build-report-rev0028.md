# IoTox cloudtainer build report — rev0028

**Date:** 2026-08-18 America/New_York
**Version:** 0.28.0
**Revision:** rev0028
**Codename:** Boot-Bound Cgroup Orphan Reaper Citadel
**Linked outer revision:** rev0015
**Qualified source commit:** `202e0d1654f11137b64ea431a172da386f9981b7`

## Outcome

rev0028 closes the delegated-terminal-cgroup crash-orphan gap without trusting a reusable numeric PID
or turning startup recovery into an unbounded destructive scan. Every newly created leaf is bound to
the creating daemon's canonical Linux boot ID, positive PID, procfs field-22 start time, and a local
sequence. Startup acquires the signed device-bound Ratox host-incarnation lease before it inspects or
mutates the delegated namespace, so two legitimate daemons cannot race the recovery decision.

Recovery opens and pins the real procfs and cgroup-v2 objects, inventories the complete bounded
reserved-name set, and preflights every candidate before the first kill or remove operation. Exact live
versioned owners are preserved. Proven-stale versioned subtrees receive `cgroup.kill`; the daemon then
waits on the already-open `cgroup.events` descriptors as one bounded `poll()` set until every recursive
`populated` value reaches zero. Empty legacy PID-only leaves may be removed without killing anything;
populated legacy leaves and malformed reserved names refuse startup fail closed.

The final product change removes the prior one-millisecond sleep loop from both startup recovery and
orderly cgroup teardown. It handles `EINTR`, rounds finite deadlines without truncating a remaining
fractional millisecond to an immediate timeout, accepts the kernel's cgroup state-change notification
bits, strictly re-reads complete event records after each wake, and rejects missing or invalid pinned
descriptors. Multiple stale leaves are multiplexed through one bounded wait rather than polled
serially.

A final Clang static-analyzer pass then found two directory-stream uses that assumed `dirfd()` could
not fail: the cgroup child-directory scan and the procfs session sweep. rev0028 now checks both
results before any descriptor-relative operation. Failure returns an I/O error and stops cleanup or
signaling rather than allowing an invalid descriptor to reach `fstatat()` or `openat()`.

The direct owned registry grows from 322 to **329** checks. A separate process oracle uses isolated
user, mount, and cgroup namespaces and a freshly mounted cgroup-v2 hierarchy to exercise the actual
kernel lifecycle rather than an ordinary-directory double.

## Online primary-source review

The construction and final event-wait review rechecked these Linux primary or first-party references
online on 2026-08-18:

- Linux cgroup v2 administration guide:
  <https://docs.kernel.org/admin-guide/cgroup-v2.html>
- Linux kernel sysctl guide, including `boot_id`:
  <https://docs.kernel.org/admin-guide/sysctl/kernel.html>
- Linux `proc_pid_stat(5)`:
  <https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html>
- Linux `pidfd_open(2)`:
  <https://man7.org/linux/man-pages/man2/pidfd_open.2.html>
- Linux `poll(2)` from the kernel man-pages publication:
  <https://www.kernel.org/doc/man-pages/online/pages/man2/poll.2.html>
- Linux `cgroups(7)`:
  <https://man7.org/linux/man-pages/man7/cgroups.7.html>

The relevant kernel contracts are that `cgroup.kill` targets a complete descendant subtree;
`cgroup.events` `populated` is recursive and reports whether the cgroup or a descendant contains a
live process; `cgroup.events` state changes can be monitored with `poll()` exceptional-event
notification; the boot ID is generated once per boot; procfs field 22 identifies process start time
after boot; and a pidfd is a pollable handle to a process lifetime. IoTox's naming, ownership,
preflight, mutation-order, and legacy-refusal rules are deliberately stricter product decisions rather
than claims supplied by those interfaces.

## Constructed security and recovery boundary

### Boot-bound owner names

New terminal leaves use the canonical form:

```text
_iotox_session_v2_<32-lowercase-boot-id-hex>_<pid>_<start-time-ticks>_<sequence>
```

The parser rejects uppercase or noncanonical UUID spellings, zero identity fields, overflow, missing
or trailing components, and aliases. The current daemon identity is read from verified procfs and
canonical boot state rather than accepted from configuration text.

A candidate owner is live only when the recorded boot ID equals the current boot, a pidfd can be
opened for the recorded PID, pinned procfs state remains coherent around that acquisition, field 22
matches exactly, and the task is not already dead or a zombie. Unavailable or contradictory evidence
is an error or stale classification under the documented branch; it is never treated as proof that an
unrelated process may be killed.

### Serialized, complete preflight

The startup order is:

```text
validate static terminal profile and path shape
acquire signed Ratox host-incarnation lease
open and verify procfs plus delegated cgroup-v2 root
inventory and preflight the complete bounded reserved namespace
recover only the preflighted stale set
construct the PTY factory
publish local services and start transport/network work
```

The reserved candidate bound is configurable only within `1..1024`; the quiescence deadline must be
positive and no greater than 30 seconds. Recovery checks the exact cgroup2 filesystem, descriptor-
relative no-follow access, daemon ownership and restrictive modes, domain state, empty child-control
state, absence of nested cgroups, and pinned inode identity. A malformed later candidate therefore
prevents all earlier destructive mutation instead of producing a partial recovery.

### Notification-driven kill and quiescence

After preflight, every proved-stale versioned subtree receives `cgroup.kill`. IoTox keeps each pinned
`cgroup.events` descriptor and repeatedly:

1. reads and strictly parses the complete current record;
2. removes already-empty leaves after exact pathname/inode revalidation;
3. assembles all still-populated descriptors into one bounded `poll()` set;
4. waits only until the shared absolute deadline; and
5. re-reads state after a kernel notification.

`POLLPRI` is requested. `POLLPRI` and `POLLERR` are accepted as documented cgroup state-change
notification, while invalid or hung descriptors fail closed. `EINTR` retries without extending the
absolute deadline. This construction avoids the former fixed-frequency wake loop and scales one wait
over the bounded stale set.

Orderly session teardown uses the same event-notification helper after its own `cgroup.kill`, so normal
cleanup and crash recovery share the same finite recursive-quiescence semantics.

### Legacy and observability policy

An empty legacy `_iotox_session_<pid>_<sequence>` leaf can be removed because no process is affected.
A populated legacy leaf cannot prove a PID-reuse-safe historical owner and therefore blocks startup
without killing or removing its payload. A malformed reserved-prefix name also blocks startup.

Runtime status exposes only aggregate recovery counts: reserved names, exact live incarnations,
classified stale incarnations, recovered incarnations, and empty legacy leaves removed. It does not
publish boot IDs, PIDs, cgroup names, terminal bytes, command data, profile content, or error payloads.

### Analyzer-driven descriptor failure fences

Both directory-stream conversions now cache and validate the `dirfd()` result once before entering
their bounded enumeration loops. The cgroup path refuses child inspection if the adopted stream
cannot expose a valid descriptor. The fallback procfs supervisor similarly refuses session-member
inventory before opening any process directory. Focused Clang static-analyzer reruns over
`terminal_cgroup.cpp` and `terminal_posix.cpp` produced no findings after the correction.

## Adversarial evidence added

Seven direct checks account for the registry increase from 322 to 329:

1. canonical Linux boot UUID parsing and compact rendering;
2. exact boot/PID/start-time/sequence cgroup-name round trip;
3. rejection of aliases, zero fields, uppercase hex, overflow, and trailing components;
4. live current-incarnation preservation plus stale boot/start-time classification;
5. pidfd-backed zombie-owner rejection;
6. recovery count/deadline policy validation before filesystem access; and
7. ordinary-filesystem refusal for both creation and recovery.

Agent integration additionally verifies that the signed host lease is held before delegated-root
recovery and that a configured lookalike directory fails before transport state is created.

The `iotox.terminal-cgroup-recovery-process` route performs real kernel operations inside
`unshare -UrCm` and proves:

- exact live-owner preservation;
- an intentionally crashed creator leaves a populated versioned leaf;
- recursive `cgroup.kill` terminates the surviving payload;
- notification-driven waiting observes `populated 0` and removes the exact leaf;
- empty legacy cleanup;
- populated legacy refusal without payload death;
- malformed-name refusal; and
- candidate-bound refusal before any candidate mutation.

The route uses CTest skip code 77 only when the host cannot construct the required namespaces. It
passed, rather than skipped, under both retained compiler builds on this qualification host.

## Validation matrix

All retained compiler lanes use the project's warnings-as-errors configuration. The qualified product
commit is `202e0d1654f11137b64ea431a172da386f9981b7`; evidence/report changes made afterward do not
change product or test source.

### Native and optimized builds

- **GCC 14.2.0 Debug:** final build graph reported no work; the complete direct registry passed
  `tests=329 selected=329 shard=0/1 failures=0`; all **15/15** default CTest routes passed.
- **Clang 17.0.0 Debug:** final build graph reported no work; all **15/15** default CTest routes
  passed with warnings promoted to errors.
- **GCC 14.2.0 Release:** optimized warnings-as-errors build completed; the final build graph reported
  no work; all **15/15** default CTest routes passed.

Every native suite includes the namespace-backed `iotox.terminal-cgroup-recovery-process` route. A
separate direct invocation also printed `PASS boot-bound cgroup orphan recovery process oracle`.

### Dynamic sanitizer

- **Clang 17.0.0 ASan+UBSan:** the complete instrumented build finished with warnings as errors and a
  16-way owned-registry shard surface. All **30/30** configured routes passed after the final
  analyzer-driven source correction, including all 16 registry shards, the whole-binary lifecycle
  route, the real cgroup-v2 process oracle, and the Ratox R7 analyzer.
- A retained diagnostic scan found no AddressSanitizer, LeakSanitizer, UndefinedBehaviorSanitizer, or
  `runtime error:` signature.

ThreadSanitizer was not rerun for the exact final source commit and is not claimed.

### Static and auxiliary validation

- Focused Clang static analysis of `src/terminal_cgroup.cpp`: zero findings.
- Focused Clang static analysis of `src/terminal_posix.cpp`: zero findings.
- Python bytecode compilation: all three `tools/*.py` programs passed.
- Product identity: `IoTox 0.28.0 rev0028`.
- Source integrity: `git diff --check` passed and the source worktree was clean at qualified commit
  capture.
- Final build proofs: GCC Debug, Clang Debug, Clang ASan+UBSan, and GCC Release each ended with
  `ninja: no work to do`.

## Qualification-host facts

```text
kernel: Linux 6.18.35 x86_64
CMake: 3.31.6
Ninja: 1.12.1
GCC: 14.2.0
Clang: 17.0.0
Python: 3.13.5
user/mount/cgroup namespace process oracle: passed
fresh writable cgroup-v2 mount inside that namespace: passed
```

This host proves the executed Linux branches on this kernel and toolchain combination. It does not
qualify every kernel version, libc, cgroup delegation topology, service manager, filesystem, scheduler,
or production target.

## Evidence inventory

Revision-owned evidence is retained under `artifacts/rev0028/`:

- final no-work build proofs for GCC Debug, Clang Debug, Clang ASan+UBSan, and GCC Release;
- complete zero-exit CTest transcripts for all three native/optimized 15-route suites and the
  30-route sanitizer suite;
- the complete 329-check direct registry transcript and the direct real-cgroup process oracle;
- focused zero-finding Clang static-analyzer results for the cgroup and procfs supervisor units;
- Python bytecode, source-integrity, host/toolchain, sanitizer-signature, CTest-inventory, online-
  source, exact-history, exit-code, validation-summary, and SHA-256 evidence.

The repository datacube packages a clean tracked commit, complete reachable Git history, and exact
revision-owned evidence. The earlier evidence-only commit `3802ebd` qualified the parent before the
`dirfd()` correction and is explicitly superseded by the final evidence directory; it is retained in
Git history only as provenance.

## Nonclaims and remaining work

rev0028 does not claim:

- protection from root or another writer with equivalent delegated-cgroup authority;
- cryptographic authorization or isolation among arbitrary processes intentionally sharing one UID;
- cgroup CPU, memory, I/O, process-count, or denial-of-service resource policy;
- namespace, container, VM, network, or complete LSM isolation of a terminal payload;
- PTY/controller state continuity across daemon restart;
- automatic migration or killing of populated legacy PID-only leaves;
- proof across every target kernel, cgroup delegation arrangement, service manager, or hardware fleet;
- public tox-network or two-physical-host Ratox R7 qualification;
- power-cut, storage-rollback, or long-duration fault-injection qualification;
- independent security audit, production certification, or production readiness.
