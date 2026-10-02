# ADR 0087: Retain cgroup lifetime peaks and complete CPU work

- Status: accepted and implemented in rev0036
- Date: 2026-08-19
- Scope: delegated cgroup-v2 PTY teardown evidence, optional kernel capabilities, aggregate runtime truth
- Wire effect: none
- Canonical terminal-profile effect: none; v5 remains current

## Context

rev0033 began retaining completed-session PID, memory, and CPU controller outcomes. rev0034 added
whole-leaf I/O accounting, and rev0035 added cumulative pressure-stall totals. Two important pieces of
kernel truth remained incomplete:

1. cumulative counters do not reveal the maximum number of tasks or bytes resident at one time; and
2. IoTox opened `cpu.stat` only when it configured a CPU quota, even though cgroup v2 exposes CPU work
   accounting independently of quota policy.

Current cgroup-v2 kernels expose lifetime high-water marks in `pids.peak`, `memory.peak`, and
`memory.swap.peak`. Those files are naturally bounded completed-session outcomes when opened through
protected descriptors before payload attachment and read after recursive quiescence but before exact
leaf removal. Kernel and controller variation still requires each interface to remain independently
optional.

The `cpu.stat` record always supplies `usage_usec`, `user_usec`, and `system_usec` when the interface is
present. CPU-controller bandwidth accounting adds `nr_periods`, `nr_throttled`, and
`throttled_usec`; newer kernels may also add `nr_bursts` and `burst_usec`. Treating every field as
universally mandatory rejects valid controller-disabled or older-kernel records, while treating
partial tuples as zero would manufacture evidence.

## Decision

1. Attempt to open protected read-only descriptors for `pids.peak`, `memory.peak`, and
   `memory.swap.peak` before the first payload task enters the session leaf. Open each independently;
   absence is a capability gap, not a confinement failure.
2. Parse a peak record as exactly one canonical unsigned decimal followed by one LF, bounded to 64
   bytes. Reject empty, multiline, whitespace-padded, signed, overflowing, noncanonical, truncated,
   and oversized records.
3. Require every available peak to be zero in the fresh empty leaf. Read the same pinned descriptor
   after recursive `populated=0` and before descriptor reset and exact inode removal. Preserve an
   optional final value so interface absence remains distinguishable from an observed zero peak.
4. Attempt to open `cpu.stat` for every session, not only sessions with an IoTox CPU quota. A configured
   quota still makes the interface mandatory; otherwise absence remains an optional capability gap.
5. Parse `usage_usec`, `user_usec`, and `system_usec` as one mandatory CPU work tuple. Reject a record
   that omits any member.
6. Parse `nr_periods`, `nr_throttled`, and `throttled_usec` as one optional all-or-none CPU bandwidth
   tuple. Reject a partial tuple.
7. Parse `nr_bursts` and `burst_usec` as one optional all-or-none burst tuple nested under the
   bandwidth tuple. Reject a partial or detached burst tuple. This admits controller-disabled records
   and older bandwidth records without fabricating missing data.
8. Preserve explicit per-session capability flags for the CPU work, bandwidth, and burst tuples.
   Legitimate zero work or throttling remains different from an unavailable tuple.
9. Keep the complete-outcome boundary. If any descriptor selected for one session cannot be read or
   parsed at teardown, contribute one incomplete outcome and aggregate none of that session's partial
   PID, memory, CPU, I/O, pressure, or peak evidence. Proved-empty cleanup may still finish.
10. Aggregate each peak interface with three saturation-safe values: observed-session count, sum of
    peaks, and maximum peak. Aggregate CPU tuple availability counts and saturation-safe usage, user,
    system, bandwidth, throttling, and burst totals.
11. Publish the new aggregates only through owner-private, content-free runtime status fields. Do not
    label them by session, profile, payload identity, process, command, path, peer, device, or terminal
    content.
12. Keep peaks and CPU work outside authorization and adaptive policy. rev0036 observes completed
    session behavior; it does not infer memory working sets, CPU capacity, service quality, or future
    resource needs.
13. Extend unit, fuzz, aggregate saturation, runtime projection, and live cgroup process oracles. The
    lifecycle route must prove CPU accounting without configured CPU quota and compare available
    final peak files with the exact one-shot retained outcome.

## Consequences

- Operators can distinguish cumulative work and limit events from lifetime high-water marks.
- CPU work is retained for an otherwise unlimited session when the kernel exposes `cpu.stat`.
- User and system CPU contributions survive teardown separately, while their kernel-reported total is
  preserved without recomputation.
- Capability counts prevent a zero aggregate from falsely implying that every completed session had
  the corresponding kernel interface or optional tuple.
- Peak sums answer aggregate consumption questions only as sums of independent session high-water
  marks; the maximum records the largest one-session observation. Neither is simultaneous fleet
  usage.
- A protected descriptor and zero fresh-leaf baseline bind each accepted value to the exact cgroup
  leaf lifetime despite pathname replacement after attachment.
- Saturation prevents wraparound from turning a very large cumulative value into a deceptively small
  one.

## Retained nonclaims

- A lifetime peak is not a time series, duration, percentile, average, allocation trace, working set,
  or proof that a configured ceiling was reached.
- Summed session peaks are not concurrent host demand and must not be used as reserved capacity.
- `memory.peak` and `memory.swap.peak` do not identify the allocating process, command, path, peer,
  profile, or payload operation.
- CPU user plus system values are not recomputed into usage and are not required by IoTox to equal it;
  the kernel fields are retained as reported.
- CPU bandwidth and burst tuple absence is not reported as zero throttling or zero bursts.
- The implementation does not reset peak files, sample live peaks, expose per-session histories, add
  thresholds, shed load, or change admission.
- The feature does not exclude privileged cgroup co-writers, qualify every kernel/controller
  combination, or prove production readiness.

## Rejected alternatives

### Read peak files by pathname only at teardown

Rejected because the pathname can be replaced or redirected during a session. Opening the protected
leaf file before attachment preserves the same descriptor/inode trust boundary used by existing
outcome interfaces.

### Treat absent peak files as zero

Rejected because it conflates unsupported capability with an observed zero-resource session.

### Open `cpu.stat` only when a quota is configured

Rejected because work accounting is useful and available without quota policy. Coupling observation
to enforcement loses truthful outcomes for unlimited sessions.

### Require every modern `cpu.stat` field

Rejected because CPU-controller-disabled records legitimately omit bandwidth fields and older kernels
may omit burst fields. Optional complete tuples preserve compatibility without accepting malformed
partial evidence.

### Derive CPU user or system time from the other fields

Rejected because the kernel reports each field directly and does not promise an IoTox-specific
arithmetic identity. Retaining the source values is more honest than inventing a residual.

### Use peaks for automatic aggregate admission

Rejected because independent session high-water marks do not establish simultaneous demand or future
capacity. A safe admission model would need target-specific temporal and workload evidence beyond
this completed-session observation.
