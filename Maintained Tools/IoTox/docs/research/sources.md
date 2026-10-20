# Research sources and retained readings

## rev0039 continuous cgroup PSI trigger sources

Primary online sources retrieved and rechecked 2026-08-19:

- Linux kernel, *PSI — Pressure Stall Information*: https://docs.kernel.org/accounting/psi.html
- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux man-pages, *poll(2)*: https://man7.org/linux/man-pages/man2/poll.2.html

Applied records:

```text
linux-cgroup-psi-trigger-tripwire-rev0039.md
../decisions/0090-latch-ratox-admission-with-continuous-cgroup-psi-triggers.md
```

Applied boundary: independently opened per-cgroup PSI trigger descriptors; one finite poll/eventfd monitor;
validated 500ms..10s windows and positive cumulative stall thresholds; saturation-safe atomic event transfer;
minimum-window holds; exact avg10-hysteresis reopening; fail-closed monitor health and owner-private bounded
projection. This is proactive host-local load shedding, not real-time delivery, atomic multi-resource sampling,
capacity prediction, tuned defaults, existing-session preemption, or target-fleet qualification.

## rev0038 cgroup PSI admission sources

Primary online sources retrieved and rechecked 2026-08-19:

- Linux kernel, *PSI — Pressure Stall Information*: https://docs.kernel.org/accounting/psi.html
- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux source, *kernel/sched/psi.c*: https://github.com/torvalds/linux/blob/master/kernel/sched/psi.c

Applied records:

```text
linux-cgroup-psi-admission-rev0038.md
../decisions/0089-admit-new-pty-sessions-with-cgroup-psi-hysteresis.md
```

Applied boundary: exact delegated-root CPU `some avg10`, memory `full avg10`, and I/O `full avg10`
basis-point thresholds; descriptor-pinned startup capability validation; fail-closed synchronous sampling;
latched hysteresis before aggregate reservation or process mutation; saturation-safe owner-private policy and
outcome counters. This is host-local load shedding, not atomic cross-resource sampling, capacity prediction,
a latency/throughput guarantee, adaptive thresholding, remote profile policy, or target-fleet qualification.

## rev0037 memory-work, swap-failure, freeze, and IRQ-accounting sources

Primary online sources retrieved 2026-08-19:

- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux kernel, *PSI — Pressure Stall Information*: https://docs.kernel.org/accounting/psi.html
- Linux source, *include/linux/psi_types.h*: https://github.com/torvalds/linux/blob/master/include/linux/psi_types.h
- Linux source, *kernel/sched/psi.c*: https://github.com/torvalds/linux/blob/master/kernel/sched/psi.c

Applied records:

```text
memory-work-swap-irq-freeze-kernel-accounting-rev0037.md
../decisions/0088-retain-memory-work-swap-freeze-and-irq-outcomes.md
```

Applied boundary: protected pre-attachment `memory.stat`, `memory.swap.events`, `cgroup.stat.local`,
and `irq.pressure`; exact zero baselines; complete optional reclaim/swap tuples; current-kernel-correct
IRQ `full` semantics; post-quiescence one-shot capture; saturation-safe content-free owner-private
projection. These are completed-session cumulative outcomes, not causal attribution, live monitoring,
working-set analysis, adaptive policy, or target-fleet qualification.

## rev0036 peak-resource kernel-accounting sources

Primary online sources retrieved 2026-08-19:

- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux source tree, *Control Group v2*: https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/cgroup-v2.rst

Applied records:

```text
peak-resource-kernel-accounting-rev0036.md
../decisions/0087-retain-cgroup-lifetime-peaks-and-complete-cpu-work.md
```

Applied boundary: protected optional `pids.peak`, `memory.peak`, `memory.swap.peak`, and quota-independent
`cpu.stat`; exact zero baseline; post-quiescence lifetime peaks and complete CPU work/bandwidth/burst
tuples; explicit capability counts; saturation-safe content-free runtime projection. These outcomes are
not live policy, simultaneous capacity estimates, working-set inference, or per-process attribution.

## rev0035 pressure-stall kernel-accounting sources

Primary online sources retrieved 2026-08-19:

- Linux kernel, *PSI — Pressure Stall Information*: https://docs.kernel.org/accounting/psi.html
- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html

Applied records:

```text
pressure-stall-kernel-accounting-rev0035.md
../decisions/0086-retain-cgroup-pressure-stall-outcomes.md
```

Applied boundary: protected optional per-cgroup CPU, memory, and I/O PSI interfaces; exact enabled
state when `cgroup.pressure` exists; zero-baseline and post-quiescence absolute microsecond totals;
explicit whole-interface and `full` availability; saturating content-free runtime projection. This is
completed-session observation, not rolling averages, trigger monitoring, adaptive admission, causal
diagnosis, capacity estimation, or target-fleet qualification.

## rev0034 I/O bandwidth and kernel-accounting sources

Primary online sources retrieved 2026-08-19:

- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html
- systemd, *Control Group APIs and Delegation*: https://systemd.io/CGROUP_DELEGATION/

Applied records:

```text
io-bandwidth-kernel-accounting-rev0034.md
../terminal-profile-v5.md
../decisions/0085-add-device-io-ceilings-and-retain-kernel-io-accounting.md
```

Applied boundary: historical canonical profile v5 device/rate policy (preserved in current profile
v6); exact host/profile device agreement and
per-direction minima; delegated `io` controller activation; complete `io.max` write and semantic
readback; protected zero-baseline `io.stat`; teardown-time saturating read/write/discard totals;
owner-private content-free projection. Rate ceilings are not aggregate bandwidth reservations,
latency guarantees, topology discovery, PSI policy, or target-fleet qualification.

