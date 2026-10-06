# Related-work research pass 028 — provider-integrated resilience histories

Carry-forward revision: rev0033

This pass treats BrowserRT resilience as a **composition problem** rather than as another isolated controller. The recent rungs already have storage-lane scheduling, retry policy, retry budgets, circuit breakers, bulkheads, persisted-spill delivery, and model/history checks. The new question is whether future sessions can reason about these governors when they run together.

## Ideas stolen

- **Resilience4j decorator composition.** Resilience4j presents circuit breaker, retry, rate limiter, bulkhead, time limiter, and cache as separate decorators that can be stacked. BrowserRT should steal the separation, not the exact API: retry, retry-budget, bulkhead, circuit, and storage-provider health should be individually inspectable, traceable, and testable.
- **Resilience4j event streams.** Its components emit events. BrowserRT should make that mandatory: provider-governor composition without trace events is not acceptable.
- **Envoy retry budget + circuit breaking.** Envoy explicitly treats retry budgets and circuit breakers as related overload controls. BrowserRT should keep retry budget and circuit-breaker state in the same proof history when validating provider resilience.
- **Google SRE cascading-failure guidance.** Retrying through overload can amplify failure. BrowserRT should assume retry is dangerous until admitted by budget, provider health, idempotency, and circuit/bulkhead gates.
- **Temporal retry policy.** Retry policy is a named contract that decides when and how to try again. BrowserRT should keep retry policy deterministic in fake-provider proofs before real timers or OPFS/browser providers enter.

## What this pass adds

Rev0033 adds `ProviderResilienceHistoryRunner`: a fake-provider, virtual-tick history runner that composes:

```txt
StorageLaneExecutor
+ PersistedSpillMailbox
+ MemoryBlockStore fake provider
+ StorageLaneRetryPolicy
+ RetryBudgetAdmissionController
+ CircuitBreakerBulkheadController
```

The goal is not a production resilience algorithm. The goal is an earned proof surface where future sessions can see how these primitives interact under transient provider failure, open-circuit rejection, retry-budget exhaustion, bulkhead saturation, half-open recovery, and generated deterministic histories.

## What remains deliberately unearned

- No OPFS provider-resilience proof.
- No browser Worker provider-resilience proof.
- No production resilience, retry-storm, circuit-breaker, bulkhead, retry-budget, storage-lane, or overload-governance claim.
- No wall-clock timer, latency, throughput, fairness, SLO, durability, fsync, quota, eviction, crash-recovery, or exactly-once claim.
- No exhaustive model checking or formal verification claim.
