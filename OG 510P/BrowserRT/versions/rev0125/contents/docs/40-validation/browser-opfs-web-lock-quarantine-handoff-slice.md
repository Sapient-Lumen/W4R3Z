# Browser OPFS Web Lock quarantine handoff slice — rev0073

`browser:opfs-web-lock-quarantine-handoff-proof` is the managed-Chromium proof for the same boundary using real OPFS writes guarded by BrowserRT Web Locks.

The proof writes a real OPFS content-addressed block through `WebLockGuardedBlockStore`, times out at the storage-lane operation boundary, lets the provider settle successfully, exports the late-success quarantine ledger, imports it into a fresh adapter over the same guarded store, and verifies that the imported lane is unhealthy until the specific operation is reviewed and cleared.

The proof also checks that direct `markHealthy()` cannot bypass the imported quarantine and that later guarded OPFS writes verify after reviewed/scoped clearing and explicit recovery.

Non-claims: managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim, no automatic persistence of quarantine ledgers, no provider cancellation, no rollback, no no-mutation guarantee, no exactly-once semantics, no OPFS fsync durability, no power-loss safety, no quota or eviction survival, no throughput/latency SLO, and no production readiness.

Audit keywords: Managed Chromium proof, not prove cross-browser behavior, not cancellation, not rollback.

Crash recovery is also out of scope.
