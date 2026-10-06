# Browser OPFS/Web Locks service-worker lifecycle slice — rev0064

## Current earned claim

`browser:opfs-web-lock-service-worker-lifecycle-proof` is a managed Chromium/CDP browser proof. It serves a module Service Worker from a controlled probe route, lets that worker import BrowserRT's OPFS block-store and Web Lock guarded block-store modules, and has the worker hold the same origin-wide guarded mutation lock while writing and verifying a real OPFS content-addressed block.

A page-side BrowserRT storage lane then schedules a guarded OPFS write behind the service-worker-held lock. The pending mutation must time out as `BRT_WEB_LOCK_TIMEOUT`, mark the storage lane unhealthy, reject follow-on storage writes without mutation, and refuse settled recovery while the service-worker lock is still held. After CDP closes the service-worker target, the lock state must drain to zero held and zero pending rows; only then can explicit `recoverWhenStoreSettled()` reopen the storage lane. The proof then verifies the service-worker-written block, proves the timed-out candidate is absent, performs a new guarded write, verifies it, unregisters the worker, and cleans the OPFS namespace.

## Why this was risky

The earlier settled-recovery work proved page/tab lifecycle boundaries. Service workers are a different same-origin actor with a different lifetime. A Web Lock held by a service worker could otherwise wedge page-side OPFS mutation recovery or reopen a storage lane while a worker still owns the mutation boundary.

This slice also found and formalized a useful fixture capability: browser probes now have explicit service-worker route serving and CDP service-worker target closing helpers instead of one-off target scraping.

## Validation commands

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-service-worker-lifecycle-proof --jobs 1 --json artifacts/validation/REV0064-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-LIFECYCLE-RUN.json
node tools/run_tests.mjs --tier release --id facility:service-worker-lifecycle-contract-audit --jobs 1 --json artifacts/validation/REV0064-SERVICE-WORKER-LIFECYCLE-AUDIT-RUN.json
```

## Non-claims

This is not a cross-browser Service Worker, Web Locks, or OPFS conformance claim. It is not a mobile/background suspension, tab discard, browser shutdown, service-worker update, fetch-event, push-event, offline, or persistent-service-worker lifetime claim. It is not automatic recovery; recovery is explicit maintenance recovery gated on settled lock state. It is not a fairness, starvation-freedom, exactly-once, distributed-lock, OPFS durability, fsync, power-loss, kernel-crash, organic quota, eviction, persistent-retention, throughput, latency, SLO, or production-readiness claim.
