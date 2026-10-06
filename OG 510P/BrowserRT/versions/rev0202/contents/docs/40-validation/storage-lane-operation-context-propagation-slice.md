# Storage-lane operation context propagation slice — rev0073

Current release-tier proof: `scheduler:storage-lane-operation-context-propagation-proof`.

This slice fixes and guards a concrete runtime bug found after the late-success quarantine work: `BlockStoreLaneAdapter` accepted an executor context containing `operationTimeoutMs`, but its wrapper called the provider callback as `run()` instead of `run(context)`. That meant a storage provider or guarded store could not observe the operation budget that the scheduler had assigned.

The rev0073 runtime fix makes the adapter pass executor context into block-store callbacks, then verifies that `operationTimeoutMs` reaches a provider through `WebLockGuardedBlockStore` for `put`, `get`, `has`, `verify`, `estimate`, `delete`, and `cleanupForTest`.

This is not provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, latency, throughput, SLO, or production-readiness evidence. Operation timeout remains a scheduler/backpressure boundary; provider context propagation only gives providers enough information to cooperate or record budget-aware telemetry.

This slice is also not durability evidence; it only proves provider option propagation.

Audit nonclaims: cross-browser, quota, eviction, crash, browser-light.
