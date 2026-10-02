# ADR 0080: Enforce global PTY resource budgets in delegated cgroups

- Status: accepted and implemented
- Date: 2026-08-18
- Revision: rev0029
- Extends: ADR 0075 delegated cgroup-v2 lifecycle ownership and ADR 0079 boot/process-incarnation recovery

## Context

The optional Ratox cgroup path already gave every hardened PTY an exact daemon-owned lifecycle
container. It attached the blocked helper before manifest release, used recursive `cgroup.kill`,
proved `cgroup.events: populated 0`, removed the pinned leaf, and recovered crash-abandoned leaves only
after boot/process-incarnation proof. It intentionally did not configure controller-backed resource
limits.

That omission left one session able to consume an unbounded number of processes, resident memory,
swap, or CPU time inside the host's broader service allocation. User-space counters cannot close this
gap: process creation, memory charging, and scheduler throttling must be enforced by the kernel at the
same cgroup boundary that owns descendants. A configured limit that silently degrades because a
controller is absent, inactive, writable by the payload identity, or normalizes to an unexpected value
would be worse than an explicit startup failure.

Linux cgroup v2 supplies the required controls:

- `pids.max` rejects excess `fork(2)`/`clone(2)` with `EAGAIN`;
- `memory.max` is the hard memory ceiling, `memory.swap.max` bounds swap, and
  `memory.oom.group=1` asks the kernel to treat the cgroup as one workload for OOM selection;
- `cpu.max` carries a quota and period in microseconds and throttles runnable work after quota is
  exhausted; and
- `cgroup.controllers` plus `cgroup.subtree_control` distinguish controller availability from
  activation for child cgroups.

The terminal lifecycle contract also depends on `cgroup.kill`, which the kernel does not support for
a threaded cgroup. A resource-policy implementation therefore cannot broaden the accepted topology
to a threaded domain merely because some controller files happen to exist.

## Decision

### One explicit global envelope

The host configuration SHALL expose one optional `CgroupResourceLimits` envelope applied uniformly to
every production hardened PTY session:

```text
maximum_processes          -> pids.max
maximum_memory_bytes       -> memory.max
maximum_swap_bytes         -> memory.swap.max
cpu_quota_microseconds     -> cpu.max quota
cpu_period_microseconds    -> cpu.max period
```

An absent field leaves that controller unchanged. A configured swap value of zero is meaningful and
forbids swap. A CPU quota without a period uses 100,000 microseconds. A period without a quota is
invalid. This revision deliberately does not add remote, profile-selected, or per-command resource
budgets; the envelope is a host deployment policy.

### Validate before service exposure

Configuration SHALL fail before Ratox transport or listener activation when:

- limits are present without an explicit delegated cgroup-v2 root;
- `pids.max` is outside `1..pid_t_max`;
- CPU quota is below 1,000 microseconds or cannot fit the supported signed kernel range;
- CPU period is outside `1,000..1,000,000` microseconds or appears without quota;
- `memory.max` is zero or not host-page aligned; or
- `memory.swap.max` is not host-page aligned.

After the signed host-incarnation lease is acquired but before orphan recovery begins, Agent startup
SHALL run one disposable exact-identity cgroup preflight for each distinct enabled PTY payload
identity. The preflight occurs before recovery mutation, the production factory, or network
activation. It creates a normal empty session leaf, proves the complete controller and ownership
contract, applies and reads back the configured controls, and removes the exact leaf before reporting
success. Only then may the rev0028 bounded recovery scan mutate a proved-stale leaf.

### Require available and activated controllers

For each configured controller, the delegated root SHALL expose its canonical name in both:

```text
cgroup.controllers
cgroup.subtree_control
```

Availability alone is insufficient. Missing controllers are unsupported; available-but-inactive
controllers are an unavailable deployment. Controller lists must parse as one canonical bounded
newline-terminated record with no duplicate names or ambiguous spacing.

### Apply controls before payload attachment

Session creation SHALL complete the following before writing the blocked helper PID to
`cgroup.procs`:

1. validate the exact payload identity and delegated root;
2. prove requested controllers are available and active;
3. create and inode-pin one non-threaded domain leaf;
4. prove lifecycle and resource control files are daemon-owned and not writable by the payload UID or
   GID;
5. write configured controller values; and
6. read each value back exactly.