## rev0033 memory-high and kernel outcome telemetry sources

Primary online sources retrieved 2026-08-19:

- Linux kernel, *Control Group v2*: https://docs.kernel.org/admin-guide/cgroup-v2.html
- systemd, *Control Group APIs and Delegation*: https://systemd.io/CGROUP_DELEGATION/

Applied records:

```text
memory-high-kernel-outcome-telemetry-rev0033.md
cloudtainer-build-report-rev0033.md
../terminal-profile-v4.md
../decisions/0084-add-memory-throttle-and-retain-kernel-session-outcomes.md
```

Applied boundary: canonical profile v4 `memory.high`; monotone host/profile composition; exact
controller write/read-back; zero-baseline protected statistics descriptors; bounded keyed parsing;
teardown-time PID, memory, and CPU outcome accumulation; private content-free runtime projection.

## rev0032 exact rational CPU reservation-admission sources

Primary references rechecked 2026-08-19 America/New_York:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://docs.kernel.org/scheduler/sched-bwc.html
https://systemd.io/CGROUP_DELEGATION/
https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html
```

Retained application records:

```text
../decisions/0083-admit-exact-rational-aggregate-cpu-bandwidth.md
exact-rational-cpu-reservation-admission-rev0032.md
cloudtainer-build-report-rev0032.md
```

Applied boundary: exact average-bandwidth comparison and integral normalization of heterogeneous
finite `cpu.max` ratios to one explicit host accounting period; atomic inclusion in the existing
process/memory/swap reservation vector; pre-network and pre-mutation rejection; teardown-coupled
release/stranding; and owner-private quota/period/current/peak truth. The sources define Linux CPU
bandwidth and systemd delegation interfaces. They do not audit IoTox, align independent period
boundaries, enforce a parent CPU ceiling, reserve processor time, establish latency/throughput or PSI
policy, exclude a privileged co-writer, qualify a deployment fleet, or prove production readiness.

## rev0031 aggregate cgroup reservation-admission sources

Primary references rechecked 2026-08-19 America/New_York:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://docs.kernel.org/accounting/psi.html
https://systemd.io/CGROUP_DELEGATION/
```

Retained application records:

```text
../decisions/0082-admit-pty-sessions-under-exact-aggregate-cgroup-reservations.md
aggregate-cgroup-reservation-admission-rev0031.md
cloudtainer-build-report-rev0031.md
```

Applied boundary: host-local exact reservation of configured post-composition process, memory, and
swap maxima; all-profile startup fit proof; atomic pre-mutation admission; move-only rollback and
full-lifecycle ownership; overflow-safe concurrency; and owner-private current/peak/rejection truth.
The sources define overcommittable cgroup-v2 limits, pressure interfaces, and delegated-tree ownership.
They do not audit IoTox, reserve physical resources, establish aggregate CPU or PSI policy, exclude a
privileged co-writer, size a deployment, or prove production readiness.

## rev0030 profile-scoped cgroup budget-ceiling sources

Primary references rechecked 2026-08-18 America/New_York:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://systemd.io/CONTROL_GROUP_INTERFACE/
```

Retained application records:

```text
../decisions/0081-compose-profile-cgroup-budgets-under-host-ceilings.md
../terminal-profile-v3.md
profile-scoped-cgroup-budget-ceilings-rev0030.md
cloudtainer-build-report-rev0030.md
```

Applied boundary: canonical profile v3 cgroup fields; monotone host/profile minima; exact
quota/period comparison without floating point or overflow; explicit delegation for every effective
budget; `(payload identity, effective budget)` startup preflight; production-factory recomposition; and
aggregate-only runtime truth. The sources define hierarchical cgroup-v2 restriction and the systemd
single-writer/delegation contract. They do not audit IoTox, establish aggregate admission policy,
exclude privileged co-writers, or qualify a deployment fleet.

## rev0029 controller-enforced cgroup resource-budget sources

Primary references rechecked 2026-08-18 America/New_York:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://docs.kernel.org/scheduler/sched-bwc.html
https://systemd.io/CGROUP_DELEGATION/
```

Retained application records:

```text
../decisions/0080-enforce-global-pty-resource-budgets-in-delegated-cgroups.md
controller-enforced-cgroup-resource-budgets-rev0029.md
cloudtainer-build-report-rev0029.md
```

Applied boundary: one optional host-owned PTY envelope for `pids.max`, `memory.max`,
`memory.swap.max`, `memory.oom.group`, and `cpu.max`; exact controller availability/activation
checks; payload-unwritable controls; pre-attachment write/read-back; and exact-identity pre-network
probe leaves. The sources define Linux and systemd interfaces. They do not audit IoTox, size a
production policy, establish privileged-writer exclusion, qualify this host's skipped positive process
oracle, or prove target-fleet readiness.

## rev0028 boot-bound delegated-cgroup recovery sources

