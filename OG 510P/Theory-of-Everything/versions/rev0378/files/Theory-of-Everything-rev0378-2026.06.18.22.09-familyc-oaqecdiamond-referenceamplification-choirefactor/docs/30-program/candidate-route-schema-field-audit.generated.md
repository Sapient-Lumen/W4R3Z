# Candidate-route schema field audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/candidate-route-state-ledger.schema.json`. Do not edit directly; run `make index` after changing route-layer families or the route schema.

- Registry revision: `rev0378`
- Registered layer families: `54`
- Registered route fields checked: `159`
- Missing schema-required route fields: `0`

## Rule

Every registered route-support field should appear in the route-row `required` list of `schemas/candidate-route-state-ledger.schema.json`. Missing fields indicate schema drift: route authority handles may exist in prose or ledgers without being schema-required.
