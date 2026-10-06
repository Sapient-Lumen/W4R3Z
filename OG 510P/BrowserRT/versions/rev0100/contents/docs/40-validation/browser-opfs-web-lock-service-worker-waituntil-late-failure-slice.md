# Browser OPFS Web Lock Service Worker waitUntil late-failure slice — rev0073

Current task: `browser:opfs-web-lock-service-worker-waituntil-late-failure-proof`

This slice proves a narrow browser lifecycle boundary in managed Chromium: a module Service Worker can return a fetch response while `event.waitUntil()` keeps BrowserRT's guarded OPFS mutation Web Lock held, and a page-side storage-lane OPFS mutation must not treat the fetch response as lock/store settlement.

The proof registers `tools/browserrt_opfs_web_lock_service_worker_holder.mjs` under a rev0073 route, fetches `/browserrt-sw-waituntil-late-failure`, and verifies that the Service Worker route responds immediately while waitUntil work remains active. The waitUntil work writes and verifies a real OPFS content-addressed block while holding the guarded Web Lock, then deliberately rejects with `BRT_SW_WAITUNTIL_LATE_FAILURE` after the response.

While the waitUntil-held lock is active, the page schedules a guarded OPFS storage-lane write. The write fails as `BRT_WEB_LOCK_TIMEOUT`, marks the lane unhealthy, rejects a follow-on write as `rejected-lane-unhealthy`, and blocks explicit recovery with `store-coordination-still-contended`. The timed-out page-side candidate remains absent.

After the waitUntil promise settles and Web Lock state drains, the page verifies the Service-Worker-written OPFS block, confirms the timed-out candidate is still absent, explicitly recovers the lane, writes and verifies a new guarded OPFS block, unregisters the worker, cleans the OPFS namespace, and confirms final held/pending lock counts are zero.

## Non-claims

- Managed Chromium only; this does not claim cross-browser Service Worker, Web Locks, or OPFS behavior.
- This does not claim automatic recovery. Recovery remains explicit and depends on guarded store settled-state checks.
- This does not claim that waitUntil rejection automatically poisons another page runtime; the earned boundary is that BrowserRT's page-side recovery gate respects Web Lock settlement rather than fetch response completion.
- This does not claim OPFS fsync durability, power-loss safety, crash safety, quota survival, eviction survival, persistent retention, fairness, exactly-once mutation semantics, throughput, latency SLOs, or production readiness.
