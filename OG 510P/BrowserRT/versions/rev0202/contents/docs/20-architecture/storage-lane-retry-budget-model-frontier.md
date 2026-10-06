# Storage-lane retry-budget model frontier

Revision: rev0031

## Why this frontier exists

Retry-budget vocabulary is dangerous. It sounds mature and production-grade before the project has earned enough evidence. The rev0031 frontier adds a retry-budget model/history oracle so future sessions can see whether budget state transitions remain coherent under generated command sequences.

## New primitive surface

```txt
validateRetryBudgetAdmissionSnapshot(snapshot)
```

This validator checks basic invariant pressure:

- retry credits stay between configured bounds;
- active retries match lease count;
- active retries do not exceed max active retries;
- lease ids are unique;
- primary success/failure stats reconcile;
- released retries never exceed accepted retries;
- provider health is explicit.

## Model-walk contract

The proof executes deterministic generated histories against:

```txt
real RetryBudgetAdmissionController
reference RetryBudgetModel
snapshot validator
```

The test compares real and model snapshots after every generated operation. It also forces targeted observations for active-limit rejection, budget exhaustion, non-idempotent rejection, provider-health rejection, critical bypass, primary refill, unknown release, and no lease growth on rejection.

## Why fake-provider first

This slice is intentionally fake-provider and release-tier. The point is to harden policy accounting before OPFS, browser Worker, wall-clock timer, and provider-integration costs enter the loop.

## Non-claims

- No OPFS retry-budget model proof.
- No browser Worker retry-budget model proof.
- No production retry-storm safety claim.
- No exhaustive model checking or formal verification claim.
- No wall-clock timer, throughput, latency, fairness, or SLO claim.
- No exactly-once delivery claim.
- No durability, fsync, quota, eviction, or crash-recovery claim.
- No cross-browser conformance claim.
