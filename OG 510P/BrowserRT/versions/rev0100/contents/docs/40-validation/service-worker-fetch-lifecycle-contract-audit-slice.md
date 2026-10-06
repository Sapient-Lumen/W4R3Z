# Service Worker fetch lifecycle contract audit — rev0067

Current audit: `facility:service-worker-fetch-lifecycle-contract-audit`

The audit is browser-light. It checks that the fetch-event lifecycle proof is wired through the Service Worker holder, managed-browser probe, docs, manifest, impact map, surface inventory, operator shortcuts, first-read currentness, and the deeper cube audit without launching Chromium.

The audit protects these current surfaces:

- `tools/browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs`
- `tools/browserrt_opfs_web_lock_service_worker_holder.mjs`
- `docs/40-validation/browser-opfs-web-lock-service-worker-fetch-lifecycle-slice.md`
- `test/manifest.json`
- `test/impact-map.json`
- `test/surface-inventory.json`
- first-read currentness surfaces and release-light shortcuts

It specifically checks for `event.respondWith`, `/browserrt-sw-fetch-lifecycle`, `BRT_WEB_LOCK_TIMEOUT`, blocked recovery while the fetch event holds the lock, settled recovery after the fetch response, and non-claim language around cross-browser behavior, durability, quota, eviction, persistence, and production readiness.

Non-claims: this audit does not launch Chromium, does not prove Service Worker runtime behavior, does not prove Web Locks fairness, does not prove OPFS durability, does not prove quota/eviction/persistent-retention behavior, does not prove offline-cache correctness, does not prove crash recovery, and does not certify production readiness.
