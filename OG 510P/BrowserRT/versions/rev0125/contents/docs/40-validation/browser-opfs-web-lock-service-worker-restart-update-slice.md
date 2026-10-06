# Browser OPFS Web Lock Service Worker restart/update slice — rev0065

`browser:opfs-web-lock-service-worker-restart-update-proof` is an explicit managed-Chromium proof for the Service Worker lifecycle boundary that was left open after the target-close lifecycle proof.

The proof uses one local origin, one reusable Chromium profile, and two browser launches. In the first launch a module Service Worker imports the BrowserRT OPFS async block store and Web Lock guarded block store, registers at root scope, writes/verifies a real content-addressed OPFS block, releases the guarded mutation Web Lock, and leaves the Service Worker registration in the profile. In the second launch the same server origin and profile are reused; the page observes the persisted v1 registration, sends another guarded OPFS write through the restarted worker, verifies the pre-restart block from the page, updates the same scope to a v2 Service Worker script, verifies that the v2 worker responds, writes/verifies another guarded OPFS block, performs a page-side storage-lane guarded OPFS write, cleans the namespace, unregisters the worker, and confirms zero held/pending Web Lock rows.

Required evidence:

- Same-origin profile reuse across two managed Chromium launches.
- v1 Service Worker registration visible after browser restart.
- OPFS block written before restart verifies after restart.
- v2 Service Worker script activates for the same scope and reports a distinct identity.
- Page-side storage-lane guarded OPFS write remains healthy after restart/update.
- Final cleanup unregisters the worker, removes proof OPFS data, reaps profile processes, and leaves no held/pending Web Lock rows.

Non-claims:

- No cross-browser Service Worker, Web Locks, or OPFS conformance claim.
- No power-loss, OS crash, mobile/background suspension, tab discard, fetch-event, push-event, offline, or browser-shutdown durability claim.
- No guarantee about every Service Worker update race or long-lived event semantic.
- No OPFS fsync, quota, eviction, persistent-retention, exactly-once, fairness/starvation-freedom, throughput, latency, SLO, automatic-recovery, or production-readiness claim.
