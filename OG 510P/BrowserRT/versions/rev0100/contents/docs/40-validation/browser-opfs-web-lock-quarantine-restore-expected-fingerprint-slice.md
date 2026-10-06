# Browser OPFS/Web Lock quarantine restore expected fingerprint slice

Task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`

This Managed Chromium proof exercises the expected-fingerprint restore gate against real OPFS and Web Locks. It persists two timeout-quarantine ledgers and two clearance receipts through `WebLockGuardedBlockStore` over `OpfsAsyncBlockStore`, then attempts restore with deliberately mismatched expected fingerprints.

The proof verifies that a valid OPFS-backed but unintended quarantine ledger rejects before import, a valid OPFS-backed but unintended clearance receipt rejects before registration, and a receipt with the correct receipt fingerprint but wrong pre-clearance fingerprint rejects as well. It then restores the intended ledger/receipt, confirms stale quarantine replay is rejected, verifies a later guarded OPFS write, and drains final Web Lock state to zero.

This is managed Chromium/CDP evidence only. It does not claim cross-browser behavior, cryptographic attestation, tamper-proof storage, provider cancellation, rollback, no-mutation-on-timeout, OPFS durability/fsync behavior, quota survival, eviction survival, throughput, latency SLOs, or production readiness.


rev0093 update: blank expected-fingerprint restore intent now fails closed before decode/import/registration; whitespace is not treated as an omitted pin. The release and Managed Chromium proofs share assertion coverage through `tools/lib/quarantine_restore_expected_fingerprint_harness.mjs`. This is still operator intent checking, not cryptographic attestation or tamper-proof storage.
