# Garden useful refusal and overload

Garden nodes are giving supernodes, not infinite sinks. A garden that cannot accept work should help by refusing predictably rather than vanishing or pretending success.

rev0011 has two garden surfaces:

```text
gardenrefusal.py  -> admission batches, family fairness, signed useful-refusal receipts
garden_churn.py   -> lookup events where gardens can return latest, stale, refusal, or drop
```

## Useful refusal

A useful refusal is:

```text
signed
fresh
bounded by retry hints
scoped to a request/service/target
local capacity evidence only
not proof that the target does not exist
not global reputation
```

## Admission guess

Garden work is scheduled with family-aware fairness. High-salience work such as witness queries and mutable-head watches can outrank bulk provider floods. A garden preserves resource budgets with explicit reasons:

```text
over_stream_budget
over_provider_budget
over_watch_budget
per_family_quota
unsupported_kind
expired_request
invalid_request
refusal_budget_exhausted
```

## Churn guess

A refusal in a mutable-head lookup is not stale data, and stale data is not a refusal. Keeping those event types distinct lets future lookup code ask better questions:

```text
Did we find the latest head?
Did enough independent families confirm it?
Did busy gardens give retryable capacity signals?
Did a path family return only stale heads?
```

The garden still does not become an authority. It gives capacity, receipts, cache, memory, and scheduling hints.
