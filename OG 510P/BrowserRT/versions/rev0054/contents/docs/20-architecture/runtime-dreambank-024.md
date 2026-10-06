# Runtime dreambank 024 — retry-budget office

Revision: rev0029

BrowserRT's retry lane now has a new dream: retries should be explicit citizens of the runtime's overload-governance plane.

A future BrowserRT task should carry enough metadata for the runtime to ask:

```txt
Is this operation idempotent?
Is this a retry or a primary attempt?
Which provider/lane owns the retry?
Which priority class and flow owns the work?
How many retry credits remain?
How many active retries are already in flight?
Is the provider healthy, degraded, or ejected?
Will retrying preserve the user's current interaction or amplify overload?
```

Rev0029 implements only the smallest fake-provider rung:

```txt
RetryBudgetAdmissionController
StorageLaneRetryController + retryBudget gate
scheduler:storage-lane-retry-budget-proof
facility:storage-lane-retry-budget-contract-audit
```

## One-runtime ambition

A one-to-rule-them-all BrowserRT could unify these policies:

```txt
WatermarkAdmissionController
AdaptiveConcurrencyController
PriorityFairScheduler
CrossLaneScheduler
StorageLaneRetryController
RetryBudgetAdmissionController
```

The ambition is a single overload office where admission, fairness, retry, provider health, and traces share vocabulary. The danger is overclaiming. Rev0029 therefore stays fake-provider, virtual-tick, and browser-light.

## Future primitives to consider

- `RetryClass`: primary, retry, hedge, replay, maintenance.
- `RetryLineage`: parent attempt, child retry, provider, cause, deadline.
- `BudgetPool`: credits by provider/flow/priority.
- `CircuitState`: closed, open, half-open, degraded.
- `RetryHint`: provider says retry-after, do-not-retry, degraded, backoff.
- `OverloadTrace`: one tree spanning scheduler, storage, retry, budget, and provider health.

## Non-claims

Rev0029 does not prove production overload control. It proves a tiny, deterministic retry-budget gate that future sessions can respect and extend.
