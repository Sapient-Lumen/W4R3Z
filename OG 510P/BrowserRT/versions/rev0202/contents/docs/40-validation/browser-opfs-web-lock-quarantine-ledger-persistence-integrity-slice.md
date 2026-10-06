# Browser OPFS/Web Lock quarantine ledger persistence-integrity slice

Task: `browser:opfs-web-lock-quarantine-ledger-persistence-integrity-proof`

Managed Chromium / managed Chromium coverage: rev0075 turns the provider-backed timeout-quarantine persistence boundary into a managed Chromium proof. It uses real OPFS, real Web Locks, the guarded block-store wrapper, and the storage-lane adapter.

Launch 1 creates mixed late timeout outcomes through guarded OPFS writes, waits for one late success and one late failure, persists the resulting timeout-quarantine ledger as a content-addressed OPFS block, and closes Chromium while preserving the profile.

Launch 2 reuses the same profile and origin for a same profile browser restart. It verifies the original OPFS data and persisted ledger block survived the clean restart, writes a malformed persisted ledger block, verifies restore rejection is fail-closed/atomic, then restores the valid persisted ledger into a fresh adapter. The fresh adapter remains backpressured until the late-success and late-failure rows are reviewed/scoped and cleared, after which a guarded OPFS recovery write verifies.

Non-claims: Managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim, no cryptographic attestation, no tamper-proof ledger storage, no fsync durability, no crash or power-loss safety, no quota or eviction survival, no automatic recovery, no no-mutation-on-timeout claim, no exactly-once semantics, no throughput/latency SLO, and no production readiness.
