# rev0105 browser block-store lane put timeout abort option slice

This managed Chromium proof checks the rev0105 `schedulePut` option-forwarding fix against real OPFS and the guarded OPFS/Web Locks smoke path.

## Browser evidence

Browser proof: `tools/browser_block_store_lane_put_timeout_abort_option_probe.mjs`.

It patches the real OPFS writable path to make timeout ordering deterministic, then verifies:

- per-put `abortProviderOnOperationTimeout: true` injects a timeout-owned `AbortSignal` with the adapter default set to false;
- the aborted real OPFS put leaves no final block file;
- per-put `abortProviderOnOperationTimeout: false` suppresses timeout-owned abort with the adapter default set to true;
- the non-aborted real OPFS put can complete late and is represented as a successful timed-out-operation row before cleanup;
- the guarded OPFS/Web Locks smoke path still writes, verifies, reads, cleans up, and drains locks.

## Non-claims

Managed Chromium is not cross-browser conformance. This proof does not claim Firefox/Safari behavior, exact quota prediction, quota reservation, organic eviction survival, persistent-storage retention, fsync durability, crash/power-loss recovery, Web Locks fairness, multi-tab atomicity, or production readiness.

Per-operation scheduled put timeout-abort behavior is the target boundary for this managed Chromium proof.
