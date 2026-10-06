# Provider-resilience model frontier

Current revision: rev0055

Manifest proof: `scheduler:provider-resilience-model-proof`.

`ProviderResilienceModelOracle` is a fake-provider reference model for the composed `ProviderResilienceHistoryRunner` stack.

## Implementation under test

```txt
ProviderResilienceHistoryRunner
  → StorageLaneExecutor
  → PersistedSpillMailbox
  → MemoryBlockStore provider
  → StorageLaneRetryPolicy
  → RetryBudgetAdmissionController
  → CircuitBreakerBulkheadController
```

## Reference model

```txt
ProviderResilienceModelOracle
  → ModelProvider
  → ModelRetryPolicy
  → ModelRetryBudget
  → ModelBreaker
```

The reference model is intentionally smaller than the implementation. It does not simulate OPFS, browser Workers, scheduler lane health, concurrent interleavings, or real time. It does model provider faults, retryable/non-retryable outcomes, operation-level max-attempt caps, retry-budget exhaustion, idempotency rejection, breaker open rejection, half-open recovery, and success/failure outcomes.

## Important refactor earned in rev0035

The model proof exposed an accounting bug. If a caller set `maxAttempts` lower than the retry policy's own `maxAttempts`, the runner could accept a retry-budget lease after the operation's last allowed attempt and then exit with the lease still active. Rev0034 makes the per-operation max-attempt cap authoritative before acquiring another retry lease.

## Non-claims

- No OPFS provider-resilience model proof.
- No browser Worker provider-resilience model proof.
- No true concurrent history proof.
- No linearizability or exhaustive model-checking proof.
- No production resilience, retry-storm safety, SLO, latency, throughput, durability, or exactly-once delivery claim.
