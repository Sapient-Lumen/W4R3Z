# Storage-lane quarantine ledger persistence-integrity contract audit slice

Task: `facility:storage-lane-quarantine-ledger-persistence-integrity-contract-audit`

This rev0075 audit keeps the runtime persistence hooks, fail-closed restore-integrity behavior, release proof, managed-Chromium proof, manifest rows, impact-map rule, surface inventory entries, Makefile/package routes, and current-office metadata aligned.

It guards `persistTimedOutOperationQuarantine()`, `restoreTimedOutOperationQuarantineFromBlockStore()`, `block-store-lane:quarantine-ledger-persisted`, `block-store-lane:quarantine-ledger-restore-rejected`, and `block-store-lane:quarantine-ledger-restored`. It also checks that malformed persisted ledgers are treated as atomic restore failures rather than partially installed maintenance state.

Non-claims: audit only; not browser execution, not cross-browser behavior, not cryptographic attestation, not fsync durability, not cancellation, not quota/eviction evidence, and not production readiness.
