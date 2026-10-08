# Claim-route binding normalization audit

rev0285 normalizes `CLAIM-ROUTE-BINDING-LEDGER.json` against `LEDGER-FAMILY-REGISTRY.json`. Every binding row now carries every registered route-layer field, even when the field is empty. This prevents late-added families from being invisible in binding rows.

The generated audit `docs/30-program/claim-route-binding-field-audit.generated.md` records the current binding-row count, registry-family count, route-field count, and missing-field total.
