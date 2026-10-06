# Storage Lane Provider Timeout Abort Slice (rev0103)

Rev0103 adds an opt-in provider cancellation boundary for storage-lane operation timeouts.

Before this slice, `StorageLaneExecutor` bounded a scheduled operation by racing the provider promise against `operationTimeoutMs`, but it did not provide a timeout-owned `AbortSignal` to the provider. That was intentional for older providers, but it left the recent OPFS `signal` support underused: a timed-out scheduled OPFS write could continue as late provider mutation and then require quarantine review.

The new behavior is explicit and compatibility-preserving:

- `abortProviderOnOperationTimeout` defaults to `false`.
- When enabled on the executor, adapter, or individual scheduled operation, the timeout context includes `signal` and `abortSignal` from a timeout-owned `AbortController`.
- On timeout, the executor aborts that signal, emits `storage-lane:operation-timeout` with `cancellation: true`, increments `providerTimeoutAborts`, and still returns `BRT_STORAGE_OPERATION_TIMEOUT` to the scheduler boundary.
- Providers remain cooperative. A provider that ignores the signal may still settle late and must still pass through timed-out-operation quarantine.
- `BlockStoreLaneAdapter` lets scheduler context signal override caller provider options so timeout-owned cancellation cannot be accidentally dropped at the scheduled block-store boundary.

The release proof in `tools/storage_lane_provider_timeout_abort_probe.mjs` checks both sides of the contract: default storage-lane timeout remains non-cancelling, while opt-in OPFS timeout abort causes the raw OPFS provider to observe `BRT_OPFS_OPERATION_ABORTED`, abort the writer, roll back the unacknowledged file path, quarantine the late failed provider settlement, and recover only after review/clear.

## Non-claims

This is not a universal cancellation guarantee. It does not prove that arbitrary providers honor `AbortSignal`, nor does it claim OPFS fsync durability, browser quota/eviction survival, crash recovery, cross-browser conformance, Web Locks fairness, or production readiness.
