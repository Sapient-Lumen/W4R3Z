# Route / binding schema array-type audit

This audit checks that every registered route-support handle field is represented as `type: array` with `items.type: string` in both `schemas/candidate-route-state-ledger.schema.json` and `schemas/claim-route-binding-ledger.schema.json`.

The audit is shape-control only. It prevents registered route-layer handles from drifting into untyped payloads, scalar strings, or mixed objects. It does not create scientific support.
