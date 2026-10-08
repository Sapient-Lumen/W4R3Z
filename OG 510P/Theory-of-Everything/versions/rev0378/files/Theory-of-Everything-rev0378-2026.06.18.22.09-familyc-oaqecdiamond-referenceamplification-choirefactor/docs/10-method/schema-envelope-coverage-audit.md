# Schema-envelope coverage audit

The schema-envelope audit checks whether registered route-support families expose their ledgers, schemas, generated summaries, row keys, and basic JSON envelope fields consistently.

Generated surface:

- `docs/30-program/schema-envelope-audit.generated.md`

The audit is not a scientific result. It is a restart-quality guard against adding a ledger family whose schema or summary has drifted out of sync with the registry.
