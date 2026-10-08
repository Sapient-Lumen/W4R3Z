# Route / binding schema array-type audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json`, `schemas/candidate-route-state-ledger.schema.json`, and `schemas/claim-route-binding-ledger.schema.json`. Do not edit directly; run `make index` after changing route-layer fields or schemas.

- Registry revision: `rev0378`
- Registered layer families: `54`
- Registered route fields checked: `159`
- Array-type property failures: `0`

## Rule

Every registered route-support field must be a schema property with `type: array` and `items.type: string` in both candidate-route rows and claim-route binding rows. Route-layer handles are lists of stable IDs, not untyped JSON payloads.
