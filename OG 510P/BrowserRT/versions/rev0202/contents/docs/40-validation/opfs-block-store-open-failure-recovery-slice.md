# OPFS block-store open failure recovery slice

Revision: rev0098  
Task: `opfs:block-store-open-failure-recovery-proof`

This slice fixes a cached-promise poisoning risk in `OpfsAsyncBlockStore`. Before rev0098, the provider memoized the root OPFS open path in `#rootPromise`. If `navigator.storage.getDirectory()` or one of the prefix `getDirectoryHandle(..., { create: true })` calls failed once, that rejected promise stayed cached. A transient browser/storage failure could therefore make every later `open()`, `put()`, `get()`, or `verify()` on the same provider instance fail without retrying the browser provider.

The provider now wraps the root-open promise with a failure handler. On open failure it:

- increments `openFailures`;
- resets the cached root promise when the failed promise is still the active root promise;
- increments `openRetryResets`;
- marks the provider unopened;
- emits `storage:opfs-blockstore-open-error` with classified error detail and `rootPromiseReset`.

The release proof uses the shared fake-OPFS harness and its `createFailOnceDirectoryOpenHarness()` helper to inject one prefix-open failure. It verifies that the same store instance can retry `open()` successfully, that a `put()` rejected by the first open failure does not acknowledge data, and that a later `put()` can retry, write, and verify one content-addressed block.

Non-claims: this is not cross-browser coverage, browser storage durability, fsync durability, crash/power-loss recovery, quota or eviction survival, multi-tab atomicity, Web Locks fairness, production readiness, or adversarial tamper resistance. It only prevents BrowserRT from permanently poisoning its own cached OPFS open promise after a failed root/prefix open attempt.
