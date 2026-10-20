# Profile-scoped cgroup budget ceilings — applied research for rev0030

Research date: 2026-08-18
Implementation target: IoTox rev0030
Source policy: primary Linux kernel and systemd documentation only for technical claims

## Question

How can IoTox add local per-profile process, memory, swap, and CPU limits while preserving the
administrator-owned rev0029 ceiling, delegated-cgroup safety, exact startup proof, and fail-closed
session admission?

## Primary findings

### Linux cgroup-v2 restrictions are hierarchical

The Linux kernel cgroup-v2 documentation states that controller behavior is hierarchical: a nested
cgroup further restricts resource distribution, and restrictions closer to the root cannot be
overridden below. Its delegation section likewise says a delegated subtree cannot escape parent
resource restrictions. This establishes the required security direction for IoTox policy
composition: profile policy may tighten a host ceiling, never weaken it.

The same document defines limits as maxima a child may consume and describes the concrete interfaces
used by IoTox:

- `pids.max` is a hard process-count limit;
- `memory.max` is the hard memory-usage limit;
- `memory.swap.max` is the hard swap-usage limit, with zero meaning no swap allocation beyond zero;
- `cpu.max` is the `$MAX $PERIOD` maximum bandwidth interface and defaults to `max 100000`.

Applied conclusion: scalar maxima compose with `min`; CPU bandwidth composes by the lower exact
quota/period ratio, using 100,000 microseconds when a period is omitted.

### Delegated subtrees need one trusted writer

systemd's control-group interface documentation explains that cgroup v2 requires each individual
cgroup to be managed by a single writer and that services which manage subcgroups on systemd systems
must receive explicit delegation. This supports retaining IoTox's explicit delegated-root contract,
supervisor ownership checks, and documented assumption that no second privileged manager mutates the
reserved subtree concurrently.

Applied conclusion: profile budgets do not authorize direct profile or payload writes. The daemon
remains the sole writer, validates controller activation, writes and reads back exact effective values,
and attaches the blocked helper only after proof.

## Design derivation

1. Add five local canonical profile fields matching the rev0029 host envelope.
2. Represent absence explicitly as `none`, because numeric zero is meaningful for swap.
3. Validate each policy independently before composition.
4. Select the smaller configured pids, memory, and swap maximum.
5. Compare CPU rationals exactly. A continued-fraction comparator avoids both floating-point rounding
   and overflow of `quota_a * period_b` at the accepted ranges.
6. Retain the host representation for equal CPU ratios to keep administrator policy stable and
   deterministic.
7. Preflight each distinct `(identity, effective budget)` pair before recovery and network startup.
8. Recompute composition in the production PTY factory so startup validation is not the sole guard.
9. Report aggregate counts only.

## Boundaries retained

This revision does not implement `io.max`, pressure-stall based admission, aggregate resource
reservation across simultaneous sessions, dynamic profile reload, or defense against a privileged
co-writer. It does not claim that a cloudtainer proves target-fleet controller topology. Existing
named-host and physical-host qualification gates remain open.

## Sources

1. Linux kernel documentation, **Control Group v2**. Accessed 2026-08-18.
   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. systemd project, **The New Control Group Interfaces**. Accessed 2026-08-18.
   https://systemd.io/CONTROL_GROUP_INTERFACE/