Primary references rechecked 2026-08-18 America/New_York:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://docs.kernel.org/admin-guide/sysctl/kernel.html
https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://man7.org/linux/man-pages/man2/poll.2.html
```

Retained application records:

```text
../decisions/0079-bind-delegated-cgroup-lifecycles-to-boot-and-process-incarnations.md
boot-bound-cgroup-orphan-recovery-rev0028.md
cloudtainer-build-report-rev0028.md
```

Applied boundary: canonical boot/PID/procfs-start-time cgroup ownership; verified procfs and cgroup-v2
descriptor roots; pidfd-backed exact owner classification; signed-host-lease serialization; bounded
full-set preflight; live preservation; recursive kill/quiescence/exact removal of proved-stale versioned
leaves; empty-legacy cleanup; and populated-legacy/malformed fail-closed refusal. The sources define
Linux interface semantics. They do not audit IoTox, establish exclusive delegation, add resource
policy or namespace isolation, recover unsafe populated legacy leaves, qualify a target fleet, or
prove production readiness.

## rev0027 process-pinned bounded local seqpacket sources

Primary references rechecked 2026-08-18 America/New_York:

- Linux UAPI socket options for `SO_PASSPIDFD` and `SO_PEERPIDFD`.
- Linux generic socket implementation for `SO_PEERPIDFD`, including the no-peer `ENODATA` result.
- Linux networking maintainer summary recording the Linux 6.5 introduction of `SCM_PIDFD` and
  `SO_PEERPIDFD` for Unix sockets.
- Linux `pidfd_open(2)` poll readability and hangup semantics after process exit/reap.
- Linux `poll(2)` readiness, finite timeout, and simultaneous socket/hangup event behavior.

Retained application records:

```text
../decisions/0077-bound-and-multiplex-local-seqpacket-admission.md
../decisions/0078-pin-local-seqpacket-connections-to-peer-process-lifetimes.md
bounded-local-ipc-admission-rev0027.md
process-pinned-local-ipc-lifetimes-rev0027.md
cloudtainer-build-report-rev0027.md
```

Applied boundary: bounded readiness-driven control and contender sets; exact connection-process pidfds
for pending control clients, control-server response waits, and the active terminal connection when
supported; queued administrative control-record-before-exit precedence; terminal live-controller
dispatch fencing; runtime-probed compatibility retaining finite leases and mandatory message-bound
credentials. Same-UID authorization, callback preemption, namespace/
cgroup traffic isolation, target-fleet qualification, and independent production review remain
outside the claim.

## rev0026 message-bound local seqpacket sources

Primary references rechecked 2026-08-18 America/New_York:

- Linux `unix(7)`: `SO_PASSCRED`, per-message `SCM_CREDENTIALS`, connection-time `SO_PEERCRED`,
  `SCM_RIGHTS`, and Unix-domain credential semantics.
- Linux `recv(2)`: `MSG_CTRUNC`, ancillary truncation, and `MSG_CMSG_CLOEXEC`.
- Linux `pidfd_open(2)`: stable process handles and poll readability after process exit.
- Linux networking documentation and kernel headers for Linux 6.5 `SO_PASSPIDFD`/`SCM_PIDFD`.

Retained application records:

```text
../decisions/0076-bind-local-seqpacket-records-to-kernel-sender-evidence.md
message-bound-local-ipc-hardening-rev0026.md
cloudtainer-build-report-rev0026.md
```

Applied boundary: connection credentials plus mandatory bidirectional per-record credentials; optional
kernel sender pidfds; exact terminal process-lifetime ownership; bounded ancillary parsing with
descriptor closure; finite administrative request lease; exact active/stale/replacement socket inode
ownership. Same-UID authorization, hostile-flood fairness, namespaces, and independent production
audit remain outside the claim.

## rev0025 delegated cgroup-v2 lifecycle sources

Primary references rechecked 2026-08-18 America/New_York:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://systemd.io/CGROUP_DELEGATION/
https://man7.org/linux/man-pages/man2/clone.2.html
https://man7.org/linux/man-pages/man7/cgroups.7.html
https://man7.org/linux/man-pages/man2/openat.2.html
https://man7.org/linux/man-pages/man2/statfs.2.html
https://man7.org/linux/man-pages/man2/unlink.2.html
```

Retained decision, applied review, and validation evidence:

```text
../terminal-profile-v2.md
../decisions/0075-own-hardened-pty-lifecycles-with-delegated-cgroup-v2.md
delegated-cgroup-session-containment-rev0025.md
cloudtainer-build-report-rev0025.md
```

Applied boundary: explicit normalized delegation; cgroup-v2 filesystem and supervisor-only ownership
checks; one inode-pinned `_iotox_session_*` domain leaf; blocked-helper migration before manifest
release; required `cgroup.kill`; recursive `cgroup.events` completion; exact empty-leaf removal before
leader reap; and fail-closed Agent/profile compatibility gates. The sources define kernel and service-
manager semantics. They do not audit IoTox, establish resource policy or crash orphan collection, or
replace positive qualification on a writable delegated target host.

## rev0024 procfd quiescence, process-handle, and host-seal sources

