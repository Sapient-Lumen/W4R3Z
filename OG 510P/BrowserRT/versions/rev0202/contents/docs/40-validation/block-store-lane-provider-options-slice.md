# rev0102 block-store lane provider-options slice

Current release task: `storage:block-store-lane-provider-options-proof`.

This slice closes a scheduled-path runtime gap: `BlockStoreLaneAdapter` now preserves explicit provider option bags when it dispatches operations through `StorageLaneExecutor`. The affected bags are `providerOptions`, `storeOptions`, and operation-specific bags such as `putOptions`, `getOptions`, `hasOptions`, `verifyOptions`, `deleteOptions`, `estimateOptions`, and `cleanupOptions`.

The risk was practical rather than doctrinal. Newer raw OPFS safety knobs such as `writeBudgetGuard` and caller abort `signal` were available on `OpfsAsyncBlockStore`, but a caller using the scheduled lane adapter could silently lose those options before the provider call. That made the scheduled path weaker than the raw provider path.

The proof checks that an impossible `writeBudgetGuard` supplied through `providerOptions` rejects a scheduled `put()` before OPFS mutation, that a named `putOptions.writeBudgetGuard = false` override can intentionally disable that inherited guard, that a pre-aborted `providerOptions.signal` reaches a scheduled read, and that all named operation bags are delivered to a recording store.

Non-claims: this does not prove quota reservation, eviction survival, crash or power-loss durability, fsync durability, cross-browser conformance, Web Locks fairness, or production readiness. It only proves option pass-through and local scheduled-path behavior for the exercised release harness.
