# Browser OPFS guarded corrupt-repair + timeout slice — rev0062

## Purpose

`browser:opfs-guarded-corrupt-repair-timeout-proof` is a managed Chromium/CDP proof for the merged rev0062 storage/coordination boundary. It exists because two different rev0062 lines were produced during the session: one line repaired OPFS content-addressed corruption handling, and another line added Web Lock acquisition timeouts for guarded OPFS mutations. This slice verifies the two runtime changes work together instead of merely coexisting in registries.

## What it proves

The proof uses a real Chromium page with OPFS and Web Locks enabled. It creates a BrowserRT `OpfsAsyncBlockStore`, wraps it in `WebLockGuardedBlockStore`, then deliberately writes corrupt bytes into the final hash-named OPFS block path. The guarded store must reject that residue through `has()`, `verify()`, and `get()`, then repair it through a guarded exclusive `put()` before a later duplicate put can dedupe.

The same proof then holds the guarded store's exclusive Web Lock while a second guarded `put()` waits behind it with a short `lockTimeoutMs`. The pending request must reject as `BRT_WEB_LOCK_TIMEOUT`, the timed-out candidate must remain absent after the holder releases, `waitForSettled()` must report no held/pending lock rows, and a later guarded recovery write must verify.

## Evidence required

- `storage:opfs-block-corrupt`
- `storage:opfs-block-repair`
- `storage:opfs-block-write-close`
- `storage:opfs-block-integrity-ok`
- `coord:web-lock-timeout`
- `coord:web-lock-wait-settled-complete`
- corrupt block rejected as `BRT_OPFS_BLOCK_CHECKSUM_MISMATCH`
- pending guarded mutation rejected as `BRT_WEB_LOCK_TIMEOUT`
- timed-out candidate absent after the lock holder releases
- later guarded recovery write verifies

## Non-claims

This is a Chromium-in-cloudtainer proof only. It is not cross-browser Web Locks or OPFS conformance evidence. The corrupt final block is deliberately injected, not organic filesystem, crash, or power-loss evidence. The timeout bounds pending lock acquisition only; it does not cancel work after a lock has already been granted. It does not prove OPFS fsync durability, quota survival, eviction survival, persistent-storage retention, mobile/background lifecycle behavior, fairness, starvation-freedom, throughput, latency, SLOs, or production readiness.
