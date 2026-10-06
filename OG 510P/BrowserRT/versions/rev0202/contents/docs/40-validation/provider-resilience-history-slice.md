# Validation slice — scheduler:provider-resilience-history-proof

Carry-forward revision: rev0033

## Purpose

Prove `ProviderResilienceHistoryRunner` as one cheap fake-provider composition slice before OPFS/browser/provider spending. The slice asks whether the recently added governors can produce coherent histories when used together:

```txt
StorageLaneExecutor
+ PersistedSpillMailbox
+ MemoryBlockStore fake provider
+ StorageLaneRetryPolicy
+ RetryBudgetAdmissionController
+ CircuitBreakerBulkheadController
```

## Command

```bash
node tools/provider_resilience_history_probe.mjs --json artifacts/validation/REV0044-PROVIDER-RESILIENCE-HISTORY-PROBE.json
```

## Required observations

- transient retry succeeds after injected provider failure;
- retry budget is acquired before retry execution;
- provider failure is observed and traced;
- circuit opens after failures;
- open-circuit rejection causes no provider mutation;
- half-open recovery closes the circuit;
- retry-budget rejection stops retry;
- bulkhead rejection causes no provider mutation;
- generated histories include both success and failure outcomes;
- snapshot validation passes;
- final lease accounting is empty;
- required trace event families are present.

## Non-claims

- No OPFS provider-resilience proof.
- No browser Worker provider-resilience proof.
- No production resilience or retry-storm safety claim.
- No wall-clock timer, throughput, latency, fairness, SLO, durability, fsync, quota, eviction, crash-recovery, exactly-once, cross-browser, or WebGPU claim.
