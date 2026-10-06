# rev0104 browser storage-lane composite AbortSignal slice

Current browser task: `browser:composite-abort-signal-proof`.

## What changed

The managed Chromium proof exercises the rev0104 composite AbortSignal path with caller AbortSignal and timeout-owned AbortSignal evidence with real OPFS and Web Locks.

The key browser risk was narrow but important: scheduled OPFS calls with `abortProviderOnOperationTimeout: true` could mask a caller's already-aborted `providerOptions.signal`. The browser proof verifies that the caller pre-abort reaches real OPFS before digest/open/mutation, and that this path does not enter storage-lane timeout quarantine.

## Evidence

`tools/browser_storage_lane_composite_abort_signal_probe.mjs` checks:

- a pre-aborted caller signal rejects scheduled real-OPFS `put()` as `BRT_OPFS_OPERATION_ABORTED` at `before-digest`;
- the proof prefix remains empty, with no files/directories created by the rejected call;
- executor timeout counters remain zero for the caller-abort case;
- a live caller signal composed with timeout-owned cancellation still allows a normal scheduled OPFS write/verify/read;
- guarded OPFS/Web Locks smoke still verifies and drains locks.

## Non-claims

Managed Chromium only. This does not claim Firefox/Safari conformance, cross-browser lock fairness, quota reservation, eviction survival, fsync durability, crash/power-loss recovery, multi-tab atomicity, or production readiness. Abort remains cooperative.
