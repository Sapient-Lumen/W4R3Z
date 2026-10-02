# ADR 0084: Add a soft memory throttle and retain exact kernel session outcomes

- Status: accepted and implemented in rev0033
- Date: 2026-08-19
- Scope: canonical local terminal policy, delegated cgroup-v2 enforcement, PTY teardown, production factory state, and private runtime truth
- Wire effect: none

## Context

rev0029 made optional per-session `pids.max`, `memory.max`, `memory.swap.max`, and `cpu.max` policy
kernel-enforced. rev0030 moved matching limits into canonical local profile v3 and composed them
monotonically beneath host policy. rev0031 and rev0032 added conservative aggregate admission over
configured hard maxima and exact average CPU bandwidth.

Two gaps remained.

First, `memory.max` is an abrupt hard boundary. Linux cgroup v2 also exposes `memory.high`, a soft
throttle boundary that routes over-limit allocations through reclaim pressure and throttling without
itself invoking the OOM killer. Operators need this independently configurable below the hard ceiling,
with the same local-policy, composition, preflight, and exact-readback guarantees.

Second, IoTox published configured limits and host-local admission state but discarded the kernel's
content-free outcome evidence when an exact session leaf was removed. `pids.events`, `memory.events`,
and controller-enabled `cpu.stat` distinguish rejected forks, memory throttling, hard-limit pressure,
OOM activity, CPU usage, and CPU throttling. Reading those records after recursive quiescence and
before removal can preserve truthful operational outcomes without retaining terminal, command,
profile, path, identity, or peer data.

The evidence path must not weaken cleanup. A malformed or unexpectedly unavailable statistics record
must not keep a proved-empty cgroup alive merely to preserve observability, but it also must not be
silently reported as complete evidence. Kernel flat-keyed files may gain fields, so parsing cannot
rely on line order or reject an otherwise valid future key.

## Decision

1. Extend `CgroupResourceLimits` with optional `maximum_memory_high_bytes`. It is local policy and
   never crosses the network.
2. Emit canonical `iotox-terminal-profile-v4` with six ordered cgroup fields. Continue accepting exact
   canonical v1, v2, and v3 records. V1 and v2 decode with an empty cgroup budget; v3 decodes with an
   absent `memory.high`; public re-encoding always emits v4.
3. Add host option `--ratox-cgroup-memory-high-bytes N`. Profile and host values must be positive and
   host-page aligned. When one envelope contains both values, `memory.high` may not exceed
   `memory.max`.
4. Compose host and profile `memory.high` monotonically by selecting the smaller configured value,
   exactly as for other scalar maxima. After independent minima are selected, clamp the effective
   `memory.high` to the effective `memory.max` when both exist. This preserves the invariant even when
   the tighter values originate in different layers.
5. Request the memory controller whenever high, hard-memory, or swap policy is present. Set
   `memory.oom.group=1`, write `memory.high` before `memory.max`, and require exact kernel readback
   before helper attachment. Startup preflight exercises the same path.
6. Keep aggregate memory reservation defined by finite effective `memory.max`. `memory.high` is a
   throttle/reclaim boundary, not a hard allocation reservation, so it does not create or increase an
   aggregate memory charge.
7. For every configured per-session controller, open its protected read-only outcome interface while
   the exact new leaf is still pinned. Prefer the local-only event interface and fall back to the
   hierarchical counterpart only when the local file is unsupported:

   ```text
   pids.events.local -> pids.events
   memory.events.local -> memory.events
   cpu.stat
   ```

   Require every selected known counter to be zero before attaching the blocked helper. This prevents
   inherited or preexisting evidence from being attributed to a new session.
8. Parse the interfaces as bounded LF-terminated flat-keyed unsigned-decimal records. Accept unknown
   future keys, reject duplicate keys and noncanonical values, and require the keys used by the
   current contract. Treat `oom_group_kill` as zero when absent so kernels predating that field remain
   usable. Require the controller-specific CPU bandwidth fields only when CPU policy selected and the
   controller was already proved active.
