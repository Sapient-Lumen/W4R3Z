# Storage-lane quarantine ledger persistence slice

Task: `scheduler:storage-lane-quarantine-ledger-persistence-proof`

rev0075 merges the persistence branch with the fail-closed quarantine-ledger importer. rev0073 proved export/import, and rev0074 hardened malformed import rejection. This slice proves the runtime API that persists the schema-bearing ledger into the block-store provider, rejects a malformed persisted ledger without mutating a fresh lane, and restores a valid persisted ledger into a fresh storage-lane adapter.

The release-tier proof creates one late-success and one late-failure provider operation after `BRT_STORAGE_OPERATION_TIMEOUT`, persists the resulting `brt.storageLane.timedOutOperationQuarantine.v1` ledger through `persistTimedOutOperationQuarantine()`, writes a malformed persisted ledger with a bad `counts.total`, verifies `restoreTimedOutOperationQuarantineFromBlockStore()` fails closed through `rejected-ledger-integrity`, then restores the valid ledger, verifies the restored lane is unhealthy/backpressured, rejects follow-on mutation with `noMutation`, and recovers only after reviewed/scoped clearing.

Non-claims: this release-tier proof is synthetic and browser-light. It is not OPFS evidence, not Web Locks evidence, not clean browser restart evidence, not fsync durability, not power-loss safety, not quota/eviction survival, not cancellation, not rollback, not exactly-once semantics, and not production readiness.
