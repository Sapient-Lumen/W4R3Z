# Browser OPFS Web-Lock tab-timeout slice — rev0062

`browser:opfs-web-lock-tab-timeout-proof` is the next risky lifecycle/storage boundary after the worker-only timeout proof. It uses managed Chromium/CDP, BrowserRT's `WebLockGuardedBlockStore`, actual OPFS writes, and two same-origin page targets.

The proof sequence is deliberately narrow:

1. The main page cleans the OPFS test namespace and verifies the named Web Lock is settled.
2. CDP opens a same-origin holder tab.
3. The holder tab acquires the BrowserRT exclusive Web Lock and writes/verifies an acknowledged OPFS content-addressed block while keeping the lock callback open.
4. The main page starts a guarded OPFS `put()` with `lockTimeoutMs` against the same lock.
5. `navigator.locks.query()` must show one held exclusive lock and one pending exclusive request while the holder tab is open.
6. The main-page guarded write aborts as `BRT_WEB_LOCK_TIMEOUT` before the provider mutation runs.
7. The holder tab still holds the lock after the timeout, proving the timeout did not steal or release the granted holder lock.
8. CDP closes the holder tab.
9. A final guarded store verifies the holder block, verifies the timed-out digest is absent, writes/verifies a recovery block, cleans the namespace, and waits until there are zero held/pending lock rows.

This is a multi-page boundary proof, not a generalized browser lifecycle theorem. It does not claim cross-browser Web Locks behavior, cross-browser OPFS behavior, mobile/background suspension safety, service-worker coordination, fairness, starvation freedom, exactly-once semantics, distributed locking, OPFS durability, fsync behavior, power-loss safety, organic eviction survival, quota survival, persistent-storage retention, throughput, latency, SLOs, or production readiness.

Run the current browser proof explicitly:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-tab-timeout-proof --jobs 1 --json artifacts/validation/REV0062-BROWSER-OPFS-WEB-LOCK-TAB-TIMEOUT-RUN.json
```

Carry-forward related browser proofs:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-tab-termination-proof,browser:opfs-web-lock-timeout-proof,browser:opfs-web-lock-guarded-contention-proof --jobs 1
```


Non-claim reminder: this slice does not prove cross-browser behavior, quota behavior, eviction survival, or crash/power-loss durability.

Final state requirement: the proof must end with zero held and zero pending Web Lock rows.
