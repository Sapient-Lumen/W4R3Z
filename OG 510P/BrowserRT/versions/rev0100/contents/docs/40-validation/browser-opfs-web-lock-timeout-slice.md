# Browser OPFS Web Lock timeout slice — rev0062

## Purpose

rev0062 adds a bounded-wait backstop for BrowserRT Web Lock guarded storage operations. rev0060 proved that two same-origin dedicated workers can serialize real OPFS content-addressed mutations through `WebLockGuardedBlockStore`. The remaining risk was that a pending guarded mutation could wait forever behind a held Web Lock and silently stall a storage lane or application-level workflow.

This slice proves the corrective behavior:

- `WebLockCoordinator` accepts `timeoutMs` / `defaultTimeoutMs` and uses an `AbortSignal` to cancel a lock request while it is still pending.
- Timeout rejection is classified as `BRT_WEB_LOCK_TIMEOUT`.
- External cancellation is classified as `BRT_WEB_LOCK_ABORTED`.
- `WebLockGuardedBlockStore` forwards `lockTimeoutMs` and emits timeout-bearing operation traces.
- A timed-out guarded OPFS `put()` does not enter the mutation callback and therefore does not write the candidate block.
- After the holder releases the lock, a later guarded OPFS write succeeds and verifies.

## Evidence

Browser-heavy proof:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-timeout-proof --jobs 1 --json artifacts/validation/REV0062-BROWSER-OPFS-WEB-LOCK-TIMEOUT-RUN.json
```

Direct probe:

```bash
node tools/browser_opfs_web_lock_timeout_probe.mjs --json artifacts/validation/REV0062-BROWSER-OPFS-WEB-LOCK-TIMEOUT-PROBE.json
```

Browser-light release guard:

```bash
node tools/run_tests.mjs --tier release --id coord:web-lock-timeout-proof --jobs 1 --json artifacts/validation/REV0062-WEB-LOCK-TIMEOUT-RUN.json
```

Contract audit:

```bash
node tools/web_lock_timeout_contract_audit.mjs --json artifacts/audit/REV0062-WEB-LOCK-TIMEOUT-CONTRACT-AUDIT.json
```

## Browser proof shape

The managed Chromium proof uses one local origin and one shared BrowserRT Web Lock name.

1. A dedicated worker creates an OPFS async block store and a `WebLockGuardedBlockStore` with the shared lock.
2. The worker enters `withExclusive()`, writes and verifies a holder OPFS block under the lock, then waits for the main page to release it.
3. The main page creates another guarded OPFS store with the same lock name and `lockTimeoutMs`.
4. The main page attempts a guarded `put()` while the worker still holds the lock.
5. The pending request aborts through `AbortSignal` and rejects as `BRT_WEB_LOCK_TIMEOUT`.
6. The worker is released.
7. The main page verifies the holder block, confirms the timed-out candidate digest is absent, performs a recovery guarded write, verifies it, cleans the namespace, and checks `navigator.locks.query()` for zero held/pending locks.

## Runtime trace requirements

The timeout path must emit:

- `coord:web-lock-timeout-arm`
- `coord:web-lock-timeout-fired`
- `coord:web-lock-timeout`
- `storage:opfs-web-lock-guard-op-error`

The recovery path must still emit normal lock acquisition/release and OPFS block put/verify/cleanup trace events.

## Non-claims

This slice is intentionally narrow. It does not claim cross-browser Web Locks behavior, cross-browser OPFS behavior, fairness, starvation freedom, mobile/background lifecycle safety, service-worker coordination, exactly-once semantics, distributed locking, Storage Buckets behavior, OPFS durability, fsync behavior, power-loss safety, organic low-disk eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.

The timeout is an acquisition backstop only. It does not cancel work after a lock has already been granted; the callback must still implement its own cancellation if post-acquisition work needs to stop early.

Additional non-claims: this slice does not test quota pressure, eviction behavior, crash recovery, or organic low-disk behavior.
