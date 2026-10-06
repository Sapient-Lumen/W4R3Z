# Storage-lane overload-governance model frontier

Current revision: rev0055

`StorageLaneOverloadGovernanceModelOracle` is a release-tier model surface for composed storage-lane overload histories. It sits above the older earned rungs:

- `WatermarkAdmissionController`
- `RetryBudgetAdmissionController`
- `CircuitBreakerBulkheadController`
- `ProviderResilienceHistoryRunner`
- `StorageLaneAdmissionHistoryRunner`
- `StorageLaneAdmissionHistoryModelOracle`

## Contract

The oracle observes an operation with:

```txt
input + real row + provider block count before/after + expected classes
```

It classifies the outcome:

- success;
- retry success;
- retry-budget rejection;
- retry-budget exhaustion;
- non-idempotent retry rejection;
- breaker rejection;
- bulkhead rejection;
- open-circuit rejection;
- admission watermark rejection;
- admission provider-health rejection;
- hard-limit rejection;
- critical bypass.

It then checks the invariants that matter before OPFS/browser spending:

```txt
admitted operations release admission leases;
rejected finals do not mutate provider block count;
expected outcome classes are present;
snapshot checks do not fail;
final admission/breaker/retry-budget accounting can be zeroed.
```

## Why it is separate from the admission model

`StorageLaneAdmissionHistoryModelOracle` primarily models the admission/backpressure layer. The rev0039 oracle looks at the composed gate chain and prevents future sessions from treating overload governance as one vague pass/fail outcome.

## Non-claims

- No OPFS storage-lane overload-governance model proof.
- No browser Worker storage-lane overload-governance model proof.
- No production overload-governance, retry-storm, circuit-breaker, bulkhead, retry-budget, storage-lane, or fairness claim.
- No wall-clock timer, throughput, latency, SLO, durability, fsync, quota, eviction, crash-recovery, or exactly-once delivery claim.
- No exhaustive model checking or formal verification claim.
- No cross-browser conformance claim.
- No WebGPU proof.


Current proof id: `scheduler:storage-lane-overload-governance-model-proof`.
