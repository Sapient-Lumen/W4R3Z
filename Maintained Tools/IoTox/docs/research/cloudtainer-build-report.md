# IoTox cloudtainer build report — rev0039

- **Version:** 0.39.0
- **Revision:** rev0039
- **Codename:** PSI Trigger Tripwire Load Shedding Citadel
- **Outer linked revision:** rev0026
- **Implementation commit:** `8c13939967ac9afdde454cecd2a966a886dea3c5`
- **Implementation tree:** `6bfd326b9e6240c591d95a7ecee88e2d5dba2c4f`
- **Construction date:** 2026-08-19 America/New_York

## Construction result

rev0039 substantially extends rev0038's descriptor-pinned, synchronous cgroup-v2 PSI admission gate.
The prior gate could observe CPU `some avg10`, memory `full avg10`, and I/O `full avg10` only while a
new Ratox PTY request was being admitted. rev0039 adds optional continuous kernel PSI triggers so a
threshold crossing can proactively latch the gate between admission requests.

Each configured trigger is registered on its own `O_RDWR | O_NONBLOCK` descriptor beneath the exact
already-pinned delegated root. The trigger record is canonical and NUL-terminated. One controller-owned
monitor polls all trigger descriptors for `POLLPRI` together with one nonblocking close-on-exec
`eventfd` shutdown descriptor. Trigger events are published through saturation-safe resource-specific
atomics before mutex transfer. Under the admission mutex, the controller records exact total and
per-resource counts, closes the gate at most once per open-to-closed transition, and extends a monotonic
hold deadline by at least one complete configured tracking window.

The monitor's entire `pollfd` set is allocated synchronously before thread creation. A successful
controller construction therefore cannot silently lose continuous monitoring because the worker's
first allocation failed. Eventfd creation, trigger registration, poll-set construction, and monitor
thread creation are all activation requirements. Fatal poll errors, invalidated or hung-up sources,
shutdown-descriptor errors, and unexpected monitor exceptions publish one typed failure and leave the
controller permanently fail closed.

Hold expiry never opens the gate by itself. A later complete descriptor-pinned PSI sample must still
satisfy rev0038's exact integer `maximum-hysteresis` boundary for every configured metric. Sampling,
parsing, or `cgroup.pressure` accounting failure remains local `unavailable` and latched closed. The
pressure check still occurs before aggregate reservation, session-cgroup creation, PTY allocation,
helper creation, or payload mutation, so a rejected request consumes no reservation and creates no
session leaf or child.

## Primary-source research

The construction rechecked these primary interfaces online on 2026-08-19:

- Linux PSI documentation: `https://docs.kernel.org/accounting/psi.html`
- current upstream PSI implementation: `https://raw.githubusercontent.com/torvalds/linux/master/kernel/sched/psi.c`
- Linux cgroup v2 administration guide: `https://docs.kernel.org/admin-guide/cgroup-v2.html`
- `poll(2)`: `https://man7.org/linux/man-pages/man2/poll.2.html`
- `eventfd(2)`: `https://man7.org/linux/man-pages/man2/eventfd.2.html`

The source review supports the following construction choices: trigger files are opened read/write;
one trigger is registered per descriptor; the record carries class, cumulative stall threshold, and
tracking window; notification is polled as priority data; closing the descriptor removes the trigger;
the documented userspace example includes the terminating NUL; accepted windows are bounded; current
upstream source restricts unprivileged monitoring to a lower-frequency window shape; and notifications
are rate-limited rather than being one exact event per unique stall episode.

The full applied analysis is retained in
`docs/research/linux-cgroup-psi-trigger-tripwire-rev0039.md`. ADR 0090 freezes the trigger, lifecycle,
ordering, recovery, observability, and nonclaim boundaries. ADR 0089 remains the synchronous sample and
hysteresis foundation.

## Policy and public configuration

`CgroupPressureAdmissionLimits` now carries:

```text
trigger_window_microseconds
cpu_some_trigger_stall_microseconds
memory_full_trigger_stall_microseconds
io_full_trigger_stall_microseconds
```

