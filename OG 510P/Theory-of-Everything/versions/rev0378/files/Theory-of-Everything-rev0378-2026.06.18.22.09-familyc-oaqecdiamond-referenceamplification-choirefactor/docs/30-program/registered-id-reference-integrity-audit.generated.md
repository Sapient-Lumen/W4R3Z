# Registered ID-reference integrity audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json`, registered executable ledgers, bibliography, and constitutional registries. Do not edit directly; run `make index` after changing executable ledger references.

- Registry revision: `rev0378`
- Registered layer families: `54`
- ID-like references checked: `93026`
- Unknown ID references: `0`

## Rule

Every ID-like value in registered ledger list fields must resolve to a known route-support row, core ledger row, bibliography REF id, claim id, or open-question id. This catches stale handles that schema shape alone cannot detect.

