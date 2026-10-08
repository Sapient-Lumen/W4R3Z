# Namespace-fold audit/refactor

`namespacefold.py` is a small audit/refactor surface for rev0023. It checks that the active namespace/admission/range surfaces exist, are listed in the active surface ledger, and are visible from the docs index.

This keeps the cube from growing invisible tendrils. Historical surfaces stay preserved for wake-from-amnesia; active surfaces must be navigable.

The audit is intentionally narrow. It is not package validation and not a proof of protocol correctness. It answers a simpler question:

```text
Can a future maintainer find the current rev0023 namespace/range/admission work from the cube surface?
```
