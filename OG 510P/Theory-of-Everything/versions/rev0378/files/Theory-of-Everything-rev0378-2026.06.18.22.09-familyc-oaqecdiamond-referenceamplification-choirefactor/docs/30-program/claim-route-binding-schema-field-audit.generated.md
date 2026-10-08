# Claim-route binding schema field audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/claim-route-binding-ledger.schema.json`. Do not edit directly; run `make index` after changing route-layer families or the binding schema.

- Registry revision: `rev0378`
- Registered layer families: `54`
- Registered route fields checked: `159`
- Missing binding-schema required fields: `0`

## Rule

Every registered route-support field should appear in the claim-route binding row `required` list. Missing fields indicate schema drift: claim-route binding rows may expose handles without requiring future rows to preserve them.
