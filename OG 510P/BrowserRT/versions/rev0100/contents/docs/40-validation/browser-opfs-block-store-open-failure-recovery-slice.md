# Browser OPFS block-store open failure recovery slice

Revision: rev0098  
Task: `browser:opfs-block-store-open-failure-recovery-proof`

This managed Chromium proof exercises the rev0098 open-failure recovery path in a real browser page. The probe temporarily monkey-patches `navigator.storage.getDirectory()` to throw a controlled `InvalidStateError` once for a direct `open()` and once for a `put()`. It then checks that the same `OpfsAsyncBlockStore` instance retries successfully instead of reusing a rejected root promise.

The browser proof checks:

- OPFS, Web Locks, secure context, and cross-origin isolation capabilities are present;
- the first direct `open()` fails with `InvalidStateError` and records `openFailures` / `openRetryResets`;
- the second direct `open()` succeeds on the same store;
- the first `put()` fails during forced root open without acknowledging data;
- the second `put()` on the same store retries, writes, verifies, and reads bytes back;
- `storage:opfs-blockstore-open-error` includes `rootPromiseReset: true`;
- a guarded OPFS/Web Locks write/verify path still succeeds and ends with no held or pending locks.

Non-claims: this is managed Chromium evidence only, not cross-browser conformance. The forced root-open failure is not a browser quota/eviction test, fsync durability test, crash-recovery test, power-loss test, multi-tab atomicity proof, tamper-resistance proof, or production-readiness claim.
