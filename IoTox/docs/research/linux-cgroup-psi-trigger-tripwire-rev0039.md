# Linux cgroup PSI trigger tripwire — applied review for rev0039

## Question

How can IoTox close its existing host-local Ratox PTY pressure-admission latch when a delegated cgroup
crosses a cumulative PSI threshold between synchronous requests, while preserving exact kernel
identity, bounded lifecycle, fail-closed behavior, and honest observability?

## Primary sources rechecked

Retrieved and rechecked online on 2026-08-19:

- Linux kernel PSI documentation:
  `https://docs.kernel.org/accounting/psi.html`
- Current upstream Linux PSI implementation:
  `https://raw.githubusercontent.com/torvalds/linux/master/kernel/sched/psi.c`
- Linux cgroup v2 administration guide:
  `https://docs.kernel.org/admin-guide/cgroup-v2.html`
- `poll(2)` interface reference:
  `https://man7.org/linux/man-pages/man2/poll.2.html`
- `eventfd(2)` interface reference:
  `https://man7.org/linux/man-pages/man2/eventfd.2.html`

The applied decision is ADR 0090. ADR 0089 remains the synchronous average/hysteresis foundation.

## Kernel ABI findings

### Registration and lifetime

A PSI trigger is written as:

```text
<some|full> <stall amount in microseconds> <tracking window in microseconds>
```

The interface file must be opened `O_RDWR`; the same descriptor is then polled for `POLLPRI`. The
kernel documentation's userspace example writes `strlen(trigger) + 1`, including the terminating NUL.
Each trigger needs a separate open descriptor, including multiple triggers on one pressure resource.
A second registration on the same descriptor fails with `EBUSY`. Closing the descriptor deregisters
the trigger.

rev0039 therefore does not write through the read-only descriptors used for synchronous PSI samples.
It opens one additional descriptor per configured CPU `some`, memory `full`, or I/O `full` trigger and
keeps those descriptors alive until the monitor thread has been stopped and joined. A typed bounded
encoder freezes the exact `some|full`, decimal-space, terminating-NUL, no-newline record before writing.

### Bounds and privilege

The documentation describes accepted tracking windows from 500 ms through 10 s. Current upstream
source enforces a nonzero window no greater than 10,000,000 microseconds and a nonzero threshold no
greater than the window.

Current source checks `CAP_SYS_RESOURCE` from the credentials captured when the pressure file was
opened. Without that effective capability, a window must be a multiple of 2,000,000 microseconds so
the lower-frequency averages worker can be used instead of a real-time polling worker. IoTox therefore
accepts only the portable subset: exact 2,000,000-microsecond multiples from 2,000,000 through
10,000,000. This makes policy validity independent of ambient capability state, prevents a deployment
from passing only while unexpectedly privileged, and avoids requesting a kernel realtime PSI worker.
IoTox never rounds a configured value.

### Event semantics

A trigger represents cumulative stall growth over an approximated sliding tracking window. PSI
monitors are sampled up to ten times per window while the relevant stall state is active. Userspace
notification is rate-limited to one event per tracking window. In the current implementation,
`psi_trigger_poll()` clears the pending event with an atomic compare/exchange when it reports
`EPOLLPRI`. Destruction or loss of the source can wake pollers with error state.

These details rule out interpreting one notification as one unique stall episode or treating it as an
instantaneous utilization sample. They also motivate keeping one userspace quiet hold for at least the
whole configured window and treating polling-source failure as permanent fail-closed state.

## Applied construction

### Policy contract

`CgroupPressureAdmissionLimits` now contains:

```text
trigger_window_microseconds
cpu_some_trigger_stall_microseconds
memory_full_trigger_stall_microseconds
io_full_trigger_stall_microseconds
```

The common window and at least one trigger must appear together. It must be an exact
2,000,000-microsecond quantum from 2 through 10 seconds, and every trigger requires its matching `avg10`
maximum. This preserves one recovery rule: after an event hold expires, a complete later sample must
satisfy ADR 0089's `maximum-hysteresis` boundaries before the latch can reopen.

The trigger record is produced by a typed encoder rather than free-form class text. It accepts only
`some` or `full`, verifies the portable window quantum and stall bound, uses locale-independent bounded
integer formatting, and returns the exact NUL-terminated record with no newline. Registration writes
that complete record and rejects a short write.

### Descriptor pinning

Controller activation first performs the existing normalized absolute path, cgroup-v2 filesystem,
daemon-ownership, `cgroup.pressure=1`, protected control-file, canonical parser, and complete sample
preflight. Before the first kernel registration it reserves storage for the exact configured trigger
count, so memory exhaustion cannot split an otherwise valid registration sequence. It then opens each
trigger source relative to the already pinned delegated-root descriptor using `O_RDWR | O_NONBLOCK`,
repeats the protected-control check, writes the canonical NUL-terminated record, and retains the
descriptor. A local capacity guard and exception translation keep the Result-returning registration
boundary fail closed even if later maintenance changes the descriptor type or call ordering.

No pathname lookup occurs after activation. Sample descriptors and trigger descriptors are separate so
one kernel trigger registration cannot alter the synchronous read contract.

### Monitor and shutdown

One monitor thread builds a bounded `pollfd` vector containing:

```text
one nonblocking CLOEXEC eventfd shutdown descriptor
one POLLPRI descriptor per configured trigger
```

