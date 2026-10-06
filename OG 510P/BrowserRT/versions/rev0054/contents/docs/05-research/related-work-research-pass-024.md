# Related-work research pass 024 — retry budgets and overload governance

Revision: rev0029

This pass asks what BrowserRT should steal before retry policy becomes dangerous. The answer is: retries are not a mere scheduler detail; they are an overload surface. A browser runtime that can schedule storage, workers, GPU, render, media, and mesh work must eventually govern retries with budget, idempotency, provider health, priority, and trace evidence.

## Sources and stolen ideas

- **Google SRE — Addressing Cascading Failures.** Steal the server-wide retry-budget lesson: once a retry budget is exhausted, stop retrying and fail fast. This is directly relevant to BrowserRT because local browser storage or worker providers can be overloaded by our own retries.
- **Google SRE — Handling Overload / client-side throttling.** Steal the per-request retry-budget pressure: a request should not fan out into unlimited attempts, especially when all providers are likely overloaded.
- **Envoy circuit breaking and retry budgets.** Steal the idea that retries need their own circuit breaker/budget, separate from primary request admission. Envoy frames retry budgets as concurrent retries relative to active/pending requests, with minimum retry concurrency.
- **Envoy transient failures and outlier detection.** Steal the distinction between retry policy, circuit breaking, outlier/provider health, and idempotency. BrowserRT must not retry non-idempotent work by default.
- **Kubernetes API Priority and Fairness.** Steal the flow-classification idea: one noisy retry source should not starve protected work. Retry budgets should eventually be per-flow/per-class, not one global bucket.
- **Resilience4j.** Steal the composition vocabulary: retry, circuit breaker, bulkhead, rate limiter, and timeout are separate policies that emit events and can be combined.

## BrowserRT translation

The first earned primitive is deliberately small:

```txt
RetryBudgetAdmissionController
```

It is not a production retry-budget algorithm. It is a fake-provider, release-tier proof surface that can reject retry attempts because:

```txt
provider unhealthy
non-idempotent operation
active retry limit exceeded
retry credit budget exhausted
```

It also allows an explicit `critical` bypass in the proof, but only as a traced policy decision. Future sessions should be suspicious of every bypass.

## Dreambank pressure

The long-run BrowserRT overload plane might include:

```txt
retry budget per provider
retry budget per flow
retry budget per priority class
retry budget per user-visible interaction
circuit breaker per lane
provider outlier/degraded state
adaptive retry dampening
hedging budget
retry-after provider hints
retry trace lineage
```

But every future claim must reduce to a primitive, a provider contract, a trace event, a manifest task, and a non-claim boundary.

## Non-claims

- No OPFS storage-lane retry-budget proof.
- No browser Worker storage-lane retry-budget proof.
- No retry-storm safety or production overload-governance claim.
- No exact Google SRE, Envoy, Kubernetes APF, Resilience4j, TCP, or circuit-breaker implementation claim.
- No wall-clock timer, throughput, latency, SLO, durability, or exactly-once delivery claim.
