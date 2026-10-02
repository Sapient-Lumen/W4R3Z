# Aggregate cgroup reservation admission — applied research for rev0031

Research date: 2026-08-19
Implementation target: IoTox rev0031
Source policy: primary Linux kernel and systemd documentation only for technical claims

## Question

How can IoTox prevent the configured maxima of simultaneous per-session cgroup-v2 leaves from
multiplying beyond an administrator-owned host policy while retaining pre-mutation rejection,
profile-specific limits, delegated-tree ownership, and exact teardown accounting?

## Primary findings

### Linux hard limits may be overcommitted across siblings

The Linux kernel cgroup-v2 documentation defines limits as maximum amounts a child may consume and
states that limits may be overcommitted: the sum of child limits may exceed the amount available to
the parent. The same documentation defines the relevant hard interfaces used by IoTox:

- `pids.max` limits the number of tasks in a cgroup hierarchy;
- `memory.max` is the hard memory usage limit;
- `memory.swap.max` is the hard swap usage limit, with zero remaining a meaningful policy;
- controller distribution is hierarchical and depends on parent controller activation.

Applied conclusion: exact per-session kernel enforcement does not itself provide an admission rule for
the sum of configured sibling maxima. A conservative userspace ledger over the already-composed
per-session maxima closes that policy gap without pretending to reserve physical pages.

### Delegated cgroup management requires an owned subtree

systemd's cgroup delegation documentation says managers which manipulate raw cgroup files should do so
inside an explicitly delegated service or scope subtree and describes delegation as the boundary below
which the service becomes the exclusive manager. It also notes that requested controllers must still
be enabled in the delegated subtree.

Applied conclusion: aggregate admission remains tied to IoTox's existing explicit delegated-root,
single-writer, signed-incarnation, controller-preflight, exact-read-back, and session-leaf lifecycle
contracts. The aggregate policy does not authorize use of an arbitrary systemd-owned cgroup.

### Pressure signals are observation, not this revision's admission contract

Linux Pressure Stall Information exposes per-cgroup `cpu.pressure`, `memory.pressure`, and
`io.pressure` files and supports pollable thresholds. These signals can support a future adaptive
admission policy, but they report contention after or while it occurs and do not replace an exact
configured-max reservation invariant.

Applied conclusion: rev0031 keeps pressure-based admission open. It records deterministic current,
peak, and rejected reservation evidence instead of changing capacity based on transient PSI values.

## Design derivation

1. Reserve only dimensions explicitly bounded by the administrator.
2. Require each configured dimension to exist as a finite effective per-session maximum.
3. Reject startup if any enabled profile cannot fit once on an idle ledger.
4. Atomically test and charge the full reservation vector before mutable factory work.
5. Use subtraction-based capacity checks to avoid unsigned overflow.
6. Carry the charge in a move-only RAII token through all early failures and the complete production
   process/cgroup teardown sequence. Release post-spawn charges only after direct-child reap and exact
   leaf removal are both proved; otherwise strand the exact charge so admission remains fail closed.
7. Keep configured maxima, current use, peaks, rejection count, and stranded-reservation count in
   owner-private aggregate status.
8. Exclude CPU until a canonical exact aggregate scheduling policy is specified.

## Boundaries retained

This construction is conservative admission accounting over configured maxima. An unproved teardown
intentionally leaves its exact charge stranded until restart recovery; that is evidence of uncertainty,
not proof that the resources are still consumed. It is not physical memory reservation, process-slot
preallocation, swap-space allocation, performance prediction, or proof that an allocation will
succeed. It does not protect against a privileged external cgroup
writer, process migration by another manager, host-wide workloads outside IoTox's delegated subtree,
or two independently configured hosts without a shared lease. It does not implement `io.max`, PSI-
driven admission, aggregate CPU bandwidth, dynamic policy reload, target-fleet sizing, or production
readiness.

## Sources

1. Linux kernel documentation, **Control Group v2**. Accessed 2026-08-19.
   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. Linux kernel documentation, **PSI — Pressure Stall Information**. Accessed 2026-08-19.
   https://docs.kernel.org/accounting/psi.html
3. systemd project, **Control Group APIs and Delegation**. Accessed 2026-08-19.
   https://systemd.io/CGROUP_DELEGATION/
