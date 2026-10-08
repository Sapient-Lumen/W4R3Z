# Registered artifact-reference integrity audit (generated)

Generated from path-like references in executable JSON surfaces. Do not edit directly; run `make index` after changing registered ledgers, schemas, generated summaries, owner surfaces, or controlling ledgers.

- Registry revision: `rev0378`
- Registered layer families: `54`
- Artifact/path references checked: `6472`
- Unknown artifact/path references: `0`

## Rule

Path-like archive references in registered ledger families, route rows, and claim-route bindings must resolve to actual files in the package. This catches stale ledger, schema, owner-surface, generated-summary, and controlling-ledger paths that ID audits cannot see.

