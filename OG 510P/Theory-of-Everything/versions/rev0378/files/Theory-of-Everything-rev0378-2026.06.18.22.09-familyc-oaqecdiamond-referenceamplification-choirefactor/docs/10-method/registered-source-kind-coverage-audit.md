# Registered source-kind coverage audit

This audit checks that every `route-local-plus-wrapper` ledger family in `LEDGER-FAMILY-REGISTRY.json` has corresponding source-kind coverage in `AUTHORITY-DEPENDENCY-GRAPH.json`.

It closes this failure mode: route fields and schemas are current, but graph source-kind generation silently omits the new family, breaking rollback and authority propagation.
