# Browser OPFS Web Lock read-timeout nonpoison slice — rev0067

Task: `browser:opfs-web-lock-read-timeout-nonpoison-proof`

## Runtime question

The previous Service Worker lifecycle slices proved that mutating guarded OPFS writes should backpressure when they time out behind a held Web Lock. rev0067 checks the opposite boundary: a read-only/shared guarded operation that times out behind an exclusive writer should be a visible read failure, but it should not poison the storage lane or reject later mutations after the writer releases.

## Proof shape

The managed Chromium proof registers a same-origin module Service Worker that imports BrowserRT's OPFS async block-store and Web Lock guarded block-store modules. The worker writes and verifies a real OPFS content-addressed block, then keeps the guarded mutation Web Lock held. The page schedules a storage-lane `verify()` through `WebLockGuardedBlockStore` with a short lock timeout. The verify request queues as a shared/read-only lock request behind the worker-held exclusive lock and fails as `BRT_WEB_LOCK_TIMEOUT`.

The proof then verifies that the storage lane remains healthy, `laneHealthFailures` remains zero, the Service Worker still owns the exclusive lock until explicit release, and after release the holder block plus a later page-side guarded write both verify.

## Expected evidence

- `BRT_WEB_LOCK_TIMEOUT` on the shared/read-only guarded verify.
- `storage` lane remains `healthy: true` after the read timeout.
- `laneHealthFailures: 0` after the read timeout.
- Held lock count remains one until the Service Worker release command.
- Final held and pending lock counts are zero.
- The holder-written OPFS block verifies after release.
- A later page-side guarded OPFS write is accepted, completes, and verifies.

## Non-claims

No cross-browser Web Locks, Service Worker, or OPFS behavior claim. No fairness or starvation-freedom claim. No mobile/background, fetch/push/offline, automatic recovery, OPFS durability, fsync, crash, quota, eviction, persistent-storage retention, throughput, latency, SLO, or production-readiness claim. Mutating Web Lock timeout backpressure remains covered by the separate storage-lane and Service Worker lifecycle proofs.
