# ADR 0086: Retain exact per-session cgroup pressure-stall outcomes

- Status: accepted and implemented in rev0035
- Date: 2026-08-19
- Scope: delegated cgroup-v2 PTY teardown evidence, bounded kernel-record parsing, aggregate runtime truth
- Wire effect: none
- Canonical terminal-profile effect: none; v5 remains current

## Context

rev0033 retained cumulative PID, memory, and CPU controller outcomes after one Ratox PTY cgroup was
proved recursively empty. rev0034 added whole-leaf I/O accounting. Those counters show work and limit
events, but they do not quantify how long tasks were stalled because CPU, memory, or I/O service was
unavailable.

Linux Pressure Stall Information (PSI) exposes `cpu.pressure`, `memory.pressure`, and `io.pressure` in
cgroup v2. Each record contains recent averages plus cumulative `total` stall time in microseconds for
`some` pressure and, where supported, `full` pressure. The cumulative totals fit IoTox's existing
teardown evidence boundary: a fresh leaf can be proved to begin at zero, then the final absolute total
can be captured after recursive quiescence and before exact removal. The rolling averages do not fit
that boundary because they are time-windowed samples whose meaning depends on observation time.

The feature must remain capability-aware. Some kernels or configurations may omit PSI interfaces, and
older CPU PSI interfaces may omit `full`. Absence must not be converted into fabricated zero support.
Conversely, when the cgroup exposes `cgroup.pressure` and reports accounting disabled, IoTox must not
publish zero totals as though they were observed pressure evidence.

## Decision

1. Add `CgroupPressure` with an absolute `some_total_microseconds` and an optional
   `full_total_microseconds`. The optional retains the difference between an observed zero and an
   unavailable `full` class.
2. Add a dedicated bounded LF-terminated nested-key parser for PSI records. Require exactly one
   canonical `some` class with `avg10`, `avg60`, `avg300`, and `total`; accept one optional `full`
   class with the same mandatory fields. Reject duplicate classes or keys, malformed spacing,
   noncanonical/overflowing totals, malformed percentages, percentages above `100.00`, empty lines,
   truncation, and oversize input. Accept well-formed future numeric fields and classes without
   assigning them current semantics.
3. Validate but do not retain the rolling averages. Retain only cumulative absolute microseconds.
   This avoids publishing observation-time-dependent samples as session-lifetime outcomes.
4. During session-leaf construction, attempt to open protected read-only `cpu.pressure`,
   `memory.pressure`, and `io.pressure` descriptors independently. Interface absence is an explicit
   optional capability and does not reject an otherwise valid cgroup policy.
5. Also attempt to open protected `cgroup.pressure`. When present, require the exact record `1\n`
   both at fresh-leaf validation and final outcome capture. A present disabled control fails the
   statistics observation rather than manufacturing zero PSI evidence.
6. Before helper attachment, parse each available resource record and require every observed
   `some`/`full` total to be zero. This makes the final absolute total attributable to that exact fresh
   session leaf without subtractive underflow or cross-session carryover.
7. After recursive `populated=0` and before descriptor reset and exact inode removal, parse every
   available pressure record into the one-shot `CgroupSessionOutcome`. A read or parse failure marks
   the complete outcome unavailable; no partial controller or PSI totals are aggregated. Proved-empty
   cleanup may still complete.
8. Aggregate each resource independently with saturating arithmetic. Publish four values per
   resource: outcomes with an observed `some` class, outcomes with an observed `full` class,
   cumulative `some` microseconds, and cumulative `full` microseconds. Separate availability counts
   prevent zero totals from implying universal kernel support.
9. Project the twelve new counters only into owner-private runtime status. Keep them unlabeled by
   session, profile, payload identity, process, device, command, path, peer, or terminal content.
10. Extend the cgroup-record fuzzer, parser tests, one-shot/saturation aggregation tests, runtime
    projection tests, and capability-aware live process oracles. Live routes compare the record read
    immediately before removal with the one-shot captured outcome when the corresponding PSI file is
    present.
11. Do not change admission or enforcement from PSI. rev0035 observes completed-session stalls; it
    does not implement threshold monitors, live sampling, load shedding, policy adaptation, or
    capacity forecasting.

## Consequences

- Owner-private status can distinguish cumulative CPU, memory, and I/O stall time from work counters
  and controller-limit events.
- A fresh zero baseline plus post-quiescence capture makes each retained absolute total a bounded
  lifetime outcome for one exact leaf.
- Whole-interface and `full` availability remain explicit, so older or capability-reduced kernels do
  not silently look identical to pressure-free workloads.
- Statistics failure remains honest: it contributes an incomplete outcome and no trusted partial
  totals, while exact empty-leaf cleanup is not blocked by observability loss.
- Opening PSI for every session, not only sessions with matching resource ceilings, records pressure
  caused by ambient contention as well as explicit IoTox throttles. The counters are outcomes, not a
  causal attribution to a particular configured limit.
- Saturated aggregate totals intentionally lose exact magnitude after `uint64` exhaustion but never
  wrap to a smaller value.

## Retained nonclaims

- The totals do not identify which operation, file, command, process, peer, or device caused a stall.
- `some` and `full` overlap by definition and must not be summed into one duration.
- Cumulative totals do not provide a denominator, utilization percentage, latency distribution,
  throughput guarantee, or real-time health signal.
- The implementation does not retain or expose `avg10`, `avg60`, or `avg300`.
- The implementation does not register PSI triggers or poll pressure events.
- PSI does not become an authorization input, profile field, remote protocol field, aggregate
  reservation dimension, or automatic admission controller.
- Missing PSI support is not reported as zero pressure, and present zero totals are not proof that the
  broader host experienced no contention.
- The feature does not exclude privileged co-writers, qualify every target kernel, or prove production
  readiness.

## Rejected alternatives

### Retain only the rolling averages

Rejected because the averages depend on when the record is sampled and decay after a workload stops.
They are useful for live control loops, but they are not stable session-lifetime outcomes.

### Subtract an initial total from a final total

Rejected for the fresh-leaf path. Requiring an exact zero baseline is simpler, catches unexpected
carryover, and avoids underflow or reset ambiguity. If future kernels make nonzero fresh-leaf totals
legitimate, that contract must be revised explicitly.

### Treat an absent PSI interface as zero

Rejected because it conflates capability absence with an observed pressure-free session and would
make aggregate totals operationally misleading.

### Reject every session when PSI is unavailable

Rejected because PSI is observability, not the confinement policy prerequisite. Existing cgroup
lifecycle and configured resource controls remain valid on a kernel without per-cgroup PSI.

### Aggregate `some + full`

Rejected because `full` is a subset of the `some` stall state. Summing them double-counts time and
creates a metric with no kernel-defined meaning.

### Use PSI immediately for adaptive admission

Rejected because a safe feedback controller needs thresholds, time windows, hysteresis, capacity
semantics, failure behavior, and target-specific qualification. rev0035 supplies truthful completed-
session evidence without pretending those policy decisions are solved.
