# Browser OPFS Web Lock Service Worker update-race proof — rev0067

Task: `browser:opfs-web-lock-service-worker-update-race-proof`

This slice tests the risky Service Worker update boundary left after the shutdown-boundary proof. A module Service Worker v1 holds BrowserRT's guarded OPFS mutation Web Lock and writes/verifies a real content-addressed OPFS block. While v1 still holds the lock, the page registers a same-scope module Service Worker v2. The proof observes v2 in the registration slots while the v1-held Web Lock remains held.

The page then schedules a storage-lane guarded OPFS write behind that held lock. The write must time out as `BRT_WEB_LOCK_TIMEOUT`, mark the storage lane unhealthy, reject follow-on mutation as `rejected-lane-unhealthy`, and refuse `recoverWhenStoreSettled()` while the old worker-held lock remains present. CDP then closes the old v1 Service Worker target. The same page adapter must recover explicitly after lock state settles, verify the v1-written block, prove the timed-out candidate is absent, and verify a later v2 Service Worker guarded OPFS write.

The proof deliberately keeps the browser evidence explicit and outside broad release. It launches managed Chromium, uses a local secure origin, module Service Workers, OPFS, Web Locks, Web Locks query state, CDP target control, and cleanup/unregister at the end.

Earned claim: in managed Chromium, a same-scope Service Worker update attempted while the old BrowserRT Service Worker holds the guarded OPFS mutation lock does not bypass the Web Lock/backpressure boundary, and the page-side storage lane can recover only after the old worker target closes and lock state settles.

Non-claims: no cross-browser Service Worker/Web Locks/OPFS behavior claim; no full Service Worker update algorithm correctness claim; no mobile/background suspension, fetch-event, push-event, offline, browser-shutdown durability, OPFS fsync, power-loss, kernel-crash, quota survival, eviction survival, persistent-retention, fairness, starvation-freedom, distributed-lock, exactly-once, throughput, latency, SLO, automatic recovery, or production-readiness claim.

Run:

```sh
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-update-race-proof --jobs 1 --json artifacts/validation/REV0067-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-UPDATE-RACE-RUN.json
```