Primary references rechecked 2026-08-17 America/New_York:

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
https://man7.org/linux/man-pages/man2/openat.2.html
https://man7.org/linux/man-pages/man2/statfs.2.html
```

Retained decision, applied review, and validation evidence:

```text
../terminal-profile-v2.md
../decisions/0074-pin-session-identities-and-seal-terminal-process-domain.md
terminal-process-domain-hardening-rev0024.md
cloudtainer-build-report-rev0024.md
```

Applied boundary: verified genuine-procfs inventory; descriptor-relative per-process reads; reported
PID/session/live-state/start-time witnesses before and after pidfd acquisition; three consecutive
empty full-session inventories before waitable-leader reap; bounded fork-churn convergence; baseline
payload denial of pidfd open/signal and reviewed pidfd memory interfaces; and enabled-host
nondumpability plus irreversible zero core limits before Agent construction. The cgroup-v2 reference
is retained specifically to distinguish the stronger `cgroup.kill` concurrent-fork/migration contract
from IoTox's bounded userspace procfs quiescence rule. The sources do not audit IoTox, qualify all
kernels, or establish cgroup/namespace/VM containment.

## rev0023 terminal argument-fence and pidfd-supervision sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://man7.org/linux/man-pages/man2/TIOCSTI.2const.html
https://man7.org/linux/man-pages/man4/tty_ioctl.4.html
https://man7.org/linux/man-pages/man2/ioctl.2.html
https://man7.org/linux/man-pages/man2/clone.2.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://man7.org/linux/man-pages/man2/wait.2.html
https://raw.githubusercontent.com/torvalds/linux/v6.18/include/uapi/linux/sched.h
https://raw.githubusercontent.com/torvalds/linux/v6.18/include/uapi/linux/wait.h
```

Retained decision, applied review, and validation evidence:

```text
../terminal-profile-v2.md
../decisions/0073-fence-terminal-lifecycle-and-contain-pty-sessions.md
terminal-session-containment-rev0023.md
cloudtainer-build-report-rev0023.md
```

Applied boundary: one shared build-header-derived terminal/console request table driving enforcement
and the exec'd oracle; request-level ioctl denial with exact compiled-count evidence; architecture-correct
legacy clone namespace-bit denial; clone3-to-legacy compatibility fallback; successful post-filter fork and
thread creation; descriptor-table inventory and proof; required pidfd/procfs support for baseline/strict;
and PID-identity-revalidated signaling of every executable member of the fixed PTY session. The references
do not audit IoTox, qualify all kernels or targets, establish cgroup/namespace/VM containment, or prove
resistance to unknown future session-escape interfaces.

## rev0022 terminal capability and kernel-confinement sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://man7.org/linux/man-pages/man7/capabilities.7.html
https://man7.org/linux/man-pages/man2/capget.2.html
https://man7.org/linux/man-pages/man2/PR_SET_SECUREBITS.2const.html
https://docs.kernel.org/userspace-api/no_new_privs.html
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://man7.org/linux/man-pages/man2/seccomp.2.html
https://docs.kernel.org/userspace-api/landlock.html
https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/landlock.h
https://man7.org/linux/man-pages/man2/PR_SET_MDWE.2const.html
https://man7.org/linux/man-pages/man2/PR_SET_DUMPABLE.2const.html
https://man7.org/linux/man-pages/man2/execve.2.html
```

Retained contract, decision, applied review, and validation evidence:

```text
../terminal-profile-v2.md
../decisions/0072-seal-terminal-capabilities-and-add-tiered-kernel-confinement.md
terminal-confinement-rev0022.md
cloudtainer-build-report-rev0022.md
```

Applied boundary: runtime capability-ceiling discovery; zero active and ambient capability sets;
privileged securebits and bounding-set sealing; a default architecture-checked seccomp hazardous-
interface floor; and an opt-in, fail-closed MDWE plus Landlock ABI 10 mutation/network/IPC profile.
The references define Linux interfaces and compatibility semantics. They do not audit IoTox, qualify
all kernels, or turn the profile into a complete namespace/cgroup/VM sandbox.

## rev0022 Ratox R7 attested-evidence sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://doc.libsodium.org/public-key_cryptography/public-key_signatures
https://docs.kernel.org/admin-guide/sysctl/kernel.html#random
https://www.rfc-editor.org/info/rfc7679/
https://docs.python.org/3/library/os.html
```

Applied in:

```text
docs/decisions/0071-bind-ratox-r7-to-attested-raw-evidence.md
docs/ratox-r7-evidence-v2.md
docs/research/ratox-r7-attested-evidence-chain-rev0022.md
docs/research/cloudtainer-build-report-rev0022.md
include/iotox/interactive_service.hpp
src/interactive_service.cpp
src/local/runtime_tree.cpp
tools/ratox_r7_evidence.py
tools/prepare-ratox-r7.py
tools/analyze-ratox-r7.py
```

The references define detached signature semantics, Linux running-kernel boot IDs, one-way delay clock
constraints, and descriptor/file primitives. They do not establish physical-host truth, route truth,
load truth, binary integrity, or remote attestation for an IoTox run.

