# Browser OPFS Web Lock quarantine lane-filter import guard slice

Current rev0084 browser proof: `browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof`.

Managed Chromium lane-filtered import proof uses real OPFS, real Web Locks, `WebLockGuardedBlockStore`, and `BlockStoreLaneAdapter`. It rejects wrong-lane timeout-quarantine import, rejects accidental mixed-lane partial import by default, then proves that explicit `allowPartialImport: true` forces backpressure, rejects a follow-on write without mutation, permits reviewed/scoped clearing, explicitly recovers, and verifies a later guarded OPFS write.

The proof keeps the browser-heavy check explicit and keeps the release harness protected by the browser-light scheduler proof.

Non-claims: managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior, no provider cancellation, no rollback, no durability, no quota/eviction survival, no persistent-storage retention, no latency SLO, and no production-readiness claim.
