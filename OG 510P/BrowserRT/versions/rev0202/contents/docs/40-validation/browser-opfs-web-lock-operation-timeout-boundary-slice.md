# Browser OPFS Web Lock operation timeout boundary slice — rev0067

Current slice: `browser:opfs-web-lock-operation-timeout-boundary-proof`

## Purpose

This slice proves the boundary that was still exposed after the Service Worker lifecycle work: Web Lock acquisition can be bounded, but a dispatched storage-lane operation can still acquire the guarded mutation lock, perform provider work, and then hang before returning to the scheduler.

rev0067 adds a storage-lane operation timeout so the executor does not wait forever for that dispatched provider promise. The timeout is treated as provider-health failure and moves the storage lane into backpressure.

## Browser proof

The managed Chromium proof creates a real OPFS async block store, wraps it in BrowserRT's WebLockGuardedBlockStore, then schedules a storage-lane `put()` through a controlled provider that:

1. acquires the real Web Lock;
2. writes and verifies a real OPFS content-addressed block;
3. intentionally holds the provider promise open past `operationTimeoutMs`;
4. lets the storage-lane executor return `BRT_STORAGE_OPERATION_TIMEOUT`;
5. verifies the Web Lock remains held and recovery is blocked;
6. explicitly releases the provider promise;
7. recovers only after held/pending lock rows settle;
8. verifies both the timed-out provider-written block and a later recovered write;
9. cleans the OPFS namespace and checks zero final held/pending locks.

## Runtime contract

`StorageLaneExecutor` now accepts `defaultOperationTimeoutMs` / `operationTimeoutMs` and emits:

- `storage-lane:operation-timeout-arm`
- `storage-lane:operation-timeout`
- `storage-lane:provider-unhealthy`

`BlockStoreLaneAdapter.schedule*()` can pass `operationTimeoutMs` through to the executor.

## Non-claims

This is not a cancellation proof. A provider may have already mutated OPFS before the operation timeout fires. The browser proof deliberately verifies that the timed-out provider-written block can be present and valid. The timeout is a bounded scheduler-observation/backpressure boundary, not rollback, no-mutation, exactly-once, or provider interruption.

No cross-browser OPFS/Web Locks behavior, OPFS fsync durability, power-loss safety, organic quota/eviction survival, persistent-storage retention, automatic recovery, fairness, starvation freedom, throughput, latency, SLO, or production-readiness claim is made.

Historical non-claim reminder: cross-browser behavior, quota behavior, eviction survival, and crash or durability behavior remain separate unearned claims for this carried-forward slice.

