# Storage-lane Web Lock settled recovery slice — rev0063

## Current claim

`scheduler:storage-lane-web-lock-settled-recovery-proof` is the browser-light regression guard for the rev0063 recovery policy. It uses an abort-aware fake Web Locks implementation and a memory block store to prove that a guarded store timeout becomes storage-lane backpressure, that the lane does not recover while the guarded store still reports held or pending lock rows, and that explicit maintenance-driven `recoverWhenStoreSettled()` reopens the lane only after the guarded store reports settled coordination state.

This proof keeps the normal release harness fast while still testing the runtime contract that the browser proof relies on.

## Evidence command

```bash
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-web-lock-settled-recovery-proof --jobs 1 --json artifacts/validation/REV0063-STORAGE-LANE-WEB-LOCK-SETTLED-RECOVERY-RUN.json
```

The direct probe output is `artifacts/validation/REV0063-STORAGE-LANE-WEB-LOCK-SETTLED-RECOVERY-PROBE.json`.

## Expected observations

The evidence should show:

- a fake holder keeping the guarded store contended;
- a scheduled storage-lane put timing out as `BRT_WEB_LOCK_TIMEOUT`;
- the storage lane becoming unhealthy;
- a follow-on put rejected as `rejected-lane-unhealthy` with no mutation;
- explicit maintenance-driven recovery refusing to clear the lane while the guard is still contended;
- recovery succeeding only after held/pending lock rows drain;
- a later scheduled write succeeding and verifying;
- the timed-out digest remaining absent.

## Non-claims

No automatic recovery. No browser lifecycle claim. No cross-browser Web Locks claim. No cross-browser OPFS claim. No OPFS durability, fsync, crash, power-loss, quota, eviction, persistent-storage, throughput, latency, SLO, or production readiness claim. The browser-light guard proves scheduler/adapter policy only; it does not replace the managed-Chromium proof.
