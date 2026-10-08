# Registered dependency-edge coverage audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json`, `CANDIDATE-ROUTE-STATE-LEDGER.json`, and `AUTHORITY-DEPENDENCY-GRAPH.json`. Do not edit directly; run `make index` after changing route-support handles or dependency graph generation.

- Registry revision: `rev0378`
- Registered layer families: `54`
- Route rows: `13`
- Route-local handle edges checked: `3822`
- Dependency edge coverage failures: `0`

## Rule

Every nonempty handle in every `route-local-plus-wrapper` route field must have a corresponding source-kind/source-id → route edge in `AUTHORITY-DEPENDENCY-GRAPH.json`. This keeps rollback and authority propagation attached to route handles instead of relying on schema presence alone.

