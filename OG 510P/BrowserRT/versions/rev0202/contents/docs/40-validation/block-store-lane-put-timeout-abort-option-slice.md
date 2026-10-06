# rev0105 block-store lane put timeout abort option slice

This slice closes a scheduled block-store cancellation gap: `BlockStoreLaneAdapter.schedulePut(...)` now forwards the per-operation scheduler control `abortProviderOnOperationTimeout` into `StorageLaneExecutor.scheduleOperation(...)`. Before this change, scheduled `put` calls could only use the adapter/executor default. A caller could opt in or opt out on a specific `schedulePut`, but that intent was silently dropped at the adapter boundary.

## Runtime claim

`abortProviderOnOperationTimeout: true` on a single scheduled put now injects the timeout-owned provider `AbortSignal` even when the adapter default is false. `abortProviderOnOperationTimeout: false` on a single scheduled put now suppresses the timeout-owned provider `AbortSignal` even when the adapter default is true.

The option remains a scheduler control. It must not leak into the provider option bag as a provider-specific key.

## Evidence

Release proof: `tools/block_store_lane_put_timeout_abort_option_probe.mjs`.

It checks:

- per-put opt-in receives a timeout-owned provider signal and records `providerTimeoutAborts`;
- per-put opt-out suppresses the provider signal and allows a late provider success quarantine row;
- the scheduler control option does not appear in provider option keys;
- existing timed-out-operation quarantine settlement remains in force.

## Non-claims

This does not make provider cancellation default. Abort remains cooperative. Providers that ignore `AbortSignal` can still mutate late and require quarantine review. This proof does not claim cross-browser conformance, quota reservation, eviction survival, fsync durability, crash or power-loss recovery, Web Locks fairness, or production readiness.
