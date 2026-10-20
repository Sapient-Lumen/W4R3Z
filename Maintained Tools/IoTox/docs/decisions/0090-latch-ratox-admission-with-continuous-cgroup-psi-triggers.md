# ADR 0090: latch Ratox admission with continuous cgroup PSI triggers

- Status: accepted and implemented in rev0039
- Date: 2026-08-19
- Scope: host-local Ratox PTY load shedding between synchronous admission checks
- Extends: ADR 0089

## Context

ADR 0089 added a descriptor-pinned, fail-closed admission gate over delegated-root CPU `some avg10`,
memory `full avg10`, and I/O `full avg10`. That gate makes an exact bounded decision immediately before
aggregate reservation and process mutation. It does not observe a short pressure burst that begins and
ends between two PTY requests, and it cannot close the latch until another request samples the rolling
averages.

Linux Pressure Stall Information (PSI) provides a separate event interface for this use case. A process
opens a pressure file `O_RDWR`, writes one `<some|full> <stall-us> <window-us>` trigger, and waits for
`POLLPRI`. Each trigger owns one file descriptor. Closing the descriptor deregisters the trigger. The
kernel bounds tracking windows, rate-limits notification to one event per window, and reports source
loss through the polling interface. The interface is useful only if IoTox preserves exact cgroup
identity, owns the descriptor lifetime, converts event and monitor failure into the existing latch,
keeps shutdown bounded, and does not imply a stronger instantaneous or causal guarantee than the ABI
provides.

## Decision

1. Extend the default-off host-local pressure policy with one optional common trigger window and
   independent CPU `some`, memory `full`, and I/O `full` cumulative-stall thresholds. The policy remains
   outside terminal profiles, authority records, Ratox packets, and remote capability negotiation.
2. Accept a common trigger window from 2,000,000 through 10,000,000 microseconds in exact
   2,000,000-microsecond quanta and each configured stall threshold from one microsecond through that
   window, inclusive. A trigger and its common window must be configured together.
3. Require every trigger to have the matching `avg10` threshold from ADR 0089. A trigger can close the
   gate asynchronously, but reopening must always be justified by a complete later synchronous sample
   against the existing hysteresis policy.
4. Deliberately constrain the broader privileged kernel range to the portable unprivileged subset.
   Linux permits monitors without effective `CAP_SYS_RESOURCE` only when the window is a multiple of two
   seconds and routes those monitors through the averages worker instead of a realtime polling thread.
   Reject nonportable windows before opening a trigger descriptor; never make policy validity depend on
   ambient capability state, silently round a value, or request an avoidable kernel realtime worker.
5. Open one new `O_RDWR | O_NONBLOCK` descriptor beneath the already pinned exact cgroup-v2 root for
   each configured trigger. Re-run the daemon-owned protected-control check on every descriptor.
6. Encode the canonical trigger record through a typed, bounded, locale-independent helper that accepts
   only `some` or `full`, verifies the portable window/stall policy, includes the terminating NUL, and
   emits no newline. Test its exact binary output directly. Reject a failed or short write. Never reuse
   one descriptor for more than one trigger.
7. Complete the existing `cgroup.pressure=1` and canonical PSI sample preflight before trigger
   registration. Preallocate the complete trigger-descriptor vector before the first kernel registration,
   then register every requested trigger and start monitoring before the production factory is exposed.
   Any allocation, registration, wakeup-descriptor, or thread-start failure aborts activation; never leave
   a partially registered set merely because later userspace storage growth failed.
8. Use one dedicated monitor thread and one nonblocking `eventfd` shutdown channel. Poll the shutdown
   descriptor and all trigger descriptors indefinitely for `POLLPRI`. The state destructor signals the
   eventfd, joins the thread, and only then closes trigger descriptors, so teardown cannot strand an
   unbounded poll or outlive the kernel registrations.
9. Publish each observed trigger into a per-resource saturation-safe atomic pending counter before the
   monitor attempts to acquire the admission mutex. Drain those counters under the controller mutex,
   retain total and per-resource event counts, and extend a monotonic hold deadline to at least one
   complete configured tracking window after userspace observes the event.
10. A first trigger that finds the gate open closes it immediately and increments both the ordinary
    close-transition count and a trigger-specific close-transition count. Further events while closed
    extend the hold and increment event counts without fabricating additional close transitions.
11. While the hold is active, reject every new PTY with typed `resource_exhausted`, increment a dedicated
    hold-rejection counter, even if the current
    rolling averages are below their reopen thresholds. Once the hold expires, retain the closed latch
    until one complete valid `avg10` sample places every configured metric at or below
    `maximum-hysteresis`.
