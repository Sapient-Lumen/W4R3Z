# Related-work research pass 030 — admission-governed storage histories

Current revision: rev0054

This pass asks what happens before the provider-resilience stack is even allowed to run. Rev0034 checked provider-resilience histories against a model. Rev0035 inserts a storage-lane admission gate in front of that stack and proves that overload, provider-health, hard-limit, and critical-bypass decisions are visible and no-mutation preserving.

## Ideas stolen

- **Envoy overload manager:** overload protection should be its own control plane, distinct from upstream circuit breaking. BrowserRT should distinguish local resource admission from provider failure gates.
- **Kubernetes API Priority and Fairness:** priority, queuing, rejection, and fairness need explicit policy surfaces rather than accidental queue behavior.
- **Reactive Streams backpressure:** backpressure belongs in the protocol. A rejected admission should be an observable outcome, not an invisible dropped task.
- **Bulkhead isolation:** resource pools should fail locally. Admission gates and breaker/bulkhead gates should keep their accounting separate.

## Earned baby rung

`StorageLaneAdmissionHistoryRunner` wraps `ProviderResilienceHistoryRunner` with a `WatermarkAdmissionController`. The new proof checks:

```txt
admit → provider-resilience success
admit → transient retry success
watermark reject → no provider mutation
critical bypass while congested → success
provider-health reject → no provider mutation
hard-limit reject → no provider mutation
all admitted operations release admission leases
```

## Non-claims

This does not prove OPFS, browser Worker behavior, real timers, crash recovery, quota, eviction, throughput, latency, fairness SLOs, production overload-governance, or exactly-once delivery.