The thread waits indefinitely. Destruction first sets an atomic stop flag and writes the eventfd, then
joins the monitor, then lets RAII close the PSI descriptors. `EAGAIN` on the shutdown write means the
event counter already contains a wakeup. This ordering prevents descriptor closure from racing a live
userspace poll and gives the monitor an explicit bounded wake path.

Thread creation, eventfd creation, PSI registration, and descriptor verification are activation
requirements. They do not degrade to synchronous-only admission.

### Event handoff and latch ordering

The monitor increments one saturation-safe atomic pending counter for the trigger resource immediately
after `poll()` reports `POLLPRI`, before acquiring the admission mutex. Under that mutex the controller:

1. drains all pending resource counters;
2. adds them to exact total/per-resource event counters;
3. extends `trigger_hold_until` to at least `now + configured window`;
4. closes an open gate and records the ordinary plus trigger-specific transition exactly once.

Admission drains pending publication before the PSI sample, after the complete sample, and again after
its first policy evaluation. The last drain is followed by a fresh evaluation. An event already
published by the monitor cannot pass that final boundary.

There remains a scheduler interval between the kernel returning a poll event and the monitor executing
its first userspace instruction. No userspace design can truthfully label that interval as an already
published IoTox latch transition. rev0039 therefore claims bounded asynchronous handoff, not strict
linearization at the kernel threshold-crossing instant.

### Hold and recovery

A hold is active while monotonic time is before `trigger_hold_until`. Each later event conservatively
extends the deadline from its userspace drain time. During the hold, every PTY request is rejected as
`resource_exhausted`. Expiration does not open the gate. The same complete descriptor-pinned
`cgroup.pressure` and CPU/memory/I/O sample must be valid, and every configured average must be at or
below `maximum-hysteresis`.

Sampling or evaluation failure continues to reject as local `unavailable`, retain the typed local
cause, and latch closed. Trigger-monitor failure has its own typed status and never restarts in place.

### Monitor failure

The following conditions publish one permanent monitor failure and close the gate:

```text
fatal poll(2) error
POLLERR, POLLHUP, or POLLNVAL on a trigger source
POLLERR, POLLHUP, or POLLNVAL on the shutdown descriptor
allocation or unexpected exception inside the monitor
```

Before interpreting an event, the monitor verifies that the `poll()` return count exactly matches the
number of descriptors carrying nonzero `revents`. An indefinite wait returning zero, an unexpected bit on
the shutdown descriptor, an unexpected bit on a trigger descriptor, or an internal poll-set cardinality
mismatch is a typed `protocol_error`. This prevents an unrecognized persistent readiness bit from turning
into a hot loop or being silently ignored.

The first published typed error is retained. The monitor exits. Later admissions remain unavailable.
This avoids an invisible conversion from continuous tripwire policy to synchronous-only policy.

## Owner-private observability

The runtime tree adds content-free fields for:

```text
which trigger dimensions are configured
common window and each configured stall threshold
monitor health and typed monitor error
active hold and remaining hold microseconds
total and CPU/memory/I/O trigger events
monitor failures
trigger-caused close transitions
admissions rejected while a trigger hold is active
```

Existing checks, admissions, rejections, sampling failures, ordinary close/reopen transitions,
last-sample validity, and last valid average observations remain. No field carries a session, profile,
principal, command, payload, process, peer, path, device, error string, or terminal byte.

## Validation constructed

The owned registry covers:

- common-window/trigger coupling;
- exact 2,000,000 and 10,000,000 microsecond window bounds plus rejection of non-2-second quanta;
- nonzero threshold and threshold-at-window bounds;
- exact typed `some`/`full`, spacing, decimal, trailing-NUL, and no-newline record encoding;
- matching-average requirements;
- malformed CLI values, detached dimensions, oversized windows/stalls, and missing delegated root;
- pure trigger-hold close, repeated hold, post-hold hysteresis retention, and exact reopen equality;
- Agent policy projection and owner-private runtime rendering.

The dedicated cgroup process oracle now attempts a quiet real per-cgroup memory-full trigger with a
2,000,000 microsecond window and equal threshold. On a capable host it proves registration, healthy
monitor state, one accepted low-pressure sample, zero fabricated events, and bounded monitor teardown.
It then runs the existing accounting-disable, fail-closed latch, exact reopen, concurrent sampling, and
startup-preflight branches with the non-triggered controller.

The current construction host does not expose per-cgroup `cgroup.pressure`, so the process route records
its explicit capability skip. The warnings-as-errors build and deterministic registry pass; no
positive live kernel trigger event is claimed on this host.

## Retained nonclaims and next qualification

rev0039 does not:

- choose workload-safe trigger windows, thresholds, or hysteresis;
- guarantee notification latency or one notification per stall episode;
- produce an atomic CPU/memory/I/O pressure snapshot;
- preempt, kill, resize, migrate, or reprioritize an existing session;
- attribute a root pressure event to a session, process, command, or peer;
- adapt policy from retained outcomes or historical pressure;
- persist latch state or counters across restart;
- establish support on a named kernel/service-manager/delegation fleet;
- provide positive event-generation evidence on this construction host;
- constrain root or another sufficiently privileged cgroup co-writer.

The next genuine qualification should run on a named host with writable delegated cgroup v2 and
per-cgroup PSI. It should register every configured class, induce controlled CPU, memory, and I/O stall
without crossing unrelated safety boundaries, capture event and hold timing on one monotonic clock,
exercise source removal/failure, and retain kernel version, configuration, capabilities, delegation,
commands, raw output, and independent review.
