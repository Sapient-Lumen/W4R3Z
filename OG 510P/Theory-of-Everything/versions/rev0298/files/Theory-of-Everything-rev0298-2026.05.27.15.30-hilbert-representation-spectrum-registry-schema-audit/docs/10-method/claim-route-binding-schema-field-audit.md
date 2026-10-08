# Claim-route binding schema field audit

rev0296 adds a generated audit that compares `LEDGER-FAMILY-REGISTRY.json` with `schemas/claim-route-binding-ledger.schema.json`.

Every registered route-support field must be required in the claim-route binding row schema. This prevents a hidden validation gap where binding rows expose new route-layer handles but the schema does not require future binding rows to carry them.
