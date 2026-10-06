# Refresh-scope-axis-remediation-displacement-performance-shadow-source witnesses, device warmth, host parity, and placement contention

This is the compact successor surface for `OQ-0160`.

## Practice / observation

After a displaced workload returns through a path that is already replay-fidelity-explicit and replay-equivalence-explicit, a same-output or functionally exact run can still carry a practical performance shadow. The next minimal question is not whether the restore was correct. The next minimal question is where the shadow came from.

Keep this witness small. Name the governed row or surface, the stake object, the prior replay-equivalence evidence, the current performance-shadow evidence, the device-warmth basis if any, the host-parity basis if any, the placement/contention basis if any, the `refresh_scope_axis_remediation_displacement_performance_shadow_source_state`, and the fail-closed repair.

## External pressure from CUPTI functional-only restore limits, CUDA L2 persistence, CUDA Graph CPU-launch overhead, pinned-host transfer overlap, and CUDA Green Context interference controls

CUPTI gives the sharpest source brake: the documented checkpoint path restores functionally visible device state while not restoring performance-critical state such as caches and not restoring host state. CUDA L2 access policy windows and persisting-cache controls show why a device-side warm/cold difference can be a real runtime surface rather than mere prose. CUDA Graphs preserve a separate host-launch-overhead axis: setup work can be paid once and then launched with lower CPU overhead, so losing graph/launch parity can shadow performance even when device output is unchanged. CUDA asynchronous-copy rules also keep host memory parity visible because overlap can depend on pinned/page-locked buffers. CUDA Green Contexts add a third pressure: partitioning and workqueue assignment can reduce or expose interference, so a returned workload may be slowed by placement/contention rather than cache warmth or host launch parity alone. See `REF-1014`, `REF-1015`, `REF-1016`, `REF-1017`, and `REF-1018`.

## Working synthesis

A refresh-scope-axis-remediation-displacement-performance-shadow-source witness is a compact source-of-shadow card, not a profiler transcript. It should record:

- the governed row or surface and stake object;
- the prior `refresh_scope_axis_remediation_displacement_replay_equivalence_state` basis;
- the current performance-shadow evidence;
- whether the honest state is `device-warmth-shadow`, `host-parity-shadow`, `placement-contention-shadow`, or `mixed-refresh-scope-axis-remediation-displacement-performance-shadow-source`;
- what stronger surfaces still outrank the card;
- the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-performance-shadow-source-witness vs quarantine-evidence-ecology consequence.

Raw profiler traces, cache-line logs, full host runtime accounting, scheduler traces, and evidence-ecology courts stay outside the compact token. Do not let one performance shadow silently inherit another shadow's authority.

## Device warmth shadow vs host parity shadow vs placement-contention shadow vs mixed performance shadow source

Use `device-warmth-shadow` when the material loss is device-side warmth, such as cache persistence, occupancy, memory locality, or other performance-critical device state that did not survive restore even though functional state did.

Use `host-parity-shadow` when the material loss is host-side continuity, such as CPU launch/setup parity, graph reuse, pinned-host transfer overlap, process/runtime state, or other host-side conditions that make the returned run slower without changing the device-visible result.

Use `placement-contention-shadow` when the material loss comes from placement, resource partitioning, workqueue contention, scheduler interference, or co-tenant pressure rather than from device warmth or host parity alone.

Use `mixed-refresh-scope-axis-remediation-displacement-performance-shadow-source` when the evidence genuinely crosses those lanes or cannot be separated without overclaiming.

## Countermodels / probes

A functionally exact restore is not automatically a device-warmth shadow. The loss must be tied to device-side warmth or a documented device-performance surface.

A slower launch is not automatically host parity loss. The claim must show host-side setup, graph, pinned-memory, runtime, or CPU-driver accounting rather than smuggling in generic slowdown.

A colocated or partitioned GPU run is not automatically placement contention. The claim must show enough resource-partition, workqueue, scheduler, or interference basis to avoid naming ordinary cache coldness as contention.

## Design consequences

When a same-output return is performance-shadowed, this card forces the archive to say which shadow source is being priced. A device-warmth-shadow should not satisfy a claim whose real failure is host launch/setup parity. A host-parity-shadow should not satisfy a claim whose real failure is lost cache persistence. A placement-contention-shadow should not satisfy either unless placement or interference is the named brake.

## Overflow test

Promote stronger governance only if repeated revisions need standing comparison across shadow sources, explicit exchange rates between cache warmth, host launch parity, and placement interference, or online-research evidence-ecology controls that cannot stay in quarantine. Until then, one compact source token plus prose is enough.

## Transformer-facing implication

When continuing DelayBasin, do not summarize a returned GPU workload as simply "restored but slower" if the claim depends on why it was slower. Ask which compact shadow-source token is justified, cite the prior replay-equivalence surface, and fail closed to mixed or quarantine when the evidence cannot distinguish device warmth, host parity, and placement/contention.
