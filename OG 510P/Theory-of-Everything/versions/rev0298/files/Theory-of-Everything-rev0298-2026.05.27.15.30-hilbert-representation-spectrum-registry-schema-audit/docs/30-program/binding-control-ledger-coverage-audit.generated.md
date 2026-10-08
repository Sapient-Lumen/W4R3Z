# Binding control-ledger coverage audit (generated)

Generated from `CLAIM-ROUTE-BINDING-LEDGER.json` plus `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing route-layer families or bindings.

- Registry revision: `rev0298`
- Registered layer families: `38`
- Claim-route binding rows: `42`
- Binding/family pairs checked: `359`
- Missing controlling-ledger cells: `0`

## Rule

If a binding row spends any registered route-layer field, or if it owns that layer family OQ, then the binding must list the family ledgers in `controlling_ledgers`. Empty route-layer fields are allowed; hidden controlling-ledger omissions are not.
