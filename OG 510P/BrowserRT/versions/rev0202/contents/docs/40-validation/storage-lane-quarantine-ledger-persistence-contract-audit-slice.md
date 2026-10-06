# Storage-lane quarantine ledger persistence contract audit slice

Task: `facility:storage-lane-quarantine-ledger-persistence-contract-audit`

This rev0075 audit keeps the block-store quarantine persistence runtime hooks, malformed persisted-ledger fail-closed restore behavior, release proof, managed-Chromium proof, manifest rows, impact-map rule, surface inventory entries, Makefile/package routes, and current-office metadata aligned.

It specifically guards `persistTimedOutOperationQuarantine()`, `restoreTimedOutOperationQuarantineFromBlockStore()`, `block-store-lane:quarantine-ledger-persisted`, `block-store-lane:quarantine-ledger-restored`, `timed-out-quarantine-import-rejected`, and `rejected-ledger-integrity` so future sessions cannot silently regress from provider-backed persistence to in-memory export/import only or bypass the fail-closed importer during persisted restore.

Non-claims: audit-only coverage; not browser execution, not cross-browser behavior, not fsync durability, not cancellation, not quota/eviction evidence, and not production readiness.
