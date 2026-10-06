# Service Worker waitUntil late-failure contract audit slice — rev0073

Current audit: `facility:service-worker-waituntil-late-failure-contract-audit`

This browser-light audit keeps the rev0073 waitUntil late-failure proof wired without launching Chromium. It checks that the shared Service Worker holder exposes `/browserrt-sw-waituntil-late-failure`, calls `event.waitUntil(waitUntil.wait)`, records `BRT_SW_WAITUNTIL_LATE_FAILURE`, and that the managed Chromium proof checks `BRT_WEB_LOCK_TIMEOUT`, `store-coordination-still-contended`, OPFS verification, worker status, cleanup, and final zero lock counts.

It also checks manifest, impact-map, surface-inventory, first-read docs, and package currentness for `browser:opfs-web-lock-service-worker-waituntil-late-failure-proof`.

## Non-claims

- The audit is a wiring/currentness guard only; it is not browser evidence by itself.
- The audit does not claim cross-browser behavior, automatic recovery, OPFS durability, quota/eviction survival, or production readiness.
