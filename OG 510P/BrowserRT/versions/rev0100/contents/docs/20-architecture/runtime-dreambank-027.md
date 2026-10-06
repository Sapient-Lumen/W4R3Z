# Runtime dreambank 027 — resilience policy machines

Carry-forward revision: rev0033.

Rev0032 imagines BrowserRT as a runtime that can place every overload/resilience policy behind three things:

1. a snapshot;
2. a reference model;
3. a trace history.

That is the stair between “nice-looking controller” and “runtime primitive future sessions can respect.”

## New dreambank vocabulary

```txt
policy machine       = a deterministic controller with acquire/release/advance/snapshot operations
lease gate           = a controller that admits work by issuing an explicit lease
reference model      = independent, simpler semantics used to check the real controller
history oracle       = deterministic generated operation stream plus post-step comparison
claim boundary       = explicit non-claims attached to proof artifacts and handoff docs
```

## Why this matters for BrowserRT

BrowserRT already has bounded channels, spill mailboxes, storage-lane schedulers, retry budgets, priority fairness, and resilience controllers. Those primitives will eventually interact. Without model oracles, future sessions will only have isolated examples and vibes.

The dream is to make every important provider/policy composable under a common evidence shape:

```txt
source primitive
  -> targeted proof
  -> generated model oracle
  -> contract audit
  -> provider integration
  -> provider model oracle
  -> explicit browser/OPFS/GPU proof only when earned
```

## Resilience composition frontier

A future BrowserRT provider call could run through a composed policy chain:

```txt
PriorityFairScheduler
  -> WatermarkAdmissionController
  -> AdaptiveConcurrencyController
  -> CircuitBreakerBulkheadController
  -> RetryBudgetAdmissionController
  -> StorageLaneRetryController
  -> StorageLaneExecutor
```

The dangerous version of this is a pile of coupled knobs. The disciplined version has every stage emit traces and every stage expose a cheap model/history proof.

## Current earned rung

Rev0032 adds the generated-history oracle for `CircuitBreakerBulkheadController`. It does not integrate it with the storage lane, OPFS, browser workers, or real timers.

## Non-claims

No OPFS, browser Worker, production resilience, formal verification, latency-SLO, throughput, or cross-browser claim is made by this dreambank pass.
