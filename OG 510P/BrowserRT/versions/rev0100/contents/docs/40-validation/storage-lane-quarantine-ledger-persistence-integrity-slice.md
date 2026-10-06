# Storage-lane quarantine ledger persistence-integrity slice

Task: `scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof`

rev0075 adds a browser-light guard for `persistTimedOutOperationQuarantine()` and `restoreTimedOutOperationQuarantineFromBlockStore()` for a practical maintenance boundary: a timeout-quarantine ledger must be persistable through the block-store provider, but restoring that provider-backed ledger must still inherit the rev0074 fail-closed import-integrity rules.

The proof creates mixed late-success and late-failure provider outcomes after `BRT_STORAGE_OPERATION_TIMEOUT`, persists the resulting `brt.storageLane.timedOutOperationQuarantine.v1` ledger as a content-addressed block, stores a malformed persisted copy with a `counts.total` mismatch, and verifies that restoring the malformed block is rejected atomically without poisoning lane health or installing quarantine rows.

It then restores the valid persisted ledger into a fresh adapter. The fresh adapter marks the storage lane unhealthy, rejects follow-on writes with `noMutation`, blocks recovery while late-success / late-failure quarantine remains, and recovers only after reviewed/scoped clearing for each quarantined op.

Non-claims: synthetic release-tier proof only; not OPFS/Web Locks browser evidence, not cryptographic attestation, not tamper-proof storage, not provider cancellation, not cancellation, not rollback, not fsync durability, not crash/power-loss safety, not exactly-once semantics, not quota/eviction evidence, and not production readiness.