## rev0021 Ratox R7 observability and bounded-evidence sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://opentelemetry.io/docs/specs/otel/metrics/data-model/
https://opentelemetry.io/docs/specs/otel/metrics/sdk/
https://man7.org/linux/man-pages/man3/clock_gettime.3.html
https://www.rfc-editor.org/info/rfc6374/
https://cmake.org/cmake/help/latest/command/set_tests_properties.html
https://cmake.org/cmake/help/latest/prop_test/PROCESSORS.html
https://clang.llvm.org/docs/AddressSanitizer.html
https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
```

Retained construction, decisions, and validation evidence:

```text
ratox-r7-observability-rev0021.md
cloudtainer-build-report-rev0021.md
../decisions/0069-measure-queue-tails-and-typed-ratox-send-outcomes.md
../decisions/0070-qualify-ratox-r7-with-bounded-fail-closed-evidence.md
../../tools/analyze-ratox-r7.py
```

Applied boundary: exact-at-the-gate cumulative queue histograms, coherent typed sensitive-send
outcomes, lane-separated retained-head streak/age, monotonic lifecycle time, a bounded canonical R7
matrix analyzer, and opt-in sanitizer sharding. These references define metric, clock, measurement,
CTest, and sanitizer semantics. They do not audit IoTox or prove that a two-host experiment occurred.

## rev0020 Ratox restart-fence sources

Rechecked 2026-08-17:

```text
https://man7.org/linux/man-pages/man2/open.2.html
https://man7.org/linux/man-pages/man2/flock.2.html
https://man7.org/linux/man-pages/man2/rename.2.html
https://man7.org/linux/man-pages/man2/fsync.2.html
https://man7.org/linux/man-pages/man7/path_resolution.7.html
https://man7.org/linux/man-pages/man2/openat2.2.html
https://cwe.mitre.org/data/definitions/367.html
```

Applied notes:

```text
ratox-restart-fence-rev0020.md
cloudtainer-build-report-rev0020.md
../decisions/0068-reserve-signed-ratox-host-incarnation-before-network.md
../evidence/2026-08-17-ratox-restart-fence-process.md
```

These primary Linux references define the descriptor-relative open, close-on-exec, no-follow,
open-file-description lock, atomic rename, and file-plus-directory synchronization semantics consumed
by the restart lane. CWE-367 records the general TOCTOU weakness class. They do not audit IoTox.

Research notes capture the date, source, inference, and evidence boundary. Upstream material
may change; re-check it before changing a protocol or build decision.

## rev0020 local controller fault-gate sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/poll.2.html
https://man7.org/linux/man-pages/man2/accept.2.html
```

Retained review, decision, protocol, and build evidence:

```text
ratox-controller-fault-gate-rev0020.md
cloudtainer-build-report-rev0020.md
../decisions/0067-bound-local-controller-admission-and-contention.md
../terminal-client-v1.md
```

Applied boundary: the first local controller packet has a finite steady-clock lease; active-controller
contention is processed in bounded batches; a contender record may be consumed only to preserve the
exact stream ID and is never dispatched; and pre-OPEN typed errors are connection-scoped while every
success/progress packet remains stream-bound. A real one-binary process gate covers contention,
abrupt controller death, replacement resume, output-before-ACK, and explicit empty-restart failure.
The evidence is one-host local-controller evidence, not complete remote R6 qualification or third-party
approval.

## rev0019 private Ratox controller stream sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/accept.2.html
https://man7.org/linux/man-pages/man3/termios.3.html
https://man7.org/linux/man-pages/man2/ioctl_tty.2.html
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/blob/master/INSTALL.md
https://docs.kernel.org/userspace-api/landlock.html
https://docs.kernel.org/filesystems/proc.html
```

Retained review, decision, protocol, and build evidence:

```text
ratox-controller-stream-rev0019.md
cloudtainer-build-report-rev0019.md
../decisions/0066-separate-private-terminal-controller-stream.md
../terminal-client-v1.md
../protocol-ratox-v1.md
```

Applied boundary: the private terminal path uses Linux pathname `SOCK_SEQPACKET`, owner-only parent
and socket modes, same-user peer credentials, exact stale-inode rechecks, and close-on-exec/nonblocking
descriptors. The pure controller retains exact Ratox packets and replay state under bounds; Agent route
selection remains transcript-, online-epoch-, and authenticated-principal-bound. The one-binary client
acknowledges output only after local write and restores local terminal state. These platform references
are design inputs rather than third-party review or approval.

## rev0018 default-off Ratox Agent dispatch sources

Primary references rechecked 2026-08-17 America/New_York:

```text
https://toktok.ltd/spec.html
https://github.com/TokTok/c-toxcore
https://man7.org/linux/man-pages/man2/openat2.2.html
https://docs.kernel.org/userspace-api/no_new_privs.html
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://docs.kernel.org/userspace-api/landlock.html
```

Retained review, decision, and final build evidence:

```text
ratox-agent-dispatch-rev0018.md
cloudtainer-build-report-rev0018.md
../decisions/0065-gate-live-ratox-dispatch-before-network.md
../protocol-ratox-v1.md
../security-ratox-v1.md
```

Applied boundary: custom-lossless ownership remains with IoTox until c-toxcore accepts the exact
packet; bit 23 is selected only after secure pre-network construction and requires bilateral
transcript confirmation; exact current terminal authority and attachment identity fence every live
packet; Linux path and privilege controls are treated as specific controls rather than a complete
sandbox.

## rev0017 sealed terminal profile and Linux PTY sources

Primary references rechecked 2026-08-16 America/New_York:

```text
https://pubs.opengroup.org/onlinepubs/9799919799/functions/posix_spawn.html
https://man7.org/linux/man-pages/man7/pty.7.html
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/setresuid.2.html
https://man7.org/linux/man-pages/man2/setresgid.2.html
https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://www.kernel.org/doc/man-pages/online/pages/man2/execve.2.html
https://docs.kernel.org/userspace-api/no_new_privs.html
```

Retained contract, implementation decision, applied review, and final build evidence:

```text
../terminal-profile-v1.md
../decisions/0064-seal-local-terminal-profiles-behind-fork-safe-pty-adapter.md
linux-pty-profile-process-boundary-rev0017.md
cloudtainer-build-report-rev0017.md
```

Applied boundary: the multithreaded daemon does not run general C++ application logic after `fork`;
`posix_spawn` enters one hidden reviewed IoTox child role with fixed descriptors. UNIX peer
credentials, descriptor type checks, a verified parent-death contract, canonical bounded policy,
already-open target/cwd descriptors, reset signal state, verified no-new-privileges, exact identity
verification, resource limits, and readiness-plus-EOF form a local process-hygiene boundary. Native
tests kill the verified parent without running cleanup and use a pidfd when available to prove that a
target ignoring terminal hangup still dies. These mechanisms are not a general sandbox, an
LSM/cgroup/namespace claim, or a network terminal feature. Upstream specifications define platform
semantics; they do not audit or approve IoTox.

## rev0016 guarded authority-ledger v2 sources

Primary references rechecked 2026-08-16 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://www.rfc-editor.org/rfc/rfc6709.html
https://www.rfc-editor.org/rfc/rfc9170.html
https://www.rfc-editor.org/rfc/rfc8032.html
https://www.rfc-editor.org/rfc/rfc9591.html
```

