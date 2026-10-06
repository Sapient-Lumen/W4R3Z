# Storage-lane Web Lock timeout health slice — rev0062

## Purpose

This slice closes the gap between the browser Web Lock timeout proof and storage-lane backpressure. Before rev0062, BrowserRT could classify a guarded OPFS/Web Locks acquisition timeout as `BRT_WEB_LOCK_TIMEOUT`, but the storage lane only treated storage/OPFS provider failures as lane-health failures. A guarded block-store used behind a storage-lane adapter could therefore fail an operation without automatically putting the storage lane into no-mutation backpressure.

## Executable proof

Run:

```bash
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-web-lock-timeout-health-proof --jobs 1
```

Direct command:

```bash
node tools/storage_lane_web_lock_timeout_health_probe.mjs --json artifacts/validation/REV0062-STORAGE-LANE-WEB-LOCK-TIMEOUT-HEALTH-PROBE.json
```

The proof uses a synthetic WebLockGuardedBlockStore-shaped provider that throws `BRT_WEB_LOCK_TIMEOUT` on the first scheduled write. It verifies that:

- `StorageLaneExecutor` treats `BRT_WEB_LOCK_TIMEOUT` as a provider-health failure;
- the `storage` lane is marked unhealthy with `healthReason === "BRT_WEB_LOCK_TIMEOUT"`;
- a follow-on storage write is rejected as `rejected-lane-unhealthy` with `noMutation: true`;
- a maintenance fallback snapshot can still route while storage is unhealthy;
- explicit recovery marks the storage lane healthy and a later write succeeds.

## Runtime change

`src/storage-lane-scheduler.mjs` now classifies these guarded-provider coordination failures as storage-lane health failures:

```text
BRT_WEB_LOCK_TIMEOUT
BRT_WEB_LOCKS_UNAVAILABLE
```

This is intentionally narrower than all Web Lock errors. `BRT_WEB_LOCK_ABORTED` remains caller-cancellation territory for this slice and is not claimed as a provider-health failure.

## Why this matters

A Web Lock timeout around OPFS is not just a rejected Promise. It means the storage provider could not enter the coordinated mutation boundary in time. Treating that as backpressure prevents the next storage write from queueing blindly into the same obstructed lane.

## Non-claims

No browser Web Locks conformance claim; browser behavior is covered by explicit managed Chromium browser proofs. No automatic recovery claim. No fairness, starvation-freedom, cross-browser, mobile/background, service-worker, OPFS durability, fsync, power-loss, crash, quota, organic eviction, persistent-retention, throughput, latency, SLO, exactly-once, distributed-lock, or production readiness claim.
