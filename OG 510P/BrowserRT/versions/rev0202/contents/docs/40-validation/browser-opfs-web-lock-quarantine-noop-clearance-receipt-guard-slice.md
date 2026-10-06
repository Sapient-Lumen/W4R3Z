# Browser OPFS/Web Lock quarantine no-op clearance receipt guard slice — rev0080

Current browser slice: `browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof`.

## Risk targeted

The browser-backed maintenance path must reject a reviewed clear that matches zero timeout-quarantine rows before it can become a bogus clearance receipt for a still-active quarantine fingerprint.

## Managed Chromium proof

The proof uses real OPFS, real Web Locks, `WebLockGuardedBlockStore`, and `BlockStoreLaneAdapter` in managed Chromium. It imports a non-empty timeout-quarantine ledger, confirms backpressure is forced, tries a reviewed scope that matches no rows, verifies `timed-out-quarantine-clear-noop`, verifies zero-row clearance receipts are rejected, then performs a valid reviewed/scoped clear and a guarded OPFS recovery write.

Run:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof --jobs 1 --json artifacts/validation/REV0080-BROWSER-OPFS-WEB-LOCK-QUARANTINE-NOOP-CLEARANCE-RECEIPT-GUARD-RUN.json
```

## Non-claims

Managed Chromium/CDP only. This is not a cross-browser OPFS/Web Locks claim, not provider cancellation or rollback, not no-mutation-on-timeout, not exactly-once semantics, not OPFS fsync/durability evidence, and not quota, eviction, persistent-storage, throughput, latency SLO, or production-readiness evidence.
