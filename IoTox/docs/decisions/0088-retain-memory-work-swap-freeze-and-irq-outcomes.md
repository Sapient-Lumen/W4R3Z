# ADR 0088: retain memory work, swap failures, freeze duration, and IRQ pressure

- Status: accepted and implemented in rev0037
- Date: 2026-08-19
- Scope: completed Ratox PTY cgroup-v2 outcome evidence

## Context

rev0033 through rev0036 retain exact controller events, CPU and I/O work, pressure stalls, and lifetime
peaks only after one session cgroup is proved recursively empty. The remaining kernel-owned outcome
surface still omitted four classes that materially distinguish otherwise similar sessions:

- page-fault, reclaim, and swap work from `memory.stat`;
- swap-threshold and swap-allocation failures from `memory.swap.events`;
- cumulative freeze-to-thaw-request duration from `cgroup.stat.local`;
- IRQ/SOFTIRQ pressure from `irq.pressure`.

Reading these files only by pathname during teardown would weaken the existing inode-pinned evidence
boundary. Treating a missing interface or optional tuple as zero would also erase capability truth.
Publishing partial results after any protected read or parse failure would break the all-or-nothing
completed-session contract.

## Decision

1. Open the relevant protected read-only descriptors before the first payload enters the exact session
   leaf. `memory.stat` is mandatory when any memory or swap policy is configured and optional
   otherwise. `memory.swap.events` is mandatory when an IoTox swap ceiling is configured and optional
   otherwise. `cgroup.stat.local` and `irq.pressure` are independently optional kernel capabilities.
2. Require an exact zero baseline for every retained counter in the fresh leaf. A nonzero initial
   fault, reclaim, swap, swap-event, freeze, or IRQ-pressure value refuses construction.
3. Parse `memory.stat` as a bounded flat-keyed record. Require `pgfault` and `pgmajfault`. Accept
   `pgscan` plus `pgsteal` only as one complete reclaim tuple and `pswpin` plus `pswpout` only as one
   complete swap tuple. Reject duplicate, partial, malformed, unterminated, oversized, noncanonical,
   or overflowing evidence while accepting unrelated future canonical numeric keys.
4. Parse `memory.swap.events` as one bounded flat-keyed record requiring unique canonical `high`,
   `max`, and `fail` counters. Unknown future canonical numeric keys remain compatible.
5. Parse `cgroup.stat.local` as one bounded flat-keyed record requiring unique canonical
   `frozen_usec` while accepting unrelated future canonical numeric keys.
6. Use a dedicated `irq.pressure` semantic parser. Current Linux kernels expose the `full` class for
   IRQ/SOFTIRQ pressure, not a fabricated `some` class. Require a complete canonical `full` PSI row,
   validate rolling fields, retain only absolute `total` microseconds, and accept future well-formed
   classes without assigning them current semantics.
7. Read the same pinned descriptors only after recursive `populated=0` and before exact leaf removal.
   Any protected control-state, read, or parse failure marks the entire session outcome incomplete;
   no PID, memory, CPU, I/O, PSI, peak, freeze, or swap subset is aggregated from that session.
8. Aggregate only complete outcomes with saturating arithmetic. Publish explicit observed-session
   counts for the whole memory-stat record, reclaim tuple, swap-work tuple, swap-event record, local
   freeze record, and IRQ-pressure record so unsupported capability remains distinct from measured
   zero.
9. Keep all projection owner-private, unlabeled, cumulative, and content free. Do not retain session,
   profile, process, command, path, peer, device, terminal, error-string, rolling-average, or payload
   labels.
10. Keep the new evidence outside authorization, resource admission, enforcement, adaptive policy,
    scheduling, alerting, and causal diagnosis.
11. Extend bounded parser, malformed-record, one-shot aggregation, saturation, runtime projection,
    fuzzer, and live private-cgroup process coverage. The live lifecycle route must compare every
    available final file with the exact retained outcome, induce post-attachment page faults, and
    positively exercise `frozen_usec` where the host exposes `cgroup.stat.local`.

## Consequences

- Operators can distinguish memory demand that faulted pages, memory pressure that scanned/reclaimed
  pages, actual page swap traffic, and swap allocation failures instead of inferring them from peaks or
  OOM counters.
- A completed session can report cumulative IRQ/SOFTIRQ stall time when the kernel provides per-cgroup
  IRQ PSI.
- Freeze-to-thaw-request time becomes visible even when a session ultimately exits normally or is killed after thaw.
- Optional tuple and interface counts preserve honest cross-kernel capability interpretation.
- Descriptor pinning and zero-baseline proof bind accepted counters to the exact cgroup lifetime.
- Saturation prevents cumulative wraparound from becoming a deceptively small result.

## Retained nonclaims

- Page faults do not identify the faulting address, process, file, command, peer, or allocation cause.
- Page scans and steals are not a working-set estimate, memory efficiency score, latency attribution,
  or proof that a configured threshold caused reclaim.
- `pswpin`/`pswpout` are page counts, not byte totals, device I/O totals, or proof of durable media
  traffic; zswap and zero-page optimizations can differ from physical swap-device work.
- `memory.swap.events:fail` does not distinguish system-wide swap exhaustion from an IoTox cgroup
  ceiling without additional evidence.
- `frozen_usec` is cumulative cgroup freezer duration, not command runtime, queue delay, scheduler
  latency, or proof of who requested freezing.
- IRQ `full` PSI is not per-interrupt attribution, an interrupt-rate counter, a CPU reservation, or a
  service-level guarantee.
- The implementation does not continuously sample, retain per-session histories, install PSI
  triggers, adapt limits, exclude a privileged cgroup co-writer, qualify every kernel configuration,
  or establish production readiness.

## Rejected alternatives

### Retain every `memory.stat` key

Rejected because many keys are instantaneous footprint values rather than monotonic lifetime work and
because the kernel may add configuration-dependent fields. The selected counters have stable,
content-free, cumulative work semantics; unknown fields remain grammar-validated but unassigned.

### Treat missing reclaim or swap fields as zero

Rejected because a missing capability is not an observed zero. Complete optional tuples and explicit
observed-session counts preserve that distinction.

### Reuse the CPU/memory/I/O PSI parser unchanged for IRQ

Rejected because current kernel state definitions expose only `PSI_IRQ_FULL`. Requiring `some` would
reject the documented interface, while manufacturing `some=0` would publish evidence the kernel did
not report.

### Read the files after leaf removal or reopen by pathname

Rejected because removal destroys the evidence and pathname reopening is not bound to the descriptor
and inode proven before payload attachment.

### Feed the counters into automatic resource admission

Rejected because completed-session cumulative outcomes do not establish concurrent demand, future
workload behavior, causal operations, or safe capacity on a target deployment.
