# rev0026 — lineagebundle-workmeter-fold

This revision keeps working risk-first on the DHT that lives above I2P. The theme is that signed observations can be valid and still be unsafe when they are advanced, bundled, or counted out of context.

New surfaces:

- `lineagewindow.py`: mutable-head lineage windows with missing-predecessor repair requests, same-sequence fork quarantine, scope-mix quarantine, and family-diverse direct advancement.
- `claimbundle.py`: typed evidence bundles that preserve scope, family diversity, and conflict checks before downstream work can consume them.
- `workmeter.py`: local garden contribution metering so useful refusals are visible but cannot become fake contribution health, payment, or authority.
- `lineagefold.py`: audit/refactor fold that pins rev0026 code, tests, docs, public pointers, and active surface-ledger entries.

Core rule:

```text
A signed latest pointer, a signed evidence bundle, and a signed useful refusal are still only typed local observations.
```

This revision remains a deterministic Python prototype. It does not implement live I2P/SAM transport, a production DHT, production authorization, production mutable-head consensus, private retrieval, global reputation, Sybil resistance, anonymity guarantees, or any application patch.
