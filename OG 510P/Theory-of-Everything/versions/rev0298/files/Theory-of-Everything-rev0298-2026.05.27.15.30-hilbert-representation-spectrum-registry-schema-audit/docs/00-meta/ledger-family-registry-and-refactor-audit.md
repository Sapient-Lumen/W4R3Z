# Ledger-family registry and rev0282 refactor audit

`LEDGER-FAMILY-REGISTRY.json` is the compact index of executable support-layer families. It records each layer family, its owning ledgers, route-row fields, open-question gate, and cardinality policy.

## rev0282 audit finding

The route rows had inherited overbroad composition/interface/global-consistency handles: every route referenced every composition row. The composition rows themselves were route-local, so this inflated dependency-graph edges and made route ownership less precise.

## repair

rev0282 narrows those fields to route-local-plus-wrapper ownership and adds a generated route-layer coverage audit to catch future regressions.
