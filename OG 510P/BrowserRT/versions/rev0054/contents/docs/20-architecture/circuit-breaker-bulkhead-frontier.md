# Circuit-breaker and bulkhead frontier

Revision: rev0031

## Runtime noun

```txt
CircuitBreakerBulkheadController
```

It is a fake-provider/virtual-tick resilience governor. It combines two separable controls:

- **Circuit breaker:** decides whether calls should be attempted based on recent outcomes.
- **Bulkhead:** bounds concurrent in-flight calls.

## Contract

Public surface:

```ts
const c = createCircuitBreakerBulkheadController({
  maxConcurrent: 2,
  slidingWindowSize: 4,
  minimumCalls: 4,
  failureRateThreshold: 50,
  slowCallRateThreshold: 50,
  slowCallDurationTicks: 5,
  openDurationTicks: 3,
  halfOpenMaxCalls: 2
})

const lease = c.tryAcquire({ opId: 'write-1', priority: 'user-visible' })
c.release(lease, { ok: true, durationTicks: 1 })
c.advanceTicks(3)
```

State machine:

```txt
closed
  ├─ failure/slow threshold -> open
  └─ manual force          -> forced-open
open
  └─ virtual open duration -> half-open
half-open
  ├─ enough successful probes -> closed
  └─ failed probe             -> open
```

Bulkhead invariant:

```txt
active <= maxConcurrent
leaseCount == active
rejected acquisition does not mutate active or leaseCount
```

## Trace events

Required baby events:

```txt
resilience:create
resilience:acquire
resilience:release
resilience:reject
resilience:window-record
resilience:state-transition
resilience:tick
resilience:half-open-probe-success
```

## Non-claims

- No OPFS circuit-breaker/bulkhead proof.
- No browser Worker circuit-breaker/bulkhead proof.
- No wall-clock timer semantics.
- No production resilience, latency-SLO, retry-storm-safety, or overload-governance claim.
- No exact Resilience4j, Hystrix, Envoy, Azure, or SRE implementation claim.
