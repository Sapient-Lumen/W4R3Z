# rev0104 storage-lane composite AbortSignal slice

Current release task: `storage:composite-abort-signal-proof`.

## What changed

`BlockStoreLaneAdapter` now composes caller AbortSignal / abortSignal provider cancellation with the timeout-owned AbortSignal provider signal created by `abortProviderOnOperationTimeout`.

Before this slice, enabling timeout-owned provider cancellation could overwrite `providerOptions.signal` / `providerOptions.abortSignal`. That meant a pre-aborted caller signal could be masked by the scheduler's still-live timeout signal, allowing a scheduled OPFS write to continue instead of failing before digest/open/mutation.

The adapter now uses a composite AbortSignal when both cancellation sources are present. The provider receives the same composed signal on `signal` and `abortSignal`, plus non-contract observability booleans `compositeAbortSignal` and `providerSignalComposed`. Invalid caller signal shapes are preserved for the provider to reject instead of being hidden by a scheduler context signal.

## Evidence

`tools/storage_lane_composite_abort_signal_probe.mjs` checks four runtime cases:

1. a pre-aborted caller signal reaches scheduled fake-OPFS `put()` before digest/open/mutation and leaves zero directories/files;
2. a caller abort that fires before the operation timeout rejects as caller/provider abort, with no timeout quarantine or provider-timeout-abort counter;
3. a distinct caller `abortSignal` composes alongside `signal` and can abort before the timeout;
4. the timeout-owned abort still fires when the caller supplied a live signal that never aborts.

## Non-claims

This release proof uses fake OPFS and recording providers. It does not prove cross-browser behavior, quota reservation, eviction survival, fsync durability, crash/power-loss recovery, Web Locks fairness, or production readiness. Abort remains cooperative: a provider that ignores AbortSignal can still settle late and require quarantine review.
