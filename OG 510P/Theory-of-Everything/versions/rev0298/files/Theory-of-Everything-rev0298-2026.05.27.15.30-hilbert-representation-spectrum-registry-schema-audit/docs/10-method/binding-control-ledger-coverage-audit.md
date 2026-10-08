# Binding control-ledger coverage audit

rev0285 normalized binding-row fields. rev0286 adds the complementary audit: a binding row that spends a registered route-layer field, or that owns the OQ gate for a registered family, must list that family's controlling ledgers in `controlling_ledgers`.

This prevents a subtle failure mode:

```text
new support layer added
+ binding rows expose the new field
+ binding spends nonempty row IDs
+ controlling_ledgers omits the owning ledger
= hidden authority-propagation gap
```

The generated audit is `docs/30-program/binding-control-ledger-coverage-audit.generated.md`.
