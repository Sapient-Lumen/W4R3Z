# GPU replay cross-observer bridge witnesses, trace context, external correlation, metric exemplars, placement scope, missing bridge, and mixed bridge

This is the compact successor surface for `OQ-0168`.

## Practice / observation

`gpu_replay_observer_conflict_state` says why runtime self-attestation, profiler traces, and external monitoring disagree. The next bounded repair is not a telemetry treaty. It is a bridge witness: a small public statement of which join mechanism, if any, lets a GPU replay claim compare graph lineage, service traces, cluster metrics, and placement without pretending that every observer now shares one authority layer.

A cross-observer bridge should be admitted only after a replay envelope, receipt, trace-grade packet, or observer-conflict packet needs a comparison across observers. The question is: what bridge makes the comparison possible, what remains out of scope, and what conclusion must still fail closed?

## External pressure from CUPTI external correlation, Nsight NVTX projection, W3C trace context, OpenTelemetry metric exemplars, DCGM Kubernetes telemetry, and device placement

CUPTI external correlation makes bridge pressure concrete because it can correlate native CUDA records with external API records. That supports a bounded `external-correlation-bridge`, but it still does not make external records replay-lineage authority by themselves. `REF-1055`

Nsight Systems makes high-level region marking useful because NVTX markers and ranges can appear with CPU regions and with GPU work launched from those regions. That supports a bridge from application or service regions to GPU work, but not a standing custody mesh. `REF-1056`

W3C Trace Context gives service traces a standard carrier: the `traceparent` header carries version, trace id, parent id, and trace flags across services. That supports `trace-context-bridge` when replay work is deliberately bound to a service trace id. `REF-1057`

OpenTelemetry metric exemplars show why metric-to-trace links are useful but limited. Exemplars can associate a metric recording with OpenTelemetry context, including optional trace and span identifiers. That supports `metric-exemplar-bridge` while preserving that a metric point is not a graph receipt. `REF-1058`

DCGM-Exporter and Kubernetes GPU telemetry expose device and workload metrics into Prometheus-style monitoring and Kubernetes environments. They support cluster-side comparison windows and device or pod context, not graph-node truth. `REF-1059`

Kubernetes device plugins and GPU scheduling expose hardware resources such as GPUs to the kubelet and allow pods to be scheduled onto GPU-bearing nodes. That supports `placement-scope-bridge` when the bridge depends on placement and resource identity rather than trace context alone. `REF-1060`

## Working synthesis

Use `gpu_replay_cross_observer_bridge_state` when a GPU replay claim needs a bounded join across graph lineage, service traces, cluster metrics, and placement context. Do not use it for ordinary observer conflict classification; `gpu_replay_observer_conflict_state` still owns the conflict kind. Do not use it to create a telemetry treaty; the bridge only licenses a local comparison.

`external-correlation-bridge` means a CUDA/profiler activity can be joined to an external API, runtime phase, or application marker through an explicit correlation record or equivalent public join key.

`trace-context-bridge` means a service or request trace context is the public bridge. The trace id/span context links the replay work to a service operation, but it does not prove graph identity, resource lifetime, or locality lease unless those receipts are separately present.

`metric-exemplar-bridge` means a metric observation is linked to trace context through an exemplar or equivalent trace-bearing metric record. It can route from aggregate or sampled GPU telemetry back to an operation, but it cannot turn utilization or memory pressure into replay lineage.

`placement-scope-bridge` means the comparison is grounded in cluster placement, device identity, pod/workload identity, MIG/MPS or partition identity, or a bounded scheduling/resource window. It can say which device/workload window a claim concerns, but it does not settle profiler/runtime lineage by itself.

`missing-cross-observer-bridge` means no safe bridge has been established. The correct repair is to narrow the replay claim, mark the observer conflict, or add a bridge in a later pass rather than infer one from temporal proximity or dashboard similarity.

`mixed-cross-observer-bridge` means more than one bridge kind is materially present or the honest packet must preserve multiple partial joins without forcing one bridge to carry the whole claim.

## External-correlation vs trace-context vs metric-exemplar vs placement-scope vs missing vs mixed bridge

- Use `external-correlation-bridge` when the GPU-side record has an explicit join to an external API, phase, span surrogate, or application marker.
- Use `trace-context-bridge` when distributed trace context is the bridge between service work and replay work.
- Use `metric-exemplar-bridge` when a metric point or exemplar links telemetry back to a trace/span context.
- Use `placement-scope-bridge` when the decisive bridge is bounded placement, device, partition, pod, or workload scope.
- Use `missing-cross-observer-bridge` when the observers cannot be joined tightly enough for the claimed comparison.
- Use `mixed-cross-observer-bridge` when several bridge kinds are required or the bridge state is deliberately composite.

## Countermodels / probes

Countermodel one: a CUDA graph launch appears near a service span and near a DCGM utilization spike, but there is no external correlation record, trace-context binding, exemplar, or placement-scope statement. That is `missing-cross-observer-bridge`, not a lucky bridge.

Countermodel two: CUPTI external correlation links GPU work to an application phase, and the service trace also carries the same request id. If both are needed for the claim, the packet is `mixed-cross-observer-bridge` unless one bridge clearly owns the comparison.

Countermodel three: a Prometheus sample or DCGM dashboard shows GPU memory pressure for the right node, but no exemplar or trace link binds it to the replayed request. That may be useful external observation, but it is not `metric-exemplar-bridge`.

Countermodel four: a pod is scheduled on the expected GPU-bearing node and the device id matches the claim window, but graph ids and update deltas are absent. That is at most `placement-scope-bridge`; it cannot prove capture lineage.

## Design consequences

A bridge witness should name the bridge kind, the exact join key or scope key, the observer surfaces it joins, the conclusion it licenses, and the conclusion it still does not license. It should also carry a fail-closed repair: narrow the claim, split the packet, add a missing bridge, or leave the stronger telemetry-treaty move quarantined.

The compact bridge is a local join statement, not a new court. It does not require every replay claim to emit span escrow, trace-metric custody, or placement treaty records. It only prevents a future operator from silently relying on loose temporal adjacency, shared dashboards, or rich profiler output as if they were bridges.

## Overflow test

Promote a cross-observer bridge notary, exemplar escrow, placement treaty, or standing telemetry bridge only if several later revisions show that external-correlation, trace-context, metric-exemplar, placement-scope, missing, and mixed bridge tokens repeatedly fail to preserve honest replay comparisons. One missing exemplar, one loose trace id, or one pod/device mismatch is not enough.

## Transformer-facing implication

When a model sees GPU traces, service spans, and cluster metrics together, do not hallucinate a bridge from co-occurrence. Ask which public bridge, if any, joins the observers; preserve the missing-bridge state when the join is not present; and keep bridge authority narrower than replay truth.