9. After `cgroup.events` proves recursive `populated=0`, capture the selected counters before resetting
   pinned descriptors and removing the exact inode. Return that outcome at most once. A missing leaf,
   read failure, or parse failure produces one incomplete outcome rather than partial values. It does
   not block otherwise valid exact cleanup.
10. Accumulate completed outcomes with saturating arithmetic in the factory-owned cgroup state. Keep
    this state available even when aggregate reservation ceilings are empty, so observability is not
    coupled to admission policy. Duplicate recording from one move-only reservation is ignored.
11. Publish only cumulative owner-private counters for complete/incomplete outcomes, PID-limit hits,
    memory high/max/OOM events and kills, CPU usage, periods, throttled periods, and throttled duration.
    Do not add dimensions, labels, commands, identities, paths, profile IDs, peer IDs, terminal bytes,
    or error strings.
12. Split the real-kernel resource oracle by controller dependency. The memory/PID route requires
    exact `memory.high` readback, a live allocation that increments the high event, and one-shot
    teardown outcomes retaining observed `pids.max` rejection and memory throttling. The CPU route
    independently retains observed usage, periods, and `cpu.max` throttling. Keep named skip code 77
    per route when the execution environment cannot supply that delegated controller; do not
    synthesize positive kernel evidence.

## Consequences

- Operators may establish a reclaim/throttling threshold below the hard OOM boundary without making
  it remotely selectable.
- Host/profile composition remains monotone and cannot generate `memory.high > memory.max`.
- Runtime status can distinguish clean session completion from fork rejection, memory pressure/OOM,
  and CPU throttling without collecting payload content or identity.
- Outcome counters are cumulative and saturating. They do not provide per-profile attribution,
  rates, histograms, sampled utilization, current memory use, PSI, latency, throughput, or causal
  diagnosis.
- Local event files provide direct attribution on kernels that expose them. Hierarchical
  `pids.events` and `memory.events` remain an exact compatibility fallback because every IoTox session
  object is validated as a childless domain and represents the complete session subtree.
- An outcome-interface failure is visible as incomplete telemetry while exact teardown can still
  finish. This deliberately prioritizes eliminating a proved-empty kernel object over retaining a
  statistics file solely for diagnosis.
- No outcome is claimed when session teardown itself is unproved. Existing conservative reservation
  stranding remains the admission response to that uncertainty.
- `memory.high` can be exceeded under extreme conditions and does not itself invoke OOM. It is not a
  physical reservation, a working-set guarantee, or an adaptive memory controller.

## Rejected alternatives

### Replace `memory.max` with `memory.high`

Rejected because the two controls have different meanings. A soft reclaim boundary does not provide
the hard finite maximum required by aggregate admission or OOM containment.

### Charge aggregate memory from `memory.high`

Rejected because doing so would describe a throttle target as reserved hard capacity. Aggregate
accounting continues to use the finite effective hard maximum.

### Read statistics continuously

Rejected because polling creates avoidable overhead, rate semantics, observation races, and a larger
privacy surface. Teardown-time counters are bounded, cumulative kernel truth for the exact completed
leaf.

### Publish one record per profile or session

Rejected because labels and session histories would widen retained metadata and cardinality. The
private status projection needs only aggregate content-free outcomes.

### Fail cgroup removal when telemetry parsing fails

Rejected because a proved-empty exact leaf should not survive solely to retain diagnostics. The
incomplete counter makes evidence loss explicit without weakening cleanup.

### Reject all unknown kernel keys

Rejected because Linux flat-keyed controller files can gain fields. Strictness applies to grammar,
duplicates, bounds, and required keys; unrelated future keys are ignored.

### Require `memory.events.local` and `pids.events.local`

Rejected because availability differs across deployed kernels. IoTox prefers the local interfaces
when present, then uses its existing childless-leaf proof to make hierarchical records attributable to
the same exact subtree while preserving broader cgroup-v2 compatibility.
