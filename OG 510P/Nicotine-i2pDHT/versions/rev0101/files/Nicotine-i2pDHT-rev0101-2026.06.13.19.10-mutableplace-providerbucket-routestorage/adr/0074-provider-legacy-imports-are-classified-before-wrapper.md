# ADR 0074 — Provider legacy imports are classified before wrapper

## Decision

Classify legacy `providerpoison.py` imports as historical or active before turning the module into a compatibility wrapper.

## Rationale

The cube intentionally kept old provider-poison behavior-pinning tests. Those imports should remain visible without being confused with new active callers.

## Consequence

`ProviderMigrationPlan` now reports historical and active import counts separately. The wrapper step remains future work.
