# Browser OPFS/Web Lock quarantine clearance replay-key receipt integrity slice

Current browser proof: `browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof`.

Managed Chromium proof phrase anchor. The proof uses real OPFS, real Web Locks, `WebLockGuardedBlockStore`, and `BlockStoreLaneAdapter`. It imports synthetic timeout-quarantine rows into a storage-lane adapter over a guarded OPFS block store, clears the mixed rows, and creates a clearance receipt. The receipt must carry the exact cleared row `operationReplayKeys`; missing/extra replay keys and row-inconsistent replay-key metadata fail validation and registration. The valid receipt still rejects stale quarantine replay, and a later guarded OPFS write verifies.

## Non-claims

Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim. No provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction survival, cryptographic attestation, tamper-proof storage, or production readiness claim.