Retained review, implementation decision, protocol, and final build evidence:

```text
authority-v2-terminal-capability-migration-rev0016.md
../decisions/0063-explicit-signed-authority-ledger-v2-migration.md
../protocol-authority-v2.md
cloudtainer-build-report-rev0016.md
```

Applied boundary: terminal authority is a major protocol/security extension, so v1 meaning is frozen
and v2 is explicit, versioned, domain-separated, negotiated, and testable. Exact canonical signing
bytes are compared with requested semantics before RecallRoot signs. A separate committed/pending
head guard detects rollback, deletion, or fork of the ledger alone and recovers the two exact
interrupted replace states; it is not an external monotonic witness and does not detect coordinated
rollback of both local files. The references are design inputs, not protocol dependencies or
third-party approval.

## rev0015 Ratox R1 fail-closed state sources

Primary references rechecked 2026-08-16 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore
```

Retained review, implementation decision, and protocol:

```text
c-toxcore-0.2.23-ratox-r1-fail-closed-state-review-rev0015.md
../decisions/0062-complete-ratox-r1-with-a-fail-closed-pure-session-engine.md
../protocol-ratox-v1.md
```

Applied boundary: the upstream release records a critical manually audited bug plus bounds,
allocation-failure, lifetime, and test improvements; the repository documents sanitizer, static
analysis, and continuous fuzzing practice. IoTox applies that assurance lesson to its own pure
session state through pre-effect replay reservations, terminal-session execution fencing,
failure-atomic attachment/quota transitions, deterministic boundary tests, and ASan/UBSan state
fuzzing. This is design evidence, not a claim that upstream tested or approved IoTox.

## rev0015 interactive carrier and reconnect planning sources

Primary references rechecked 2026-08-15 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/net_crypto.h
https://mosh.org/mosh-paper.pdf
```

Retained evidence, plan, and decision:

```text
c-toxcore-0.2.23-ratox-latency-lab-rev0015.md
../ratox-interactive-plan.md
../decisions/0059-prioritize-interactive-work-and-qualify-custom-carriers.md
```

Applied boundary: c-toxcore 0.2.23 defines lossless custom application IDs 160..191, lossy
application IDs 200..254, a 1,373-byte maximum custom packet, and explicit duplicate/reorder/loss
semantics for the lossy API. IoTox consumes only public `tox.h` functions. The pinned source range
declaration explains why diagnostic lossy ID `0xC8` is used instead of the ToxAV-reserved
`0xC0..0xC7`. The Mosh paper is design precedent for explicit application state synchronization;
IoTox does not claim Mosh compatibility or copy its protocol/security properties.

## rev0015 ordinary outgoing-request ingress sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.1
https://raw.githubusercontent.com/pranomostro/ratox/master/README
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/fpathconf.html
```

Retained contract, evidence, and decision:

```text
c-toxcore-0.2.23-ratox-outgoing-request-ingress-rev0015.md
cloudtainer-build-report-rev0015.md
../ratox-friend-lifecycle-v1.md
../decisions/0049-root-request-fifo-is-an-exact-complete-address-adapter.md
```

Applied boundary: an outgoing request requires the complete 38-byte Tox address and a nonempty
1..921-byte message. IoTox preserves ratox's ordinary global request write but replaces first-
whitespace/default-message parsing with one exact `<76 hex><TAB><message><LF>` record. The root FIFO
is private, atomically bounded against its actual `PIPE_BUF`, inode-checked, and only an adapter to
one typed Agent operation. Kernel admission, parser acceptance, local `tox_friend_add`, remote
acceptance, and IoTox authority remain separate evidence states.

## rev0014 friendship lifecycle sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://toktok.ltd/spec.html
https://github.com/pranomostro/ratox
https://raw.githubusercontent.com/pranomostro/ratox/master/README
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
```

Retained contracts, evidence, and decision:

```text
c-toxcore-0.2.23-ratox-friend-lifecycle-rev0014.md
cloudtainer-build-report-rev0014.md
../ratox-friend-lifecycle-v1.md
../decisions/0048-friendship-mutations-are-public-key-bound-exact-token-decisions.md
```

Applied boundary: outgoing requests use a complete Tox address and nonempty bounded message;
incoming requests are callbacks rather than provider queue objects; acceptance adds by public key;
rejection is client-side ignore; deletion is local and silent; and numeric friend handles may be
reused. IoTox therefore projects public-key directories, exact word FIFOs, a bounded local evidence
journal, and one owner-thread public-key lookup-plus-delete operation while leaving the independent
signed authorization ledger unchanged. Ratox supplies the ordinary filesystem precedent; its
process-local numeric deletion and add-then-delete rejection are not copied.

