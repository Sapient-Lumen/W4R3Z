# Registered generated-summary revision freshness audit

The registered generated-summary revision audit checks that every generated summary named in `LEDGER-FAMILY-REGISTRY.json` exists and contains the current release revision token.

The audit exists because a generated summary can survive a rebuild as a stale file even when its ledger, schema, and route fields are current. It is archive-control only and creates no scientific support.
