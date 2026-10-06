# Browser OPFS Web-Lock tab-termination slice — rev0062

Current revision: rev0062

## Purpose

`browser:opfs-web-lock-tab-termination-proof` extends the rev0060/rev0062 guarded OPFS/Web Locks work from dedicated-worker contention into a real multi-page lifecycle boundary. The risk is simple: one same-origin tab can hold the BrowserRT OPFS mutation lock while another context is waiting. If the holder tab is closed, BrowserRT must not leave peer mutations wedged forever.

This slice proves that boundary in managed Chromium/CDP without converting it into a general lifecycle, durability, cross-browser, or browser-light claim. Browser-light release remains guarded by the release-tier wrapper semantics proof plus the query/wait-settled fake-lock proof; this lifecycle proof stays explicit browser tier.

## Runtime/refactor surface

The runtime refactor is intentionally small and directly supports lifecycle proofs:

- `WebLockCoordinator.queryLocks(name)` normalizes `navigator.locks.query()` rows and can filter by one BrowserRT lock name.
- `WebLockCoordinator.waitForSettled(name, { timeoutMs, intervalMs })` polls until the named lock has no held or pending rows.
- `tools/browser_cdp_fixture.mjs` exposes reusable browser-level CDP helpers for multi-target proofs: `connectBrowserCdp`, `openPageTarget`, and `closePageTarget`.
- `coord:web-lock-timeout-proof` remains the normal release harness guard and now also checks the normalized query/wait-settled helpers after timeout/recovery.

The existing `WebLockGuardedBlockStore` remains the mutation wrapper. No new storage doctrine is introduced.

## Browser proof

The managed Chromium proof uses one local same-origin page plus a second CDP-created page target:

1. The main page cleans the OPFS test prefix.
2. The holder page target boots BrowserRT, opens a guarded OPFS block store, acquires the exclusive Web Lock, writes one acknowledged content-addressed OPFS block, and intentionally holds the lock open.
3. The main page starts a second guarded exclusive mutation using the same lock name.
4. `navigator.locks.query()` must show one held exclusive lock and one pending exclusive lock.
5. CDP closes the holder page target.
6. The waiting main-page mutation must acquire, write, verify, settle, and clean up.
7. The acknowledged holder block and acknowledged waiter block must both verify after the holder tab has closed.
8. The final normalized lock query must report zero held and zero pending rows.

## Non-claims

This is not a cross-browser Web Locks claim, not a mobile or background suspension claim, not a service-worker claim, not a fairness or starvation-freedom claim, not a distributed-lock or exactly-once claim, and not a production multi-tab lifecycle guarantee.

This is also not an OPFS fsync, power-loss, kernel-crash, drive-cache flush, organic eviction, quota, Storage Buckets, or persistent-storage-retention claim. It only proves that in managed Chromium, a waiting guarded OPFS mutation is not wedged when a same-origin tab holding the BrowserRT lock is closed by CDP.

## Commands

```bash
node tools/run_tests.mjs --tier release --id coord:web-lock-guarded-block-store-proof --jobs 1 --json artifacts/validation/REV0062-WEB-LOCK-GUARDED-BLOCK-STORE-RUN.json
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-tab-termination-proof --jobs 1 --json artifacts/validation/REV0062-BROWSER-OPFS-WEB-LOCK-TAB-TERMINATION-RUN.json
```
