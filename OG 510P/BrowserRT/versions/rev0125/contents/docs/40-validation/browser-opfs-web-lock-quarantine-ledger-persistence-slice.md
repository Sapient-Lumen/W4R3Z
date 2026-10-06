# Browser OPFS/Web Lock quarantine ledger persistence slice

Task: `browser:opfs-web-lock-quarantine-ledger-persistence-proof`

rev0075 turns quarantine-ledger persistence into a narrow managed-Chromium proof while preserving the rev0074 fail-closed ledger-integrity proof as carried-forward sidecar evidence. The proof uses real OPFS, real Web Locks, the guarded block-store wrapper, and the storage-lane adapter.

Launch 1 creates mixed late timeout outcomes through guarded OPFS writes, waits for one late success and one late failure, persists the resulting timeout-quarantine ledger as a content-addressed OPFS block, and then shuts Chromium down while preserving the profile.

Launch 2 reuses the same profile and same origin, verifies the persisted ledger block and original OPFS blocks are still present, restores the valid ledger into a fresh adapter, confirms the lane remains unhealthy and rejects follow-on mutation, then recovers only after reviewed/scoped clearing and verifies a later guarded OPFS write. The separate release-tier persistence proof also checks malformed persisted-ledger restore failure; the carried browser integrity proof checks malformed ledger rejection against real OPFS/Web Locks import state.

Non-claims: managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim, no fsync durability, no power-loss safety, no organic quota or eviction survival, no crash safety, no automatic recovery, no provider cancellation, no rollback, no no-mutation-after-dispatch guarantee, no exactly-once semantics, no latency SLO, and no production readiness.

Managed Chromium note: this browser proof is explicit browser-tier evidence using managed Chromium/CDP, not a cross-browser claim.
