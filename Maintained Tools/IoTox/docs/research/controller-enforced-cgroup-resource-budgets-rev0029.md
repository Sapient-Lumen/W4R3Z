# Controller-enforced cgroup resource budgets — rev0029 applied research

**Reviewed:** 2026-08-18
**Revision:** rev0029
**Decision:** ADR 0080

## Question

How can IoTox add optional per-PTY process, memory, swap, and CPU ceilings without weakening the
existing exact cgroup lifecycle, recovery, identity, and fail-closed startup construction?

## Primary sources rechecked online

1. Linux kernel cgroup v2 documentation
   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. Linux kernel CFS bandwidth-control documentation
   https://docs.kernel.org/scheduler/sched-bwc.html
3. systemd control-group APIs and delegation guidance
   https://systemd.io/CGROUP_DELEGATION/

These sources define kernel and service-manager interfaces. They do not audit IoTox or qualify a
specific production deployment.

## Applied kernel contracts

### Delegation and controller activation

`cgroup.controllers` lists controllers available to a cgroup. A controller must also be enabled in the
parent's `cgroup.subtree_control` before its interface is distributed to child cgroups. Therefore
checking only for a child control file, or checking only the available-controller list, is not a
sufficient preflight. rev0029 parses both canonical records and requires every requested controller in
both sets before creating a session leaf.

The kernel's no-internal-process rule and topology transitions make cgroup ownership a tree-management
problem, not a collection of independent files. IoTox continues to require one exclusive daemon-owned
manager root and one non-threaded domain leaf per hardened PTY. Under systemd, this root should be
provided by a service or scope with controller delegation; systemd's documentation emphasizes a
single manager for a delegated subtree.

### Process ceiling

`pids.max` is hierarchical. When the limit would be exceeded, `fork(2)` or `clone(2)` fails with
`EAGAIN`, while migration of an existing task may temporarily place the cgroup above the configured
value. IoTox therefore applies and reads back `pids.max` before attaching the blocked helper, then the
normal helper/descendant creation occurs under the ceiling. The process oracle expects a positive
`pids.events:max` counter and `EAGAIN` after the payload plus descendants reaches the exact bound.

### Memory and swap ceilings

`memory.max` is the hard memory boundary; `memory.swap.max` bounds swap usage independently. A value of
zero for swap is meaningful and must not be mistaken for an absent option. The kernel may round memory
limits to page granularity. IoTox avoids ambiguous operator intent by accepting only positive,
host-page-aligned `memory.max` and page-aligned `memory.swap.max`, then requiring exact read-back.

`memory.oom.group=1` asks the kernel to treat the cgroup as one workload when it selects victims for a
memory-cgroup OOM. This matches the existing IoTox model in which the leader and descendants form one
terminal lifecycle unit. It is set whenever either memory or swap policy is requested.

### CPU bandwidth

In cgroup v2, `cpu.max` is a quota/period pair. The scheduler's bandwidth documentation explains that
runnable tasks are throttled after consuming the available quota and become runnable again when the
period replenishes it. IoTox uses microseconds, rejects a quota below the kernel's 1 ms bandwidth
minimum, constrains the period to 1 ms through 1 second, and uses the conventional 100 ms period when
only a quota is supplied. The process oracle witnesses a rising `cpu.stat:nr_throttled` counter under
a continuously runnable payload rather than treating configuration read-back alone as enforcement.

### Lifecycle topology remains stricter than controller availability

The cgroup v2 documentation states that `cgroup.kill` is unsupported for a threaded cgroup. IoTox's
teardown and crash-recovery proof relies on recursive `cgroup.kill`; consequently a mount or delegated
root that yields `domain threaded` children cannot be used for the positive lifecycle/resource oracle.
rev0029 retains literal non-threaded `domain` leaves and reports a deterministic skip when the local
namespace topology cannot construct that environment. It does not reinterpret a skip as a pass.

## Construction chosen

The public host configuration carries one optional `CgroupResourceLimits` value. The CLI, Agent,
production factory, and direct session constructor all share the same validation. The Agent rejects a
policy without a delegated root, acquires the signed host-incarnation lease, creates one disposable
preflight leaf for each distinct enabled profile identity, and only then performs rev0028 orphan
recovery.
Only after every probe has applied, read back, and removed its exact leaf may the PTY factory and
Ratox transport activate.

For a real session, the daemon proves the root, requested controllers, leaf type, ownership, mode,
inode, and control-file boundary; writes all requested values; reads them back exactly; and only then
attaches the still-blocked helper. Any open, ownership, write, parse, activation, read-back, or cleanup
failure stops construction. There is no configured fallback to lifecycle-only containment.

## Qualification-host observation

The local cloudtainer can enter user, mount, and cgroup namespaces and mount cgroup v2, but the fresh
namespace root reports `domain threaded`, does not expose the complete `cpu`/`memory`/`pids`
non-threaded child-delegation topology, and therefore cannot support the existing `cgroup.kill`
contract. The expanded process oracle returns CTest skip code 77 with that exact reason. This is an
honest environmental limitation, not a source-construction failure and not positive enforcement
qualification.

The direct owned registry, CLI checks, Agent/factory ordering checks, warnings-as-errors build, and
negative controller/topology paths remain executable in this host. The positive real-kernel
`pids.max` and `cpu.max` branches remain in the process oracle and will run automatically on a suitable
non-threaded delegated hierarchy.

## Remaining gaps

rev0029 does not add I/O bandwidth or IOPS controls, pressure-stall-driven adaptation, per-profile or
per-command limits, aggregate host-wide Ratox budgeting, protection from root/equivalent delegated
writers, target-fleet qualification, or a physical-host R7 run. Memory/OOM sizing and service-manager
delegation still require deployment-specific validation.
