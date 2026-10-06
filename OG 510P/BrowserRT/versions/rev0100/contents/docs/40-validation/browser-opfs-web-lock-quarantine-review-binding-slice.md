# Browser OPFS/Web Lock quarantine review binding slice — rev0076

Current browser proof: `browser:opfs-web-lock-quarantine-review-binding-proof`.

Managed Chromium only. The proof uses real OPFS, real Web Locks, `WebLockGuardedBlockStore`, `BlockStoreLaneAdapter`, and the storage-lane timeout-quarantine path. Two guarded OPFS writes time out at the lane boundary but later settle as one late success and one late failure. The proof then exports a timeout-quarantine ledger with `quarantineFingerprint` / `reviewFingerprint`, rejects a tampered ledger, imports the valid ledger into a fresh adapter, rejects missing/stale review fingerprints, clears using a review manifest bound to the current fingerprint, and verifies a later guarded OPFS write after explicit recovery.

The fingerprint is deterministic review binding for this cube's maintenance handoff; it is not cryptographic attestation and not a tamper-proof storage guarantee. The proof also does not claim rollback or provider cancellation.

## Non-claims

No cross-browser OPFS/Web Locks behavior, no mobile/background lifecycle claim, no OPFS fsync durability, no power-loss safety, no crash safety, no quota survival, no eviction survival, no persistent-storage retention, no no-mutation-on-timeout claim, no exactly-once semantics, no throughput/latency SLO, and no production readiness.
