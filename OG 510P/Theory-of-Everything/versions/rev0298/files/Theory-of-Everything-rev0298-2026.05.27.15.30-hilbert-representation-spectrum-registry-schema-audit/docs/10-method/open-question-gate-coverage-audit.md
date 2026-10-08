# Open-question gate coverage audit

This audit closes a registry-maintenance gap.

Each registered route-support family in `LEDGER-FAMILY-REGISTRY.json` names an owning open question. That OQ must be registered in `docs/20-constitution/open-question-registry.md`, must have a claim-route binding row in `CLAIM-ROUTE-BINDING-LEDGER.json`, and that binding must list the family ledgers in `controlling_ledgers`.

The generated audit surface is:

`docs/30-program/open-question-gate-coverage-audit.generated.md`

This is not a promotion surface. It only prevents a new support layer from existing without a visible OQ gate.