The common window exists if and only if at least one trigger exists. IoTox accepts exact
2,000,000-microsecond window quanta from 2,000,000 through 10,000,000 microseconds and a positive
stall threshold no greater than that window. This portable subset does not depend on effective
`CAP_SYS_RESOURCE` and avoids the kernel realtime PSI poll worker. Every trigger requires its matching
avg10 maximum so the controller always has a deterministic lower hysteresis rule for recovery.

The `iotox run` surface adds:

```text
--ratox-cgroup-admission-trigger-window-us
--ratox-cgroup-admission-cpu-some-trigger-stall-us
--ratox-cgroup-admission-memory-full-trigger-stall-us
--ratox-cgroup-admission-io-full-trigger-stall-us
```

Malformed, detached, incomplete, out-of-range, and metric-mismatched combinations fail before service
activation. The feature remains default off and host local. The terminal profile record and Ratox wire
protocol are unchanged.

## Owner-private runtime truth

The runtime tree adds content-free projection for:

```text
configured trigger dimensions
common tracking window and resource stall thresholds
monitor health and typed monitor error
active hold and remaining hold microseconds
total and CPU/memory/I/O trigger events
monitor failures
trigger-caused close transitions
hold-specific admission rejections
```

The projection contains no peer, principal, session, profile, command, process, path, device, payload,
terminal byte, or error string. Existing checks, admissions, rejections, sampling failures, ordinary
close/reopen transitions, last-sample validity, typed last sampling failure, observation-presence flags,
and last valid configured values remain.

## Deterministic coverage added

The owned registry now contains 359 fixture-aware checks. New coverage freezes:

- common-window and trigger coupling;
- exact 2,000,000 and 10,000,000 microsecond window boundaries plus non-quantized rejection;
- exact typed NUL-terminated trigger-record encoding without a newline;
- positive stall thresholds and exact threshold-at-window equality;
- matching avg10 requirements for CPU `some`, memory `full`, and I/O `full`;
- malformed, missing, detached, undersized, oversized, zero, and metric-mismatched CLI values;
- pure trigger-held close, repeated hold, low-sample rejection during hold, post-hold hysteresis
  retention, and exact lower-boundary reopening;
- Agent policy projection before network activation;
- owner-private runtime configuration, health, hold, typed error, event, failure, and transition fields;
- quiet real trigger registration and bounded monitor destruction when a private cgroup namespace
  exposes the required per-cgroup PSI interface.

The live process route deliberately does not fabricate a positive threshold event. On a capable host it
registers a quiet memory `full` trigger with a 2,000,000 microsecond window and equal threshold, proves
healthy monitor startup and zero invented events, then continues the existing accounting-disable,
fail-closed latch, exact reopen, and concurrent admission checks. Capability absence returns CTest skip
code 77 with a named reason.

## Qualification executed on the implementation commit

Construction host:

```text
Linux 6.18.35 x86_64 GNU/Linux
GCC 14.2.0
Clang 17.0.0
CMake 3.31.6
Ninja 1.12.1
```

Results retained under `artifacts/rev0039/`:

```text
git diff --check                                  PASS
tracked shell syntax                              PASS
Python compileall                                 PASS
GCC Debug warnings-as-errors build                PASS
GCC Debug default CTest                           19/19 complete
  ordinary passes                                 15
  named host-capability skips                     4
  failures                                        0
GCC Release warnings-as-errors build              PASS
GCC Release default CTest                         19/19 complete
  ordinary passes                                 15
  named host-capability skips                     4
  failures                                        0
Clang Debug warnings-as-errors build              PASS
Clang Debug default CTest                         19/19 complete
  ordinary passes                                 15
  named host-capability skips                     4
  failures                                        0
Clang ASan+UBSan warnings-as-errors build         PASS
Clang ASan+UBSan sharded CTest                    34/34 complete
  ordinary passes                                 30
  named host-capability skips                     4
  failures                                        0
  sanitizer diagnostics                           0
GCC ThreadSanitizer warnings-as-errors build      PASS
GCC ThreadSanitizer sharded CTest                 34/34 complete
  ordinary passes                                 30
  named host-capability skips                     4
  failures                                        0
  race diagnostics                                0
Clang libFuzzer smoke                             11 targets x 5,000 runs
  completed target runs                           55,000
  failures                                        0
host-linked Argon2 build and CTest                19/19 complete
  ordinary passes                                 15
  named host-capability skips                     4
  failures                                        0
Mutorr preservation build and CTest              21/21 complete
  ordinary passes                                 17
  named host-capability skips                     4
  failures                                        0
exclusive Agent/session stress                    100/100 passed, shard=1/359
direct owned registry                             359/359, failures=0
product identity                                  IoTox 0.39.0 rev0039
```

