# GPU replay-receipt witnesses, capture lineage, update delta, resource lifetime, and locality lease

This is the compact successor surface for `OQ-0165`.

## Practice / observation

After `gpu_replay_envelope_state`, the next temptation is to build a standing graph escrow or replay-envelope notary.  That is too much machinery for the current archive.  The useful smaller move is a receipt-grade witness: when a same-envelope GPU replay claim becomes load-bearing, the archive should ask what public receipt makes the claim auditable without pretending that every profiler trace is ground truth.

A receipt is not a proof of identical performance.  It is a bounded public carrier for why the claimed replay envelope should be treated as the same, updated, resource-continuous, locality-continuous, or mixed.  It sits between mere verbal assurance and a full telemetry court.

## External pressure from CUDA graph updates, graph memory/user-object lifetime, CUPTI/Nsight traces, and green-context locality

CUDA graph update material makes update lineage a first-class question: whole-graph update requires a topologically compatible graph, while individual node update changes node parameters without replacing the whole envelope.  That suggests a receipt split between capture lineage and update delta rather than a generic "same graph" claim.  `REF-1041`

CUDA user objects, graph memory nodes, and stream-ordered allocation make resource lifetime explicit enough that a replay receipt can name whether memory and owned resources were carried by graph/user-object/pool semantics or merely reacquired around a similar launch.  `REF-1041`, `REF-1042`

CUPTI and Nsight Systems provide a narrower trace basis: graph launches, graph-node launches, creation callbacks, API/GPU trace correlation, memory-pool records, and graph/node trace granularity can support a receipt, but they do not by themselves prove that the trace captured every causal condition the archive might care about.  `REF-1043`, `REF-1044`

CUDA green contexts and related execution-context material make locality lease auditable in a limited way: a receipt can say the workload targeted a partitioned context or resource lease, but this does not automatically certify interference, cache state, or every scheduler-side externality.  `REF-1045`

## Working synthesis

Use `gpu_replay_receipt_state` when the live claim is not just "the replay envelope was the same" but "the envelope sameness has a public receipt."  The receipt answers a narrower question than graph escrow: what kind of evidence makes this replay-envelope claim auditable enough for the current move?

`capture-lineage-receipt` means the claim is carried by visible capture, instantiation, graph handle, or creation-lineage evidence.  It says the same graph family is being replayed, not that every update or resource condition is unchanged.

`update-delta-receipt` means the claim is carried by a named update path: a topologically compatible whole-graph update, an explicit node update, or another bounded delta.  It avoids quietly treating a changed graph as unchanged.

`resource-lifetime-receipt` means the claim is carried by graph memory nodes, user-object lifetime, stream-ordered allocation/free, memory-pool operation traces, or equivalent resource-continuity receipts.  It avoids treating "similar allocation" as "same resource envelope."

`locality-lease-receipt` means the claim is carried by an explicit resource partition, green context, MPS/MLOPart allocation, execution context, or locality lease surface.  It avoids treating ordinary device identity as stable locality.

`mixed-gpu-replay-receipt` means more than one receipt family is material or the receipt packet is deliberately composite.

## Capture-lineage vs update-delta vs resource-lifetime vs locality-lease vs mixed GPU replay receipt

- Use `capture-lineage-receipt` when the decisive evidence is graph/capture identity or creation lineage.
- Use `update-delta-receipt` when replay continuity depends on a bounded graph or node update rather than unchanged capture.
- Use `resource-lifetime-receipt` when continuity depends on graph memory, user-object, stream-ordered allocator, pool, or memory-operation lineage.
- Use `locality-lease-receipt` when continuity depends on green context, MPS/MLOPart, execution context, SM/WQ partition, or another explicit locality/resource lease.
- Use `mixed-gpu-replay-receipt` when the receipt cannot be honest with only one branch.

## Countermodels / probes

Countermodel one: a graph is replayed from the same source code, but a fresh capture or incompatible update path is used.  That is not enough for `capture-lineage-receipt`; it needs lineage evidence or an `update-delta-receipt` if the changed path is bounded.

Countermodel two: CUPTI or Nsight shows a graph/node trace, but the relevant question is memory-pool continuity or resource ownership.  A trace supports a receipt only if it names the relevant lifetime branch; otherwise the archive should mark the branch missing or mixed.

Countermodel three: a green context or partition exists somewhere in the system, but the replayed work was not targeted through it.  That does not earn `locality-lease-receipt`.

Countermodel four: a rich trace exists, so the archive declares a notary.  That is overclaiming.  The witness is receipt-grade unless a later revision proves that receipt classes repeatedly fail.

## Design consequences

A same-envelope GPU replay claim now gets a two-step discipline: first classify the replay envelope with `gpu_replay_envelope_state`; then, only when auditability is load-bearing, classify the receipt with `gpu_replay_receipt_state`.

Receipts should be small.  They should name the concrete public handle, update path, resource lifetime, or locality lease that carries the claim.  They should also name what the receipt does not certify: performance warmth, hidden host parity, profiler completeness, or future launch behavior unless those are separately witnessed.

This revision therefore promotes a receipt witness, not graph escrow.  It leaves flight-recorder, trace-escrow, and locality-lease market machinery in quarantine.

## Overflow test

Promote stronger graph escrow only if several future revisions need a durable public process for storing, comparing, or adjudicating graph traces and locality leases, and the compact receipt tokens repeatedly fail to preserve honest replay claims.  One vivid profiler trace, one launch graph, or one green-context example is not enough.

## Transformer-facing implication

When a model argues from GPU replay continuity, ask two questions.  First: what envelope family is being claimed?  Second: what receipt family carries the claim?  If the answer is only "same code" or "same profiler screenshot," do not silently infer `capture-lineage-receipt`, `resource-lifetime-receipt`, or `locality-lease-receipt`.
