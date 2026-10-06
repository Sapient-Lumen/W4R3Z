# Storage-lane late failure quarantine slice — rev0070

Current runtime target: `scheduler:storage-lane-late-failure-quarantine-proof`.

This slice closes the hole left after late provider settlement tracking. A timed-out provider operation can settle late with a rejection, not just success. rev0070 keeps that late rejection visible as a quarantined failed timed-out operation and refuses settled recovery until maintenance explicitly clears the reviewed failure.

## Evidence

The release-tier proof uses a synthetic block store that commits a block before provider settlement, waits past `BRT_STORAGE_OPERATION_TIMEOUT`, then rejects with `BRT_OPFS_OPERATION_FAILED` after explicit release.

The proof checks:

- `BRT_STORAGE_OPERATION_TIMEOUT` marks the storage lane unhealthy.
- `recoverWhenStoreSettled()` first blocks as `timed-out-operation-still-unsettled`.
- Late rejection records `storage-lane:late-provider-failure` and increments `failedTimedOutOperationCount`.
- `recoverWhenStoreSettled()` then blocks as `timed-out-operation-late-failure` even though the provider is settled.
- Follow-on writes remain `rejected-lane-unhealthy` while the late failure is quarantined.
- `clearFailedTimedOutOperations()` is required before explicit recovery reopens the lane.

## Non-claims

This is not cancellation, not rollback, no-mutation, exactly-once, durability, automatic recovery, or production-readiness evidence. The point is conservative recovery gating after a late provider failure.

Additional non-claims: this slice does not prove cross-browser behavior, quota survival, eviction survival, crash recovery, persistent-storage retention, throughput/latency SLOs, or production readiness.