The complete matrix ended with exactly one `final-source-matrix=pass` marker. Every configured compiler,
sanitizer, fuzzer, system-Argon2, and preservation lane ran against the implementation commit identified
above. The 100-run Agent stress tool first discovered the exact linked registry and target shard, then
required the same Agent/session proof and canonical summary on every repetition. Retained-artifact
refresh additionally rejects a transcript unless its shard denominator equals the current 359-check
source registry.

The four skipped routes require private delegated cgroup capabilities not exposed by this container:
preactivated memory, CPU, or I/O controllers, and per-cgroup `cgroup.pressure`. The dedicated trigger
route reports:

```text
SKIP cgroup PSI pressure-admission oracle:
required per-cgroup PSI interface 'cgroup.pressure' is unavailable
```

The host also exposes no `/proc/pressure`. No synthetic pseudo-file substitutes for the missing kernel
interface, and no positive trigger-registration, notification, hold-timing, or event-delivery result is
claimed on this host.

## Qualification limits retained honestly

The complete local build matrix and repeated Agent stress are green, but they do not replace a live
per-cgroup PSI trigger-delivery qualification. No standalone source-linked c-toxcore/libsodium/Argon2
provider build, public Tox peer, named service-manager delegation, physical-host R7 exercise, or coverage
report is newly claimed for rev0039. The required focused Clang lane is retained separately with zero
diagnostics. Historical evidence for
earlier commits remains historical and is not silently reused as proof of this implementation commit.

## Security and concurrency review notes

The monitor owns no session content and performs no PTY operation. It only publishes typed counters and
closes a host-wide admission latch. Trigger descriptors and the eventfd outlive the monitor because the
state destructor sets a stop flag, signals the eventfd, joins the thread, and only then permits RAII
descriptor closure. Trigger policy and descriptor vectors are immutable after startup. Mutable gate,
last-sample, transition, hold, and exported-counter state remains behind one mutex. The monitor publishes
pending events before attempting that mutex, allowing an admission already inside the critical section
to observe events at its final drain boundary.

This is not strict linearization at the kernel's internal threshold-crossing instant. There is an
unavoidable scheduler interval before userspace receives and publishes a poll result. An event whose
atomic publication completes after an admission's final drain may affect the next admission. The
construction claims bounded asynchronous handoff and fail-closed recovery, not a hard real-time or
zero-race threshold guarantee.

## Retained nonclaims

rev0039 does not:

- choose generally safe pressure thresholds, windows, or hysteresis;
- guarantee notification latency or one event per stall episode;
- atomically sample CPU, memory, and I/O pressure files;
- predict capacity, latency, throughput, fairness, or deadline success;
- preempt, kill, resize, reprioritize, or migrate an already admitted session;
- attribute a root pressure event to a peer, profile, session, command, process, or device;
- persist latch state, event counts, or hold deadlines across daemon restart;
- adapt policy from pressure history or retained session outcomes;
- defend against root or another sufficiently privileged delegated-root co-writer;
- qualify a named kernel, service-manager, delegation, or hardware fleet;
- establish production readiness, independent audit, or public-network Ratox qualification.

## Next qualification

The next useful gate is a named writable cgroup-v2 delegation with per-cgroup PSI enabled. It should
register each supported trigger class, induce controlled CPU, memory, and I/O stall without crossing
unrelated safety limits, capture kernel notification, userspace publication, gate close, hold expiry,
and hysteretic reopen on one monotonic clock, exercise source invalidation and bounded teardown, and
retain kernel configuration, capabilities, service-manager delegation, commands, raw output, and
independent review. Focused static-analysis and coverage evidence would further strengthen the local
review, but the primary missing proof is live kernel trigger delivery through a named delegation.
