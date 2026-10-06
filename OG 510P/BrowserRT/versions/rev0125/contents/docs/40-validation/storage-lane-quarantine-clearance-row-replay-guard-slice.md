# rev0081 storage-lane quarantine clearance row replay guard slice

Current task: `scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof`

This release-light slice covers a maintenance bypass left after exact stale-ledger replay and no-op clearance receipt guards. A timeout-quarantine ledger can be reshaped so the full `quarantineFingerprint` changes while it still carries operation rows that were already reviewed, cleared, and represented by a clearance receipt.

rev0081 records row-level replay keys in registered clearance receipts:

```text
clearedRowKeys
clearedOperationKeys
clearedReplayKeys
```

Import now rejects a non-empty timeout-quarantine ledger if any imported row matches a previously cleared operation identity. The guard is deliberately stronger than a status-specific key: a stale failed timeout row rewritten as a successful timeout row still rejects by operation identity.

Earned claim: BrowserRT rejects exact stale-ledger replay, modified-row replay, and status-rewritten cleared-operation replay without mutating the fresh adapter quarantine state or poisoning the fresh lane.

Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, tamper-proof storage, OPFS durability, quota survival, eviction survival, cross-browser behavior, or production readiness.

This is not provider cancellation, not rollback, and not proof that timeout means no mutation happened.
