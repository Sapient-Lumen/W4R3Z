# Browser OPFS/Web Lock quarantine clearance replay guard slice — rev0079

Current browser proof: `browser:opfs-web-lock-quarantine-clearance-replay-guard-proof`.

The managed Chromium proof exercises real OPFS, real Web Locks, the guarded OPFS block-store wrapper, and the storage-lane adapter. Launch 1 creates guarded OPFS writes that time out at the storage-lane level and later settle as one success and one failure. It exports the stale timeout-quarantine ledger, clears the quarantine with a bound review manifest, persists a clearance receipt as a guarded OPFS block, and verifies a post-clear guarded write.

Launch 2 relaunches the same browser profile and origin, restores the persisted clearance receipt, then attempts to import the stale pre-clearance ledger. The import is rejected as `rejected-cleared-quarantine-replay`; the fresh lane remains healthy, the quarantine remains empty, malformed receipt restoration is rejected, and a later guarded OPFS write verifies.

Non-claims: managed Chromium/CDP only. This is not cross-browser Web Locks or OPFS behavior, not cryptographic ledger attestation, not tamper-proof storage, not provider cancellation or rollback, not OPFS durability/fsync/crash/power-loss evidence, not quota/eviction survival, and not production readiness.

Managed Chromium same profile proof note: this is not cross-browser evidence.
