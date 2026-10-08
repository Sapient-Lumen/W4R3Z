# Ledger-family registry schema audit

This audit checks that the registry that owns the route-support stack is itself schema-disciplined.

Every `LEDGER-FAMILY-REGISTRY.json` row must expose the same minimum envelope: family id, introduced revision, ledger files, schema files, route fields, owning open question, cardinality policy, maximum route-field cardinality, generated summary path, and audit note. The schema must require and declare those fields. The generated audit exists because a missing registry field can hide a late-added route-support family from summary, binding, gate, or cardinality audits.
