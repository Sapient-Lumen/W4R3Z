# Exact rational CPU reservation admission — applied research for rev0032

Research date: 2026-08-19
Implementation target: IoTox rev0032
Source policy: primary Linux kernel and systemd documentation only for technical claims

## Question

How can IoTox extend its exact host-local cgroup reservation ledger to heterogeneous per-session
`cpu.max` policies without floating point, overflowing cross-products, hidden rounding, or weakening
the pre-mutation and teardown invariants established in rev0031?

## Primary findings

### `cpu.max` is a quota/period bandwidth interface

The Linux cgroup-v2 documentation defines `cpu.max` as a two-value file containing `$MAX $PERIOD`,
with a default of `max 100000`. A finite maximum permits up to `$MAX` microseconds of CPU time in each
`$PERIOD` microseconds. The CFS bandwidth-control documentation explains that quota is replenished on
period boundaries and runnable work is throttled after the group consumes its quota.

Applied conclusion: quota alone is not comparable across profiles. The exact average-bandwidth value is
the positive rational `quota / period`. Period still has burst/throttling effects, so IoTox must keep
the session's kernel policy unchanged and treat the aggregate period only as an admission-accounting
unit.

### Delegated subtree ownership remains the mutation boundary

systemd's cgroup-delegation guidance retains a single-manager subtree boundary: a service with an
explicit delegation may manage below that point, while it must not modify cgroups outside the
delegated subtree. Resource-control documentation exposes CPU quota and quota-period controls over the
unified hierarchy.

Applied conclusion: aggregate CPU admission does not create new cgroup authority. It remains tied to
IoTox's explicit delegated root, signed host-incarnation lease, controller preflight, exact read-back,
per-session leaf ownership, and bounded recovery lifecycle.

### Exact normalization can be decided with bounded integer arithmetic

For session quota `q_s`, session period `p_s`, and aggregate accounting period `p_a`, the desired charge
is:

```text
q_a = q_s * p_a / p_s
```

Let `g = gcd(p_s, p_a)`. Then:

```text
q_a = (q_s / (p_s / g)) * (p_a / g)
```

The charge is integral exactly when `(p_s / g)` divides `q_s`. Dividing first minimizes the
multiplication and permits an explicit overflow check. Separately, continued-fraction comparison can
decide `q_s/p_s <= Q_a/p_a` without multiplying potentially large numerators.

Applied conclusion: IoTox can reject all nonintegral conversions, compare exact ratios without floating
point or overflowing cross-products, and store one canonical unsigned quota charge at the configured
aggregate period.

## Design derivation

1. Reuse the per-session CPU quota/period validation range for aggregate quota/period policy.
2. Default an omitted aggregate period to 100000 microseconds, matching the documented `cpu.max`
   default. Reject a period with no aggregate quota.
3. Require a finite effective per-session quota whenever aggregate CPU accounting is active.
4. Compare session and aggregate ratios exactly before normalization so one session that cannot fit on
   an idle ledger fails activation with a direct policy error.
5. Normalize with GCD reduction and require an integral result. Never floor, ceil, or approximate.
6. Resolve process, memory, swap, and CPU into one charge, then atomically check/add all dimensions
   under the existing reservation mutex.
7. Carry CPU through move construction, move assignment, exact release, conservative stranding,
   current totals, peak totals, and capacity-rejection evidence.
8. Validate all enabled profiles before network exposure and independently recompute the charge in the
   production process factory before helper/filesystem/cgroup/process mutation.
9. Publish the selected accounting period so current and peak quota totals are interpretable.

## Test derivation

The focused proof surface includes:

- aggregate quota/period semantic validation and default-period behavior;
- missing finite session quota and single-session ratio overflow rejection;
- exact normalization across unequal periods;
- rejection when normalization would require fractional microseconds;
- a bounded lattice of 1,120 quota/period combinations checked against an
  independent small-integer cross-product/divisibility oracle;
- atomic current/peak/release/strand accounting;
- deterministic concurrent saturation across both process and CPU dimensions;
- Agent pre-network rejection and production-factory pre-mutation rejection;
- failed-spawn rollback evidence for normalized CPU quota;
- CLI rejection cases and owner-private runtime rendering.

## Boundaries retained

This is conservative admission over configured average-bandwidth maxima. It does not enforce a parent
`cpu.max`, align period boundaries, model burst concurrency, reserve processor time, infer the number of
online CPUs, guarantee scheduling latency, or predict performance. It does not cover CPU weights,
`cpu.max.burst`, real-time/deadline scheduling, cpusets, workloads outside IoTox's delegated subtree,
privileged external writers, cross-daemon capacity, dynamic policy reload, PSI-driven admission,
per-device I/O policy, target-fleet qualification, independent audit, or production readiness.

## Sources

1. Linux kernel documentation, **Control Group v2**. Accessed 2026-08-19.
   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. Linux kernel documentation, **CFS Bandwidth Control**. Accessed 2026-08-19.
   https://docs.kernel.org/scheduler/sched-bwc.html
3. systemd project, **Control Group APIs and Delegation**. Accessed 2026-08-19.
   https://systemd.io/CGROUP_DELEGATION/
4. systemd project, **systemd.resource-control**. Accessed 2026-08-19.
   https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html
