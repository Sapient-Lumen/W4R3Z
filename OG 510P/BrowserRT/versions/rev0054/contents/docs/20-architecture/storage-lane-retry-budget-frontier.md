# Storage-lane retry-budget frontier

Revision: rev0029

`StorageLaneRetryPolicy` decides whether an error class is retryable and when the next virtual-tick attempt should be ready. `RetryBudgetAdmissionController` decides whether the retry attempt is allowed to exist at all.

That split is intentional:

```txt
retry policy  = classification + attempt limit + delay
retry budget  = overload gate + idempotency + active retry limit + provider health
storage lane  = provider execution + mailbox mutation + trace evidence
```

## New runtime noun

```txt
RetryBudgetAdmissionController
```

It currently supports:

- retry credits;
- active retry limit;
- idempotency requirement;
- provider health gate;
- primary observation/refill;
- critical bypass under credit exhaustion;
- lease release accounting;
- trace events for acquire, reject, release, health, primary observation, and refill.

## StorageLaneRetryController integration

`StorageLaneRetryController` now accepts `retryBudget`. On a delayed retry becoming ready, it asks `tryAcquireRetry(...)` before scheduling the next attempt. If the gate rejects, the logical operation fails finally without scheduling another storage mutation.

This specifically protects the current fake-provider storage lane from the easiest self-inflicted failure mode: a retryable provider error creating endless or uncontrolled attempts.

## Trace events

Expected trace surface:

```txt
retry-budget:create
retry-budget:acquire
retry-budget:release
retry-budget:reject
retry-budget:provider-unhealthy
retry-budget:provider-healthy
retry-budget:primary-observed
retry-budget:refill
storage-retry:retry-budget-gate
storage-retry:retry-budget-release
```

## Future questions

- Should retry budgets be per-provider, per-lane, per-flow, per-priority, or all of those?
- How should retry credits interact with `AdaptiveConcurrencyController`?
- Should critical bypass consume a separate scarce budget?
- Should provider health be half-open/degraded rather than boolean?
- How should browser OPFS retry differ from fake-provider retry?

## Non-claims

- No OPFS storage-lane retry-budget proof.
- No browser Worker storage-lane retry-budget proof.
- No retry-storm safety or production overload-governance claim.
- No exact Google SRE, Envoy, Kubernetes, Resilience4j, TCP, or circuit-breaker implementation claim.
- No wall-clock timer, throughput, latency, SLO, durability, quota, eviction, crash-recovery, or exactly-once delivery claim.
