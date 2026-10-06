# Browser OPFS Web Lock quarantine clearance lane-wide query scope slice

Current in rev0087: `browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof`.

This Managed Chromium proof repeats the lane-wide query/replay scope check over BrowserRT's real guarded OPFS path.  It uses `OpfsAsyncBlockStore`, `WebLockGuardedBlockStore`, `BlockStoreLaneAdapter`, same-origin Web Locks, and a local Chromium profile.

The proof registers a valid `allowLaneWide: true` clearance receipt for the `storage` lane.  It then proves that the receipt is visible through storage-lane receipt queries, absent from maintenance-lane receipt queries, still rejects stale storage replay, and does not suppress a maintenance-lane timeout-quarantine import with the same visible operation ids.  The maintenance import remains backpressured, and a later guarded OPFS write verifies after the storage replay path remains healthy.

This is intentionally not a cross-browser claim.  It is also not a durability, quota, eviction, rollback, cancellation, exactly-once, latency, SLO, cryptographic attestation, tamper-proof storage, or production-readiness claim.
