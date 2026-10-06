# Storage-lane timeout-quarantine partial clearance replay scope slice

Revision: rev0087  
Task: `scheduler:storage-lane-quarantine-partial-clearance-replay-scope-proof`

This browser-light proof guards the timeout-quarantine clearance path where a receipt clears only some rows from a pre-clearance quarantine fingerprint.

## Risk

A partial clearance receipt can legitimately carry the original `preClearanceFingerprint`, because the review happened against the full quarantine set. If exact stale-ledger replay rejection keys only on that full-fingerprint value, a receipt that cleared one row can suppress replay/import of rows that were never cleared.

## Expected behavior

`StorageLaneExecutor` now treats exact replay as fully cleared only when the registered clearance receipt covers every imported row. If a stale ledger contains a cleared row plus an uncleared row, the import fails closed as `rejected-cleared-quarantine-row-replay` rather than `rejected-cleared-quarantine-replay`. A ledger containing only the uncleared row still imports, forces storage-lane backpressure, and requires reviewed/scoped clearing before recovery.

The proof also registers a self-consistent full-count receipt whose rows do not match the stale ledger. That receipt does not suppress stale-ledger import; the lane imports/backpressures normally.

## Non-claims

This is a browser-light synthetic-provider proof. It does not claim OPFS/Web Locks behavior, provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, tamper-proof storage, durability, quota/eviction survival, throughput, latency SLOs, or production readiness.

Phrase anchor: not provider cancellation.

Phrase anchor: row coverage.
