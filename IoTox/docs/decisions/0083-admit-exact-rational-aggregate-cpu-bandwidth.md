# ADR 0083: Admit exact rational aggregate CPU bandwidth

- Status: accepted and implemented in rev0032
- Date: 2026-08-19
- Scope: local Ratox PTY admission, production process-factory lifecycle, command-line policy, and private aggregate runtime truth
- Wire effect: none

## Context

rev0031 added one conservative production-factory ledger over configured per-session process, memory,
and swap maxima. It deliberately excluded CPU because Linux `cpu.max` is not a scalar resource count:
it is a quota/period pair representing bandwidth, and enabled profiles may use different valid periods.
Summing raw quotas would be wrong whenever periods differ. Floating-point conversion or integer rounding
would silently change the administrator's scheduling policy.

Linux cgroup v2 exposes `cpu.max` as `$MAX $PERIOD`; the default period is 100000 microseconds. CFS
bandwidth control replenishes each cgroup's quota at its own period boundary and throttles further work
once that quota has been consumed. The ratio `quota / period` therefore provides the exact average CPU
bandwidth ceiling, while the chosen period also affects burst and throttling cadence.

IoTox needs a host-local admission invariant that can sum heterogeneous finite ratios without
floating point, overflowing cross-products, or invented rounding. The invariant must reject before
helper, filesystem, PTY, cgroup-leaf, or process mutation and must remain coupled to rev0031's exact
release/strand lifecycle.

## Decision

1. Extend `CgroupAggregateLimits` with an optional maximum reserved CPU quota and optional aggregate
   accounting period. A configured quota with no period uses 100000 microseconds. A period without a
   quota is invalid. Quota and period use the same validated ranges as per-session `cpu.max` policy.
2. Define aggregate CPU admission as the exact sum of each admitted session's rational average
   bandwidth, expressed as quota units at the administrator-selected aggregate accounting period.
   This is an admission-accounting period; it does not rewrite the session's kernel `cpu.max` period.
3. Require every admitted effective session policy to carry a finite CPU quota whenever aggregate CPU
   admission is configured. Compare the session and aggregate ratios exactly using the existing
   continued-fraction comparator, which avoids floating point and overflowing numerator products.
4. Normalize one session charge from `session_quota / session_period` to the aggregate period using:

   ```text
   g = gcd(session_period, aggregate_period)
   source_divisor = session_period / g
   target_multiplier = aggregate_period / g
   normalized_quota = (session_quota / source_divisor) * target_multiplier
   ```

   Admission is valid only when `session_quota` is divisible by `source_divisor`. A ratio that would
   require any fractional aggregate quota unit fails closed. Multiplication is checked before it is
   performed, and the normalized result is rechecked against the aggregate quota.
5. Resolve all configured process, memory, swap, and CPU dimensions into one canonical
   `CgroupAggregateCharge`. The production ledger atomically checks and charges that complete vector
   under one mutex. No dimension may be partially admitted.
6. Carry normalized CPU quota in the existing move-only RAII reservation. Exact release subtracts it
   once after proved teardown; uncertain post-spawn cleanup strands it with the rest of the charge.
   Current and peak CPU reservation totals are monotone/accounted under the same ledger lock.
7. Validate every enabled profile's effective CPU envelope during Agent activation before delegated
   recovery or networking. Recompute and enforce the same resolution in the production POSIX factory
   before mutable spawn work.
8. Expose host-only CLI options:

   ```text
   --ratox-cgroup-aggregate-cpu-quota-us N
   --ratox-cgroup-aggregate-cpu-period-us N
   ```

   Publish only configuration presence, quota, period, current normalized quota, and peak normalized
   quota in the owner-private runtime status. No profile identity, command, path, or terminal bytes are
   added.

## Consequences

- Heterogeneous `cpu.max` ratios can share one exact host-local reservation ceiling when each ratio is
  exactly representable at the selected accounting period.
- Ratios that would need floor, ceiling, nearest, or stochastic rounding are rejected rather than
  undercharging or overcharging silently.
- Concurrent admission cannot exceed the configured exact rational bandwidth sum inside one
  legitimate IoTox host incarnation.
- A failed spawn releases its normalized CPU charge with the rest of the vector. An unproved teardown
  retains the charge, so uncertainty cannot reopen CPU capacity.
- The aggregate accounting period does not synchronize session period boundaries, change kernel
  throttling cadence, enforce a parent `cpu.max`, reserve physical processor time, or guarantee latency
  or throughput. Administrators should choose an accounting period compatible with the finite ratios
  used by enabled profiles.
- CPU weights, `cpu.max.burst`, real-time/deadline scheduling, cpuset placement, host workloads outside
  the delegated subtree, privileged co-writers, cross-daemon distributed capacity, and pressure-
  adaptive admission remain outside this decision.

## Rejected alternatives

### Sum raw quota fields

Rejected because `50000/100000` and `250000/500000` are equal bandwidth but have different quota
fields. Raw quota sums depend on representation rather than policy.

### Convert ratios through floating point

Rejected because binary floating point cannot represent many decimal/rational values exactly and
comparison near a ceiling could vary with precision, optimization, or architecture.

### Floor normalized quota

Rejected because flooring undercharges a session and can admit a total rational bandwidth above the
administrator's ceiling.

### Round up normalized quota

Rejected because it changes exact policy and may reject combinations that fit mathematically. An
operator who wants conservative coarser accounting can select a compatible period explicitly.

### Require every session to use the same period

Rejected as unnecessarily restrictive. Exact normalization supports different periods whenever the
ratio maps to an integral quota at the aggregate period.

### Select a dynamic least-common-multiple period

Rejected because the period would become profile-set-dependent, may exceed the kernel period range,
complicates stable runtime truth, and changes when policy is reloaded. The administrator-selected
period keeps the accounting unit explicit and bounded.

### Rely only on a parent cgroup CPU limit

Rejected as a substitute for admission. A parent kernel limit can throttle the subtree, but it does
not reject a new session whose configured maximum would exceed an administrator-owned reservation
sum, and it does not provide rev0031's pre-mutation capacity decision or per-session lifecycle token.
