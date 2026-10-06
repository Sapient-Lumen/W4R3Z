# GPU replay observer-conflict witnesses, scope boundaries, correlation keys, intrusion shifts, authority gaps, and mixed conflict

This is the compact successor surface for `OQ-0167`.

## Practice / observation

`gpu_replay_trace_grade_state` keeps runtime self-attestation, profiler trace backing, external observation, missing trace receipts, and mixed trace grade distinct.  The next failure mode is not simply a richer trace.  It is an observer conflict: the runtime account, CUPTI or Nsight trace, and cluster or hardware monitor can each be locally honest while disagreeing because they saw different scopes, joined on different keys, changed the workload while observing it, or lacked authority over the branch being claimed.

A compact observer-conflict witness should classify the disagreement before the archive reaches for a telemetry court.  The question is: what kind of cross-observer mismatch is present, and what modest repair keeps the replay claim bounded?

## External pressure from CUPTI graph correlation, Nsight graph/node trace scope, DCGM exporter cluster metrics, and OpenTelemetry GPU metrics

CUPTI makes correlation powerful but not self-interpreting.  Its CUDA graph trace sample is explicitly about collecting CUDA graph traces and correlating graph-node launches back to node creation APIs, so correlation keys are real public evidence rather than merely operator lore.  `REF-1051`

Nsight Systems exposes a scope choice rather than a universal view.  CUDA graph tracing can be graph-level or node-level; graph-level collection omits node activities while node-level collection may add significant runtime overhead.  That creates both scope-boundary and intrusion-shift pressure.  `REF-1052`

DCGM-exporter gives an external monitoring lane: it gathers GPU metrics through DCGM and exposes them at an HTTP endpoint for Prometheus-style monitoring.  That can corroborate activity, saturation, memory pressure, and cluster context, but it is not the same authority as a graph-lineage trace.  `REF-1053`

OpenTelemetry's GPU metric semantic conventions add a cross-stack naming layer for GPU hardware metrics.  That standardizes observation vocabulary while still remaining metric observation, not replay receipt authority.  `REF-1054`

## Working synthesis

Use `gpu_replay_observer_conflict_state` only when a GPU replay receipt or trace-grade packet faces a material disagreement among observers.  Ordinary single-observer evidence remains under `gpu_replay_trace_grade_state`; same-envelope classification remains under `gpu_replay_envelope_state` or `gpu_replay_receipt_state`.

`scope-boundary-conflict` means the observers covered different objects, times, processes, graph granularity, nodes, pods, contexts, streams, or hardware slices.  The disagreement is primarily about what was inside the observation envelope.

`correlation-key-conflict` means the observers plausibly saw overlapping work but cannot be joined cleanly because graph ids, node ids, correlation ids, context/stream ids, process ids, pod labels, device ids, MIG/MPS partitions, or timestamps do not line up tightly enough for the claim.

`intrusion-shift-conflict` means the act of observation likely changed the workload, timing, scheduling, or replay envelope.  A node-level profiler run, callback-heavy trace, metric-sampling mode, or diagnostic wrapper may be useful evidence while no longer matching the low-intrusion run being explained.

`authority-gap-conflict` means no observer owns the disputed conclusion: the runtime can attest local handles, a profiler can report trace events, an external monitor can report hardware or cluster metrics, but none of them alone has authority to prove the replay branch now being claimed.

`mixed-observer-conflict` means more than one conflict source is materially present or the archive must preserve a deliberate multi-observer conflict packet without over-selecting one cause.

## Scope-boundary vs correlation-key vs intrusion-shift vs authority-gap vs mixed observer conflict

- Use `scope-boundary-conflict` when the disagreement comes from different observation envelopes.
- Use `correlation-key-conflict` when overlapping observations cannot be safely joined by public keys or timestamps.
- Use `intrusion-shift-conflict` when the instrumentation or monitoring path changes the run enough that the observed branch may not be the branch being claimed.
- Use `authority-gap-conflict` when each observer is locally relevant but none has authority over the asserted replay conclusion.
- Use `mixed-observer-conflict` when several of the above are load-bearing or the honest packet must keep them bundled.

## Countermodels / probes

Countermodel one: the runtime says a graph exec was updated and launched, while Nsight was configured only at graph granularity.  If the disputed claim depends on node-level update identity, the conflict is a scope-boundary conflict, not proof that either observer lied.

Countermodel two: CUPTI graph activity and DCGM utilization refer to the same time window, but context/stream, device, pod, and timestamp joins are too loose for a lineage claim.  That is a correlation-key conflict until a tighter join key is added.

Countermodel three: a node-level trace changes timing enough that an external monitor reports a different saturation pattern than the unprofiled run.  That is an intrusion-shift conflict, not an excuse to discard profiler evidence wholesale.

Countermodel four: runtime logs, profiler traces, and external metrics are all present, but the claim asks whether same-envelope replay, resource lifetime, and locality lease were preserved.  If no observer carries all three, the conflict is an authority-gap conflict.

## Design consequences

Attach observer-conflict classification only after a trace-grade packet would otherwise be ambiguous.  The witness should name the observed scopes, join keys, intrusion budget, authority limit, and fail-closed repair.  It should not create a standing telemetry court for every GPU replay claim.

For small archives, the high-leverage repair is usually narrower prose: say which observer supports which branch, which join is missing, and which conclusion is not licensed.  Promote stronger bridge machinery only when the same conflict pattern repeatedly blocks compact replay receipts.

## Overflow test

Promote cross-observer span escrow, GPU telemetry treaty, or correlation-futures machinery only if several future revisions show that scope-boundary, correlation-key, intrusion-shift, authority-gap, and mixed tokens repeatedly fail to route live GPU replay conflicts.  One Nsight/CUPTI mismatch, one DCGM dashboard discrepancy, or one missing correlation id is not enough.

## Transformer-facing implication

When a model sees multiple telemetry sources, do not reward fluent majority vote.  Ask whether the disagreement is about scope, join keys, observer intrusion, authority, or mixture.  Treat the richest trace as evidence, not automatic precedence.
