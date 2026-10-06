# rev0106 Web Lock guarded AbortSignal slice

## What changed

`WebLockGuardedBlockStore` now treats direct guarded caller cancellation as a first-class boundary. The direct guarded API accepted both `signal` and `abortSignal` option names, but the lock acquisition path only routed `signal` to `WebLockCoordinator`, while the provider path did not receive a composed `signal` / `abortSignal` pair. Rev0106 composes valid caller signals, sends the composed signal to the Web Lock request, and forwards the same signal to the underlying block-store provider.

The slice also tightens `WebLockCoordinator` abort classification. External abort is now reported as `BRT_WEB_LOCK_ABORTED` only before a lock has been acquired. Once the lock callback is running, provider errors are preserved instead of being relabeled as lock-abort errors.

## Proof boundary

`tools/web_lock_guarded_abort_signal_probe.mjs` uses a fake queued Web Locks manager and a recording block store to prove:

- `abortSignal`-only pending guarded `put()` cancels before provider mutation;
- `abortSignal`-only `withShared()` cancels before the callback runs;
- dual `signal` + `abortSignal` is composed and reaches the provider as both option names;
- invalid `abortSignal` shapes are preserved for strict local validation and rejected before the lock manager is called;
- normal guarded writes still work after the abort cases.

## Non-claims

This is not a Web Locks fairness proof, cross-browser conformance proof, quota or eviction proof, crash/power-loss durability proof, fsync durability proof, or production readiness claim. Abort remains cooperative: the lock request and the OPFS provider must observe the signal for cancellation to prevent late mutation.
