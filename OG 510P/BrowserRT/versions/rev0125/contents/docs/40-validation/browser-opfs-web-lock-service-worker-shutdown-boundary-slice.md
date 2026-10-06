# Browser OPFS Web Lock Service Worker shutdown-boundary slice — rev0066

Current task: `browser:opfs-web-lock-service-worker-shutdown-boundary-proof`

This browser-heavy proof targets the lifecycle boundary after the Service Worker restart/update proof: a module Service Worker holds BrowserRT's guarded OPFS mutation Web Lock, a page-side storage-lane guarded OPFS write times out and marks the storage lane unhealthy, and the browser process is killed while the Service Worker holder is still unresolved. A second launch reuses the same profile and origin and verifies that Web Lock state is drained, the closed Service Worker OPFS block remains verifiable, the timed-out page candidate is absent, explicit settled recovery succeeds, and later guarded page and Service Worker writes verify.

Important observations the proof must preserve:

- `BRT_WEB_LOCK_TIMEOUT` is surfaced for the page-side storage-lane mutation.
- The storage lane becomes unhealthy and a follow-on mutation is rejected as `rejected-lane-unhealthy` with no mutation.
- `recoverWhenStoreSettled()` refuses to recover while the Service Worker-held lock remains live.
- The first Chromium launch uses process-group kill teardown while the holder is unresolved.
- On relaunch, held and pending rows for the BrowserRT lock are zero.
- The Service Worker-written block verifies after relaunch, while the timed-out candidate remains absent.
- The Service Worker registration is unregistered, OPFS test prefix is cleaned, and BrowserRT-managed Chromium profile processes are reaped.

Non-claims: no cross-browser Service Worker/Web Locks/OPFS behavior claim; no OPFS fsync, power-loss, kernel-crash, browser-shutdown durability, quota, eviction, persistent-retention, automatic recovery, fairness, starvation-freedom, exactly-once, throughput, latency, SLO, or production-readiness claim.
