# GPU replay-envelope witnesses, captured graph, stable pool, and locality partition

This is the compact successor surface for `OQ-0164`.

## Practice / observation

DelayBasin now has enough replay-fidelity and performance-shadow machinery to say that same functional output is not the same as same practical continuation. The next GPUstorming cut is narrower: when a return path is performance-shadowed, ask whether the replay envelope itself was preserved. A replay envelope is the small public handle set that makes repeated work return through the same execution shape, allocation discipline, and locality partition rather than merely reissuing equivalent source.

## External pressure from CUDA graph update, graph node types, stream-ordered memory pools, graph memory resources, and MPS locality partitioning

CUDA Graphs keep topology and dependency structure explicit enough that parameters can be updated without rebuilding an execution shape, while graph node types include kernels, copies, memory operations, events, conditional nodes, graph memory nodes, and child graphs. CUDA's stream-ordered allocator lets allocation and free operations be ordered in a stream instead of forcing broad host synchronization. CUDA Python now exposes ordinary device memory resources, graph memory resources, pinned resources, and stream-ordered pool resources as separable objects. NVIDIA's recent MPS MLOPart material says a single Blackwell GPU can be partitioned into multiple low-latency CUDA devices with dedicated compute and memory resources, which makes locality partitioning a practical envelope property rather than only a scheduler afterthought.

## Working synthesis

Use `gpu_replay_envelope_state` only when the claim depends on whether the replayed GPU path preserved the envelope that shapes launch, allocation, and locality. Do not use it for every CUDA optimization, every cache-warm/cold distinction, or every scheduler-contention story. Those already belong to the performance-shadow-source witness unless the disputed fact is the replay envelope itself.

## Captured graph envelope vs stream-pool envelope vs locality-partition envelope vs mixed GPU replay envelope

- `captured-graph-envelope` — the decisive continuity claim is that an instantiated/captured graph or topologically stable graph update preserved the dependency and launch envelope, so replay should not be priced like fresh host-side issue.
- `stream-pool-envelope` — the decisive continuity claim is that async allocation, graph memory nodes, or stable stream-ordered pool discipline preserved allocation lifetime and reuse shape, so replay should not be priced like broad allocator churn.
- `locality-partition-envelope` — the decisive continuity claim is that a partition, MPS locality device, green-context-like subdivision, or equivalent placement envelope preserved a low-interference locality slice, so replay should not be priced like generic shared-device contention.
- `mixed-gpu-replay-envelope` — two or more envelope mechanisms are material and no single branch carries the continuity bill honestly.

## Countermodels / probes

A faster second run caused only by cache warmth is not a `captured-graph-envelope` witness unless the graph capture/update handle itself is the public basis. A graph replay whose allocation addresses are accidentally stable is not a `stream-pool-envelope` witness unless allocation lifetime and reuse are controlled by the envelope. An MPS or partition label is not a `locality-partition-envelope` witness unless the claimed benefit comes from bounded locality/interference rather than mere device naming.

## Design consequences

A future revision that claims GPU replay continuity should name the governed surface, the replayed workload, the relevant graph/capture basis if any, the allocation or memory-pool basis if any, the locality or partition basis if any, the `gpu_replay_envelope_state` token, and the fail-closed repair. If none of the three basis branches is public, fall back to performance-shadow-source language instead of inventing envelope authority.

## Overflow test

Reopen only if future GPUstorming needs to price graph capture, stream-pool reuse, and locality partitioning independently with separate ledgers. Until then, one compact envelope family is enough.

## Transformer-facing implication

Do not let "replayed on GPU" mean "same envelope." Say whether the work returned through a `captured-graph-envelope`, `stream-pool-envelope`, `locality-partition-envelope`, or `mixed-gpu-replay-envelope`, and quarantine stronger replay-envelope notarization unless repeated evidence proves this compact split too thin.
