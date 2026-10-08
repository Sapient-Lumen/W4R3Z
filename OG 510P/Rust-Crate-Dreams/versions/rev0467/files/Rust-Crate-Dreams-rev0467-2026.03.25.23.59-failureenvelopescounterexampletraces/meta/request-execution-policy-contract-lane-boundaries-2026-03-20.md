# Request Execution Policy Contract Kit — lane boundaries (2026-03-20)

**P-0530** is about the receiver-facing support contract for one request’s replay, budget, admission, and attempt topology.

It answers questions like:

- Why is replay safe?
- How many attempts can happen, under what budget and timeout shape?
- Does admission wait, queue, limit, shed, or reject?
- Are attempts serial retries or parallel hedges?

## It is not:

### Not `channel-surface-contract-kit`
That lane is about message-passing primitives: buffers, overflow, delivery meaning, and shutdown/drain truth for channels.
**P-0530** is about one request/call path through retries, deadlines, quotas, hedges, and admission control.

### Not `crate-lifecycle-surface-pack-kit`
That lane is about stop verbs, activation boundaries, shutdown phases, and timeout aftermath for background work.
**P-0530** is about execution policy while a request is being attempted.

### Not `crate-observability-surface-pack-kit`
That lane is about telemetry activation, route truth, and delivery/completeness posture.
**P-0530** is about whether the request itself is retried, hedged, delayed, or rejected.

### Not `crate-resource-surface-pack-kit`
That lane is about queues, pools, caches, threads, and saturation evidence more broadly.
**P-0530** is narrower: the receiver-facing request path through buffering/limits/retries/hedges.

### Not another middleware crate
Tower, `reqwest`, `reqwest-retry`, `governor`, `tonic`, and resilience suites already provide execution primitives.
**P-0530** publishes the support contract above them.

### Not a general circuit-breaker / bulkhead catalog
Those may be adjacent import lanes later, but **P-0530** does not aim to be a full resilience-pattern encyclopedia.
