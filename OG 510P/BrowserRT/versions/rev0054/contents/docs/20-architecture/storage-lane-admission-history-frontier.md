# Storage-lane admission history frontier

Current revision: rev0054

Manifest proof: `scheduler:storage-lane-admission-history-proof`.

`StorageLaneAdmissionHistoryRunner` composes:

```txt
WatermarkAdmissionController
  → ProviderResilienceHistoryRunner
    → StorageLaneExecutor
    → PersistedSpillMailbox
    → MemoryBlockStore provider
    → StorageLaneRetryPolicy
    → RetryBudgetAdmissionController
    → CircuitBreakerBulkheadController
```

The admission gate is intentionally separate from retry-budget admission and circuit-breaker/bulkhead gates. Its job is local resource admission: bytes, congestion, provider-health flag, critical bypass, hard limit, and release accounting.

## Contract shape

Every operation should end in one of two broad classes:

```txt
admission rejected
  → no provider mutation
  → no resilience attempt
  → trace explains why

admission accepted
  → provider-resilience runner executes
  → admission lease releases exactly once
  → trace binds admission row to final outcome
```

## Why this is not production admission control

The rev0035 controller uses deterministic byte watermarks and fake-provider histories. It does not perform adaptive latency control, wall-clock scheduling, multi-tenant fairness, OPFS quota enforcement, browser Worker coordination, or real overload prediction.

## Non-claims

- No OPFS storage-lane admission-history proof.
- No browser Worker storage-lane admission-history proof.
- No production overload-governance, retry-storm safety, fairness, throughput, latency, SLO, durability, or exactly-once delivery claim.
- No exhaustive model checking or formal verification claim.

Rev0036 note: the generated model-oracle extension is `StorageLaneAdmissionHistoryModelOracle`, proved by `scheduler:storage-lane-admission-model-proof`; this does not replace the targeted history proof.
