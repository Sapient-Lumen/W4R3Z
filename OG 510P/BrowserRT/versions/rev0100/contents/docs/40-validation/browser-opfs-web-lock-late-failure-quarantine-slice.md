# Browser OPFS Web Lock late failure quarantine slice — rev0070

Current browser target: `browser:opfs-web-lock-late-failure-quarantine-proof`.

This managed Chromium proof exercises the same late-failure quarantine policy through a real OPFS/Web Lock guarded store. The wrapper writes a real OPFS content-addressed block through BrowserRT's guarded block store, lets the storage-lane operation time out, then rejects late with `BRT_OPFS_OPERATION_FAILED`.

## Evidence

The browser proof checks:

- OPFS and Web Locks are available in managed Chromium.
- The guarded provider writes a real OPFS block before the scheduler timeout.
- The Web Lock drains, so recovery is no longer blocked by lock contention.
- The late provider rejection is recorded as `storage-lane:late-provider-failure`.
- `failedTimedOutOperationCount` becomes `1`.
- `recoverWhenStoreSettled()` refuses recovery with `timed-out-operation-late-failure`.
- The timed-out operation does not publish adapter success.
- Follow-on writes reject while the failure is quarantined.
- Explicit maintenance clearing enables a later guarded OPFS write, which verifies.
- OPFS cleanup and final held/pending lock counts are clean.

## Non-claims

Managed Chromium only. This does not prove cancellation, cross-browser behavior, rollback, no-mutation on timeout, exactly-once semantics, OPFS durability, quota or eviction survival, persistent-storage retention, SLOs, or production readiness.

Additional non-claims: this slice does not prove cross-browser behavior, quota survival, eviction survival, crash recovery, persistent-storage retention, throughput/latency SLOs, or production readiness.
