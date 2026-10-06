# Browser OPFS Web Lock Service Worker fetch lifecycle proof — rev0067

Current browser slice: `browser:opfs-web-lock-service-worker-fetch-lifecycle-proof`

This slice targets the fetch-event gap left after the message-triggered Service Worker lifecycle, restart/update, and shutdown-boundary proofs. It proves a real Service Worker `fetch` event can hold BrowserRT's guarded OPFS mutation Web Lock while a page-side storage-lane OPFS write times out and moves into backpressure, then releases the lock through the fetch response path and recovers explicitly after lock state settles.

The managed Chromium proof uses:

- a module Service Worker served from `tools/browserrt_opfs_web_lock_service_worker_holder.mjs`
- a proof-only fetch route at `/browserrt-sw-fetch-lifecycle`
- a real `event.respondWith()` fetch response path
- `WebLockGuardedBlockStore` around a real OPFS async block store
- `BlockStoreLaneAdapter.recoverWhenStoreSettled()` after the fetch event releases the lock
- final unregister, OPFS cleanup, lock-drain checks, and browser profile process reaping

Expected observations:

- Service Worker fetch response returns `X-BrowserRT-Service-Worker-Fetch: opfs-web-lock-lifecycle`
- the fetch event writes and verifies a real OPFS content-addressed block while holding the Web Lock
- a page-side storage-lane guarded OPFS put times out as `BRT_WEB_LOCK_TIMEOUT`
- the storage lane becomes unhealthy and rejects follow-on writes as `rejected-lane-unhealthy`
- recovery is blocked while the fetch event still holds the lock
- after the fetch response completes, held/pending locks drain to zero
- explicit settled recovery reopens the lane
- the fetch-written block verifies, the timed-out block remains absent, and a later guarded write verifies

Run directly:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-fetch-lifecycle-proof --jobs 1
```

Non-claims: this is not a cross-browser Service Worker/Web Locks/OPFS claim, not a push-event claim, not a navigation-preload or offline-cache correctness claim, not a Service Worker lifetime guarantee, not a mobile/background suspension claim, not OPFS durability/fsync/power-loss/crash safety, not quota/eviction/persistent-retention evidence, not fairness/starvation-freedom, not exactly-once semantics, and not production readiness. Browser-heavy proof remains explicit and outside broad browser-light release.