12. Validate the complete `poll(2)` result before reuse: the returned ready count must equal the exact
    number of nonzero `revents` entries, the indefinite wait must not return zero, the shutdown descriptor
    may report only `POLLIN` or terminal bits, and trigger descriptors may report only `POLLPRI` or
    terminal bits. Treat an unknown bit or structural mismatch as `protocol_error`; treat `POLLERR`,
    `POLLHUP`, `POLLNVAL`, fatal `poll(2)` failure, allocation failure in the monitor, or any unexpected
    monitor exception as permanent monitor failure for that controller instance. Publish one typed error,
    increment the monitor-failure count, and fail the gate closed. Do not restart the monitor or reopen
    trigger files in place.
13. Drain pending trigger/error publication before sampling, immediately after sampling, and after the
    first evaluation. Re-evaluate after the final drain. This establishes a bounded userspace ordering:
    an event published by the monitor before the final drain cannot be admitted past the gate. It does
    not claim that userspace can eliminate the scheduler interval between the kernel waking a poller
    and that poller publishing the event.
14. Retain owner-private, content-free evidence for configured trigger dimensions, monitor health,
    active-hold state and remaining microseconds, typed monitor error, total and per-resource events,
    monitor failures, trigger-caused close transitions, and hold-specific rejections. Do not attach profile, peer, command,
    payload, process, session, path, device, or terminal-content labels.
15. Add exact policy/CLI boundaries, pure hold-and-hysteresis decisions, Agent configuration projection,
    runtime-tree rendering, warnings-as-errors builds, and a capability-aware real-kernel process route
    that registers a quiet per-cgroup trigger and proves monitor lifecycle when the host exposes the
    ABI. Preserve an explicit named skip instead of fabricating positive kernel evidence.

## Consequences

- A qualifying PSI event can close new-session admission even when no request is currently sampling
  the delegated root.
- A full-window quiet hold prevents an immediate reopen from a low rolling average after a sharp
  cumulative-stall event.
- Descriptor lifetime exactly owns kernel trigger lifetime, and the eventfd/join sequence gives the
  indefinite poll a bounded explicit shutdown path.
- Trigger observation and synchronous averages compose through one latch instead of creating two
  conflicting policy engines.
- Monitor loss cannot silently turn a configured tripwire into an always-open gate.
- Private counters distinguish pressure events, monitor health, ordinary close transitions, and
  trigger-caused close transitions without creating per-session operational telemetry.

## Retained nonclaims

- A PSI trigger is cumulative stall over an approximated sliding tracking window. It is not an
  instantaneous utilization meter, causal diagnosis, queue-depth bound, forecast, free-capacity
  measurement, or proof that one additional session would fail.
- Notification is rate-limited by the kernel and asynchronous. IoTox does not claim zero latency from
  threshold crossing to latch publication, strict linearization at the kernel wakeup instant, or that
  every underlying stall episode produces a separate userspace event.
- Sequential CPU, memory, and I/O `avg10` reads are not one atomic cross-resource kernel snapshot.
- The monitor rejects future PTY creation only. It does not preempt, kill, migrate, resize, throttle,
  reprioritize, or attribute already-running sessions.
- Window and threshold fitness remain deployment-specific. IoTox does not choose safe defaults,
  adapt thresholds, infer fleet capacity, or persist latch/counters across daemon restart.
- Construction-host compilation and a capability-aware process skip do not establish support on a
  named target kernel, service manager, delegation layout, or production fleet.
- Descriptor and ownership checks do not constrain root or another sufficiently privileged cgroup
  co-writer.

## Rejected alternatives

### Poll the rolling averages periodically

Rejected because it adds an arbitrary userspace sampling cadence, can miss short bursts, and duplicates
an event facility already maintained by the kernel. Rolling averages remain the bounded recovery
criterion, not the continuous tripwire.

### Reopen automatically when the hold timer expires

Rejected because elapsed time is not evidence that current pressure is below policy. A complete valid
sample must still satisfy every hysteresis boundary.

### Register several triggers on one descriptor

Rejected because the Linux ABI permits one trigger per descriptor and returns `EBUSY` for another
write. Separate descriptors also preserve exact per-resource attribution.

### Silently coerce unprivileged windows to two-second multiples

Rejected because hidden rounding changes host policy and makes configuration evidence false. The exact
requested policy either registers or activation fails with a typed local error.

### Continue with synchronous sampling after the monitor fails

Rejected because that would silently degrade an explicitly configured continuous tripwire. Missing
monitor evidence is not evidence of low pressure.

### Kill existing sessions after a trigger

Rejected because load-shedding admission and session revocation are distinct safety decisions. This
revision prevents new mutation and does not create a pressure-based remote-effect or preemption policy.
