# Browser OPFS Web-Lock-guarded contention slice — rev0062 (carried forward from rev0060)

Current revision: rev0062

## Purpose

`browser:opfs-web-lock-guarded-contention-proof` is the first slice that wires the previously separate Web Locks and async OPFS evidence into a BrowserRT runtime wrapper. It proves that two same-origin dedicated workers can use one `WebLockGuardedBlockStore` lock name to serialize OPFS mutations, then the main page verifies the acknowledged content-addressed blocks and performs a normal guarded OPFS put.

This closes the gap between “Web Locks exist” and “BrowserRT can route real OPFS writes through a same-origin coordination boundary.”

## Runtime surface

The slice adds:

- `src/web-lock-coordinator.mjs`
- `src/opfs-web-lock-guarded-block-store.mjs`
- `rt.webLockCoordinator()`
- `rt.opfsWebLockGuardedBlockStore()`
- release-tier fake-lock guard proof: `coord:web-lock-guarded-block-store-proof`
- browser-tier OPFS/Web Locks contention proof: `browser:opfs-web-lock-guarded-contention-proof`

`WebLockGuardedBlockStore` serializes mutating calls (`put`, `delete`, `cleanupForTest`, `open`) through an exclusive Web Lock and routes read-like calls (`get`, `has`, `verify`, `estimate`) through shared locks by default.

## Browser proof

The browser proof launches managed Chromium/CDP on a local origin with COOP/COEP headers. The page cleans the OPFS test prefix, then starts a slow worker that acquires the shared lock and holds it around an OPFS write. A fast worker attempts a same-lock OPFS mutation while the slow worker still holds the lock.

The expected evidence is:

- `navigator.locks.request` is available on the page and workers.
- `navigator.storage.getDirectory` is available.
- The fast worker does not acquire during the slow worker's hold window.
- Both worker-written content-addressed OPFS blocks verify from the main page.
- A standard guarded `put()` from the main page reaches OPFS after contention.
- Final guarded cleanup succeeds.
- `navigator.locks.query()` reports no held/pending locks at the end.

## Non-claims

This is not a cross-browser Web Locks claim, not a cross-browser OPFS claim, not a quota claim, not an eviction claim, not a crash or power-loss durability claim, not an fsync guarantee, not a persistent-storage retention claim, not a fairness or starvation-freedom claim, and not a production distributed-lock or exactly-once claim.

It coordinates two dedicated workers plus a main page on one local origin in managed Chromium. Browser-light release remains browser-light; this browser proof is explicit browser-tier evidence. Multi-tab lifecycle, background throttling, service-worker interactions, mobile suspension, and organic low-disk pressure remain future proof targets.

## Commands

```bash
node tools/run_tests.mjs --tier release --id coord:web-lock-guarded-block-store-proof --jobs 1 --json artifacts/validation/REV0060-WEB-LOCK-GUARDED-BLOCK-STORE-RUN.json
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-guarded-contention-proof --jobs 1 --json artifacts/validation/REV0060-BROWSER-OPFS-WEB-LOCK-GUARDED-CONTENTION-RUN.json
```
