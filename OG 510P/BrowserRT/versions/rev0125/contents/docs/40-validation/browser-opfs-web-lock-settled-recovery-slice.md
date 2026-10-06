# Browser OPFS Web Lock settled recovery slice — rev0063

## Current claim

`browser:opfs-web-lock-settled-recovery-proof` proves a narrow managed-Chromium recovery boundary for BrowserRT guarded OPFS writes. A same-origin holder tab acquires the BrowserRT Web Lock and writes a real OPFS content-addressed block. The main page schedules a guarded OPFS write through the storage-lane adapter, observes the pending lock state, times out as `BRT_WEB_LOCK_TIMEOUT`, marks the storage lane unhealthy, and refuses an immediate follow-on mutation. While the holder tab still owns the lock, explicit maintenance recovery is blocked. After CDP closes the holder page and the guarded store reports zero held and pending lock rows, explicit maintenance-driven `recoverWhenStoreSettled()` reopens the lane and a later guarded OPFS write verifies successfully.

This is the substance added in rev0063: recovery is tied to observed same-origin lock-settlement state rather than blindly clearing storage-lane backpressure after a timeout.

## Evidence command

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-settled-recovery-proof --jobs 1 --json artifacts/validation/REV0063-BROWSER-OPFS-WEB-LOCK-SETTLED-RECOVERY-RUN.json
```

The probe itself writes `artifacts/validation/REV0063-BROWSER-OPFS-WEB-LOCK-SETTLED-RECOVERY-PROBE.json` when run directly.

## Expected observations

The evidence should show:

- one held Web Lock and one pending Web Lock while the main-page storage-lane write is queued behind the holder page;
- timeout classification as `BRT_WEB_LOCK_TIMEOUT`;
- `rejected-lane-unhealthy` for a follow-on write while the lane remains unhealthy;
- blocked recovery while the holder page still owns the lock;
- `Target.closeTarget`/page-close cleanup of the holder page;
- zero held and pending locks after settlement;
- explicit maintenance-driven lane recovery;
- verified holder and recovery OPFS blocks;
- absence of the timed-out candidate block.

## Non-claims

No automatic recovery. No cross-browser Web Locks claim. No cross-browser OPFS claim. No mobile/background tab lifecycle claim. No service-worker lifecycle claim. No Web Locks fairness or starvation-freedom claim. No OPFS durability, fsync, crash, power-loss, or transactional recovery claim. No organic quota, eviction, persistent-storage, throughput, latency, SLO, or production readiness claim. The browser-light release guard is the scheduler policy regression proof; this browser slice is the managed-Chromium lifecycle proof only.
