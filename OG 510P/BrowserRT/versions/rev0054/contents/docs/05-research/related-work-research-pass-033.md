# Related-work research pass 033 — OPFS provider bridge

Current revision: rev0054

This pass pulls BrowserRT back toward real browser storage after many fake-provider scheduler/resilience rungs. The important lesson is not "OPFS is durable now." The lesson is that OPFS is the browser-local storage substrate where BrowserRT's fake block-store/provider contracts can eventually land, but only if the cube preserves narrow provider proofs, explicit non-claims, and browser-light release posture.

## Sources and ideas stolen

- MDN Origin Private File System: OPFS is private to the origin, optimized for performance, and supports in-place write access. BrowserRT should treat it as an origin-local provider, not as user-visible filesystem access.
- MDN `createSyncAccessHandle`: synchronous access handles are worker-only and OPFS-only. BrowserRT must keep async-window OPFS, sync-worker OPFS, and future storage-lane sync providers separate.
- SQLite Wasm persistence docs: the OPFS VFS family splits performance and concurrency tradeoffs; BrowserRT should not pretend one provider mode solves all browser storage cases.
- MDN storage quotas and eviction criteria: browser storage remains quota/eviction-bound; persistent storage requests can reduce some eviction risk but do not become a durability theorem.
- web.dev OPFS and storage docs: OPFS is useful for private local files, but future storage claims still need explicit estimates, cleanup, recovery, and non-claim surfaces.

## Design consequence

Rev0038 adds the baby provider bridge: `OpfsAsyncBlockStore`. It proves content-addressed put/get/has/verify/delete, duplicate dedupe, page-reload readback in one temporary Chromium profile, and trace evidence. It does not yet connect to the storage-lane executor, persisted-spill mailbox, journal/manifest recovery, OPFS sync handles, quota pressure, crash recovery, or multi-tab locks.

## Stolen caution

SQLite's OPFS VFS variants are the warning sign. BrowserRT should eventually expose provider variants, not one magical OPFS mode:

```txt
opfs-async-block-store
opfs-sync-worker-block-store
opfs-journaled-block-store
opfs-sah-pool-like-provider
opfs-web-locks-coordinated-provider
fake-opfs-provider-for-models
```

Each variant needs its own capabilities, trace events, tests, and non-claims.
