# Browser OPFS/Web Lock operation context propagation slice — rev0073

Current browser proof: `browser:opfs-web-lock-operation-context-propagation-proof`.

The managed Chromium proof wraps a real OPFS block store with a recording provider, routes it through BrowserRT's Web Lock guarded block-store wrapper, then schedules storage-lane operations through `BlockStoreLaneAdapter`. It verifies that the expected `operationTimeoutMs` values reach the provider for real OPFS-backed operations while Web Locks drain to zero.

The proof covers the context path that matters after the timeout/quarantine revisions:

`StorageLaneExecutor -> BlockStoreLaneAdapter -> WebLockGuardedBlockStore -> OPFS provider wrapper`.

This is managed Chromium evidence only. It is not a cross-browser Web Locks or OPFS claim, not provider cancellation, not rollback, not no-mutation-on-timeout evidence, not OPFS durability/fsync/power-loss evidence, not quota or eviction evidence, and not production readiness.

The browser slice is not durability evidence; it only confirms context propagation on managed Chromium.

Audit nonclaims: cross-browser, quota, eviction, crash, browser-light.