## rev0013 finite-file and control sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.c
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/Messenger.c
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/Messenger.h
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://github.com/pranomostro/ratox
https://raw.githubusercontent.com/JFreegman/toxic/v0.16.3/src/file_transfers.c
```

Retained contracts and decisions:

```text
c-toxcore-0.2.23-ratox-finite-file-control-rev0013.md
cloudtainer-build-report-rev0013.md
../ratox-file-fifo-v1.md
../decisions/0046-ratox-file-fifos-name-finite-local-files.md
../decisions/0047-file-control-tracks-two-sided-pause.md
```

Applied boundary: ratox proves that one ordinary per-peer filesystem surface can make Tox useful.
IoTox preserves that operation but lets each FIFO record name one finite local source, destination,
or control instead of treating FIFO bytes as the bulk stream. The pinned c-toxcore contract requires
incoming resource acquisition before RESUME, exact/repeatable chunk service, independent pause
ownership, terminal zero-length callbacks, and transfer cleanup at disconnect. The complete
friend-specific file number is preserved as an opaque provider handle even though the pinned
implementation currently encodes incoming direction at values of at least 65536.

## rev0012 live-text and receipt-boundary sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://git.2f30.org/ratox/file/README.html
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://man7.org/linux/man-pages/man3/write.3p.html
https://man7.org/linux/man-pages/man3/fpathconf.3p.html
```

Retained contracts and decisions:

```text
c-toxcore-0.2.23-ratox-text-receipt-boundary-rev0012.md
c-toxcore-0.2.23-file-admission-completion-boundary-rev0012.md
cloudtainer-build-report-rev0012.md
../ratox-message-fifo-v1.md
../decisions/0043-ratox-message-and-action-fifos-are-live-transport-lanes.md
../decisions/0044-connection-callbacks-own-online-epochs.md
../decisions/0045-file-receive-acknowledges-admission-not-live-residency.md
```

Applied boundary: c-toxcore v0.2.23 permits 1..1372-byte normal/action messages, returns a
per-friend message id whose first valid value is zero after local queue acceptance, and reports a
later friend read receipt separately. Ratox proves the value of an ordinary FIFO write but appends
local feedback before any remote receipt. rev0012 preserves that ease while separating local FIFO
ingress, toxcore send acceptance, incoming text, and remote read receipt. It queries each FIFO's
actual `_PC_PIPE_BUF`, preserves every non-LF body byte, performs no hidden offline retry, and keeps
human text outside durable command authority.

The same source review distinguishes level-triggered friend inventory from ordered
friend-connection callbacks. rev0012 makes the required callback the sole online-epoch authority;
an older copied list may update presentation but cannot open, close, or replace the canonical
session transcript.

The same pinned header defines incoming file RESUME as acceptance and zero-length
`file_recv_chunk` as terminal completion, without promising a minimum delay between those events.
rev0012 therefore returns a frozen admitted receive record after successful RESUME instead of
requiring the transfer to remain in the live map; safe publication is separate asynchronous truth.

## rev0011 ordinary-write and FIFO-boundary sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://github.com/pranomostro/ratox
https://git.2f30.org/ratox/commit/99b652c0c07c6acf81b6a8cf36a107be76fbe98d.html
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
```

Retained contracts and decisions:

```text
ratox-fifo-and-toxcore-boundary-rev0011.md
cloudtainer-build-report-rev0011.md
../ratox-command-fifo-v1.md
../decisions/0040-fifo-adapter-is-not-a-queue.md
../decisions/0041-operation-executor-is-transport-and-storage-blind.md
../decisions/0042-runtime-projections-are-atomic-not-durable.md
```

Applied boundary: ratox's FIFO-first interface is preserved as an ordinary private Unix adapter, not copied as a persistence or authorization model. FIFO bytes live in a kernel byte stream, write boundaries are not records, and portable atomicity requires one write no larger than `PIPE_BUF`. IoTox fixes its v1 record at no more than 256 printable bytes plus LF, commits the exact signed durable command before toxcore delivery, and keeps all toxcore calls on one owner thread.

## rev0010 durable-command and ratox-successor sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/security/advisories/GHSA-42vg-9mg3-399f
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://toktok.ltd/spec.html
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
```

Retained notes and contracts:

```text
c-toxcore-0.2.23-durable-command-carrier-rev0010.md
c-toxcore-0.2.23-durable-command-boundary-rev0010.md
durable-command-semantics-rev0010.md
cloudtainer-build-report-rev0010.md
../command-store-v2.md
../command-store-v3.md
../protocol-command-v1.md
../decisions/0036-commit-command-before-transport-or-effect.md
../decisions/0037-directional-local-command-lanes.md
../decisions/0038-command-operation-registry-and-restart-policy.md
../decisions/0039-generic-one-binary-command-entrance.md
../decisions/0055-durable-offline-outbox-lifecycle.md
```

Applied boundary: c-toxcore lossless custom packets provide reliable ordered packet framing after
local queue acceptance. `SENDQ` is a local full-queue error. IoTox owns persistent command
identity, commit order, application receipts, authority admission, execution state, exact replay,
and restart recovery. Ratox remains the interface inspiration: ordinary Unix files and FIFOs are
valuable projections, but they are not themselves durable queues or authorization ledgers.

## rev0009 authority and first-operation sources

