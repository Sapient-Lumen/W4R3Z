# rev0058 — finalityledger-retryescrow-pruneguard

This revision moves one seam beyond rev0057 dead-letter / retry-quorum / effect-reconcile work.

```text
effect reconcile accepted
+ retry/dead-letter memory exists
    ≠ terminal local truth
    ≠ safe retry rerun
    ≠ safe evidence deletion
```

The new risk-first surfaces are:

- `finalityledger.py` — signed finality markers after reconcile.
- `retryescrow.py` — retry tickets that must carry dead-letter lineage and exact idempotency.
- `pruneguard.py` — explicit evidence-deletion boundary for terminal versus pending effects.
- `finalityfold.py` — current-path audit preserving `reconcilefold` as predecessor history.

Strong sentence:

```text
Finality, retry, and pruning are separate local permissions; none may launder unresolved dead-letter memory into terminal truth.
```

This is still no-network DHT design algebra. It performs no I2P/SAM side effects, publishes no DHT records, and does not claim production persistence.
