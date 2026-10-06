# GPU replay trace-grade witnesses, self-attestation, profiler trace, external observer, and missing receipt

This is the compact successor surface for `OQ-0166`.

## Practice / observation

`gpu_replay_receipt_state` says what kind of public receipt carries a same-envelope GPU replay claim.  The remaining failure mode is trace-grade inflation: a runtime log, CUPTI correlation, Nsight report, or cluster metric starts being treated as if it were an impartial notary.

A trace-grade witness should be smaller than a flight recorder.  It classifies the evidence grade around a replay receipt, not the truth of the replay itself.  The useful question is: who or what made the receipt visible, with what scope boundary, and what still remains unobserved?

## External pressure from CUDA graph updates, CUPTI graph correlation, Nsight trace scope, DCGM monitoring, and OpenTelemetry GPU metrics

CUDA graph update semantics leave a runtime-level self-attestation lane: an application can name capture, instantiation, update, and launch facts, but that local account is still the runtime's own story about the replay path.  `REF-1041`

CUPTI makes graph correlation concrete.  It can collect CUDA graph traces, attach graph and graph-node identifiers to GPU activity, issue callbacks around graph operations, and correlate graph-node launch back to creation APIs.  The `CUpti_ActivityGraphTrace` record also names correlation id, start/end timestamps, device, graph, context, and stream, while allowing missing timestamps.  That is trace-backed evidence, not omniscience.  `REF-1046`, `REF-1047`

Nsight Systems exposes a different profiler grade.  Its CUDA graph trace setting can collect either graph-level or node-level information, and node-level tracing can add significant overhead; system-wide/process-tree scope and API-trace settings also make the trace boundary explicit.  A report can therefore be strong evidence while still being scoped, intrusive, or intentionally incomplete.  `REF-1048`

DCGM and dcgm-exporter add an external-observer lane: cluster or datacenter monitors can continuously collect device-level profiling metrics and expose GPU metrics to monitoring systems without relying on the workload's own replay receipt.  OpenTelemetry GPU metric conventions add a cross-stack naming pressure for hardware GPU metrics, but those metrics are status/usage observations rather than graph-lineage receipts.  `REF-1049`, `REF-1050`

## Working synthesis

Use `gpu_replay_trace_grade_state` when the archive already has a GPU replay receipt but must say how trace-visible that receipt is without pretending telemetry equals truth.

`runtime-self-attested` means the receipt is carried by application/runtime-visible handles, logs, update results, graph ids, launch paths, or local invariants.  This is useful but interested testimony.

`profiler-trace-backed` means CUPTI, Nsight Systems, or an equivalent profiler produced trace evidence with explicit graph/node/API/memory/correlation scope.  This is stronger than self-attestation but still bounded by collection scope, overhead, sampling, and tool configuration.

`external-observer-backed` means out-of-process monitoring, scheduler-side telemetry, DCGM/DCGM-exporter style metrics, cluster logs, or standardized hardware metrics corroborate a replay or resource claim from outside the application path.  This can catch externality and contention signals, but usually does not prove graph lineage or update identity.

`missing-trace-receipt` means the replay receipt is asserted or inferred but no adequate trace-grade evidence is present for the claim currently being made.

`mixed-gpu-replay-trace-grade` means more than one trace grade is materially involved or the receipt packet deliberately combines self-attestation, profiler traces, and external observation.

## Runtime self-attested vs profiler-trace-backed vs external-observer-backed vs missing trace receipt vs mixed GPU replay trace grade

- Use `runtime-self-attested` when the live evidence is the application's own replay/update/log account.
- Use `profiler-trace-backed` when a profiler trace with explicit CUDA graph, node, API, memory, or correlation scope carries the claim.
- Use `external-observer-backed` when cluster, datacenter, scheduler, DCGM, exporter, or standardized hardware metrics corroborate the replay condition from outside the application.
- Use `missing-trace-receipt` when the archive lacks adequate trace-grade evidence for the asserted replay receipt.
- Use `mixed-gpu-replay-trace-grade` when an honest packet needs several grades or the decisive ambiguity is cross-grade conflict.

## Countermodels / probes

Countermodel one: a runtime log says the graph was replayed, but no profiler or external trace is present.  That is `runtime-self-attested`, not `profiler-trace-backed`.

Countermodel two: Nsight or CUPTI shows graph activity, but the collection is graph-level only while the claim depends on node-level update identity.  The trace is useful but may be `missing-trace-receipt` for the decisive branch or `mixed-gpu-replay-trace-grade` if it must be paired with a runtime update receipt.

Countermodel three: DCGM shows GPU activity and memory pressure during the run.  That can support `external-observer-backed` contention or usage claims, but it does not by itself prove capture lineage, node update, or resource lifetime.

Countermodel four: the absence of trace is treated as proof that replay failed.  That is also overclaiming.  `missing-trace-receipt` records the evidence gap, not a negative replay verdict.

## Design consequences

Trace-grade classification should be attached only when trace visibility changes the replay claim.  The archive should not require a profiler run for every compact receipt, and it should not let a profiler screenshot replace the receipt family, resource-lifetime branch, locality lease, or performance-shadow source.

A useful replay packet now has three separable questions: what replay envelope is claimed, what public receipt carries it, and what trace grade supports or fails to support that receipt.

## Overflow test

Promote flight-recorder, trace-escrow, or cross-observer adjudication machinery only if several future revisions produce irreducible conflicts among runtime self-attestation, profiler traces, and external observation that the compact trace-grade tokens cannot route.  One missing graph trace, one rich Nsight report, or one DCGM dashboard is not enough.

## Transformer-facing implication

When a model argues from telemetry, ask whether it is reading self-attestation, profiler trace, external observation, or an evidence gap.  Do not silently convert trace presence into truth, trace absence into falsity, or external metrics into graph-lineage receipts.