Memory policy SHALL write `memory.oom.group=1` whenever either memory or swap policy is configured.
No configured write, open, ownership, or read-back failure may degrade to lifecycle-only containment.
The existing blocked-helper handoff means no payload code executes inside a partially configured leaf.

### Preserve the non-threaded lifecycle invariant

A session leaf SHALL remain the literal cgroup-v2 type `domain`. `domain threaded`, `threaded`, and
invalid-domain states are rejected. This preserves availability of `cgroup.kill` and the existing
recursive teardown proof instead of trading lifecycle correctness for broader but ambiguous topology
acceptance.

### CLI surface

The one-binary host SHALL accept:

```text
--ratox-cgroup-pids-max N
--ratox-cgroup-memory-max-bytes N
--ratox-cgroup-swap-max-bytes N
--ratox-cgroup-cpu-quota-us N
--ratox-cgroup-cpu-period-us N
```

All values are unsigned decimal integers. Validation is shared by CLI parsing, Agent startup, the
production factory, and direct cgroup construction so alternate callers cannot bypass the policy.

## Consequences

### Positive

- A configured session process explosion is stopped by `pids.max` in the kernel.
- Memory and swap consumption can be bounded at the exact descendant-owning session boundary.
- CPU-heavy payloads are throttled without relying on cooperative scheduling in IoTox.
- Whole-session OOM grouping aligns memory failure with the existing lifecycle-unit model.
- Exact pre-network preflight catches missing delegation, inactive controllers, unsafe control
  ownership, topology mismatch, and write/read-back failures before the host advertises service.
- Applying policy before helper attachment prevents a payload from racing setup.
- Empty configuration preserves rev0028 lifecycle-only cgroup behavior.

### Costs and tradeoffs

- Operators must delegate and activate every requested controller at the IoTox-managed root.
- Page-aligned memory values reject convenient but kernel-normalized byte counts rather than accepting
  an inexact limit.
- One global envelope cannot tune resources per terminal profile or command.
- `memory.max` and `memory.swap.max` alter reclaim/OOM behavior and require deployment-specific sizing.
- CPU quota controls throughput, not latency, fairness against every other cgroup, or real-time work.
- The construction remains Linux/cgroup-v2 specific and depends on exclusive delegated-root
  management.

## Rejected alternatives

### Configure limits after attaching the helper

Rejected. Even a blocked or short-lived process should never inhabit a leaf whose mandatory policy has
not been proved. Configuration and exact read-back precede attachment.

### Trust control-file presence without checking root activation

Rejected. A file may be absent in children because the controller was not enabled in the parent's
`cgroup.subtree_control`. The host checks both advertised availability and active delegation.

### Accept kernel-rounded memory values

Rejected. Silent normalization weakens the operator's requested boundary. rev0029 requires page-
aligned values and exact read-back.

### Fall back to lifecycle-only containment on controller failure

Rejected. A deployment that requested a resource envelope must either receive it exactly or remain
offline.

### Accept `domain threaded` because CPU and pids controls may exist

Rejected. The terminal lifecycle contract requires `cgroup.kill`, which is not available for threaded
cgroups. A broader topology would weaken cleanup and recovery semantics.

### Make resource policy remotely selectable

Rejected for this revision. Remote or profile-specific budgets would add an authorization, persistence,
compatibility, and denial-of-service policy surface. The first construction is an explicit host-owned
deployment envelope.

## Executable evidence

The owned registry and Linux process oracle SHALL cover:

- malformed and ambiguous policy rejection before filesystem access;
- limits-without-root rejection in CLI, Agent, and production factory paths;
- exact preflight leaf creation and removal;
- inactive-controller refusal before leaf creation;
- exact `pids.max`, `memory.max`, `memory.swap.max`, `memory.oom.group`, and `cpu.max` read-back;
- real `pids.max` enforcement with `fork(2)` returning `EAGAIN`;
- real CPU throttling through a positive `cpu.stat:nr_throttled` witness;
- cgroup-wide kill, recursive empty proof, and exact removal after enforcement; and
- deterministic CTest skip code 77, with a named reason, when the qualification host cannot expose a
  non-threaded domain with `cpu`, `memory`, and `pids` delegated to children.

A skip is not a positive resource-controller qualification. Unit, parser, ordering, construction, and
negative topology evidence remain valid, while the process oracle stays executable on a suitable
kernel/delegation host.
