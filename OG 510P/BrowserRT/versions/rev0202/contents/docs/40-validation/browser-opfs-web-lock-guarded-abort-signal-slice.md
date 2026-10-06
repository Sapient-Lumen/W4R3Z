# rev0106 browser OPFS/Web Lock guarded AbortSignal slice

## Managed-browser evidence

`tools/browser_opfs_web_lock_guarded_abort_signal_probe.mjs` runs in managed Chromium with real OPFS and real `navigator.locks`. It proves the rev0106 direct guarded cancellation path against browser primitives rather than only the fake lock manager.

The browser proof:

- holds the guarded Web Lock, queues a guarded `put()` with `abortSignal` only, aborts while pending, and verifies the provider write never creates the OPFS block file;
- patches the OPFS writable path to abort after lock acquisition and verifies the provider reports `BRT_OPFS_OPERATION_ABORTED`, not a relabeled `BRT_WEB_LOCK_ABORTED`;
- runs a normal guarded OPFS write, verify, get, cleanup smoke path;
- checks that held and pending Web Locks drain at the end.

## Boundary

This is a focused Chromium canary for the changed direct `WebLockGuardedBlockStore` path. It does not claim Safari/Firefox parity, Web Locks scheduling fairness, quota reservation, eviction survival, OPFS crash durability, fsync durability, or production readiness. OPFS remains origin-private browser-managed storage and abort handling remains cooperative.

This is not cross-browser evidence.
