# Browser Storage Lane Provider Timeout Abort Slice (rev0103)

This managed Chromium proof exercises rev0103's opt-in provider timeout abort through real browser OPFS and Web Locks surfaces.

`tools/browser_storage_lane_provider_timeout_abort_probe.mjs` launches a managed Chromium page, imports `src/browserrt.mjs`, creates a real `OpfsAsyncBlockStore`, and schedules a put through `BlockStoreLaneAdapter` with `abortProviderOnOperationTimeout: true`. The page temporarily wraps `FileSystemFileHandle.prototype.createWritable` so the operation deterministically times out after the file handle is opened but before bytes are acknowledged. The timeout-owned signal reaches the OPFS provider, `writable.abort()` is called, rollback removes the unacknowledged `.blk` file, and the proof confirms the prefix contains no block files or block bytes.

The browser proof also verifies that the late provider abort remains quarantined as a failed timed-out operation until reviewed and cleared. After recovery, a scheduled OPFS write succeeds, and a separate Web-Lock-guarded OPFS smoke path writes, verifies, cleans up, and drains held/pending locks.

## Non-claims

This is a focused Chromium proof. It does not claim cross-browser or Firefox/Safari conformance, browser quota reservation, eviction survival, OPFS fsync durability, crash/power-loss recovery, Web Locks fairness, multi-tab atomicity, or production readiness.
