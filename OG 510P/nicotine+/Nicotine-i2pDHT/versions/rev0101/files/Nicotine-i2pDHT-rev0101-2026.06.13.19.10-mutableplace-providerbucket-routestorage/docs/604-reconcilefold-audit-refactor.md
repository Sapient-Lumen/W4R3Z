# Reconcilefold audit/refactor

`reconcilefold.py` pins the rev0057 current path:

```text
src/i2p_dht_lab/deadletter.py
src/i2p_dht_lab/retryquorum.py
src/i2p_dht_lab/effectreconcile.py
src/i2p_dht_lab/reconcilefold.py
tests/test_rev0057_deadletter_retry_reconcile.py
```

It also calls the rev0056 `recoveryfold` predecessor audit, the declarative fold map, fold registry, and active surface ledger.

The audit/refactor move this turn is modest but important: the previous recovery/cleanup surfaces now lead into a named dead-letter/retry/reconcile path rather than a loose next-step promise.