Primary references rechecked 2026-08-14 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://github.com/jedisct1/libsodium/releases/tag/1.0.22-RELEASE
https://doc.libsodium.org/public-key_cryptography/public-key_signatures
https://git.2f30.org/ratox/file/ratox.c.html
```

Retained notes and contracts:

```text
c-toxcore-0.2.23-authority-command-route-contract-rev0009.md
libsodium-ed25519-authority-ledger-rev0009.md
../protocol-authority-v1.md
../protocol-command-v1.md
../decisions/0034-transcript-bound-directional-stable-principal-proof.md
../decisions/0035-capability-gated-device-describe.md
```

Applied boundary: c-toxcore supplies reliable ordered lossless custom packets only after local
queue acceptance; `SENDQ` is a local full-queue error and not a remote receipt. IoTox owns exact
retry, transcript binding, signed principal proof, capability decisions, command correlation,
and durable execution semantics. v0.2.23 options expose proxy/UDP/discovery/DHT/DNS controls
useful for future route experiments, but those switches alone do not prove Tox/Tor or Tox/I2P.

## rev0008 transcript-confirmation sources

Primary references reviewed 2026-08-13 America/New_York:

```text
https://github.com/TokTok/c-toxcore/releases
https://github.com/TokTok/c-toxcore
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://github.com/toxext/toxext
https://raw.githubusercontent.com/toxext/toxext/master/DESIGN.md
https://www.rfc-editor.org/rfc/rfc8446.html
https://www.rfc-editor.org/rfc/rfc9147.html
https://noiseprotocol.org/noise.html
```

Current notes:

```text
tox-session-confirmation-rev0008.md
c-toxcore-0.2.23-custom-packet-send-contract-rev0008.md
```

The design inference is deliberately limited: mature protocols use an explicit transcript
commit/barrier before ordinary application traffic and freeze logical handshake retransmits.
IoTox borrows that state-machine discipline; it does not claim TLS/Noise cryptographic
properties for its unsigned CAPABILITIES record.

## rev0007 capability-session and friend-request sources

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/CMakeLists.txt
https://git.2f30.org/ratox/file/ratox.c.html
```

Retained notes:

```text
tox-capability-session-rev0007.md
c-toxcore-0.2.23-session-and-friend-request-contract-rev0007.md
```

## c-toxcore and standalone build readings

```text
c-toxcore 0.2.23 release and official public headers
c-toxcore CMake target/option declarations
libsodium 1.0.22 release archive and build contract
```

Retained notes:

```text
c-toxcore-0.2.23-client-file-and-build-contract-rev0005.md
c-toxcore-0.2.23-profile-text-and-packets-rev0006.md
toxcore-bootstrap-api-v0.2.23.md
```

Dependency URLs and SHA-256 values are frozen in `../../dependencies.lock`.

## ratox readings

The preserved assessment and source reading cover:

```text
filesystem/FIFO control surface
explicit incoming request decision
profile and peer projection
message and file behavior
single-event-loop implementation tradeoffs
```

Retained notes:

```text
ratox-surface-contract.md
ratox-human-interface-rev0006.md
ratox-agent-dispatch-rev0018.md
../ratox-successor-assessment.md
```

## RecallRoot and ownership readings

Retained notes:

```text
argon2id-contract.md
offline-guessing-model.md
../recovery-and-ownership.md
```

The EFF large word list and attribution are retained under `../../third_party/`.

## Mutorr/Milehigh readings

Retained notes and source:

```text
milehigh-small-circles-review.md
performance-rev0003.md
../../incubator/mutorr/
../history/milehigh-small-circles-rev0002/
```

Mutorr is historical/incubator research, not the current product northstar.

## Rescue-shell and toolbox readings

ADR 0287 and `../ratox-rescue-toolbox.md` are grounded in the current upstream surfaces:

```text
Toybox overview, status matrix, and 0BSD license: https://landley.net/toybox/
Toybox 0.8.14 source tag: https://github.com/landley/toybox/releases/tag/0.8.14
oksh portable OpenBSD-ksh source and 7.9 tag: https://github.com/ibara/oksh/tree/oksh-7.9
```

Toybox is selected for the multicall utilities, not for `sh`/`toysh`; upstream still classifies that
shell as partially implemented. The exact source-archive hashes are frozen in
`../../dependencies.lock`, and the separate Nix output carries the upstream notices.

## Build and execution evidence

The current report is `cloudtainer-build-report.md`. Revision-specific reports are retained as:

```text
cloudtainer-build-report-rev0001.md
cloudtainer-build-report-rev0003.md
cloudtainer-build-report-rev0004.md
cloudtainer-build-report-rev0005.md
cloudtainer-build-report-rev0006.md
cloudtainer-build-report-rev0007.md
cloudtainer-build-report-rev0008.md
cloudtainer-build-report-rev0009.md
cloudtainer-build-report-rev0010.md
cloudtainer-build-report-rev0011.md
cloudtainer-build-report-rev0012.md
cloudtainer-build-report-rev0013.md
cloudtainer-build-report-rev0014.md
cloudtainer-build-report-rev0015.md
cloudtainer-build-report-rev0016.md
cloudtainer-build-report-rev0017.md
cloudtainer-build-report-rev0018.md
cloudtainer-build-report-rev0019.md
cloudtainer-build-report-rev0020.md
cloudtainer-build-report-rev0021.md
cloudtainer-build-report-rev0022.md
cloudtainer-build-report-rev0023.md
cloudtainer-build-report-rev0024.md
cloudtainer-build-report-rev0025.md
cloudtainer-build-report-rev0026.md
```

A report must say which compilers, sanitizers, fuzz budgets, binaries, providers, and network
paths actually ran. A failed dependency fetch remains useful evidence but cannot be promoted to
a source-linked build.
